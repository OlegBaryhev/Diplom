import {
  cloneDeep,
  differenceBy,
  isEqual,
} from 'lodash';

import { useModals } from '@/stores/modals';
import { isCancelError } from '@/api';
import { TABLE_ITEM_COUNT_TO_FETCH } from '@/consts';
import type { ItemChecking } from '@/common/components/tables/types';

export const useTable = <K extends string, T extends { [key in K]: number | string }>({
  primaryKey,
  getAllItemsRequest,
  getRecordCount,
  deleteItemsRequest,
  scrollerSelector,
  isOptimisticUpdate,
}: {
  primaryKey: K;
  getAllItemsRequest: (page: number, size: number, overwrite?: boolean) => Promise<{ newItems: T[] | null; actualTotal?: number }>;
  getRecordCount?: (signal?: AbortSignal) => Promise<{ actualTotal?: number }> | string;
  deleteItemsRequest?: (itemChecking: ItemChecking<T[K]>, total?: number) => Promise<void>;
  scrollerSelector?: string;
  isOptimisticUpdate?: boolean;
}) => {
  const modalStore = useModals();

  const items = shallowRef<T[]>([]);
  const itemsBeforeOptimisticUpdate = shallowRef<T[]>([]);
  const total = ref<number>(0);
  const page = ref<number>(1);
  const addCount = ref<number>(0);

  const loading = ref<boolean>(false);
  const totalLoading = ref<boolean>(false);

  const totalCount = ref<number | undefined>(0);
  let totalAbortController: AbortController | null = null;

  const error = ref<boolean>(false);
  const fetchItemsError = ref<unknown | null>(null);
  const appliedFilterData = ref<Record<string, any>>({});

  const worker = new Worker(new URL('@/common/workers/table-worker.worker.ts', import.meta.url), { type: 'module' });

  const defaultValue = {
    add: [],
    delete: {
      include: [],
      exclude: [],
      excludeAccepted: false,
    },
    edit: {
      include: [],
      exclude: [],
      template: null,
      excludeAccepted: false,
    },
  };

  const sevedTablesData = ref<{
    add: T[],
    delete: {
      include: T[],
      exclude: T[],
      excludeAccepted: boolean,
    },
    edit: {
      include: T[],
      exclude: T[],
      template: any,
      excludeAccepted: boolean,
    },
  }>(defaultValue);

  const ignoreAdd = ref<boolean>(false);
  const ignoreDelete = ref<boolean>(false);

  /** @todo ИСПРАВИТЬ БАГ пересечений include/exclude */
  const optimisticTotal = computed(() => {
    const addedItems = sevedTablesData.value.add;
    const deletedItems = sevedTablesData.value.delete.include;
    const excludedItems = sevedTablesData.value.delete.exclude;

    const addedNotDeleted = differenceBy(addedItems, deletedItems, primaryKey);
    const deletedNotAdded = differenceBy(deletedItems, addedItems, primaryKey);
    const excludedNotDeleted = differenceBy(excludedItems, deletedItems, primaryKey);

    return total.value + addedNotDeleted.length - deletedNotAdded.length + excludedNotDeleted.length;
  });

  const saveItem = (item: any, mode: 'include' | 'exclude' = 'include', template: Record<string, any> | null = null): void => {
    if (mode === 'exclude' && template) {
      sevedTablesData.value.edit.excludeAccepted = true;
      sevedTablesData.value.edit.template = template;
      sevedTablesData.value.edit.exclude = item;
    } else if (mode === 'include') {
      sevedTablesData.value.edit[mode].push(...(item instanceof Array ? item : [item]));
    }
  };

  const addItem = (item: any, id?: string): void => {
    const newItem = {
      [primaryKey]: item?.[primaryKey] ?? id ?? `${primaryKey}:${String(addCount.value).padStart(7, '0')}temp`,
      ...((!item?.[primaryKey] && !id) && { isAddedItem: true }),
      ...item,
    };
    if (!item?.[primaryKey] && !id) addCount.value++;
    sevedTablesData.value.add.push(...(newItem instanceof Array ? newItem : [newItem]));
  };

  if (isOptimisticUpdate) {
    worker.onmessage = (event: MessageEvent<{ types: string, values: T[]}>) => {
      const { type, values } = event.data;
      items.value = values;

      if (type === 'updateDelete') {
        if (event.data?.add && !isEqual(sevedTablesData.value?.add, event.data?.add)) {
          ignoreAdd.value = true;
          sevedTablesData.value.add = event.data?.add;
        }
        if (event.data?.deleteInclude && !isEqual(sevedTablesData.value?.delete?.include, event.data?.deleteInclude)) {
          sevedTablesData.value.delete.include = event.data?.deleteInclude;
        }
      }
    };

    worker.onerror = (err) => {
      console.error('Ошибка WebWorker:', err);
      error.value = true;
    };
  }

  watch(
    () => sevedTablesData.value.edit,
    (val) => {
      if (!isOptimisticUpdate) return;
      worker.postMessage({
        type: 'updateEdit',
        data: {
          items: cloneDeep(items.value),
          edit: cloneDeep(val),
          primaryKey,
        },
      } as WorkerMessage);
    },
    { deep: true },
  );

  watch(
    () => sevedTablesData.value.add,
    (val) => {
      if (!isOptimisticUpdate) return;
      if (!ignoreAdd.value) {
        worker.postMessage({
          type: 'updateAdd',
          data: {
            items: cloneDeep(items.value),
            add: cloneDeep(val),
            primaryKey,
          },
        } as WorkerMessage);
      } else {
        ignoreAdd.value = false;
      }
    },
    { deep: true },
  );

  watch(
    () => sevedTablesData.value.delete,
    (val, old) => {
      if (!isOptimisticUpdate) return;
      if (!ignoreDelete.value) {
        worker.postMessage({
          type: 'updateDelete',
          data: {
            items: cloneDeep(items.value),
            delete: cloneDeep(val),
            oldDelete: cloneDeep(old),
            primaryKey,
            add: cloneDeep(sevedTablesData.value.add),
          },
        } as WorkerMessage);
      } else {
        ignoreDelete.value = false;
      }
    },
    { deep: true },
  );

  const disableTemporaryItems = (): void => {
    items.value = items.value.map((el) => ('isTemporary' in el) ? ({ ...el, isTemporary: false }) : el);
    sevedTablesData.value.edit.exclude = [];
    sevedTablesData.value.edit.include = [];
    sevedTablesData.value.add = [];
    sevedTablesData.value.edit.excludeAccepted = false;
  };

  const fetchTotal = async (): Promise<void> => {
    if (!getRecordCount) {
      total.value = totalCount.value ?? 0;
      return;
    }

    totalLoading.value = true;
    try {
      if (totalAbortController) {
        totalAbortController?.abort();
        totalAbortController = null;
      }

      totalAbortController = new AbortController();

      const recordTotal = (await getRecordCount(totalAbortController.signal))?.actualTotal ?? totalCount.value;
      total.value = recordTotal ?? 0;
    } catch (err) {
      console.error('Неудачная загрузка количества записей');
      throw err;
    } finally {
      totalLoading.value = false;
    }
  };

  const fetchItems = async (overwriteList: boolean = false): Promise<void> => {
    let requestHasBeenCanceled = false;

    if (overwriteList) {
      loading.value = true;
      totalLoading.value = true;
      page.value = 1;
      error.value = false;

      sevedTablesData.value = defaultValue;

      if (totalAbortController) {
        totalAbortController?.abort();
        totalAbortController = null;
      }
    }

    fetchItemsError.value = null;

    try {
      const { newItems, actualTotal } = await getAllItemsRequest(page.value, TABLE_ITEM_COUNT_TO_FETCH, overwriteList);

      if (overwriteList) {
        const scrollerElement = scrollerSelector ? document.querySelector(scrollerSelector) : null;
        (scrollerElement ?? window).scrollTo({ top: 0 });
        items.value = [];
      }

      /** @See https://vuejs.org/guide/best-practices/performance.html#reduce-reactivity-overhead-for-large-immutable-structures */
      items.value = items.value.concat(newItems ?? []);
      itemsBeforeOptimisticUpdate.value = cloneDeep(items.value);
      totalCount.value = actualTotal;
      if (!getRecordCount) {
        total.value = totalCount.value ?? 0;
      }
    } catch (err) {
      fetchItemsError.value = err;

      if (isCancelError(err)) {
        requestHasBeenCanceled = true;
        throw err;
      }

      if (overwriteList) {
        error.value = true;
        items.value = [];
      } else console.error('Неудачная загрузка');

      throw err;
    } finally {
      if (overwriteList && !requestHasBeenCanceled) {
        loading.value = false;
      }
    }
    overwriteList && fetchTotal();
  };

  const detailedItem = ref<T | null>(null);
  const itemChecking = ref<ItemChecking<T[K]>>({ mode: 'include', ids: [] }) as Ref<ItemChecking<T[K]>>;

  const itemToDelete = ref<T | null>(null) as Ref<T | null>;

  const deleteItems = async (): Promise<void> => {
    if (!deleteItemsRequest) return;

    try {
      await deleteItemsRequest(itemChecking.value, total.value);

      if (isOptimisticUpdate) {
        if (!itemChecking.value.ids.length) return;

        if (itemChecking.value.mode === 'exclude') sevedTablesData.value.delete.excludeAccepted = true;
        sevedTablesData.value.delete[itemChecking.value.mode] = [...sevedTablesData.value.delete[itemChecking.value.mode].filter((el) => el?.[primaryKey]), ...itemChecking.value.ids];
      }

      !isOptimisticUpdate && (await fetchItems(true));
      itemChecking.value = { mode: 'include', ids: [] };
    } catch (err) {
      console.error('Неудачное множественное удаление');

      throw err;
    }
  };

  const deleteOnlyOneItem = async (): Promise<void> => {
    if (!(deleteItemsRequest && itemToDelete.value)) return;

    try {
      await deleteItemsRequest({ mode: 'include', ids: [itemToDelete.value[primaryKey]] });
      if (!isOptimisticUpdate) {
        await fetchItems(true);
        itemChecking.value.ids = itemChecking.value.ids.filter(
          (id) => id !== itemToDelete.value![primaryKey],
        );
      }
      if (isOptimisticUpdate) {
        sevedTablesData.value.delete.include.push(itemToDelete.value?.[primaryKey]);
      }
      itemToDelete.value = null;
    } catch (err) {
      console.error('Неудачное одиночное удаление');

      throw err;
    }
  };

  const isItemBeingAdded = ref(false);

  onUnmounted(() => {
    worker.terminate();
  });

  return {
    modalStore,
    items,
    total: isOptimisticUpdate ? optimisticTotal : total,
    page,
    loading,
    error,
    fetchItems,
    fetchItemsError,
    detailedItem,
    itemChecking,
    appliedFilterData,
    deleteItems,
    itemToDelete,
    deleteOnlyOneItem,
    isItemBeingAdded,
    saveItem,
    addItem,
    addCount,
    fetchTotal,
    totalLoading,
    disableTemporaryItems,
  };
};

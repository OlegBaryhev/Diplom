<template>
  <div
    class="advanced-flex-table-container"
    :class="{ 'advanced-flex-table-container--padded': areSomeItemsChecked }"
  >
    <VFlexTable
      class="advanced-flex-table"
      :column-headers="columnHeaders"
      :items="items"
      :item-id-key="itemIdKey"
      :row-height="rowHeight"
      :header-row-heigh="headerRowHeight"
      :has-dividing-line="hasDividingLine"
      :get-item-additional-props="(item: any) => ({
        ...(noActiveItemFunc ? {} : { tag: 'a', role: 'button' }),
        class: [
          'advanced-flex-table__row',
          { 'advanced-flex-table__row--active': item[itemIdKey] === activeItem?.[itemIdKey] },
          ...getItemAdditionalClasses(item),
        ],
      })"
      :get-item-additional-listeners="noActiveItemFunc ? undefined : (item: any) => ({
        click: () => $emit('update:activeItem', item),
      })"
      :item-checking="itemChecking"
      :loading="loading"
      :fetch-more-items-loading="fetchMoreItemsLoading"
      :skeleton-body-row-count="skeletonBodyRowCount"
      :large-skeleton="largeSkeleton"
      :scroller-buffer="scrollerBuffer"
      :disable-page-mode="disablePageMode"
      :custom-scroll="customScroll"
      :has-footer-buttons="hasFooterButtons"
      :actions-list="actionsList"
      @update:item-checking="$emit('update:itemChecking', $event)"
      @scroll-end="onScrollEnd"
      @action="$emit('action', $event);"
    >
      <template #default="{ item }: { item: any }">
        <slot :item="item" />
      </template>
    </VFlexTable>

    <Transition name="advanced-flex-table-bottom-panel">
      <div
        v-if="areSomeItemsChecked"
        class="advanced-flex-table-bottom-panel"
      >
        <p class="advanced-flex-table-bottom-panel__info">
          <span class="font-medium text-additional-300">Выбрано строк:</span>
          {{ formattedCheckedItemCount }} из {{ formattedTotal }}
        </p>

        <div class="advanced-flex-table-bottom-panel__actions">
          <slot
            name="checkedItemsActions"
            v-bind="mergedProcessCheckedItems"
            :on-uncheck-all="onUncheckAll"
            :on-select-checked="onSelectChecked"
          >
            <VBtn
              :text="mergedProcessCheckedItems.uncheckAllButtonText"
              outlined
              small
              data-test="uncheckAll"
              @click="onUncheckAll"
            />

            <VBtn
              :text="mergedProcessCheckedItems.actionButtonText"
              small
              :disabled="mergedProcessCheckedItems.isActionButtonDisabled"
              data-test="processCheckedItems"
              @click="onSelectChecked"
            />
          </slot>
        </div>
      </div>
    </Transition>

    <VLoader
      v-if="fetchMoreItemsLoading && !disablePageMode"
      class="advanced-flex-table-loader"
    />

    <VConfirmationModal
      v-if="itemChecking"
      id="processCheckedItemsModal"
      :title="mergedProcessCheckedItems.modalTitle"
      :text="mergedProcessCheckedItems.modalText"
      :confirmation-text="mergedProcessCheckedItems.actionButtonText"
      :async-confirmation-func="mergedProcessCheckedItems.func"
    />
  </div>
</template>

<script lang="ts" setup>
import { useModals } from '@/stores/modals';
import { formatNumber } from '@/common/utils/format';
import type {
  ColumnHeader,
  ItemChecking,
  ProcessCheckedItems,
} from './types';
import { TABLE_ITEM_COUNT_TO_FETCH } from '@/consts';

const DEFAULT_PROCESS_CHECKED_ITEMS = {
  uncheckAllButtonText: 'Сбросить выбранное',
  actionButtonText: 'Удалить',
  modalTitle: 'Удалить выбранное?',
  modalText: 'Строки будут удалены без возможности восстановления',
};

const modalStore = useModals();

// eslint-disable-next-line no-spaced-func
const props = withDefaults(defineProps<{
  columnHeaders: ColumnHeader[];
  items: any[];
  itemIdKey?: string;
  // eslint-disable-next-line func-call-spacing
  getItemAdditionalClasses?: (item: unknown) => (string | Record<string, any>)[];
  activeItem?: any;
  noActiveItemFunc?: boolean;
  itemChecking?: ItemChecking;
  processCheckedItems?: ProcessCheckedItems;
  loading?: boolean;
  skeletonBodyRowCount?: number;
  fetchingMoreItemsFunc?: (...args: any[]) => Promise<any>;
  total?: number;
  page?: number;
  scrollerBuffer?: number;
  disablePageMode?: boolean;
  rowHeight?: number;
  headerRowHeight?: number;
  hasDividingLine?: boolean;
  customScroll?: boolean;
  hasFooterButtons?: boolean;
  largeSkeleton?: boolean;
  actionsList?: any;
}>(), {
  itemIdKey: 'id',
  getItemAdditionalClasses: () => [],
  noActiveItemFunc: false,
  total: 0,
  page: 1,
  hasDividingLine: false,
  customScroll: false,
  hasFooterButtons: true,
  largeSkeleton: false,
  actionsList: [],
});

// eslint-disable-next-line func-call-spacing, no-spaced-func
const emit = defineEmits<{
  (evt: 'update:itemChecking', newItemChecking: ItemChecking): void;
  (evt: 'update:activeItem', newActiveItem: any): void;
  (evt: 'update:page', newPage: number): void;
  (evt: 'action', action: any): void;
}>();

const mergedProcessCheckedItems = computed(() => ({
  ...DEFAULT_PROCESS_CHECKED_ITEMS,
  ...(props.processCheckedItems ?? {}),
}));

const areSomeItemsChecked = computed(() => {
  if (!props.itemChecking) {
    return false;
  }

  return props.itemChecking.mode === 'include'
    ? props.itemChecking.ids.length > 0
    : props.itemChecking.ids.length !== props.items.length;
});

const formattedTotal = computed(() => formatNumber(props.total || props.items.length));
const formattedCheckedItemCount = computed(() => {
  if (!props.itemChecking) {
    return '';
  }

  const length = props.itemChecking.mode === 'include'
    ? props.itemChecking.ids.length
    : (props.total || props.items.length) - props.itemChecking.ids.length;

  return formatNumber(length);
});

const fetchMoreItemsLoading = ref<boolean>(false);

const onScrollEnd = async (): Promise<void> => {
  if (!props.fetchingMoreItemsFunc || props.items.length === props.total || props.items.length % TABLE_ITEM_COUNT_TO_FETCH !== 0) {
    return;
  }

  emit('update:page', props.page + 1);

  await nextTick();
  fetchMoreItemsLoading.value = true;

  try {
    await props.fetchingMoreItemsFunc();
  } catch (err) {
    console.error('Неудачная подгрузка элементов');

    throw err;
  } finally {
    fetchMoreItemsLoading.value = false;
  }
};

const onUncheckAll = () => {
  emit('update:itemChecking', { mode: 'include', ids: [] });
};

const onSelectChecked = () => {
  modalStore.open('processCheckedItemsModal');
};
</script>

<style lang="scss" scoped>
.advanced-flex-table-container--padded {
  padding-bottom: 64px;
}

.advanced-flex-table {
  :deep() &__row--active {
    background-color: theme('colors.main.50');

    &.flex-table__body-row--checked {
      @apply bg-main-200/70;

      color: theme('colors.black');
    }
  }
}

.advanced-flex-table-bottom-panel {
  padding: 24px 24px 24px 32px;
  right: 0;
  height: 88px;
  position: fixed;
  left: 88px;
  bottom: 0;
  z-index: 10;
  background-color: theme('colors.white');
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0px 0px 1px rgba(111, 146, 185, 0.15),
    0px -3px 15px -3px rgba(156, 172, 190, 0.15);

  &-enter-active,
  &-leave-active {
    transition-property: opacity, transform;
    transition-duration: 0.2s;
    transition-timing-function: ease-out;
  }

  &-enter-from,
  &-leave-to {
    opacity: 0;
    transform: translateY(100%);
  }

  &__info {
    @apply text-sm-regular;
  }

  &__actions {
    display: flex;
    align-items: center;
    gap: 16px;
  }
}

.advanced-flex-table-loader {
  display: block;
  margin: 16px auto;
}
</style>

<template>
  <div class="recalculations-page min-h-screen w-full">
    <div class="recalculations-page__content w-full h-full">
      <VFixedHeaderNTable
        v-model:sorting="sorting"
        v-model:search="searchQuery"
        v-model:active-item="detailedItem"
        class="items"
        :column-headers="TABLE_COLUMN_HEADERS"
        :sorting-options="SORTING_OPTIONS"
        :title="PAGE_TITLE"
        :disable-filter-button="isEqual(temporaryFilters, filters)"
        :disable-clear-button="checkDisableClear(temporaryFilters)"
        show-total
        :total="total"
        :page="page"
        :items="recalculations"
        :loading="loading"
        :fetching-more-items-func="fetchMoreRecalculations"
        @update:page="page = $event"
        @accept-filter="acceptFilters()"
        @clear-filter="clearFilters()"
      >
        <template #default="{ item }">
          <TableBody :item="item" />
        </template>

        <template #filter>
          <VMultiselect
            v-model="temporaryFilters.recalculation_type"
            :options="typeFilterOptions"
            item-name="label"
            primary-key="value"
            clearable
            sm
            label="Тип"
          />

          <VMultiselect
            v-model="temporaryFilters.trigger_type"
            :options="triggerFilterOptions"
            item-name="label"
            primary-key="value"
            clearable
            sm
            label="Инициатор"
          />

          <VMultiselect
            v-model="temporaryFilters.is_active"
            :options="statusFilterOptions"
            item-name="label"
            primary-key="value"
            clearable
            sm
            label="Статус"
          />
        </template>

        <template #header-actions>
          <VBtn
            v-if="userHasPermission(Permissions.Write)"
            data-test="add"
            @click="isItemBeingAdded = true"
          >
            Создать
          </VBtn>
        </template>
      </VFixedHeaderNTable>
    </div>

    <SidePanel
      v-if="detailedItem || isItemBeingAdded"
      :item="detailedItem"
      :fetch-items="refetchRecalculations"
      @close="onClose"
      @delete="onDeleteRequest"
      @executed="refetchRecalculations"
    />

    <VConfirmationModal
      id="removeRecalculation"
      :title="itemToDelete?.name
        ? `Удалить правило «${itemToDelete.name}»?`
        : 'Удалить правило?'"
      text="Правило будет удалено без возможности восстановления"
      confirmation-text="Удалить"
      :async-confirmation-func="confirmDelete"
      @closed="itemToDelete = null"
    />
  </div>
</template>

<script setup lang="ts">
import { debounce, isEqual, cloneDeep } from 'lodash';
import { watch } from 'vue';
import { searchRecalculationsRequest, deleteRecalculationRequest } from '../api';
import { TABLE_ITEM_COUNT_TO_FETCH } from '@/consts';
import type { Recalculation } from '../types';
import { RECALCULATION_TYPES, TRIGGER_TYPES } from '../types';
import { useModals } from '@/stores/modals';

import TableBody from '../components/TableBody.vue';
import SidePanel from '../components/SidePanel.vue';
import type { ColumnHeader } from '@/common/components/VTable/types';
import { Permissions } from '@/common/types/permissions';
import { userHasPermission } from '@/common/utils/permissions';

const PAGE_TITLE = 'Перерасчеты';

const TABLE_COLUMN_HEADERS: ColumnHeader[] = [
  { name: 'Наименование', key: 'name' },
  { name: 'Тип', key: 'recalculation_type' },
  { name: 'Инициатор', key: 'trigger_type' },
  { name: 'Приоритет', key: 'priority' },
  { name: 'Статус', key: 'is_active' },
  { name: 'Обновлен', key: 'updated_at' },
];

const SORTING_OPTIONS = [
  { value: 'priority_desc', name: 'Приоритет: высокий' },
  { value: 'priority_asc', name: 'Приоритет: низкий' },
  { value: 'created_desc', name: 'Дата: новые' },
  { value: 'created_asc', name: 'Дата: старые' },
  { value: 'name_asc', name: 'Название: А-Я' },
  { value: 'name_desc', name: 'Название: Я-А' },
];

const typeFilterOptions = [{ value: null, label: 'Все' }, ...RECALCULATION_TYPES];
const triggerFilterOptions = [{ value: null, label: 'Все' }, ...TRIGGER_TYPES];
const statusFilterOptions = [
  { value: null, label: 'Все' },
  { value: true, label: 'Активен' },
  { value: false, label: 'Отключен' },
];

const DEFAULT_FILTERS = {
  recalculation_type: null as any,
  trigger_type: null as any,
  is_active: null as any,
};

const modalStore = useModals();
const searchQuery = ref<string>('');
const detailedItem = ref<Recalculation | null>(null);
const isItemBeingAdded = ref(false);
const itemToDelete = ref<Recalculation | null>(null);
const sorting = ref<any>(SORTING_OPTIONS[0]);
const temporaryFilters = ref(cloneDeep(DEFAULT_FILTERS));
const filters = ref(cloneDeep(DEFAULT_FILTERS));
const recalculations = ref<Recalculation[]>([]);
const page = ref<number>(1);
const total = ref<number>(0);
const recalculationsLoading = ref(false);
const loading = computed(() => recalculationsLoading.value);

const checkDisableClear = (obj: any) =>
  Object.values(obj).every((el) => el === null || el === '' || el === undefined);

const buildParams = (p = 1) => ({
  ...(searchQuery.value && { search: searchQuery.value }),
  ...(sorting.value?.value && { sort_by: sorting.value.value }),
  ...(filters.value.recalculation_type?.value && {
    recalculation_type: filters.value.recalculation_type.value,
  }),
  ...(filters.value.trigger_type?.value && { trigger_type: filters.value.trigger_type.value }),
  ...(filters.value.is_active?.value !== null
    && filters.value.is_active?.value !== undefined && {
    is_active: filters.value.is_active.value,
  }),
  page: p,
  page_size: TABLE_ITEM_COUNT_TO_FETCH,
});

const refetchRecalculations = async (): Promise<void> => {
  recalculationsLoading.value = true;
  page.value = 1;
  try {
    const { data } = await searchRecalculationsRequest(buildParams(1));
    recalculations.value = data?.items ?? [];
    total.value = data?.total ?? 0;
  } catch (err) {
    console.error(err);
  } finally {
    recalculationsLoading.value = false;
  }
};

const fetchRecalculations = debounce(refetchRecalculations, 300);

const fetchMoreRecalculations = async (): Promise<void> => {
  try {
    const { data } = await searchRecalculationsRequest(buildParams(page.value));
    recalculations.value = [...recalculations.value, ...(data?.items ?? [])];
    total.value = data?.total ?? 0;
  } catch (err) {
    console.error(err);
    throw err;
  }
};

const onClose = () => {
  detailedItem.value = null;
  isItemBeingAdded.value = false;
};

const onDeleteRequest = (item: Recalculation) => {
  itemToDelete.value = item;
  modalStore.open('removeRecalculation');
};

const confirmDelete = async () => {
  if (!itemToDelete.value) return;
  await deleteRecalculationRequest(itemToDelete.value.id);
  await refetchRecalculations();
};

const clearFilters = async () => {
  temporaryFilters.value = cloneDeep(DEFAULT_FILTERS);
  filters.value = cloneDeep(DEFAULT_FILTERS);
  await refetchRecalculations();
};

const acceptFilters = async () => {
  filters.value = cloneDeep(temporaryFilters.value);
  await refetchRecalculations();
};

watch(
  () => [searchQuery.value, sorting.value?.value],
  () => fetchRecalculations(),
  { deep: true },
);

refetchRecalculations();
</script>

<style scoped lang="scss">
.items :deep() .table {
  .flex-table-cell {
    &:nth-child(2) {
      min-width: 80px;
      width: 100%;
      max-width: 80px;
    }

    &:nth-child(3) {
      min-width: 180px;
      width: 100%;
      max-width: 280px;
      padding-right: 24px;
    }

    &:nth-child(4) {
      min-width: 140px;
      width: 100%;
      max-width: 200px;
      padding-left: 0;
      padding-right: 24px;
    }

    &:nth-child(5) {
      min-width: 80px;
      width: 80px;
      max-width: 80px;
      padding-left: 0;
      padding-right: 24px;
    }

    &:nth-child(6) {
      min-width: 72px;
      width: 72px;
      max-width: 80px;
      padding-left: 0;
      padding-right: 12px;
    }

    &:nth-child(7) {
      min-width: 130px;
      width: 130px;
      padding-left: 0;
      padding-right: 12px;
    }

    &:nth-child(8) {
      min-width: 80px;
      width: 100%;
      max-width: 80px;
    }
  }
}
</style>

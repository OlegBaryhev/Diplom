<template>
  <div class="recalculateHistory-page min-h-screen w-full">
    <div class="recalculateHistory-page__content w-full h-full">
      <VFixedHeaderNTable
        v-model:sorting="sorting"
        v-model:search="searchQuery"
        v-model:active-item="detailedItem"
        class="items"
        :column-headers="TABLE_COLUMN_HEADERS"
        :sorting-options="SORTING_OPTIONS"
        :title="PAGE_TITLE"
        show-total
        :total="total"
        :page="page"
        :items="recalculateHistorys"
        :loading="loading"
        :fetching-more-items-func="fetchMoreRecalculateHistorys"
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
            label="Тип перерасчета"
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

          <VInput
            v-model="temporaryFilters.min_date"
            class="w-full"
            label="Дата от"
            sm
            placeholder="2026-01-01"
          />

          <VInput
            v-model="temporaryFilters.max_date"
            class="w-full"
            label="Дата до"
            sm
            placeholder="2026-12-31"
          />
        </template>

        <template #header-actions>
          <VExportBtn
            v-if="userHasPermission(Permissions.Download)"
            :disabled="loading || !recalculateHistorys.length"
            :export-function="exportRecalculateHistorys"
          />
        </template>
      </VFixedHeaderNTable>
    </div>

    <SidePanel
      v-if="detailedItem"
      :item="detailedItem"
      :fetch-items="fetchRecalculateHistorys"
      @close="detailedItem = null"
    />
  </div>
</template>

<script setup lang="ts">
import { debounce, isEqual, cloneDeep } from 'lodash';
import { watch } from 'vue';
import {
  getRecalculateHistorysRequest,
  exportRecalculateHistorysRequest,
} from '../api';
import { TABLE_ITEM_COUNT_TO_FETCH } from '@/consts';

import TableBody from '../components/TableBody.vue';
import SidePanel from '../components/SidePanel.vue';
import type { ColumnHeader } from '@/common/components/VTable/types';
import { downloadFileByBlob } from '@/common/utils/download-file';
import { RECALCULATION_TYPES, TRIGGER_TYPES } from '@/modules/recalculations/types';

import { Permissions } from '@/common/types/permissions';
import { userHasPermission } from '@/common/utils/permissions';

const PAGE_TITLE = 'История перерасчета цен';

const TABLE_COLUMN_HEADERS: ColumnHeader[] = [
  { name: 'Наименование', key: 'name' },
  { name: 'Тип', key: 'recalculation_type' },
  { name: 'Инициатор', key: 'trigger_type' },
  { name: 'Выполнил', key: 'recalculated_by' },
  { name: 'Товаров', key: 'products_affected_count' },
  { name: 'Время (мс)', key: 'execution_time_ms' },
  { name: 'Дата', key: 'recalculated_at' },
];

const SORTING_OPTIONS = [
  { value: 'date_desc', name: 'Дата: новые' },
  { value: 'date_asc', name: 'Дата: старые' },
  { value: 'name_asc', name: 'Название: А-Я' },
  { value: 'name_desc', name: 'Название: Я-А' },
];

const typeFilterOptions = [
  { value: null, label: 'Все типы' },
  ...RECALCULATION_TYPES,
];

const triggerFilterOptions = [
  { value: null, label: 'Все' },
  ...TRIGGER_TYPES,
];

const DEFAULT_FILTERS = {
  recalculation_type: null as any,
  trigger_type: null as any,
  min_date: '',
  max_date: '',
};

const searchQuery = ref<string>('');
const detailedItem = ref<any>(null);
const sorting = ref<any>(SORTING_OPTIONS[0]);
const temporaryFilters = ref(cloneDeep(DEFAULT_FILTERS));
const filters = ref(cloneDeep(DEFAULT_FILTERS));
const recalculateHistorys = ref<any[]>([]);
const page = ref<number>(1);
const total = ref<number>(0);
const recalculateHistorysLoading = ref<boolean>(false);
const loading = computed<boolean>(() => recalculateHistorysLoading.value);

const buildParams = (p = 1) => ({
  ...(searchQuery.value && { search: searchQuery.value }),
  ...(sorting.value?.value && { sort_by: sorting.value.value }),
  ...(filters.value.recalculation_type?.value && { recalculation_type: filters.value.recalculation_type.value }),
  ...(filters.value.trigger_type?.value && { trigger_type: filters.value.trigger_type.value }),
  ...(filters.value.min_date && { min_date: filters.value.min_date }),
  ...(filters.value.max_date && { max_date: filters.value.max_date }),
  page: p,
  page_size: TABLE_ITEM_COUNT_TO_FETCH,
});

const exportRecalculateHistorysLoading = ref<boolean>(false);
const exportRecalculateHistorys = async () => {
  exportRecalculateHistorysLoading.value = true;

  try {
    const formData = new FormData();
    const params = {
      ...(searchQuery.value && { search: searchQuery.value }),
      ...(sorting.value?.value && { sort_by: sorting.value.value }),
      ...(filters.value.recalculation_type?.value && { recalculation_type: String(filters.value.recalculation_type.value) }),
      ...(filters.value.trigger_type?.value && { trigger_type: filters.value.trigger_type.value }),
      ...(filters.value.min_date && { min_date: filters.value.min_date }),
      ...(filters.value.max_date && { max_date: filters.value.max_date }),
    };

    // eslint-disable-next-line no-restricted-syntax, guard-for-in
    for (const key in params) {
      formData.append(key, (params as any)[key].toString());
    }
    formData.append('filename', 'recalculate_history.xlsx');

    const { data } = await exportRecalculateHistorysRequest(formData);
    downloadFileByBlob(data, 'recalculate_history.xlsx');
  } finally {
    exportRecalculateHistorysLoading.value = false;
  }
};

const fetchRecalculateHistorys = debounce(async () => {
  recalculateHistorysLoading.value = true;
  page.value = 1;

  try {
    const result = await getRecalculateHistorysRequest(buildParams(1));
    recalculateHistorys.value = result?.data?.items ?? [];
    total.value = result?.data?.total ?? 0;
  } catch (error) {
    console.error(error);
  } finally {
    recalculateHistorysLoading.value = false;
  }
}, 300);

const fetchMoreRecalculateHistorys = async (): Promise<void> => {
  try {
    const result = await getRecalculateHistorysRequest(buildParams(page.value));
    recalculateHistorys.value = [...recalculateHistorys.value, ...(result?.data?.items ?? [])];
    total.value = result?.data?.total ?? 0;
  } catch (error) {
    console.error(error);
    throw error;
  }
};

const clearFilters = async (): Promise<void> => {
  temporaryFilters.value = cloneDeep(DEFAULT_FILTERS);
  filters.value = cloneDeep(DEFAULT_FILTERS);
  await fetchRecalculateHistorys();
};

const acceptFilters = async (): Promise<void> => {
  filters.value = cloneDeep(temporaryFilters.value);
  await fetchRecalculateHistorys();
};

watch(
  () => [searchQuery.value, sorting.value?.value],
  () => fetchRecalculateHistorys(),
  { deep: true },
);

fetchRecalculateHistorys();
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
      min-width: 120px;
      width: 100%;
      max-width: 180px;
      padding-left: 0;
      padding-right: 24px;
    }

    &:nth-child(5) {
      min-width: 100px;
      width: 100%;
      max-width: 140px;
      padding-left: 0;
      padding-right: 24px;
    }

    &:nth-child(6) {
      min-width: 80px;
      width: 80px;
      padding-left: 0;
      padding-right: 24px;
    }

    &:nth-child(7) {
      min-width: 90px;
      width: 90px;
      padding-left: 0;
      padding-right: 12px;
    }

    &:nth-child(8) {
      min-width: 140px;
      width: 140px;
      padding-left: 0;
      padding-right: 12px;
    }

    &:nth-child(9) {
      min-width: 80px;
      width: 80px;
      max-width: 80px;
    }
  }
}
</style>

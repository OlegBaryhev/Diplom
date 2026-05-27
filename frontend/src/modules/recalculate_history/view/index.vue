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
      @close="detailedItem = null"
    />
  </div>
</template>

<script setup lang="ts">
import { debounce } from 'lodash';
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

import { Permissions } from '@/common/types/permissions';
import { userHasPermission } from '@/common/utils/permissions';

const PAGE_TITLE = 'История пересчета цен';

const TABLE_COLUMN_HEADERS: ColumnHeader[] = [
  { name: 'Наименование', key: 'name' },
  { name: 'Описание', key: 'description' },
  { name: 'Категория', key: 'category' },
  { name: 'Бренд', key: 'brand' },
  { name: 'Цена, ₽', key: 'price' },
];

const searchQuery = ref<string>('');

const SORTING_OPTIONS = [
  { value: 'price_ask', name: 'По возрастанию' },
  { value: 'price_desc', name: 'По убыванию' },
  { value: 'name_asc', name: 'Название: А-Я' },
  { value: 'name_desc', name: 'Название: Я-А' },
];

const detailedItem = ref<any>(null);

const sorting = ref<string>(SORTING_OPTIONS[0] ?? '');

const recalculateHistorys = ref<any[]>([]);
const page = ref<number>(1);
const total = ref<number>(0);

const recalculateHistorysLoading = ref<boolean>(false);
const loading = computed<boolean>(() => recalculateHistorysLoading.value);

const exportRecalculateHistorysLoading = ref<boolean>(false);
const exportRecalculateHistorys = async () => {
  exportRecalculateHistorysLoading.value = true;

  try {
    const formData = new FormData();
    const params = {
      ...(searchQuery.value && { search: searchQuery.value }),
      ...(sorting.value?.value && { sort_by: sorting.value?.value }),
    };

    // eslint-disable-next-line no-restricted-syntax, guard-for-in
    for (const key in params) {
      formData.append(key, params[key].toString());
    }
    formData.append('filename', 'recalculateHistorys.xlsx');

    const { data } = await exportRecalculateHistorysRequest(formData);
    downloadFileByBlob(data, 'recalculateHistorys.xlsx');
  } finally {
    exportRecalculateHistorysLoading.value = false;
  }
};

const fetchRecalculateHistorys = debounce(async () => {
  recalculateHistorysLoading.value = true;
  page.value = 1;

  try {
    const result = await getRecalculateHistorysRequest({
      ...(searchQuery.value && { search: searchQuery.value }),
      ...(sorting.value?.value && { sort_by: sorting.value?.value }),
      page: 1,
      page_size: TABLE_ITEM_COUNT_TO_FETCH,
    });

    recalculateHistorys.value = result?.data?.items ?? [];
    total.value = result?.data?.total ?? 0;
  } catch (error) {
    console.error(error);
  } finally {
    recalculateHistorysLoading.value = false;
  }
});

const fetchMoreRecalculateHistorys = async (): Promise<void> => {
  try {
    const result = await getRecalculateHistorysRequest({
      ...(searchQuery.value && { search: searchQuery.value }),
      ...(sorting.value?.value && { sort_by: sorting.value?.value }),
      page: page.value,
      page_size: TABLE_ITEM_COUNT_TO_FETCH,
    });

    recalculateHistorys.value = [...recalculateHistorys.value, ...(result?.data?.items ?? [])];
    total.value = result?.data?.total ?? 0;
  } catch (error) {
    console.error(error);
    throw error;
  }
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
    // ID
    &:nth-child(2) {
      min-width: 80px;
      width: 100%;
      max-width: 80px;
    }

    // Наименование
    &:nth-child(3) {
      min-width: 16px + 136px + 24px;
      width: 100%;
      max-width: 250px;
      padding-right: 24px;
    }

    // Описание
    &:nth-child(4) {
      min-width: 128px + 24px;
      width: 100%;
      padding-left: 0;
      padding-right: 24px;
    }

    // Категория
    &:nth-child(5) {
      min-width: 56px + 24px;
      width: 100%;
      max-width: 200px;
      padding-left: 0;
      padding-right: 24px;
    }

    // Бренд
    &:nth-child(6) {
      min-width: 184px + 24px;
      width: 184px + 24px;
      padding-left: 0;
      padding-right: 24px;
    }

    // Цена
    &:nth-child(7) {
      min-width: 120px;
      width: 100%;
      max-width: 120px;
      padding-left: 12px;
      padding-right: 12px;
    }
    // Действия
    &:nth-child(8) {
      min-width: 100px;
      width: 100%;
      max-width: 100px;
    }
  }
}
</style>

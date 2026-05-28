<template>
  <div class="log-page min-h-screen w-full">
    <div class="log-page__content w-full h-full">
      <VFixedHeaderNTable
        v-model:sorting="sorting"
        v-model:search="searchQuery"
        v-model:active-item="detailedItem"
        class="items"
        :column-headers="TABLE_COLUMN_HEADERS"
        :sorting-options="SORTING_OPTIONS"
        title="Логи таблицы Бренды"
        show-total
        :total="logs.length"
        :items="logs"
        :loading="loading"
      >
        <template #default="{ item }">
          <TableBody :item="item" />
        </template>
      </VFixedHeaderNTable>
    </div>

    <SidePanel
      v-if="detailedItem"
      :item="detailedItem"
      @close="detailedItem = null"
      @delete="itemToDelete = $event; modalStore.open('removeBrandLog')"
    />

    <VConfirmationModal
      id="removeBrandLog"
      title="Вы действительно хотите удалить запись лога?"
      text="Запись будет удалена без возможности восстановления"
      confirmation-text="Удалить"
      :async-confirmation-func="deleteItem"
      @closed="itemToDelete = null"
    />
  </div>
</template>

<script setup lang="ts">
import { debounce } from 'lodash';
import { watch } from 'vue';
import { getBrandLogsRequest, deleteBrandLogRequest } from '../api';
import type { ILogData } from '@/modules/_logs/types';
import { useModals } from '@/stores/modals';
import TableBody from '../components/TableBody.vue';
import SidePanel from '../components/SidePanel.vue';
import type { ColumnHeader } from '@/common/components/tables/types';

const modalStore = useModals();

const TABLE_COLUMN_HEADERS: ColumnHeader[] = [
  { name: 'Операция', key: 'operation' },
  { name: 'Данные', key: 'row_data' },
  { name: 'Дата изменения', key: 'changed_at' },
];

const SORTING_OPTIONS = [
  { value: 'changed_at_desc', name: 'Дата: сначала новые' },
  { value: 'changed_at_asc', name: 'Дата: сначала старые' },
  { value: 'operation_asc', name: 'Операция: А-Я' },
  { value: 'operation_desc', name: 'Операция: Я-А' },
];

const searchQuery = ref<string>('');
const detailedItem = ref<ILogData | null>(null);
const sorting = ref(SORTING_OPTIONS[0]);
const logs = ref<ILogData[]>([]);
const itemToDelete = ref<ILogData | null>(null);
const loading = ref<boolean>(false);

const fetchLogs = debounce(async () => {
  loading.value = true;

  try {
    const result = await getBrandLogsRequest({
      ...(searchQuery.value && { search: searchQuery.value }),
      ...(sorting.value?.value && { sort_by: sorting.value?.value }),
    });

    logs.value = result?.data ?? [];
  } catch (error) {
    console.error(error);
  } finally {
    loading.value = false;
  }
});

const deleteItem = async () => {
  try {
    await deleteBrandLogRequest(itemToDelete.value?.id);
    detailedItem.value = null;
    await fetchLogs();
  } finally {
    itemToDelete.value = null;
  }
};

watch(
  () => [searchQuery.value, sorting.value?.value],
  () => fetchLogs(),
  { deep: true },
);
fetchLogs();
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

    // Операция
    &:nth-child(3) {
      min-width: 16px + 136px + 24px;
      width: 100%;
      max-width: 250px;
      padding-right: 24px;
    }

    // Данные
    &:nth-child(4) {
      min-width: 128px + 24px;
      width: 100%;
      padding-left: 0;
      padding-right: 24px;
    }

    // Дата изменения
    &:nth-child(5) {
      min-width: 118px;
      width: 118px;
      padding-left: 0;
    }
  }
}
</style>

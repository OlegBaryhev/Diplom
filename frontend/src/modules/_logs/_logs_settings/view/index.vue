<template>
  <div class="log-settings-page min-h-screen w-full">
    <div class="log-settings-page__content w-full h-full">
      <VFixedHeaderNTable
        v-model:search="searchQuery"
        v-model:sorting="sorting"
        v-model:active-item="detailedItem"
        class="items"
        :column-headers="TABLE_COLUMN_HEADERS"
        :sorting-options="SORTING_OPTIONS"
        title="Настройки логгирования"
        show-total
        :total="filteredSettings.length"
        :items="filteredSettings"
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
      :fetch-items="fetchSettings"
      @close="detailedItem = null"
    />
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { getLogSettingsRequest } from '../api';
import type { ILogSettings } from '@/modules/_logs/types';
import TableBody from '../components/TableBody.vue';
import SidePanel from '../components/SidePanel.vue';
import type { ColumnHeader } from '@/common/components/tables/types';

const TABLE_COLUMN_HEADERS: ColumnHeader[] = [
  { name: 'Таблица', key: 'table_name' },
  { name: 'Хранение (мин.)', key: 'time_retention_minutes' },
  { name: 'Лимит записей', key: 'count_retention_limit' },
];

const SORTING_OPTIONS = [
  { value: 'table_name_asc', name: 'Таблица: А-Я' },
  { value: 'table_name_desc', name: 'Таблица: Я-А' },
  { value: 'retention_asc', name: 'Хранение: по возрастанию' },
  { value: 'retention_desc', name: 'Хранение: по убыванию' },
];

const searchQuery = ref<string>('');
const sorting = ref(SORTING_OPTIONS[0]);
const detailedItem = ref<ILogSettings | null>(null);
const settings = ref<ILogSettings[]>([]);
const loading = ref<boolean>(false);

const filteredSettings = computed<ILogSettings[]>(() => {
  let result = [...settings.value];

  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase();
    result = result.filter((s) => s.table_name.toLowerCase().includes(query));
  }

  const sortValue = sorting.value?.value ?? '';

  if (sortValue === 'table_name_asc') {
    result.sort((a, b) => a.table_name.localeCompare(b.table_name));
  } else if (sortValue === 'table_name_desc') {
    result.sort((a, b) => b.table_name.localeCompare(a.table_name));
  } else if (sortValue === 'retention_asc') {
    result.sort((a, b) => a.time_retention_minutes - b.time_retention_minutes);
  } else if (sortValue === 'retention_desc') {
    result.sort((a, b) => b.time_retention_minutes - a.time_retention_minutes);
  }

  return result;
});

const fetchSettings = async () => {
  loading.value = true;

  try {
    const result = await getLogSettingsRequest();
    settings.value = result?.data ?? [];
  } catch (error) {
    console.error(error);
  } finally {
    loading.value = false;
  }
};

fetchSettings();
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

    // Таблица
    &:nth-child(3) {
      min-width: 200px;
      width: 100%;
      max-width: 300px;
      padding-right: 24px;
    }

    // Хранение
    &:nth-child(4) {
      min-width: 140px;
      width: 100%;
      max-width: 200px;
      padding-left: 0;
      padding-right: 24px;
    }

    // Лимит
    &:nth-child(5) {
      min-width: 130px;
      width: 130px;
      padding-left: 0;
    }
  }
}
</style>

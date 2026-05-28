<template>
  <div class="log-settings-page min-h-screen w-full">
    <div class="log-settings-page__content w-full h-full">
      <VFixedHeaderNTable
        v-model:search="searchQuery"
        v-model:active-item="detailedItem"
        class="items"
        :column-headers="TABLE_COLUMN_HEADERS"
        title="Настройки логгирования"
        show-total
        :total="settings.length"
        :items="settings"
        :loading="loading"
        no-filtering
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

const searchQuery = ref<string>('');
const detailedItem = ref<ILogSettings | null>(null);
const settings = ref<ILogSettings[]>([]);
const loading = ref<boolean>(false);

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

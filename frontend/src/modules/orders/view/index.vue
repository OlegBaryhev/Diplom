<template>
  <div class="product-page min-h-screen w-full">
    <div class="product-page__content w-full h-full">
      <VFixedHeaderNTable
        v-model:sorting="sorting"
        v-model:search="searchQuery"
        v-model:active-item="detailedItem"
        class="items"
        :disable-filter-button="isEqual(temporaryFilters, filters)"
        :disable-clear-button="checkDisableClear(temporaryFilters)"
        :column-headers="TABLE_COLUMN_HEADERS"
        :sorting-options="SORTING_OPTIONS"
        show-total
        :total="orders?.length"
        :items="orders"
        :loading="loading"
        title="Заказы"
        @accept-filter="acceptFilters()"
        @clear-filter="clearFilters()"
      >
        <template #default="{ item }">
          <TableBody :item="item" />
        </template>

        <template #header-actions>
          <VExportBtn
            v-if="userHasPermission(Permissions.Download)"
            :disabled="loading || !orders.length"
            :export-function="exportOrders"
          />
        </template>

        <template #filter>
          <div class="prices flex w-full gap-3">
            <VInput
              v-model="temporaryFilters.quantity_from"
              class="w-full"
              label="Товары, от"
              mask="number-int"
              sm
              data-test="min-product-count"
            />

            <VInput
              v-model="temporaryFilters.quantity_to"
              class="w-full"
              label="Товары, до"
              mask="number-int"
              sm
              data-test="max-product-count"
            />
          </div>

          <VMultiselect
            v-model="temporaryFilters.user"
            :options="users"
            item-name="name"
            primary-key="value"
            clearable
            sm
            label="Пользователь"
            :loading="filterLoading"
            data-test="select-categories"
          />

          <VMultiselect
            v-model="temporaryFilters.status"
            :options="STATUSES"
            item-name="name"
            primary-key="value"
            clearable
            sm
            label="Статус"
            :loading="filterLoading"
            data-test="select-categories"
          />
        </template>
      </VFixedHeaderNTable>
    </div>

    <SidePanel
      v-if="detailedItem"
      :item="detailedItem"
      :fetch-items="fetchOrders"
      @close="detailedItem = null"
      @delete="itemToDelete = $event; modalStore.open('removeProduct')"
    />
  </div>
</template>

<script setup lang="ts">
import { debounce, isEqual, cloneDeep } from 'lodash';
import { watch } from 'vue';
import {
  searchOrdersRequest,
  exportOrdersRequest,
} from '../api';

import type { OrderRead } from '../types';

import TableBody from '../components/TableBody.vue';
import SidePanel from '../components/SidePanel.vue';

import type { ColumnHeader } from '@/common/components/VTable/types';
import { Permissions } from '@/common/types/permissions';
import { userHasPermission } from '@/common/utils/permissions';
import { downloadFileByBlob } from '@/common/utils/download-file';
import { STATUSES } from '@/modules/orders/const';

import { getUsersSimple } from '@/modules/users_control/api';

const TABLE_COLUMN_HEADERS: ColumnHeader[] = [
  { name: 'Код заказа', key: 'products_total' },
  { name: 'Пользователь', key: 'user' },
  { name: 'Кол-во позиций\nпродуктов', key: 'total_assortment' },
  { name: 'Кол-во\nпродуктов', key: 'total_count' },
  { name: 'Статус', key: 'products_total' },
  { name: 'Дата отправки', key: 'created_at' },
];

const searchQuery = ref<string>('');

const SORTING_OPTIONS = [
  { value: 'created_at_asc', name: 'Дата создания: по возрастанию' },
  { value: 'created_at_desc', name: 'Дата создания: по убыванию' },
  { value: 'status_asc', name: 'Статус: по возрастанию' },
  { value: 'status_desc', name: 'Статус: по убыванию' },
];

const DEFAULT_FILTERS = {
  quantity_from: '',
  quantity_to: '',
  user: '',
  status: '',
};

const temporaryFilters = ref<any>(cloneDeep(DEFAULT_FILTERS));
const filters = ref<any>(cloneDeep(DEFAULT_FILTERS));

const detailedItem = ref<any>(null);

const checkDisableClear = (obj) =>
  Object.values(obj).every((el) => Array.isArray(el) ? !el?.length : !el);

const sorting = ref<string>(SORTING_OPTIONS[0] ?? '');

const orders = ref<OrderRead[] | null>([]);

const filterLoading = ref<boolean>(false);
const ordersLoading = ref<boolean>(false);
const loading = computed<boolean>(() => filterLoading.value || ordersLoading.value);

const users = ref<any[] | null>([]);
const itemToDelete = ref(null);

const fetchFilters = async () => {
  filterLoading.value = true;

  try {
    const { data: usersData } = await getUsersSimple();
    users.value = usersData;
  } catch (error) {
    console.error(error);
    throw error;
  } finally {
    filterLoading.value = false;
  }
};

fetchFilters();

const exportOrdersLoading = ref<boolean>(false);
const exportOrders = async () => {
  exportOrdersLoading.value = true;

  try {
    const formData = new FormData();
    const params = {
      ...(searchQuery.value && { search: searchQuery.value }),
      ...(filters.value?.quantity_from && { quantity_from: Number(filters.value.quantity_from) }),
      ...(filters.value?.quantity_to && { quantity_to: Number(filters.value.quantity_to) }),
      ...(filters.value?.user?.value && { user_id: filters.value.user.value }),
      ...(filters.value?.status?.value && { statuses: [filters.value.status.value] }),
      ...(sorting.value?.value && { sort_by: sorting.value?.value }),
    };

    // eslint-disable-next-line no-restricted-syntax, guard-for-in
    for (const key in params) {
      formData.append(key, params[key].toString());
    }
    formData.append('filename', 'orders.xlsx');

    const { data } = await exportOrdersRequest(formData);
    downloadFileByBlob(data, 'orders.xlsx');
  } finally {
    exportOrdersLoading.value = false;
  }
};

const fetchOrders = debounce(async () => {
  ordersLoading.value = true;

  try {
    const params = {
      ...(searchQuery.value && { search: searchQuery.value }),
      ...(filters.value?.quantity_from && { quantity_from: Number(filters.value.quantity_from) }),
      ...(filters.value?.quantity_to && { quantity_to: Number(filters.value.quantity_to) }),
      ...(filters.value?.user?.value && { user_id: filters.value.user.value }),
      ...(filters.value?.status?.value && { statuses: [filters.value.status.value] }),
      ...(sorting.value?.value && { sort_by: sorting.value?.value }),
    };

    const result = await searchOrdersRequest(params);

    orders.value = result?.data ?? [];
  } catch (error) {
    console.error(error);
  } finally {
    ordersLoading.value = false;
  }
});

const clearFilters = async (): Promise<void> => {
  temporaryFilters.value = cloneDeep(DEFAULT_FILTERS);
  filters.value = cloneDeep(DEFAULT_FILTERS);
  await fetchOrders();
};

const acceptFilters = async (): Promise<void> => {
  filters.value = cloneDeep(temporaryFilters.value);
  await fetchOrders();
};

watch(
  () => [searchQuery.value, sorting.value?.value],
  () => fetchOrders(),
  { deep: true },
);
fetchOrders();
</script>

<style scoped lang="scss">
.items :deep() .table {

  .flex-table-cell {
    // ID
    &:first-child {
      min-width: 80px;
      width: 100%;
      max-width: 80px;
    }

    // Код-заказа
    &:nth-child(2){
      min-width: 100px;
      max-width: 100px;
    }

    // Пользователь
    &:nth-child(3) {
      min-width: 128px + 24px;
      width: 100%;
      padding-left: 24px;
      padding-right: 24px;
    }

    // Кол-во позиций продуктов
    &:nth-child(4) {
      min-width: 140px;
      max-width: 200px;
    }

    // Кол-во продуктов
    &:nth-child(5) {
      min-width: 140px;
      max-width: 200px;
    }

    // Статус
    &:nth-child(6) {
      min-width: 140px;
      max-width: 200px;
    }

    // Дата
    &:nth-child(7) {
      min-width: 150px;
      max-width: 150px;
    }
  }
}
</style>

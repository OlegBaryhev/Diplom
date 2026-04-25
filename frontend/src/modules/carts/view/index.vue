<template>
  <div class="product-page min-h-screen w-full">
    <div class="product-page__content w-full h-full">
      <VFixedHeaderNTable
        v-model:sorting="sorting"
        v-model:search="searchQuery"
        class="items"
        :column-headers="TABLE_COLUMN_HEADERS"
        :sorting-options="SORTING_OPTIONS"
        show-total
        :total="carts.length"
        :items="carts"
        :loading="loading"
        title="Все корзины"
      >
        <template #default="{ item }">
          <TableBody :item="item" />
        </template>
      </VFixedHeaderNTable>
    </div>
  </div>
</template>

<script setup lang="ts">
import { debounce } from 'lodash';
import { watch } from 'vue';
import {
  getCartSearchRequest,
} from '../api';

import type { Brand } from '../types';

import TableBody from '../components/TableBody.vue';
import type { ColumnHeader } from '@/common/components/VTable/types';

const TABLE_COLUMN_HEADERS: ColumnHeader[] = [
  { name: 'Пользователь', key: 'user' },
  { name: 'Всего товаров', key: 'products_total' },
  { name: 'Общая цена товаров', key: 'total_price' },
];

const searchQuery = ref<string>('');

const SORTING_OPTIONS = [
  { value: 'name_asc', name: 'Название: А-Я' },
  { value: 'name_desc', name: 'Название: Я-А' },
];

const sorting = ref<string>(SORTING_OPTIONS[0] ?? '');

const carts = ref<Brand[] | null>([]);

const filterLoading = ref<boolean>(false);
const cartsLoading = ref<boolean>(false);
const loading = computed<boolean>(() => filterLoading.value || cartsLoading.value);

const fetchCarts = debounce(async () => {
  cartsLoading.value = true;

  try {
    const params = {
      ...(searchQuery.value && { search: searchQuery.value }),
      ...(sorting.value?.value && { sort_by: sorting.value?.value }),
    };

    const result = await getCartSearchRequest(params);

    carts.value = result?.data ?? [];
  } catch (error) {
    console.error(error);
  } finally {
    cartsLoading.value = false;
  }
});

watch(
  () => [searchQuery.value, sorting.value?.value],
  () => fetchCarts(),
  { deep: true },
);
fetchCarts();
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

    // Пользователь
    &:nth-child(2){
      min-width: 128px + 24px;
      width: 100%;
      padding-left: 0;
      padding-right: 24px;
    }

    // Всего типов товаров
    &:nth-child(3) {
      min-width: 16px + 236px + 24px;
      width: 100%;
      max-width: 250px;
      padding-right: 24px;
    }

    // Количество товара
    &:nth-child(4) {
      min-width: 16px + 136px + 24px;
      width: 100%;
      max-width: 250px;
      padding-right: 24px;
    }

    // Цена целиком
    &:nth-child(5) {
      min-width: 16px + 136px + 24px;
      width: 100%;
      max-width: 250px;
      padding-right: 24px;
    }
  }
}
</style>

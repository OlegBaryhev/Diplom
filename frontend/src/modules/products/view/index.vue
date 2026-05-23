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
        :actions-list="ACTIONS_LIST"
        :column-headers="TABLE_COLUMN_HEADERS"
        :sorting-options="SORTING_OPTIONS"
        :title="PAGE_TITLE"
        :modes="ICON_ITEMS"
        show-total
        :total="products?.length"
        :items="products"
        :loading="loading"
        @accept-filter="acceptFilters()"
        @clear-filter="clearFilters()"
        @action="onActionsClick"
      >
        <template #default="{ item }">
          <TableBody :item="item" />
        </template>

        <template #header-actions>
          <VBtn
            v-if="userHasPermission(Permissions.Recalculate)"
            data-test="fast_recalculate"
            outlined
            @click="modalStore.open('recalculateModal');"
          >
            Быстрый пересчет цен
          </VBtn>

          <VBtn
            v-if="userHasPermission(Permissions.Write)"
            data-test="add"
            @click="isItemBeingAdded = true"
          >
            Добавить
          </VBtn>

          <VExportBtn
            v-if="userHasPermission(Permissions.Download)"
            :disabled="loading || !products.length"
            :export-function="exportProducts"
          />
        </template>

        <template #filter>
          <div class="prices flex w-full gap-3">
            <VInput
              v-model="temporaryFilters.min_price"
              class="w-full"
              label="Цена от, ₽"
              sm
              data-test="min_price"
            />

            <VInput
              v-model="temporaryFilters.max_price"
              class="w-full"
              label="Цена до, ₽"
              sm
              data-test="max_price"
            />
          </div>

          <VMultiselect
            v-model="temporaryFilters.category_id"
            :options="categories"
            item-name="name"
            primary-key="id"
            clearable
            sm
            label="Категории"
            :loading="filterLoading"
            data-test="select-categories"
          />

          <VMultiselect
            v-model="temporaryFilters.brand_id"
            :options="brand"
            item-name="name"
            primary-key="id"
            clearable
            sm
            :loading="filterLoading"
            label="Бренд"
            data-test="select-brand"
          />
        </template>
      </VFixedHeaderNTable>
    </div>

    <SidePanel
      v-if="detailedItem || isItemBeingAdded"
      :item="detailedItem"
      :fetch-items="fetchProducts"
      @close="detailedItem ? detailedItem = null : isItemBeingAdded = false"
      @delete="itemToDelete = $event; modalStore.open('removeProduct')"
    />

    <VConfirmationModal
      id="removeProduct"
      :title="!itemToDelete?.name ? `Вы действительно хотите удалить этот продукт?`
        : `Вы действительно хотите удалить продукт «${itemToDelete?.name ?? ''}»?`"
      text="Продукт будет удален без возможности восстановления"
      confirmation-text="Удалить"
      :async-confirmation-func="deleteItem"
      @closed="itemToDelete = null"
    />

    <RecalculateModal
      modal-id="recalculateModal"
    />
  </div>
</template>

<script setup lang="ts">
import { debounce, isEqual, cloneDeep } from 'lodash';
import { watch } from 'vue';
import {
  getCategoriesRequest,
  getBrandsRequest,
  getProductsRequest,
  exportProductsRequest,
  deleteProductsRequest,
} from '../api';

import type {
  Category,
  Product,
  productFilter,
} from '../types';

import { useModals } from '@/stores/modals';

import TableBody from '../components/TableBody.vue';
import SidePanel from '../components/SidePanel.vue';
import RecalculateModal from '../components/RecalculateModal.vue';

import type { ColumnHeader } from '@/common/components/VTable/types';
import { downloadFileByBlob } from '@/common/utils/download-file';

import { Permissions } from '@/common/types/permissions';
import { userHasPermission } from '@/common/utils/permissions';
import { useCart } from '@/stores/cart';

const cartStore = useCart();

const PAGE_TITLE = 'Продукты';

const modalStore = useModals();

const TABLE_COLUMN_HEADERS: ColumnHeader[] = [
  { name: 'Наименование', key: 'name' },
  { name: 'Описание', key: 'description' },
  { name: 'Категория', key: 'category' },
  { name: 'Бренд', key: 'brand' },
  { name: 'Цена, ₽', key: 'price' },
];

const ACTIONS_LIST = [
  {
    name: 'Добавить в корзину',
    icon: 'cart',
    emit: 'add-to-cart',
  },
];

const addProductToCart = (item: Product) => {
  cartStore.addToCart(item);
};

const onActionsClick = (event: any) => {
  if (event.action.emit === 'add-to-cart') {
    addProductToCart(event.item);
  }
};

const DEFAULT_FILTERS = {
  min_price: '',
  max_price: '',
  category_id: '',
  brand_id: '',
};

const ICON_ITEMS = [
  {
    icon: 'table',
    instance: 'table',
    hint: 'Таблица',
  },
  {
    icon: 'rows',
    instance: 'rows',
    hint: 'Список',
  },
  {
    icon: 'cards',
    instance: 'cards',
    hint: 'Карточки',
  },
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

const temporaryFilters = ref<productFilter>(cloneDeep(DEFAULT_FILTERS));
const filters = ref<productFilter>(cloneDeep(DEFAULT_FILTERS));

const checkDisableClear = (obj) =>
  Object.values(obj).every((el) => Array.isArray(el) ? !el?.length : !el);

const products = ref<Product[] | null>([]);

const categories = ref<Category[] | null>([]);
const brand = ref<any[] | null>([]);

const itemToDelete = ref(null);
const isItemBeingAdded = ref<boolean>(false);

const filterLoading = ref<boolean>(false);
const productsLoading = ref<boolean>(false);
const loading = computed<boolean>(() => filterLoading.value || productsLoading.value);

const fetchFilters = async () => {
  filterLoading.value = true;

  try {
    const { data: categoryData } = await getCategoriesRequest();
    categories.value = categoryData;

    const { data: brandsData } = await getBrandsRequest();
    brand.value = brandsData;
  } catch (error) {
    console.error(error);
    throw error;
  } finally {
    filterLoading.value = false;
  }
};

fetchFilters();

const exportProductsLoading = ref<boolean>(false);
const exportProducts = async () => {
  exportProductsLoading.value = true;

  try {
    const formData = new FormData();
    const params = {
      ...(searchQuery.value && { search: searchQuery.value }),
      ...(filters.value?.min_price && { min_price: filters.value.min_price * 100 }),
      ...(filters.value?.max_price && { max_price: filters.value.max_price * 100 }),
      ...(filters.value?.category_id?.id && { category_id: filters.value?.category_id?.id }),
      ...(filters.value?.brand_id?.id && { brand_id: filters.value?.brand_id?.id }),
      ...(sorting.value?.value && { sort_by: sorting.value?.value }),
    };

    // eslint-disable-next-line no-restricted-syntax, guard-for-in
    for (const key in params) {
      formData.append(key, params[key].toString());
    }
    formData.append('filename', 'products.xlsx');

    const { data } = await exportProductsRequest(formData);
    downloadFileByBlob(data, 'products.xlsx');
  } finally {
    exportProductsLoading.value = false;
  }
};

const fetchProducts = debounce(async () => {
  productsLoading.value = true;

  try {
    const params = {
      ...(searchQuery.value && { search: searchQuery.value }),
      ...(filters.value?.min_price && { min_price: filters.value.min_price * 100 }),
      ...(filters.value?.max_price && { max_price: filters.value.max_price * 100 }),
      ...(filters.value?.category_id?.id && { category_id: filters.value?.category_id?.id }),
      ...(filters.value?.brand_id?.id && { brand_id: filters.value?.brand_id?.id }),
      ...(sorting.value?.value && { sort_by: sorting.value?.value }),
    };

    const result = await getProductsRequest({
      ...params,
    });

    products.value = result?.data ?? [];
  } catch (error) {
    console.error(error);
  } finally {
    productsLoading.value = false;
  }
});

const fetchAll = async () => {
  await fetchProducts();
  await fetchFilters();
};

const deleteItem = async () => {
  try {
    await deleteProductsRequest(itemToDelete.value?.id);
    await fetchAll();
  } finally {
    itemToDelete.value = null;
  }
};

const clearFilters = async (): Promise<void> => {
  temporaryFilters.value = cloneDeep(DEFAULT_FILTERS);
  filters.value = cloneDeep(DEFAULT_FILTERS);
  await fetchProducts();
};

const acceptFilters = async (): Promise<void> => {
  filters.value = cloneDeep(temporaryFilters.value);
  await fetchProducts();
};

watch(
  () => [searchQuery.value, sorting.value?.value],
  () => fetchProducts(),
  { deep: true },
);
fetchProducts();
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

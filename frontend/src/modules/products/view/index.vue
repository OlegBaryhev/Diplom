<template>
  <div class="product-page min-h-screen w-full">
    <div class="product-page__content w-full h-full">
      <VFixedHeaderNTable
        v-model:sorting="sorting"
        v-model:search="searchQuery"
        v-model:active-item="detailedItem"
        class="items"
        :class="{ 'items--cards': viewMode === 'cards' }"
        :cards-mode="viewMode === 'cards'"
        :disable-filter-button="isEqual(temporaryFilters, filters)"
        @update:filter-open="filterIsOpen = $event"
        :disable-clear-button="checkDisableClear(temporaryFilters)"
        :actions-list="ACTIONS_LIST"
        :column-headers="TABLE_COLUMN_HEADERS"
        :sorting-options="SORTING_OPTIONS"
        :title="PAGE_TITLE"
        show-total
        :total="total"
        :page="page"
        :items="products"
        :loading="loading"
        :fetching-more-items-func="fetchMoreProducts"
        @update:page="page = $event"
        @accept-filter="acceptFilters()"
        @clear-filter="clearFilters()"
        @action="onActionsClick"
      >
        <template #default="{ item }">
          <TableBody :item="item" />
        </template>

        <template #view-mode>
          <div class="view-switcher">
            <VBtn
              v-for="mode in VIEW_MODES"
              :key="mode.value"
              ghost
              small
              :icon="mode.icon"
              :title="mode.label"
              :class="{ 'view-switcher__btn--active': viewMode === mode.value }"
              @click="viewMode = mode.value"
            />
          </div>
        </template>

        <template #header-actions>
          <VBtn
            v-if="userHasPermission(Permissions.Recalculate)"
            data-test="fast_recalculate"
            outlined
            @click="modalStore.open('recalculateModal');"
          >
            Быстрый пересчёт
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
        <template #cards-content>
          <div
            v-if="viewMode === 'cards'"
            class="cards-content"
          >
            <VCardList
              v-if="products.length"
              :items="products"
              :cards-height="440"
              :cards-width="280"
              :vertical-margin="10"
              :horizontal-margin="10"
              :title-lines-count="1"
              :filter-panel-width="filterIsOpen ? 350 : 70"
              @scroll-end="onCardsScrollEnd"
            >
              <template #default="{ item }">
                <div class="card-cell">
                  <ProductCard
                    :product="item"
                    @edit="detailedItem = item"
                    @buy="cartStore.addToCart(item)"
                  />
                </div>
              </template>
            </VCardList>

            <p
              v-else-if="!loading"
              class="cards-empty"
            >
              Нет товаров
            </p>
          </div>
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
      :filters="activeRecalculateFilters"
      @done="fetchProducts()"
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
import { TABLE_ITEM_COUNT_TO_FETCH } from '@/consts';

import type { Category, Product, productFilter } from '../types';

import { useModals } from '@/stores/modals';
import TableBody from '../components/TableBody.vue';
import SidePanel from '../components/SidePanel.vue';
import RecalculateModal from '../components/RecalculateModal.vue';
import ProductCard from '../components/ProductCard.vue';

import type { ColumnHeader } from '@/common/components/VTable/types';
import { downloadFileByBlob } from '@/common/utils/download-file';
import { Permissions } from '@/common/types/permissions';
import { userHasPermission } from '@/common/utils/permissions';
import { useCart } from '@/stores/cart';

const cartStore = useCart();
const PAGE_TITLE = 'Продукты';
const modalStore = useModals();

const VIEW_MODES = [
  { value: 'table', icon: 'table', label: 'Таблица' },
  { value: 'cards', icon: 'cards', label: 'Карточки' },
] as const;

type ViewMode = typeof VIEW_MODES[number]['value'];

const SESSION_KEY = 'products-view-mode';
const storedMode = sessionStorage.getItem(SESSION_KEY) as ViewMode | null;
const viewMode = ref<ViewMode>(
  (storedMode && VIEW_MODES.some((m) => m.value === storedMode)) ? storedMode : 'table',
);
watch(viewMode, (v) => sessionStorage.setItem(SESSION_KEY, v));

const filterIsOpen = ref(true);

const TABLE_COLUMN_HEADERS: ColumnHeader[] = [
  { name: 'Фото', key: 'image' },
  { name: 'Наименование', key: 'name' },
  { name: 'Описание', key: 'description' },
  { name: 'Категория', key: 'category' },
  { name: 'Бренд', key: 'brand' },
  { name: 'Скидка', key: 'discount' },
  { name: 'Цена, ₽', key: 'price' },
];

const ACTIONS_LIST = [
  { name: 'Добавить в корзину', icon: 'cart', emit: 'add-to-cart' },
];

const addProductToCart = (item: Product) => cartStore.addToCart(item);

const onActionsClick = (event: any) => {
  if (event.action.emit === 'add-to-cart') addProductToCart(event.item);
};

const DEFAULT_FILTERS = {
  min_price: '',
  max_price: '',
  category_id: '',
  brand_id: '',
};

const SORTING_OPTIONS = [
  { value: 'price_ask', name: 'По возрастанию' },
  { value: 'price_desc', name: 'По убыванию' },
  { value: 'name_asc', name: 'Название: А-Я' },
  { value: 'name_desc', name: 'Название: Я-А' },
];

const searchQuery = ref<string>('');
const detailedItem = ref<any>(null);
const sorting = ref<string>(SORTING_OPTIONS[0] ?? '');
const temporaryFilters = ref<productFilter>(cloneDeep(DEFAULT_FILTERS));
const filters = ref<productFilter>(cloneDeep(DEFAULT_FILTERS));
const checkDisableClear = (obj: any) =>
  Object.values(obj).every((el) => Array.isArray(el) ? !el?.length : !el);

const products = ref<Product[]>([]);
const page = ref<number>(1);
const total = ref<number>(0);
const cardsIsFetching = ref(false);
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
      formData.append(key, (params as any)[key].toString());
    }
    formData.append('filename', 'products.xlsx');
    const { data } = await exportProductsRequest(formData);
    downloadFileByBlob(data, 'products.xlsx');
  } finally {
    exportProductsLoading.value = false;
  }
};

const activeRecalculateFilters = computed(() => ({
  ...(searchQuery.value && { search: searchQuery.value }),
  ...(filters.value?.min_price && { min_price: Number(filters.value.min_price) * 100 }),
  ...(filters.value?.max_price && { max_price: Number(filters.value.max_price) * 100 }),
  ...(filters.value?.category_id?.id && { category_id: filters.value.category_id.id }),
  ...(filters.value?.brand_id?.id && { brand_id: filters.value.brand_id.id }),
}));

const buildParams = (p = 1) => ({
  ...(searchQuery.value && { search: searchQuery.value }),
  ...(filters.value?.min_price && { min_price: filters.value.min_price * 100 }),
  ...(filters.value?.max_price && { max_price: filters.value.max_price * 100 }),
  ...(filters.value?.category_id?.id && { category_id: filters.value?.category_id?.id }),
  ...(filters.value?.brand_id?.id && { brand_id: filters.value?.brand_id?.id }),
  ...(sorting.value?.value && { sort_by: sorting.value?.value }),
  page: p,
  page_size: TABLE_ITEM_COUNT_TO_FETCH,
});

const fetchProducts = debounce(async () => {
  productsLoading.value = true;
  page.value = 1;
  try {
    const result = await getProductsRequest(buildParams(1));
    products.value = result?.data?.items ?? [];
    total.value = result?.data?.total ?? 0;
  } catch (error) {
    console.error(error);
  } finally {
    productsLoading.value = false;
  }
});

const fetchMoreProducts = async (): Promise<void> => {
  try {
    const result = await getProductsRequest(buildParams(page.value));
    products.value = [...products.value, ...(result?.data?.items ?? [])];
    total.value = result?.data?.total ?? 0;
  } catch (error) {
    console.error(error);
    throw error;
  }
};

const deleteItem = async () => {
  try {
    await deleteProductsRequest(itemToDelete.value?.id);
    await fetchProducts();
    await fetchFilters();
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

const onCardsScrollEnd = () => {
  if (cardsIsFetching.value || products.value.length >= total.value) return;
  cardsIsFetching.value = true;
  page.value += 1;
  fetchMoreProducts().finally(() => { cardsIsFetching.value = false; });
};

watch(
  () => [searchQuery.value, sorting.value?.value],
  () => fetchProducts(),
  { deep: true },
);
fetchProducts();
</script>

<style scoped lang="scss">
.view-switcher {
  display: flex;
  gap: 2px;

  &__btn--active {
    color: theme('colors.main.DEFAULT');
    position: relative;

    &::after {
      content: '';
      position: absolute;
      bottom: 0;
      left: 4px;
      right: 4px;
      height: 2px;
      background: theme('colors.main.DEFAULT');
      border-radius: 1px;
    }
  }
}

.cards-content {
  padding: 0 0 40px;
}

.card-cell {
  padding: 10px;
  height: 100%;
  box-sizing: border-box;
}

.cards-empty {
  @apply text-sm-regular;
  color: theme('colors.additional.300');
  text-align: center;
  padding-top: 48px;
}

.items--cards :deep() .table,
.items--cards :deep() .no-data-block {
  display: none;
}

.items :deep() .table {
  .flex-table-cell {
    &:nth-child(2) {
      min-width: 80px;
      width: 100%;
      max-width: 80px;
    }

    &:nth-child(3) {
      min-width: 60px;
      width: 60px;
      max-width: 60px;
      padding-left: 8px;
      padding-right: 8px;
    }

    &:nth-child(4) {
      min-width: 176px;
      width: 100%;
      max-width: 250px;
      padding-right: 24px;
    }

    &:nth-child(5) {
      min-width: 152px;
      width: 100%;
      padding-left: 0;
      padding-right: 24px;
    }

    &:nth-child(6) {
      min-width: 80px;
      width: 100%;
      max-width: 200px;
      padding-left: 0;
      padding-right: 24px;
    }

    &:nth-child(7) {
      min-width: 120px;
      width: 120px;
      padding-left: 0;
      padding-right: 24px;
    }

    &:nth-child(8) {
      min-width: 72px;
      width: 72px;
      max-width: 80px;
      padding-left: 0;
      padding-right: 12px;
    }

    &:nth-child(9) {
      min-width: 120px;
      width: 100%;
      max-width: 140px;
      padding-left: 12px;
      padding-right: 12px;
    }

    &:nth-child(10) {
      min-width: 100px;
      width: 100%;
      max-width: 100px;
    }
  }
}
</style>

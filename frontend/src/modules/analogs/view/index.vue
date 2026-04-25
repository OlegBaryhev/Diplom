<template>
  <div class="analog-page min-h-screen w-full">
    <div class="analog-page__content w-full h-full">
      <VFixedHeaderNTable
        v-model:sorting="sorting"
        v-model:search="searchQuery"
        v-model:active-item="detailedItem"
        class="items"
        :disable-filter-button="isEqual(temporaryFilters, filters)"
        :disable-clear-button="checkDisableClear(temporaryFilters)"
        :column-headers="TABLE_COLUMN_HEADERS"
        :sorting-options="SORTING_OPTIONS"
        :title="PAGE_TITLE"
        :modes="ICON_ITEMS"
        show-total
        :total="analogs?.length"
        :items="analogs"
        :loading="loading"
        @accept-filter="acceptFilters()"
        @clear-filter="clearFilters()"
        @action="onActionsClick"
      >
        <template #default="{ item }">
          <TableBody :item="item" />
        </template>

        <template #header-actions>
          <VExportBtn
            v-if="userHasPermission(Permissions.Download)"
            :disabled="loading || !analogs.length"
            :export-function="exportAnalogs"
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
      v-if="detailedItem"
      :item="detailedItem"
      :fetch-items="fetchAnalogs"
      @close="detailedItem = null"
    />
  </div>
</template>

<script setup lang="ts">
import { debounce, isEqual, cloneDeep } from 'lodash';
import { watch } from 'vue';
import {
  getCategoriesRequest,
  getBrandsRequest,
  getAnalogsRequest,
  exportAnalogsRequest,
} from '../api';

import type {
  Category,
  Analog,
  analogFilter,
} from '../types';

import TableBody from '../components/TableBody.vue';
import SidePanel from '../components/SidePanel.vue';
import type { ColumnHeader } from '@/common/components/VTable/types';
import { downloadFileByBlob } from '@/common/utils/download-file';

import { Permissions } from '@/common/types/permissions';
import { userHasPermission } from '@/common/utils/permissions';
import { useCart } from '@/stores/cart';

const cartStore = useCart();

const PAGE_TITLE = 'Аналоги';

const TABLE_COLUMN_HEADERS: ColumnHeader[] = [
  { name: 'Наименование', key: 'name' },
  { name: 'Описание', key: 'description' },
  { name: 'Категория', key: 'category' },
  { name: 'Бренд', key: 'brand' },
  { name: 'Цена, ₽', key: 'price' },
];

const addAnalogToCart = (item: Analog) => {
  cartStore.addToCart(item);
};

const onActionsClick = (event: any) => {
  if (event.action.emit === 'add-to-cart') {
    addAnalogToCart(event.item);
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

const temporaryFilters = ref<analogFilter>(cloneDeep(DEFAULT_FILTERS));
const filters = ref<analogFilter>(cloneDeep(DEFAULT_FILTERS));

const checkDisableClear = (obj) =>
  Object.values(obj).every((el) => Array.isArray(el) ? !el?.length : !el);

const analogs = ref<Analog[] | null>([]);

const categories = ref<Category[] | null>([]);
const brand = ref<any[] | null>([]);

const filterLoading = ref<boolean>(false);
const analogsLoading = ref<boolean>(false);
const loading = computed<boolean>(() => filterLoading.value || analogsLoading.value);

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

const exportAnalogsLoading = ref<boolean>(false);
const exportAnalogs = async () => {
  exportAnalogsLoading.value = true;

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
    formData.append('filename', 'analogs.xlsx');

    const { data } = await exportAnalogsRequest(formData);
    downloadFileByBlob(data, 'analogs.xlsx');
  } finally {
    exportAnalogsLoading.value = false;
  }
};

const fetchAnalogs = debounce(async () => {
  analogsLoading.value = true;

  try {
    const params = {
      ...(searchQuery.value && { search: searchQuery.value }),
      ...(filters.value?.min_price && { min_price: filters.value.min_price * 100 }),
      ...(filters.value?.max_price && { max_price: filters.value.max_price * 100 }),
      ...(filters.value?.category_id?.id && { category_id: filters.value?.category_id?.id }),
      ...(filters.value?.brand_id?.id && { brand_id: filters.value?.brand_id?.id }),
      ...(sorting.value?.value && { sort_by: sorting.value?.value }),
    };

    const result = await getAnalogsRequest({
      ...params,
    });

    analogs.value = result?.data ?? [];
  } catch (error) {
    console.error(error);
  } finally {
    analogsLoading.value = false;
  }
});

const clearFilters = async (): Promise<void> => {
  temporaryFilters.value = cloneDeep(DEFAULT_FILTERS);
  filters.value = cloneDeep(DEFAULT_FILTERS);
  await fetchAnalogs();
};

const acceptFilters = async (): Promise<void> => {
  filters.value = cloneDeep(temporaryFilters.value);
  await fetchAnalogs();
};

watch(
  () => [searchQuery.value, sorting.value?.value],
  () => fetchAnalogs(),
  { deep: true },
);
fetchAnalogs();
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

    // Наименование
    &:nth-child(2){
      min-width: 16px + 136px + 24px;
      width: 100%;
      max-width: 250px;
      padding-right: 24px;
    }

    // Описание
    &:nth-child(3) {
      min-width: 128px + 24px;
      width: 100%;
      padding-left: 0;
      padding-right: 24px;
    }

    // Категория
    &:nth-child(4) {
      min-width: 56px + 24px;
      width: 100%;
      max-width: 200px;
      padding-left: 0;
      padding-right: 24px;
    }

    // Бренд
    &:nth-child(5) {
      min-width: 184px + 24px;
      width: 184px + 24px;
      padding-left: 0;
      padding-right: 24px;
    }

    // Цена
    &:nth-child(6) {
      min-width: 120px;
      width: 100%;
      max-width: 120px;
      padding-left: 12px;
      padding-right: 12px;
    }
    // Действия
    &:nth-child(7) {
      min-width: 100px;
      width: 100%;
      max-width: 100px;
    }
  }
}
</style>

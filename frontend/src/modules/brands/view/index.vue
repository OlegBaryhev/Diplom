<template>
  <div class="product-page min-h-screen w-full">
    <div class="product-page__content w-full h-full">
      <VFixedHeaderNTable
        v-model:sorting="sorting"
        v-model:search="searchQuery"
        v-model:active-item="detailedItem"
        class="items"
        :column-headers="TABLE_COLUMN_HEADERS"
        :sorting-options="SORTING_OPTIONS"
        show-total
        :total="total"
        :page="page"
        :items="brands"
        :loading="loading"
        :fetching-more-items-func="fetchMoreBrands"
        title="Бренды"
        @update:page="page = $event"
      >
        <template #default="{ item }">
          <TableBody :item="item" />
        </template>

        <template #header-actions>
          <VBtn
            v-if="userHasPermission(Permissions.Write)"
            data-test="add"
            @click="isItemBeingAdded = true"
          >
            Добавить
          </VBtn>

          <VExportBtn
            v-if="userHasPermission(Permissions.Download)"
            :disabled="loading || !brands.length"
            :export-function="exportBrands"
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
  </div>
</template>

<script setup lang="ts">
import { debounce } from 'lodash';
import { watch } from 'vue';
import {
  getBrandsRequest,
  exportBrandsRequest,
  deleteBrandsRequest,
} from '../api';
import { TABLE_ITEM_COUNT_TO_FETCH } from '@/consts';

import type { Brand } from '../types';

import { useModals } from '@/stores/modals';

import TableBody from '../components/TableBody.vue';
import SidePanel from '../components/SidePanel.vue';
import type { ColumnHeader } from '@/common/components/VTable/types';
import { downloadFileByBlob } from '@/common/utils/download-file';

import { Permissions } from '@/common/types/permissions';
import { userHasPermission } from '@/common/utils/permissions';

const modalStore = useModals();

const TABLE_COLUMN_HEADERS: ColumnHeader[] = [
  { name: 'Наименование', key: 'name' },
  { name: 'Описание', key: 'description' },
  { name: 'Зарегистрирован', key: 'created_at' },
];

const searchQuery = ref<string>('');

const SORTING_OPTIONS = [
  { value: 'name_asc', name: 'Название: А-Я' },
  { value: 'name_desc', name: 'Название: Я-А' },
];

const detailedItem = ref<any>(null);

const sorting = ref<string>(SORTING_OPTIONS[0] ?? '');

const brands = ref<Brand[]>([]);
const page = ref<number>(1);
const total = ref<number>(0);

const itemToDelete = ref(null);
const isItemBeingAdded = ref<boolean>(false);

const filterLoading = ref<boolean>(false);
const productsLoading = ref<boolean>(false);
const loading = computed<boolean>(() => filterLoading.value || productsLoading.value);

const exportBrandsLoading = ref<boolean>(false);
const exportBrands = async () => {
  exportBrandsLoading.value = true;

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
    formData.append('filename', 'brands.xlsx');

    const { data } = await exportBrandsRequest(formData);
    downloadFileByBlob(data, 'brands.xlsx');
  } finally {
    exportBrandsLoading.value = false;
  }
};

const fetchBrands = debounce(async () => {
  productsLoading.value = true;
  page.value = 1;

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
    formData.append('page', '1');
    formData.append('page_size', TABLE_ITEM_COUNT_TO_FETCH.toString());

    const result = await getBrandsRequest(formData);

    brands.value = result?.data?.items ?? [];
    total.value = result?.data?.total ?? 0;
  } catch (error) {
    console.error(error);
  } finally {
    productsLoading.value = false;
  }
});

const fetchMoreBrands = async (): Promise<void> => {
  try {
    const formData = new FormData();
    if (searchQuery.value) formData.append('search', searchQuery.value);
    if (sorting.value?.value) formData.append('sort_by', sorting.value.value);
    formData.append('page', page.value.toString());
    formData.append('page_size', TABLE_ITEM_COUNT_TO_FETCH.toString());

    const result = await getBrandsRequest(formData);

    brands.value = [...brands.value, ...(result?.data?.items ?? [])];
    total.value = result?.data?.total ?? 0;
  } catch (error) {
    console.error(error);
    throw error;
  }
};

const deleteItem = async () => {
  try {
    await deleteBrandsRequest(itemToDelete.value?.id);
    await fetchBrands();
  } finally {
    itemToDelete.value = null;
  }
};

watch(
  () => [searchQuery.value, sorting.value?.value],
  () => fetchBrands(),
  { deep: true },
);
fetchBrands();
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
    &:nth-child(3){
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

    // Зарегистрирован
    &:nth-child(5) {
      min-width: 118px;
      width: 118px;
      padding-left: 0;
    }
  }
}
</style>

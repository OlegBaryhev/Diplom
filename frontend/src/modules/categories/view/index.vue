<template>
  <div class="categories-page min-h-screen w-full">
    <div class="categories-page__content w-full h-full">
      <VFixedHeaderNTable
        v-model:sorting="sorting"
        v-model:search="searchQuery"
        v-model:active-item="detailedItem"
        class="items"
        :column-headers="TABLE_COLUMN_HEADERS"
        :sorting-options="SORTING_OPTIONS"
        show-total
        :total="categories?.length"
        :items="categories"
        :loading="loading"
        title="Категории"
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
            :disabled="loading || !categories.length"
            :export-function="exportCategories"
          />
        </template>
      </VFixedHeaderNTable>
    </div>

    <SidePanel
      v-if="detailedItem || isItemBeingAdded"
      :item="detailedItem"
      :fetch-items="fetchCategories"
      @close="detailedItem ? detailedItem = null : isItemBeingAdded = false"
      @delete="itemToDelete = $event; modalStore.open('removecategories')"
    />

    <VConfirmationModal
      id="removecategories"
      :title="!itemToDelete?.name ? `Вы действительно хотите удалить эту категорию?`
        : `Вы действительно хотите удалить категорию «${itemToDelete?.name ?? ''}»?`"
      text="Категория будет удалена без возможности восстановления"
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
  getCategoriesRequest,
  exportCategoriesRequest,
  deleteCategoriesRequest,
} from '../api';

import type { Category } from '../types';

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
];

const searchQuery = ref<string>('');

const SORTING_OPTIONS = [
  { value: 'name_asc', name: 'Название: А-Я' },
  { value: 'name_desc', name: 'Название: Я-А' },
];

const detailedItem = ref<any>(null);

const sorting = ref<string>(SORTING_OPTIONS[0] ?? '');

const categories = ref<Category[] | null>([]);

const itemToDelete = ref(null);
const isItemBeingAdded = ref<boolean>(false);

const categoriesLoading = ref<boolean>(false);
const exportCategoriesLoading = ref<boolean>(false);
const loading = computed<boolean>(() => categoriesLoading.value || exportCategoriesLoading.value);

const exportCategories = async () => {
  exportCategoriesLoading.value = true;

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
    formData.append('filename', 'categories.xlsx');

    const { data } = await exportCategoriesRequest(formData);
    downloadFileByBlob(data, 'categories.xlsx');
  } finally {
    exportCategoriesLoading.value = false;
  }
};

const fetchCategories = debounce(async () => {
  categoriesLoading.value = true;

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
    const result = await getCategoriesRequest(formData);

    categories.value = result?.data ?? [];
  } catch (error) {
    console.error(error);
  } finally {
    categoriesLoading.value = false;
  }
});

const deleteItem = async () => {
  try {
    await deleteCategoriesRequest(itemToDelete.value?.id);
    await fetchCategories();
  } finally {
    itemToDelete.value = null;
  }
};

watch(
  () => [searchQuery.value, sorting.value?.value],
  () => fetchCategories(),
  { deep: true },
);
fetchCategories();
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
  }
}
</style>

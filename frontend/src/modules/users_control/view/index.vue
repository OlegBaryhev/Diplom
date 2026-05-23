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
        :total="users.length"
        :items="users"
        :loading="loading"
        title="Пользователи"
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
            :disabled="loading || !users.length"
            :export-function="exportUsers"
          />
        </template>
      </VFixedHeaderNTable>
    </div>

    <SidePanel
      v-if="detailedItem || isItemBeingAdded"
      :item="detailedItem"
      :fetch-items="fetchUsers"
      @close="detailedItem ? detailedItem = null : isItemBeingAdded = false"
      @delete="itemToDelete = $event; modalStore.open('removeProduct')"
    />

    <VConfirmationModal
      id="removeProduct"
      :title="!itemToDelete?.name ? `Вы действительно хотите удалить этого пользователя?`
        : `Вы действительно хотите удалить пользователя «${itemToDelete?.name ?? ''}»?`"
      text="Пользователь будет удален без возможности восстановления"
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
  getUsersRequest,
  exportUsersRequest,
  deleteUserRequest,
} from '../api';

import type { UserItem } from '../types';

import { useModals } from '@/stores/modals';

import TableBody from '../components/TableBody.vue';
import SidePanel from '../components/SidePanel.vue';
import type { ColumnHeader } from '@/common/components/VTable/types';
import { downloadFileByBlob } from '@/common/utils/download-file';

import { Permissions } from '@/common/types/permissions';
import { userHasPermission } from '@/common/utils/permissions';

const modalStore = useModals();

const TABLE_COLUMN_HEADERS: ColumnHeader[] = [
  { name: 'Имя', key: 'name' },
  { name: 'Фамилия', key: 'surname' },
  { name: 'Эл. Почта', key: 'email' },
  { name: 'Роль', key: 'role' },
  { name: 'Статус', key: 'is_active' },
];

const searchQuery = ref<string>('');

const SORTING_OPTIONS = [
  { value: 'name_asc', name: 'Название: А-Я' },
  { value: 'name_desc', name: 'Название: Я-А' },
  { value: 'status_asc', name: 'Начать с активных' },
  { value: 'status_desc', name: 'Начать с не активных' },
];

const detailedItem = ref<any>(null);

const sorting = ref<string>(SORTING_OPTIONS[0] ?? '');

const users = ref<UserItem[] | null>([]);

const itemToDelete = ref(null);
const isItemBeingAdded = ref<boolean>(false);

const filterLoading = ref<boolean>(false);
const productsLoading = ref<boolean>(false);
const loading = computed<boolean>(() => filterLoading.value || productsLoading.value);

const exportUsersLoading = ref<boolean>(false);
const exportUsers = async () => {
  exportUsersLoading.value = true;

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
    formData.append('filename', 'users.xlsx');

    const { data } = await exportUsersRequest(formData);
    downloadFileByBlob(data, 'users.xlsx');
  } finally {
    exportUsersLoading.value = false;
  }
};

const fetchUsers = debounce(async () => {
  productsLoading.value = true;

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

    const result = await getUsersRequest(formData);

    users.value = result?.data ?? [];
  } catch (error) {
    console.error(error);
  } finally {
    productsLoading.value = false;
  }
});

const deleteItem = async () => {
  try {
    await deleteUserRequest(itemToDelete.value?.id);
    await fetchUsers();
  } finally {
    itemToDelete.value = null;
  }
};

watch(
  () => [searchQuery.value, sorting.value?.value],
  () => fetchUsers(),
  { deep: true },
);
fetchUsers();
</script>

<style scoped lang="scss">
.items :deep() .table {

  .flex-table-cell {
    // ID
    &:nth-child(2){
      min-width: 80px;
      width: 100%;
      max-width: 80px;
    }

    // Имя
    &:nth-child(3){
      min-width: 16px + 136px + 24px;
      width: 100%;
      max-width: 150px;
      padding-right: 24px;
    }

    // Фамилия
    &:nth-child(4) {
      min-width: 16px + 136px + 24px;
      width: 100%;
      max-width: 250px;
      padding-right: 24px;
    }

    // Email
    &:nth-child(5) {
      min-width: 118px;
      width: 100%;
      padding-left: 0;
    }

    // Роль
    &:nth-child(6) {
      min-width: 158px;
      width: 158px;
      padding-left: 0;
    }

    // Статус
    &:nth-child(7) {
      min-width: 118px;
      width: 118px;
      padding-left: 0;
    }
  }
}
</style>

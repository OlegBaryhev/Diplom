<template>
  <div class="roles-page min-h-screen w-full">
    <div class="roles-page__content w-full h-full">
      <VFixedHeaderNTable
        v-model:sorting="sorting"
        v-model:search="searchQuery"
        v-model:active-item="detailedRole"
        class="items"
        :column-headers="TABLE_COLUMN_HEADERS"
        :sorting-options="SORTING_OPTIONS"
        show-total
        :total="total"
        :page="page"
        :items="roles"
        :loading="loading"
        :fetching-more-items-func="fetchMoreRoles"
        title="Роли"
        @update:page="page = $event"
      >
        <template #default="{ item }">
          <TableBody :item="item" />
        </template>
        <template #header-actions>
          <VBtn
            v-if="isSuperuser"
            data-test="add"
            @click="isRoleBeingAdded = true"
          >
            Добавить
          </VBtn>
        </template>
      </VFixedHeaderNTable>
    </div>

    <SidePanel
      v-if="detailedRole || isRoleBeingAdded"
      :role="detailedRole"
      :fetch-roles="fetchRoles"
      @close="detailedRole = null; isRoleBeingAdded = false"
    />

    <VConfirmationModal
      id="deleteRole"
      :title="`Вы действительно хотите удалить роль «${roleToDelete?.name ?? ''}»?`"
      text="Роль будет удалена без возможности восстановления"
      confirmation-text="Удалить"
      :async-confirmation-func="deleteRole"
      @closed="roleToDelete = null"
    />
  </div>
</template>

<script setup lang="ts">
import { debounce } from 'lodash';
import { useUser } from '@/stores/user';
import { getRolesRequest, deleteRoleRequest } from '../api';
import { TABLE_ITEM_COUNT_TO_FETCH } from '@/consts';
import type { Role } from '../types';
import TableBody from '../components/TableBody.vue';
import SidePanel from '../components/SidePanel.vue';
import type { ColumnHeader } from '@/common/components/VTable/types';

const userStore = useUser();
const isSuperuser = computed(() => userStore.user?.role === 'superuser');

const TABLE_COLUMN_HEADERS: ColumnHeader[] = [{ name: 'Название', key: 'name' }];
const SORTING_OPTIONS = [
  { value: 'name_asc', name: 'Название: А-Я' },
  { value: 'name_desc', name: 'Название: Я-А' },
];

const searchQuery = ref('');
const sorting = ref(SORTING_OPTIONS[0] ?? '');
const roles = ref<Role[]>([]);
const page = ref<number>(1);
const total = ref<number>(0);
const detailedRole = ref<Role | null>(null);
const isRoleBeingAdded = ref(false);
const roleToDelete = ref<Role | null>(null);
const loading = ref(false);

const fetchRoles = debounce(async () => {
  loading.value = true;
  page.value = 1;
  try {
    const formData = new FormData();
    if (searchQuery.value) formData.append('search', searchQuery.value);
    if (sorting.value?.value) formData.append('sort_by', sorting.value.value);
    formData.append('page', '1');
    formData.append('page_size', TABLE_ITEM_COUNT_TO_FETCH.toString());
    const { data } = await getRolesRequest(formData);
    roles.value = data.items;
    total.value = data.total;
  } finally {
    loading.value = false;
  }
});

const fetchMoreRoles = async (): Promise<void> => {
  try {
    const formData = new FormData();
    if (searchQuery.value) formData.append('search', searchQuery.value);
    if (sorting.value?.value) formData.append('sort_by', sorting.value.value);
    formData.append('page', page.value.toString());
    formData.append('page_size', TABLE_ITEM_COUNT_TO_FETCH.toString());
    const { data } = await getRolesRequest(formData);
    roles.value = [...roles.value, ...data.items];
    total.value = data.total;
  } catch (error) {
    console.error(error);
    throw error;
  }
};

const deleteRole = async () => {
  if (roleToDelete.value) {
    await deleteRoleRequest(roleToDelete.value.id);
    await fetchRoles();
  }
};

watch([searchQuery, () => sorting.value?.value], () => fetchRoles(), { deep: true });
fetchRoles();
</script>

<style scoped lang="scss">
.items :deep() .table .flex-table-cell {
  &:first-child {
    min-width: 200px;
    width: 100%;
    max-width: 300px;
  }
}
</style>

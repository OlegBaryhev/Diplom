<template>
  <VSidePanel
    class="item-side-panel"
    :title="title"
    data-test="item-side-panel"
    @close="$emit('close')"
  >
    <template #default>
      <div class="content">
        <VInput
          v-model="formModel.name"
          label="Название роли"
          class="mb-6"
          secondary
          sm
          :error="v$.name.$errors?.[0]?.$message"
        />
        <div class="permissions-editor-wrapper rounded-2xl border border-gray-200 p-4 bg-white">
          <PermissionsEditor v-model="formModel.permissions" />
        </div>
      </div>
    </template>
    <template #foot="{ onClose }">
      <div class="flex justify-end space-x-4">
        <VBtn
          :text="formModel.id ? 'Отменить' : 'Отмена'"
          outlined
          small
          :disabled="saveLoading"
          @click="onClose"
        />
        <VBtn
          text="Сохранить"
          small
          :loading="saveLoading"
          @click="save"
        />
      </div>
    </template>
  </VSidePanel>
</template>

<script lang="ts" setup>
import { required, helpers } from '@vuelidate/validators';
import { useVuelidate } from '@vuelidate/core';
import PermissionsEditor from './PermissionsEditor.vue';
import { createRoleRequest, updateRoleRequest } from '../api';
import type { Role } from '../types';

const props = defineProps<{ role?: Role | null; fetchRoles: () => Promise<void> }>();
const emit = defineEmits(['close']);

const formModel = ref<Partial<Role>>(props.role ? { ...props.role } : { name: '', permissions: {} });
const saveLoading = ref(false);

const rules = {
  name: { required: helpers.withMessage('Название обязательно', required) },
};
const v$ = useVuelidate(rules, formModel);

const title = computed(() => props.role ? 'Редактирование роли' : 'Создание роли');

const save = async () => {
  v$.value.$touch();
  if (v$.value.$invalid) return;
  saveLoading.value = true;
  try {
    if (props.role) {
      await updateRoleRequest(props.role.id, formModel.value);
    } else {
      await createRoleRequest(formModel.value);
    }
    await props.fetchRoles();
    emit('close');
  } finally {
    saveLoading.value = false;
  }
};
</script>

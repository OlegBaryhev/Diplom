<template>
  <VSidePanel
    class="item-side-panel"
    :title="title"
    :loading="fetchFormOptionsLoading"
    data-test="item-side-panel"
    @close="$emit('close')"
  >
    <template
      v-if="!formModel"
      #head
    >
      <VSidePanelInfoItem
        caption="ID"
        :value="item?.id"
        is-head
      />
    </template>

    <template #default>
      <div
        class="content"
      >
        <template v-if="!formModel">
          <VSidePanelInfoItem
            class="mb-4"
            caption="Наименование"
            :value="item?.name"
            data-test="category-name"
          />

          <VSidePanelInfoItem
            class="mb-4"
            caption="Описание"
            :value="item?.description"
            data-test="category-description"
          />
        </template>

        <template v-else>
          <VInput
            v-model="formModel.name"
            label="Наименование"
            secondary
            sm
            :error="v$.formModel.name.$errors?.[0]?.$message || dateApiError"
            @update:model-value="dateApiError = ''"
          />

          <VInput
            v-model="formModel.description"
            input-classes="resize-none"
            tag="textarea"
            class="mt-7"
            label="Описание"
            optional
            secondary
            sn
            :max-length="180"
            :error="v$.formModel.description.$errors?.[0]?.$message"
            data-test="description"
          />
        </template>
      </div>
    </template>

    <template
      v-if="!(formModel && fetchFormOptionsLoading)"
      #foot="{ onClose }"
    >
      <div class="flex justify-end space-x-4">
        <VBtn
          v-if="formModel || userHasPermission(Permissions.Delete)"
          :text="formModel ? 'Отменить' : 'Удалить'"
          outlined
          small
          :disabled="saveChangesLoading"
          :data-test="formModel ? 'cancel-editing' : 'delete-item'"
          @click="cancelOrDelete(onClose)"
        />

        <VBtn
          v-if="userHasPermission(Permissions.Edit)"
          :text="formModel ? 'Сохранить' : 'Редактировать'"
          small
          :loading="saveChangesLoading"
          :data-test="formModel ? 'save-changes' : 'start-editing'"
          @click="formModel ? saveOrChange().then(onClose) : startEditing()"
        />
      </div>
    </template>
  </VSidePanel>
</template>

<script lang="ts" setup>
import { onBeforeUnmount } from 'vue';
import { required, helpers } from '@vuelidate/validators';

import { useVuelidate } from '@vuelidate/core';
import {
  ERRORS,
} from '@/common/validations';
import type { Category } from '@/modules/categories/types';

import {
  addCategoriesRequest,
  updateCategoriesRequest,
} from '../api';

import { isAPIError } from '@/api';
import { Permissions } from '@/common/types/permissions';
import { userHasPermission } from '@/common/utils/permissions';

const props = withDefaults(defineProps<{
  item?: Category | null;
  // eslint-disable-next-line func-call-spacing
  fetchItems:() => Promise<void>;
}>(), {
  item: null,
});

// eslint-disable-next-line func-call-spacing, no-spaced-func
const emits = defineEmits<{
  (evt: 'close'): void;
  (evt: 'delete', item: Category): void;
}>();

const dateApiError = ref('');
const hasBeenDeleted = ref<boolean>(false);

const formModel = ref<{
  name: string,
  description: string,
} | null>(null);

onBeforeUnmount(() => {
  if (hasBeenDeleted.value && props.item) emits('delete', props.item);
});

const title = computed(() => {
  if (!props.item) {
    return 'Добавление';
  }

  return formModel.value ? 'Редактирование' : 'Категория';
});

const validationRules = computed(() => ({
  formModel: {
    name: {
      required: helpers.withMessage(ERRORS.required, required),
    },
    description: {
      required: helpers.withMessage(ERRORS.required, required),
    },
  },
}));

const v$ = useVuelidate(validationRules, { formModel });

const startEditing = () => {
  formModel.value = {
    name: props.item ? props.item?.name ?? '' : '',
    description: props.item ? props.item?.description ?? '' : '',
  };
};

if (props.item === null) {
  startEditing();
}

const saveChangesLoading = ref(false);
const cancelOrDelete = (onClose: () => void) => {
  if (formModel.value && props.item) {
    formModel.value = null;
    return;
  }

  hasBeenDeleted.value = true;
  onClose();
};

const saveOrChange = async (): Promise<void> => {
  v$.value.$touch();
  try {
    if (!formModel.value || v$.value.$invalid) {
      throw new Error('validation err');
    }
    saveChangesLoading.value = true;

    const requestData = {
      name: formModel.value?.name ?? '',
      description: formModel.value?.description ?? '',
    };

    if (props.item) {
      await updateCategoriesRequest(props.item.id, requestData);
    } else {
      await addCategoriesRequest(requestData);
    }

    await props.fetchItems();
  } catch (err) {
    console.error(err.message);
    if (!isAPIError(err)) {
      throw err;
    }
    if (err.response?.status === 409) {
      dateApiError.value = 'Такая категория уже существует';
    }
    throw err;
  } finally {
    saveChangesLoading.value = false;
  }
};
</script>

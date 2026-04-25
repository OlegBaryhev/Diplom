<template>
  <VSidePanel
    class="item-side-panel"
    :title="title"
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
            class="mb-6"
            caption="Имя"
            :value="item?.name"
            data-test="user-name"
          />

          <VSidePanelInfoItem
            class="mb-6"
            caption="Фамилия"
            :value="item?.surname"
            data-test="user-surname"
          />

          <VSidePanelInfoItem
            class="mb-6"
            caption="Email"
            :value="item?.email"
            data-test="user-email"
          />
        </template>

        <template v-else>
          <VInput
            v-model="formModel.name"
            label="Имя"
            class="mb-6"
            secondary
            sm
            :error="v$.formModel.name.$errors?.[0]?.$messages"
          />

          <VInput
            v-model="formModel.surname"
            label="Фамилия"
            class="mb-6"
            secondary
            sm
          />

          <VInput
            v-model="formModel.email"
            label="Email"
            class="mb-6"
            secondary
            sm
            :error="v$.formModel.email.$errors?.[0]?.$message || dateApiError"
            @update:model-value="dateApiError = ''"
          />

          <template
            v-if="!item"
          >
            <VPasswordField
              v-model="formModel.password"
              class="w-full mb-6"
              label="Пароль"
              sm
              :error="v$.formModel.password?.$errors[0]?.$message"
              data-test="password"
              @update:model-value="v$.formModel.password.$reset()"
            />

            <VPasswordField
              v-model="confirmation"
              class="w-full mb-6"
              label="Подтверждение пароля"
              :error="v$.confirmation?.$errors[0]?.$message"
              sm
              data-test="password-confirmation"
              @update:model-value="v$.confirmation.$reset()"
            />
          </template>
        </template>

        <VSidePanelInfoItem
          v-if="!formModel || !userHasPermission(Permissions.ChangeRole)"
          class="mb-6"
          caption="Роль"
          :value="ROLES_LOCALIZATION_NAMES[item?.role]"
          data-test="user-email"
        />

        <VMultiselect
          v-else
          v-model="formModel.role"
          :options="ROLES_LOCALIZATION_NAMES_LIST(userStore.user?.role)"
          item-name="name"
          primary-key="value"
          class="mb-6"
          sm
          label="Роль"
          data-test="select-role"
        />

        <VSidePanelInfoItem
          v-if="!formModel || !userHasPermission(Permissions.Status)"
          class="mb-6"
          caption="Статус"
          data-test="user-status"
        >
          <VStatus
            class="mt-1"
            :value="item.is_active ? 'active' : 'not_activated'"
          >
            {{ item?.is_active ? 'Активный' : 'Не активный' }}
          </VStatus>
        </VSidePanelInfoItem>

        <VMultiselect
          v-else
          v-model="formModel.is_active"
          :options="USER_STATUS_LIST"
          item-name="name"
          primary-key="value"
          class="mb-6"
          sm
          label="Статус"
          data-test="select-role"
        />
      </div>
    </template>

    <template
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
import type { Brand } from '@/modules/brands/types';

import {
  validEmail,
  checkLength,
  ERRORS,
} from '@/common/validations';

import {
  ROLES_LOCALIZATION_NAMES,
  ROLES_LOCALIZATION_NAMES_LIST,
  USER_STATUS_LIST,
} from '@/consts';

import {
  createUserRequest,
  updateUserRequest,
} from '../api';

import { isAPIError } from '@/api';
import { Permissions } from '@/common/types/permissions';
import { useUser } from '@/stores/user';
import { userHasPermission } from '@/common/utils/permissions';

const props = withDefaults(defineProps<{
  item?: Brand | null;
  // eslint-disable-next-line func-call-spacing
  fetchItems:() => Promise<void>;
}>(), {
  item: null,
});

// eslint-disable-next-line func-call-spacing, no-spaced-func
const emits = defineEmits<{
  (evt: 'close'): void;
  (evt: 'delete', item: Brand): void;
}>();
const dateApiError = ref('');
const hasBeenDeleted = ref<boolean>(false);

const formModel = ref<{
  name: string,
  surname: string,
  email: string,
  role: string,
  is_active: boolean,
} | null>(null);

const userStore = useUser();

onBeforeUnmount(() => {
  if (hasBeenDeleted.value && props.item) emits('delete', props.item);
});

const title = computed(() => !props.item ? 'Добавление' : (formModel.value ? 'Редактирование' : 'Пользователь'));

const passwordError = ref<string>('');
const confirmation = ref<string>('');

const validationRules = computed(() => ({
  formModel: {
    name: {
      required: helpers.withMessage(ERRORS.required, required),
    },
    email: {
      required: helpers.withMessage(ERRORS.required, required),
      validEmail: helpers.withMessage(ERRORS.email, validEmail),
    },
    ...(!props.item && {
      password: {
        required: helpers.withMessage(ERRORS.required, required),
        checkLength: helpers.withMessage(ERRORS.checkLength(8), () => checkLength(formModel.value.password, 8)),
      },
    }),
  },

  ...(!props.item && {
    confirmation: {
      required: helpers.withMessage(ERRORS.required, required),
    },
  }),
}));

const v$ = useVuelidate(validationRules, { formModel, confirmation });

const startEditing = () => {
  formModel.value = {
    name: props.item ? props.item?.name ?? '' : '',
    surname: props.item ? props.item?.surname ?? '' : '',
    email: props.item ? props.item?.email ?? '' : '',
    role: props.item ? ROLES_LOCALIZATION_NAMES_LIST(userStore.user?.role).find(({ value }) => value === props.item?.role) ?? ROLES_LOCALIZATION_NAMES_LIST()[0] : ROLES_LOCALIZATION_NAMES_LIST()[0],
    is_active: props.item ? USER_STATUS_LIST.find(({ value }) => value === props.item?.is_active) ?? USER_STATUS_LIST[0] : USER_STATUS_LIST[0],
  };
};

if (props.item === null) startEditing();

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
    if (!formModel.value || v$.value.$invalid) throw new Error('validation err');
    if (confirmation.value !== '' && confirmation.value !== formModel.value?.password) {
      passwordError.value = 'Пароль не подтвержден!';
      return;
    }
    saveChangesLoading.value = true;

    const requestData = {
      name: formModel.value?.name ?? '',
      surname: formModel.value?.surname ?? '',
      email: formModel.value?.email ?? '',
      ...(!props.item && formModel.value?.password && { password: formModel.value?.password ?? '' }),
      ...(userHasPermission(Permissions.ChangeRole) && { role: formModel.value?.role?.value ?? '' }),
      ...(userHasPermission(Permissions.Status) && { is_active: formModel.value?.is_active?.value ?? '' }),
    };

    if (props.item) {
      await updateUserRequest(props.item.id, requestData);
    } else {
      const formData = new FormData();
      Object.keys(requestData).forEach((key) => formData.append(key, requestData[key]));

      const { response } = await createUserRequest(formData);

      if (response?.data?.detail === 'User with this email already exists') {
        throw new Error(response?.data?.detail);
      }
    }

    if (props.item?.id === userStore.user?.id) userStore?.getUser();
    await props.fetchItems();
  } catch (err) {
    console.error(err.message);
    if (!isAPIError(err)) throw err;
    if (err.response?.status === 409) dateApiError.value = 'Такой пользователь уже существует';

    throw err;
  } finally {
    saveChangesLoading.value = false;
  }
};
</script>

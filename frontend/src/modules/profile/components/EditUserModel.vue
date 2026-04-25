<template>
  <VConfirmationModal
    :id="modalId"
    title="Вы хотите отредактировать свои данные?"
    confirmation-text="Сохранить"
    :async-confirmation-func="() => saveUser()"
  >
    <template #body>
      <div class="flex flex-col gap-5">
        <VInput
          v-model="formModel.email"
          class="w-full"
          label="Логин / Email"
          :error="v$.formModel.email?.$errors[0]?.$message"
          sm
          data-test="email"
          @update:model-value="v$.formModel.email.$reset(); resultAPIError = ''"
        />

        <VInput
          v-model="formModel.name"
          class="w-full"
          label="Имя"
          :error="v$.formModel.name?.$errors[0]?.$message"
          sm
          data-test="name"
          @update:model-value="v$.formModel.name.$reset()"
        />

        <VInput
          v-model="formModel.surname"
          class="w-full"
          label="Фамилия"
          sm
          data-test="surname"
        />
      </div>
    </template>
  </VConfirmationModal>
</template>

<script lang="ts" setup>
import { useVuelidate } from '@vuelidate/core';
import { required, helpers } from '@vuelidate/validators';
import { editUserRequest } from '@/modules/profile/api';
import {
  validEmail,
  ERRORS,
} from '@/common/validations';

const props = withDefaults(defineProps<{
  modalId: string,
  userData: any,
}>(), {
  modalId: '',
});

// eslint-disable-next-line func-call-spacing, no-spaced-func
const emits = defineEmits<{ (evt: 'saveUser'): void }>();

const resultAPIError = ref<string>('');

const DEFAULT_FORM = {
  email: props.userData?.email ?? '',
  name: props.userData?.name ?? '',
  surname: props.userData?.surname ?? '',
};

const formModel = ref<any>(DEFAULT_FORM);

const validationRules = computed(() => ({
  formModel: {
    email: {
      required: helpers.withMessage(ERRORS.required, required),
      validEmail: helpers.withMessage(ERRORS.email, validEmail),
    },
    name: {
      required: helpers.withMessage(ERRORS.required, required),
    },
  },
}));

const v$ = useVuelidate(validationRules, { formModel });
const saveChangesLoading = ref<boolean>(false);

const saveUser = async (): Promise<void> => {
  saveChangesLoading.value = true;

  try {
    v$.value.$touch();

    if (v$.value.$invalid) throw new Error('validation err');

    await editUserRequest(formModel.value);
    emits('saveUser');
  } catch (error) {
    console.error(error.message);

    if (error.message === 'User with this email already exists') {
      resultAPIError.value = 'Пользователь уже существует!';
      return;
    }

    throw error;
  } finally {
    saveChangesLoading.value = false;
  }
};
</script>

<script lang="ts">
export default defineComponent({
  name: 'EditUserModel',
});
</script>

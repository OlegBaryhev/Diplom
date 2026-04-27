<template>
  <section class="auth-wrapper relative flex w-[100vw] min-h-full h-full flex-wrap items-center justify-center">
    <aside class="auth-wrapper__title-aside pl-5 items-center pl-5 flex h-full justify-center w-[50vw] gap-[130px]">
      <VCursorLevel
        class="h-[80%]"
        is-black
      />
      <h1 class="auth-wrapper__title flex flex-col text-[60px] font-bold mb-4 select-none uppercase">
        Регистрация в системе ценообразования
        <span class="text-main">"Doge Devices"</span>
      </h1>
    </aside>

    <aside class="auth-wrapper__form w-[50vw] max-w-[900px] min-w-[600px] h-fit flex flex-col gap-6 items-start justify-center">
      <form
        class="flex flex-col gap-6 justify-center w-[75%]"
        @submit.prevent="register();"
      >
        <div class="auth-wrapper__info border-l-2 border-black pl-5 w-full flex flex-col gap-2">
          <h3 class="font-bold">
            Предлагаю вам стать частью нашего сообщества
          </h3>
          <p>Авторизуйтесь в системе, чтобы получить доступ к большему количеству функций</p>
        </div>

        <VInput
          v-model="formModel.email"
          class="w-full"
          label="Логин / Email"
          :error="v$.formModel.email?.$errors[0]?.$message"
          sm
          data-test="email"
          @update:model-value="v$.formModel.email.$reset(); resultAPIError = ''"
        />

        <div class="flex justify-between items-center w-full gap-4">
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

        <div class="flex justify-between items-center w-full gap-4">
          <VPasswordField
            v-model="formModel.password"
            class="w-full"
            label="Пароль"
            sm
            :error="v$.formModel.password?.$errors[0]?.$message"
            data-test="password"
            @update:model-value="v$.formModel.password.$reset()"
          />

          <VPasswordField
            v-model="confirmation"
            class="w-full"
            label="Подтверждение пароля"
            :error="v$.confirmation?.$errors[0]?.$message"
            sm
            data-test="password-confirmation"
            @update:model-value="v$.confirmation.$reset()"
          />
        </div>

        <div class="flex flex-col w-full">
          <VErrorMessage
            v-if="resultAPIError || passwordError"
            :error="resultAPIError || passwordError"
          />

          <div class="flex items-center mt-6 gap-6 w-full max-w-[825px]">
            <VBtn
              text="Применить"
              icon="arrow-right"
              icon-scale="0.7"
              type="submit"
              :disabled="saveChangesLoading"
            />

            <VBtn
              text="Очистить"
              outlined
              :disabled="saveChangesLoading"
              @click="clearForm()"
            />
          </div>
        </div>
      </form>
    </aside>
  </section>
</template>

<script lang="ts" setup>
import { cloneDeep } from 'lodash';
import { useRouter } from 'vue-router';
import { useVuelidate } from '@vuelidate/core';
import { required, helpers } from '@vuelidate/validators';

import {
  validEmail,
  checkLength,
  ERRORS,
} from '@/common/validations';

import { registerRequest } from '@/api/auth';
import type { IAuthForm } from '../types';

const router = useRouter();
const DEFAULT_FORM: IAuthForm = {
  email: '',
  surname: '',
  name: '',
  password: '',
};

const formModel = ref<IAuthForm>(cloneDeep(DEFAULT_FORM));
const resultAPIError = ref<string>('');
const passwordError = ref<string>('');

const validationRules = computed(() => ({
  formModel: {
    email: {
      required: helpers.withMessage(ERRORS.required, required),
      validEmail: helpers.withMessage(ERRORS.email, validEmail),
    },
    name: {
      required: helpers.withMessage(ERRORS.required, required),
    },
    password: {
      required: helpers.withMessage(ERRORS.required, required),
      checkLength: helpers.withMessage(ERRORS.checkLength(8), () => checkLength(formModel.value.password, 8)),
    },
  },

  confirmation: {
    required: helpers.withMessage(ERRORS.required, required),
  },
}));

const confirmation = ref<string>('');

const v$ = useVuelidate(validationRules, { formModel, confirmation });

const saveChangesLoading = ref<boolean>(false);

const clearForm = () => {
  v$.value.$reset();
  resultAPIError.value = '';
  confirmation.value = '';
  formModel.value = cloneDeep(DEFAULT_FORM);
};

const register = async (): Promise<void> => {
  saveChangesLoading.value = true;

  try {
    v$.value.$touch();

    if (v$.value.$invalid) throw new Error('validation err');
    if (confirmation.value !== '' && confirmation.value !== formModel.value?.password) {
      passwordError.value = 'Пароль не подтвержден!';
      return;
    }

    const formData = new FormData();
    Object.keys(formModel.value).forEach((key) => formData.append(key, formModel.value[key]));

    const { response } = await registerRequest(formData);
    if (response?.data?.detail === 'User with this email already exists') {
      throw new Error(response?.data?.detail);
    }

    await nextTick();

    router.push('/login');
  } catch (error) {
    console.error(error.message);

    if (error.message === 'User with this email already exists') {
      resultAPIError.value = 'Пользователь уже существует!';
      passwordError.value = '';
      return;
    }

    throw error;
  } finally {
    saveChangesLoading.value = false;
  }
};
</script>

<style lang="scss" scoped>
@media (max-width: 1600px) {
  .auth-wrapper__title-aside {
    display: none;
  }
}
</style>

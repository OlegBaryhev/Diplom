<template>
  <section class="auth-wrapper relative flex w-[100vw] min-h-full h-full flex-wrap items-center justify-center gap-5">
    <aside class="auth-wrapper__title-aside flex items-center h-full min-w-[500px] justify-center w-[50vw] gap-[130px]">
      <VCursorLevel
        class="h-[80%]"
        is-black
      />
      <h1 class="auth-wrapper__title flex flex-col text-[60px] font-bold mb-4 select-none uppercase">
        Авторизация в системе<br />
        <span class="text-[50px]">ценообразования</span>
        <span class="text-main">"Doge Devices"</span>
      </h1>
    </aside>

    <aside
      class="auth-wrapper__form w-[50vw] max-w-[900px] min-w-[700px] h-fit flex flex-col gap-6 items-start justify-center"
    >
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
          label="Email"
          :error="v$.formModel.email?.$errors[0]?.$message"
          sm
          data-test="email"
          @update:model-value="v$.formModel.email.$reset(); resultAPIError = ''"
        />

        <VPasswordField
          v-model="formModel.password"
          class="w-full"
          label="Пароль"
          sm
          :error="v$.formModel.password?.$errors[0]?.$message"
          data-test="password"
          @update:model-value="v$.formModel.password.$reset()"
        />

        <div class="flex flex-col w-full">
          <VErrorMessage
            v-if="errorMessage"
            :error="errorMessage"
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
              @click="clearForm"
            />
          </div>
        </div>
      </form>
    </aside>
  </section>
</template>

<script lang="ts" setup>
import { cloneDeep } from 'lodash';

import { useVuelidate } from '@vuelidate/core';
import { required, helpers } from '@vuelidate/validators';
import {
  validEmail,
  checkLength,
  ERRORS,
} from '@/common/validations';

import { isAPIError } from '@/api';
import type { TLogin } from '../types';
import { useUser } from '@/stores/user';

const userStore = useUser();

const errorMessage = ref<string>();
const DEFAULT_FORM: TLogin = {
  email: '',
  password: '',
};

const formModel = ref<TLogin>(cloneDeep(DEFAULT_FORM));
const resultAPIError = ref<string>('');

const validationRules = computed(() => ({
  formModel: {
    email: {
      required: helpers.withMessage(ERRORS.required, required),
      validEmail: helpers.withMessage(ERRORS.email, validEmail),
    },
    password: {
      required: helpers.withMessage(ERRORS.required, required),
      checkLength: helpers.withMessage(ERRORS.checkLength(8), () => checkLength(formModel.value.password, 8)),
    },
  },
}));

const confirmation = ref<string>('');

const v$ = useVuelidate(validationRules, { formModel, confirmation });

const saveChangesLoading = ref<boolean>(false);

const clearForm = () => {
  v$.value.$reset();
  resultAPIError.value = '';
  formModel.value = cloneDeep(DEFAULT_FORM);
};

const register = async (): Promise<void> => {
  saveChangesLoading.value = true;

  try {
    v$.value.$touch();

    if (v$.value.$invalid) throw new Error('validation err');

    const form = new FormData();
    form.append('username', formModel.value?.email ?? '');
    form.append('password', formModel.value?.password ?? '');

    await userStore.login(form);
  } catch (error) {
    console.error(error.message);

    if (error.message === 'Incorrect email or password') {
      errorMessage.value = 'Не верный Email или пароль';
    }

    if (!isAPIError(error)) return;

    throw error;
  } finally {
    saveChangesLoading.value = false;
  }
};
</script>

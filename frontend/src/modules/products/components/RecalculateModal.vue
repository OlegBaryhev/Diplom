<template>
  <VModalWrap
    :modal-id="modalId"
    title="Быстрый перерасчет цен"
    @closed="internalFile = null"
  >
    <template #modal-body>
      <div class="flex flex-col gap-5 w-full min-w-[500px] h-full min-h-[600px]">
        <div class="flex flex-col gap-2">
          <h2 class="text-additional-300 text-base-regular">Форма пересчета</h2>
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
            label="Описание"
            :error="v$.formModel.description.$errors?.[0]?.$message"
            data-test="description"
          />
        </div>

        <h3 class="text-sm text-additional-300 text-base-regular">Тип пересчета цен</h3>
        <div class="flex gap-3 flex-col">
          <VRadio
            v-model="modeValue"
            :value="0"
            name="basic"
            label="Относительно текущей цены"
          />

          <VRadio
            v-model="modeValue"
            :value="1"
            name="basic"
            label="Приведение к значению"
          />

          <VRadio
            v-model="modeValue"
            :value="2"
            name="basic"
            label="Относительно усредненной цены"
          />
        </div>

        <div class="flex flex-col gap-4 pt-4">
          <h2 class="text-additional-300 text-base-regular">Основная форма пересчета</h2>
          <VInput
            v-model="formModel.value"
            class="w-[50%]"
            label="Значение"
            mask="number"
            sm
          />

          <div
            class="flex gap-4"
          >
            <VRadio
              v-model="formModel.negative"
              :value="false"
              name="negative"
              label="Увеличить цену"
            />

            <VRadio
              v-model="formModel.negative"
              :value="true"
              name="negative"
              label="Уменьшить цену"
            />
          </div>

          <VCheckbox
            v-if="modeValue === 2"
            v-model="formModel.offset"
            label="Применить смещение"
            :value="true"
          />

          <template
            v-if="modeValue === 0 || modeValue === 2"
          >
            <h3 class="text-sm text-additional-300 text-base-regular">Тип установки значения</h3>
            <div
              class="flex gap-4"
            >
              <VRadio
                v-model="formModel.type"
                value="rubles"
                name="type"
                label="Рубли"
              />

              <VRadio
                v-model="formModel.type"
                value="percent"
                name="type"
                label="Проценты"
              />
            </div>
          </template>
        </div>
      </div>
    </template>

    <template #modal-footer>
      <div class="space-x-4">
        <VBtn
          text="Отменить"
          outlined
          small
          data-test="cancel"
          @click="modalStore.close(modalId)"
        />

        <VBtn
          text="Подтвердить"
          small
          data-test="submit"
          @click="emit('confirm')"
        />
      </div>
    </template>
  </VModalWrap>
</template>

<script lang="ts" setup>
import { required, helpers } from '@vuelidate/validators';
import { useVuelidate } from '@vuelidate/core';
import {
  ERRORS,
} from '@/common/validations';

import {
  recalculateRelativeCurrentPrice,
  recalculateFixedValue,
  recalculateAverageRelativePrice,
} from '@/modules/recalculate_history/api';

import { MAX_FLOAT_VALUE } from '@/consts';
import { useModals } from '@/stores/modals';

const modalStore = useModals();

const props = withDefaults(defineProps<{
  file: File | null;
  accept: string;
  modalId?: string;
}>(), {
  modalId: 'recalculateModal',
});

const formModel = ref<{
  name: string,
  description: string,
  type?: 'rubles' | 'percent',
} | null>({});

const modeValue = ref(0);

watch(
  () => modeValue.value,
  (val) => {
    formModel.value = {
      name: formModel.value?.name ?? '',
      description: formModel.value?.description ?? '',
      value: formModel.value?.value ?? 0,
      negative: formModel.value?.negative ?? false,
      ...(val !== 1 && { type: formModel.value?.type ?? 'rubles' }),
    };
  },
  { immediate: true },
);
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

// eslint-disable-next-line func-call-spacing, no-spaced-func
const emit = defineEmits<{
  (evt: 'confirm'): void,
}>();
</script>

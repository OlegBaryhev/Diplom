<template>
  <VModalWrap
    :modal-id="modalId"
    title="Быстрый перерасчет цен"
    @closed="resetForm"
  >
    <template #modal-body>
      <div class="flex flex-col gap-6 w-full min-w-[460px] min-h-[420px]">
        <VInput
          v-model="formModel.name"
          label="Наименование пересчета"
          secondary
          sm
          :error="v$.formModel.name.$errors?.[0]?.$message || apiError"
          @update:model-value="apiError = ''"
        />

        <div class="flex flex-col gap-2">
          <h3 class="text-additional-300 text-sm-medium">
            Тип пересчета
          </h3>
          <div class="flex flex-col gap-2">
            <VRadio
              v-model="modeValue"
              :value="0"
              name="recalc-mode"
              label="Относительно текущей цены"
            />
            <VRadio
              v-model="modeValue"
              :value="1"
              name="recalc-mode"
              label="Приведение к фиксированному значению"
            />
            <VRadio
              v-model="modeValue"
              :value="2"
              name="recalc-mode"
              label="Относительно усредненной цены"
            />
          </div>
        </div>

        <div class="flex flex-col gap-4">
          <h3 class="text-additional-300 text-sm-medium">
            Параметры
          </h3>

          <VInput
            v-model="formModel.value"
            class="w-[50%]"
            label="Значение"
            mask="number"
            sm
            secondary
          />

          <template v-if="modeValue !== 1">
            <div class="flex gap-4">
              <VRadio
                v-model="formModel.type"
                value="rubles"
                name="recalc-type"
                label="Рубли"
              />
              <VRadio
                v-model="formModel.type"
                value="percent"
                name="recalc-type"
                label="Проценты"
              />
            </div>
          </template>

          <div class="flex gap-4">
            <VRadio
              v-model="formModel.negative"
              :value="false"
              name="recalc-negative"
              label="Увеличить"
            />
            <VRadio
              v-model="formModel.negative"
              :value="true"
              name="recalc-negative"
              label="Уменьшить"
            />
          </div>

          <VCheckbox
            v-if="modeValue === 2"
            v-model="formModel.offset"
            label="Применить смещение относительно среднего"
            :value="true"
          />
        </div>

        <p
          v-if="filtersActive"
          class="text-sm-regular text-additional-300"
        >
          Пересчет применится к товарам с учётом текущих фильтров таблицы
        </p>
        <p
          v-else
          class="text-sm-regular text-additional-300"
        >
          Пересчет применится ко всем товарам
        </p>
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
          text="Применить"
          small
          :loading="loading"
          data-test="submit"
          @click="submit"
        />
      </div>
    </template>
  </VModalWrap>
</template>

<script lang="ts" setup>
import { required, helpers } from '@vuelidate/validators';
import { useVuelidate } from '@vuelidate/core';
import { ERRORS } from '@/common/validations';
import {
  recalculateRelativeCurrentPrice,
  recalculateFixedValue,
  recalculateAverageRelativePrice,
} from '@/modules/recalculate_history/api';
import { useModals } from '@/stores/modals';
import { useUser } from '@/stores/user';

const props = withDefaults(defineProps<{
  modalId?: string;
  filters?: Record<string, any>;
}>(), {
  modalId: 'recalculateModal',
  filters: () => ({}),
});

// eslint-disable-next-line func-call-spacing, no-spaced-func
const emit = defineEmits<{
  (evt: 'done'): void;
}>();

const modalStore = useModals();
const userStore = useUser();
const loading = ref(false);
const apiError = ref('');
const modeValue = ref(0);

const formModel = ref({
  name: '',
  value: 0 as number | string,
  negative: false,
  type: 'rubles' as 'rubles' | 'percent',
  offset: false,
});

const filtersActive = computed(() => Object.keys(props.filters ?? {}).some(
  (k) => props.filters[k] !== undefined && props.filters[k] !== '',
));

const validationRules = computed(() => ({
  formModel: {
    name: { required: helpers.withMessage(ERRORS.required, required) },
  },
}));

const v$ = useVuelidate(validationRules, { formModel });

const resetForm = () => {
  modeValue.value = 0;
  formModel.value = {
    name: '',
    value: 0,
    negative: false,
    type: 'rubles',
    offset: false,
  };
  v$.value.$reset();
  apiError.value = '';
};

watch(
  () => modeValue.value,
  (val) => {
    if (val === 1) {
      formModel.value.type = 'rubles';
      formModel.value.negative = false;
    }
  },
);

const submit = async () => {
  v$.value.$touch();
  if (v$.value.$invalid) return;

  loading.value = true;
  try {
    const sign = formModel.value.negative ? -1 : 1;
    const numValue = Number(formModel.value.value) * sign;
    const recalculatedBy = userStore.user?.email ?? 'unknown';
    const base = {
      name: formModel.value.name,
      recalculated_by: recalculatedBy,
      ...(props.filters ?? {}),
    };

    if (modeValue.value === 0) {
      await recalculateRelativeCurrentPrice({
        ...base,
        value: numValue,
        type: formModel.value.type,
      });
    } else if (modeValue.value === 1) {
      await recalculateFixedValue({
        ...base,
        value: Math.abs(Number(formModel.value.value)),
      });
    } else {
      await recalculateAverageRelativePrice({
        ...base,
        value: numValue,
        type: formModel.value.type,
        offset: formModel.value.offset,
      });
    }

    emit('done');
    modalStore.close(props.modalId);
    resetForm();
  } catch (err: any) {
    apiError.value = err?.response?.data?.detail ?? 'Ошибка при выполнении перерасчёта';
  } finally {
    loading.value = false;
  }
};
</script>

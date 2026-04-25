<template>
  <VDatepicker
    :model-value="date"
    :label="filter?.name"
    hide-infinite
    :position="position"
    :error="v$.date.$errors[0]?.$message"
    data-test="datepicker"
    @focus="focusDatepicker"
    @blur="calendarValidation"
    @clear="v$.$reset()"
    @update:modelValue="updateDate"
  />
</template>

<script lang="ts" setup>
import { useVuelidate } from '@vuelidate/core';
import { helpers } from '@vuelidate/validators';
import { twoDates, validTwoDate, ERRORS } from '@/common/validations';

const emits = defineEmits(['update:modelValue', 'updateError']);

const props = withDefaults(defineProps<{
  modelValue: any[],
  filter: Record<string, any>,
  position?: 'left' | 'right',
  error?: boolean,
}>(), {
  position: 'left',
});

const date = computed(() => props.modelValue);

const rules = {
  date: {
    twoDates: helpers.withMessage(ERRORS.twoDates, twoDates),
    validTwoDate: helpers.withMessage(ERRORS.dateValid, validTwoDate),
  },
};

const v$ = useVuelidate(rules, { date });

onMounted(() => {
  if (props.error) v$.value.$validate();
});

const calendarValidation = () => v$.value.$validate();

const focusDatepicker = () => {
  if (v$.value.date.$error) v$.value.$reset();
};

const updateDate = (dateRange) => {
  const localRange = [];
  dateRange[0] && localRange.push(dateRange[0]);
  dateRange[1] && localRange.push(dateRange[1]);

  emits('update:modelValue', localRange);
};

watch(
  () => v$.value.date.$error,
  (newValue) => {
    if (!v$.value.date.$error) v$.value.$reset();
    emits('updateError', newValue);
  },
);
</script>

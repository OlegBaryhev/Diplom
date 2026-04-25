<template>
  <VInput
    ref="input"
    :model-value="inputModelValue"
    mask="search-table"
    search
    :secondary="secondary"
    :primary="primary"
    :sm="sm"
    :label="label"
    :placeholder="placeholder"
    :disabled="disabled"
    :error="error"
    :input-focus="inputFocus"
    :focus-once="focusOnce"
    :loading="loading"
    data-test="search"
    @update:model-value="inputHandler"
    @clear-input="clearHandler"
  />
</template>

<script lang="ts" setup>
import { debounce } from 'lodash';

const DEBOUNCED_SEARCH_DELAY = 500;

const props = withDefaults(defineProps<{
  modelValue: string;
  label?: string;
  placeholder?: string;
  sm?: boolean;
  minLength?: number;
  debounced?: boolean;
  disabled?: boolean;
  error?: string | boolean;
  inputFocus?: boolean;
  secondary?: boolean;
  primary?: boolean;
  focusOnce?: boolean;
  loading?: boolean;
}>(), {
  placeholder: 'Поиск',
  minLength: 0,
  debounced: false,
  secondary: false,
  primary: false,
  focusOnce: false,
});

// eslint-disable-next-line func-call-spacing, no-spaced-func
const inputModelValue = ref(props.modelValue);

const emit = defineEmits<{(evt: 'update:modelValue', newModelValue: string): void }>();

const search = (value: string): void => {
  if ((!value || value.length >= props.minLength) && value !== props.modelValue) {
    emit('update:modelValue', value);
  }
};

const input = ref(null);

const debouncedSearch = debounce(() => {
  search(inputModelValue.value.trim());
}, DEBOUNCED_SEARCH_DELAY);

const inputHandler = (value: string): void => {
  inputModelValue.value = value;
  if (props.debounced) {
    debouncedSearch();
  } else {
    search(value.trim());
  }
};

watch(() => props.modelValue, (newVal) => {
  inputModelValue.value = newVal;
});

const clearHandler = (): void => {
  inputModelValue.value = '';
  emit('update:modelValue', '');

  if (props.debounced) debouncedSearch.cancel();
};

defineExpose({ input });
</script>

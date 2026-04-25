<template>
  <VInput
    ref="input"
    class="border-none p-0"
    :model-value="inputModelValue"
    :secondary="secondary"
    :primary="primary"
    :sm="sm"
    :label="label"
    :placeholder="placeholder"
    :disabled="disabled"
    :type="!showPassword ? 'password' : 'text'"
    :error="error"
    :input-focus="inputFocus"
    :focus-once="focusOnce"
    :loading="loading"
    data-test="password-field"
    @update:model-value="inputHandler"
    @clear-input="clearHandler"
  >
    <template #iconSlot>
      <Transition name="fade">
        <VIcon
          class="cursor-pointe ml-5"
          role="button"
          :name="showPassword ? 'eye-on' : 'eye-off'"
          @click="showPassword = !showPassword; "
        />
      </Transition>
    </template>
  </VInput>
</template>

<script lang="ts" setup>

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
  secondary: false,
  primary: false,
  focusOnce: false,
});

const inputModelValue = ref<string>(props.modelValue);
const emit = defineEmits<{(evt: 'update:modelValue', newModelValue: string): void }>();

watch(
  () => props.modelValue,
  (newVal) => {
    inputModelValue.value = newVal;
  },
);

const showPassword = ref<boolean>(false);

const inputHandler = (value: string): void => {
  emit('update:modelValue', value);
};

const clearHandler = (): void => {
  inputModelValue.value = '';
  emit('update:modelValue', '');
};
</script>

<style lang="scss" scoped>
</style>

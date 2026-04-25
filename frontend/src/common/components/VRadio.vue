<template>
  <label
    class="radio"
    :class="[$attrs.class, {
      'radio--disabled': disabled,
      'radio--erroneous': error,
      'radio--boxed': boxed,
    }]"
    @[allowDeactivation&&`click`]="clickHandler"
  >
    <input
      v-model="internalModelValue"
      v-bind="attrsExcludingClass"
      class="radio__input"
      type="radio"
      :value="value"
      :disabled="disabled"
    >
    <span class="radio__control" />

    <span
      v-if="$slots.default ?? label"
      class="radio__label"
    >
      <slot>{{ label }}</slot>
    </span>
  </label>
</template>

<script lang="ts" setup>
import { omit } from 'lodash';

const attrs = useAttrs();
const attrsExcludingClass = omit(attrs, 'class');

const props = withDefaults(defineProps<{
  modelValue?: any;
  value?: any;
  label?: string;
  disabled?: boolean;
  error?: boolean;
  boxed?: boolean;
  allowDeactivation?: boolean;
  defaultValue?: any;
}>(), {
  label: '',
  disabled: false,
  error: false,
  boxed: false,
  allowDeactivation: false,
});

const emit = defineEmits(['update:modelValue']);
const internalModelValue = useVModel(props, 'modelValue', emit);
const deactivationСonditions = computed(() => internalModelValue.value === props.value && internalModelValue.value && props.allowDeactivation);
const clickHandler = (e:Event):void => {
  e.preventDefault();
  if (deactivationСonditions.value) {
    e.stopPropagation();
    emit('update:modelValue', null);
  }
};

onMounted(() => {
  if (props.defaultValue) emit('update:modelValue', props.defaultValue);
});
</script>

<script lang="ts">
export default defineComponent({
  inheritAttrs: false,
});
</script>

<style lang="scss" scoped>
.radio {
  display: flex;
  align-items: flex-start;
  user-select: none;
  cursor: pointer;

  $radio: &;

  &__control {
    @apply transition-colors;

    margin: 3px;
    border-radius: 50%;
    border: 1px solid theme('colors.additional.300');
    width: 18px;
    height: 18px;
    flex-shrink: 0;
    background-color: theme('colors.white');
    position: relative;

    &::before {
      @apply transition-all;

      content: '';
      border-radius: 50%;
      width: 8px;
      height: 8px;
      position: absolute;
      left: 50%;
      top: 50%;
      transform: translate(-50%, -50%) scale(0);
      background-color: theme('colors.white');
      will-change: transform;
    }
  }

  &__label {
    @apply text-base-regular transition-colors;

    margin: 1px 0 1px 8px;
    color: theme('colors.additional.300');
  }

  &__input {
    position: absolute;
    z-index: -1;
    opacity: 0;

    &:checked {
      + #{$radio}__control {
        border-color: theme('colors.main.400');
        background-color: theme('colors.main.400');

        &::before {
          transform: translate(-50%, -50%) scale(1);
        }
      }

      ~ #{$radio}__label {
        color: theme('colors.main.400');
      }

      &:focus-visible + #{$radio}__control {
        border-color: theme('colors.main.500');
        background-color: theme('colors.main.500');
      }
    }
  }

  &:hover {
    #{$radio}__control {
      border-color: theme('colors.main.500');
    }

    #{$radio}__label {
      color: theme('colors.main.500');
    }

    #{$radio}__input:checked + #{$radio}__control {
      background-color: theme('colors.main.500');
    }
  }
}
</style>

<template>
  <label
    class="checkbox"
    :class="[$attrs.class, {
      'checkbox--disabled': disabled,
      'checkbox--indeterminate': indeterminate,
      'checkbox--erroneous': error,
      'checkbox--boxed': boxed,
    }]"
  >
    <VLoader
      v-if="loading"
      small
    />

    <template v-else>
      <input
        v-model="internalModelValue"
        v-bind="attrsExcludingClass"
        class="checkbox__input"
        type="checkbox"
        :value="value"
        :disabled="disabled || readonly"
      >
      <span class="checkbox__control">
        <VIcon
          class="checkbox__control-icon checkbox__control-icon--checked w-4 h-4"
          name="check"
        />
        <VIcon
          class="checkbox__control-icon checkbox__control-icon--indeterminate w-4 h-4"
          name="minus"
        />
      </span>
    </template>

    <span
      v-if="$slots.default ?? label"
      class="checkbox__label"
    >
      <slot>{{ label }}</slot>
    </span>
  </label>
</template>

<script lang="ts" setup>
import { omit } from 'lodash';
import type { CheckboxValue, CheckboxChecked } from '@/common/types';

const attrs = useAttrs();
const attrsExcludingClass = omit(attrs, 'class');

const props = withDefaults(defineProps<{
  modelValue?: CheckboxChecked;
  value?: CheckboxValue;
  label?: string;
  disabled?: boolean;
  indeterminate?: boolean;
  error?: boolean;
  boxed?: boolean;
  readonly?: boolean;
  loading?: boolean;
}>(), {
  modelValue: false,
  label: '',
  disabled: false,
  indeterminate: false,
  error: false,
  boxed: false,
  readonly: false,
  loading: false,
});

// eslint-disable-next-line func-call-spacing, no-spaced-func
const emit = defineEmits<{
  (evt: 'update:modelValue', newModelValue: CheckboxChecked): void;
  (evt: 'update:indeterminate', newIndeterminate: boolean): void;
}>();

const internalModelValue = useVModel(props, 'modelValue', emit);

watchOnce(internalModelValue, () => {
  if (props.indeterminate) {
    emit('update:indeterminate', false);
  }
});
</script>

<script lang="ts">
export default defineComponent({
  inheritAttrs: false,
});
</script>

<style lang="scss" scoped>
.checkbox {
  width: fit-content;
  display: flex;
  align-items: flex-start;
  user-select: none;
  cursor: pointer;

  $checkbox: &;

  &__control {
    @apply transition-colors;

    margin: 2px;
    border-radius: 2px;
    border: 1px solid theme('colors.additional.300');
    width: 20px;
    height: 20px;
    flex-shrink: 0;
    background-color: theme('colors.white');
    position: relative;

    &-icon {
      @apply transition-all;

      position: absolute;
      top: 1px;
      left: 1px;
      opacity: 0;
      color: white;

      &--indeterminate {
        color: theme('colors.main.400');
      }
    }
  }

  &__label {
    @apply text-base-regular transition-colors;

    margin: 1px 0 1px 8px;
    text-wrap: balance;
    color: theme('colors.additional.300');
  }

  &__input {
    position: absolute;
    z-index: -1;
    opacity: 0;

    &:focus-visible + #{$checkbox}__control {
      border-color: theme('colors.main.200');
    }

    &:checked {
      + #{$checkbox}__control {
        border-color: theme('colors.main.200');
        background-color: theme('colors.main.400');

        #{$checkbox}__control-icon--checked {
          opacity: 1;
        }
      }

      ~ #{$checkbox}__label {
        color: theme('colors.main.400');
      }

      &:focus-visible + #{$checkbox}__control {
        border-color: theme('colors.main.200');
        background-color: theme('colors.main.500');
      }
    }
  }

  &:hover {
    #{$checkbox}__control {
      border-color: theme('colors.main.200');
    }

    #{$checkbox}__label {
      color: theme('colors.main.500');
    }

    #{$checkbox}__input:checked + #{$checkbox}__control {
      background-color: theme('colors.main.500');
    }
  }

  &--boxed {
    @apply transition-colors;

    border-radius: 8px;
    border: 2px solid transparent;
    padding: 8px;
    background-color: theme('colors.white');

    &:hover {
      background-color: theme('colors.main.50');
    }

    &:has(:focus-visible) {
      border-color: theme('colors.main.DEFAULT');
    }

    @supports not selector(:has(a, b)) {
      &:focus-within {
        border-color: theme('colors.main.DEFAULT');
      }

      &:hover {
        border-color: transparent;
      }
    }
  }

  &--erroneous {
    #{$checkbox}__control {
      border-color: theme('colors.negative.DEFAULT');
    }

    #{$checkbox}__label {
      color: theme('colors.negative.DEFAULT');
    }

    #{$checkbox}__input {
      &:focus-visible + #{$checkbox}__control {
        border-color: #A12A32;
      }

      &:checked {
        + #{$checkbox}__control {
          border-color: theme('colors.negative.DEFAULT');
          background-color: theme('colors.negative.DEFAULT');
        }

        ~ #{$checkbox}__label {
          color: theme('colors.negative.DEFAULT');
        }

        &:focus-visible + #{$checkbox}__control {
          border-color: #A12A32;
          background-color: #A12A32;
        }
      }
    }

    &:hover {
      #{$checkbox}__control {
        border-color: #A12A32;
      }

      #{$checkbox}__label {
        color: #A12A32;
      }

      #{$checkbox}__input:checked {
        + #{$checkbox}__control {
          background-color: #A12A32;
        }

        ~ #{$checkbox}__label {
          color: #A12A32;
        }
      }
    }

    &#{$checkbox}--boxed {
      &:hover {
        background-color: theme('colors.negative.200');
      }

      &:has(:focus-visible) {
        border-color: theme('colors.negative.light');
      }

      @supports not selector(:has(a, b)) {
        &:focus-within {
          border-color: theme('colors.negative.light');
        }

        &:hover {
          border-color: transparent;
        }
      }
    }
  }

  &--disabled {
    pointer-events: none;

    #{$checkbox}__control {
      border-color: theme('colors.additional.200');
    }

    #{$checkbox}__label {
      color: theme('colors.additional.200');
    }

    #{$checkbox}__input:checked {
      + #{$checkbox}__control {
        border-color: theme('colors.additional.200');
        background-color: theme('colors.additional.200');
      }

      ~ #{$checkbox}__label {
        color: theme('colors.additional.200');
      }
    }
  }

  &--indeterminate {
    #{$checkbox}__control {
      border-color: theme('colors.main.200');

      &-icon--indeterminate {
        opacity: 1;
      }
    }

    #{$checkbox}__input {
      &:focus-visible + #{$checkbox}__control {
        border-color: theme('colors.main.200');

        #{$checkbox}__control-icon--indeterminate {
          color: theme('colors.main.500');
        }
      }

      &:checked + #{$checkbox}__control {
        background-color: theme('colors.white');
      }

      + #{$checkbox}__control #{$checkbox}__control-icon--checked {
        opacity: 0;
      }
    }

    &:hover {
      #{$checkbox}__control-icon--indeterminate {
        color: theme('colors.main.500');
      }

      #{$checkbox}__input:checked + #{$checkbox}__control {
        background-color: theme('colors.white');
      }
    }

    &#{$checkbox}--erroneous {
      #{$checkbox}__input:focus-visible + #{$checkbox}__control {
        border-color: #A12A32;

        #{$checkbox}__control-icon--indeterminate {
          color: #A12A32;
        }
      }

      #{$checkbox}__control {
        border-color: theme('colors.negative.DEFAULT');

        &-icon--indeterminate {
          color: theme('colors.negative.DEFAULT');
        }
      }

      &:hover {
        #{$checkbox}__control {
          border-color: #A12A32;

          &-icon--indeterminate {
            color: #A12A32;
          }
        }
      }
    }

    &#{$checkbox}--disabled #{$checkbox}__control {
      border-color: theme('colors.additional.200');

      &-icon--indeterminate {
        color: theme('colors.additional.200');
      }
    }
  }
}
</style>

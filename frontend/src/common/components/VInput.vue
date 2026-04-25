<template>
  <div class="input__container">
    <div
      class="input__wrapper"
      :class="{
        'form-floating': !placeholder,
        'input__wrapper--error': error && !errorAsTooltip,
        'input__wrapper--sm': props.sm,
        'textarea': tag === 'textarea',
      }"
    >
      <VIcon
        v-if="search"
        name="search"
        class="input__icon pointer-events-none input__icon--search"
      />

      <input
        v-if="tag === 'input'"
        :id="inputId"
        ref="input"
        v-imask="maskObj"
        :type="type ?? 'text'"
        :class="inputClasses"
        class="input form-control block"
        autocomplete="off"
        :maxlength="maxLength"
        :placeholder="placeholder || (!label ? extendedLabel : null)"
        :disabled="disabled"
        :readonly="readonly || selectReadonly"
        :value="inputRenderModel"
        spellcheck="false"
        @accept="(e) => acceptInputHandler(e.detail.value)"
        @input="inputHandler($event)"
        @change="normalizeValue"
        @blur="inputBlur"
        @focus="emits('focus');"
      />

      <textarea
        v-if="tag === 'textarea'"
        :id="inputId"
        ref="textarea"
        v-imask="maskObj"
        :type="type ?? 'text'"
        :class="inputClasses"
        class="input textarea form-control block"
        autocomplete="off"
        :maxlength="maxLength"
        :placeholder="placeholder || (!label ? extendedLabel : null)"
        :disabled="disabled"
        :readonly="readonly || selectReadonly"
        :value="inputRenderModel"
        spellcheck="false"
        @accept="(e) => acceptInputHandler(e.detail.value)"
        @input="inputHandler($event)"
        @blur="inputBlur"
        @focus="emits('focus');"
      ></textarea>

      <label
        v-if="!placeholder || label && placeholder"
        :for="inputId"
        class="input--label whitespace-nowrap absolute select-none"
        :class="{ 'input--label__optional' : !!attrOptional }"
      >
        {{ extendedLabel }}
      </label>

      <div
        v-if="!readonly"
        class="input__icon_wrapper"
        @mousedown.prevent
      >
        <slot name="iconSlot"></slot>
        <VIcon
          v-if="(search || clearable) && inputRenderModel"
          class="input__icon input__icon--clear cursor-pointer"
          name="close"
          data-test="clearableInput"
          @click.stop="clearableInput"
        />

        <VIcon
          v-if="afterIcon"
          class="input__icon input__icon-after pointer-events-none"
          :name="afterIcon"
          data-test="clickAfterIcon"
          @click="$emit('clickAfterIcon')"
        />

        <VIcon
          v-if="error && !afterIcon && !errorAsTooltip"
          name="error"
          class="input__icon input__icon--error"
          no-hover
          no-cursor-pointer
        />

        <VIcon
          v-if="selectReadonly && !readonly"
          class="input__icon input__icon-arrow pointer-events-none ml-2"
          name="down"
          :class="{
            'rotate-180': inputFocus,
            'rotate-0': !inputFocus,
            'ease-in-out duration-300': true,
          }"
        />
      </div>
      <template v-if="error && typeof error === 'string'">
        <div
          v-if="!errorAsTooltip"
          class="input_error-annotation"
        >
          {{ error }}
        </div>
        <VTooltip
          v-else
          class="blank-hint"
          tooltip-classes="blank-hint-content"
          :content="error"
          :show-always="error"
        />
      </template>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { uniqueId, isRegExp } from 'lodash';
import { IMaskDirective as vImask, IMask } from 'vue-imask';
import { numWord } from '@/common/utils/numWord';
import { toNormalNumber, formatNumber } from '@/common/utils/format';
import { MAX_INTAGER_VALUE, MAX_FLOAT_VALUE } from '@/consts';

const props = withDefaults(defineProps<{
  modelValue?: string | number | any[] | object;
  label?: string;
  placeholder?: string;
  mask?: string | RegExp;
  sm?: boolean;
  primary?: boolean;
  secondary?: boolean;
  error?: string | boolean;
  errorAsTooltip?: boolean;
  optional?: boolean;
  disabled?: boolean;
  readonly?: boolean;
  selectReadonly?: boolean;
  select?: boolean;
  search?: boolean;
  afterIcon?: string;
  itemName?: string;
  clearable?: boolean;
  inputFocus?: boolean;
  focusOnce?: boolean;
  tag?: 'input' | 'textarea';
  maxLength?: number | null;
  numWords?: any[];
  showNumberSelected?: boolean;
  withBorder?: boolean;
  loading?: boolean;
  attrOptional?: boolean | string;
  min?: number;
  max?: number;
  type?: string | null;
}>(), {
  modelValue: '',
  label: '',
  placeholder: '',
  mask: '',
  primary: false,
  secondary: false,
  disabled: false,
  readonly: false,
  selectReadonly: false,
  select: false,
  search: false,
  afterIcon: '',
  itemName: 'name',
  inputFocus: false,
  sm: true,
  focusOnce: false,
  tag: 'input',
  maxLength: null,
  numWords: () => [],
  showNumberSelected: false,
  attrOptional: false,
  type: null,
});

const emits = defineEmits([
  'update:modelValue',
  'clickAfterIcon',
  'clearInput',
  'blur',
  'focus',
]);

const input = ref(null);
const textarea = ref(null);

const inputId = uniqueId('input_');

const defaultMaxNumber = () => {
  switch (props.mask) {
    case 'number': return MAX_FLOAT_VALUE;
    case 'number-int': return MAX_INTAGER_VALUE;
    default: return undefined;
  }
};

const maskObj = computed(() => {
  let maskData = null;

  if (isRegExp(props.mask)) {
    maskData = {
      mask: props.mask,
    };

    return maskData;
  }

  if (props.mask === 'date-number') {
    maskData = {
      mask: Number,
      normalizeZeros: true,
      scale: 0,
      min: 1,
      max: 31,
    };
  }

  if (props.mask.startsWith('number')) {
    maskData = {
      mask: Number,
      scale: props.mask === 'number-int' ? 0 : 2,
      signed: false,
      thousandsSeparator: ' ',
      padFractionalZeros: false,
      normalizeZeros: false,
      radix: ',',
      mapToRadix: ['.'],
      min: props.min,
      max: props.max ?? defaultMaxNumber(),
    };
  }

  if (props.mask === 'date' || props.mask === 'date-range') {
    maskData = {
      mask: props.mask === 'date' ? 'd.m.Y' : 'd.m.Y — d.m.Y',
      lazy: true,
      autofix: true,
      blocks: {
        d: {
          mask: IMask.MaskedRange, placeholderChar: 'д', from: 0, to: 99, maxLength: 2,
        },
        m: {
          mask: IMask.MaskedRange, placeholderChar: 'м', from: 0, to: 99, maxLength: 2,
        },
        Y: {
          mask: IMask.MaskedRange, placeholderChar: 'г', from: 0, to: 9999, maxLength: 4,
        },
      },
    };
  }

  if (props.mask === 'search-table') {
    maskData = {
      // eslint-disable-next-line prefer-regex-literals
      mask: new RegExp("^[\\[\\]a-zA-Z0-9_а-яА-ЯёЁ.\\-\\s!@#$%^&*():+,№'«»/\\\\]{0,100}$"),
    };
  }
  return maskData;
});

const extendedLabel = computed(() => `${props.label}${!props.attrOptional ? '' : props.optional ? ' (необязательно)' : ''}`);
const cleanZeros = (str) => (str?.replace(/0+$/, '') === '' || str?.replace(/0+$/, '') === '0' ? '' : str?.replace(/0+$/, ''));

const normalizeLineBreaks = (text) => text
  .replace(
    /^\n+|\n+$|\n{2,}/g,
    (match, offset, string) => offset === 0 || offset + match.length === string.length
      ? '\n'.repeat(props.restrictLineEdges)
      : '\n'.repeat(props.restrictLineBeetween),
  );

const changeTextAreaHeight = (el) => {
  if (props.tag === 'textarea') {
    el.style.minHeight = '96px';
    el.style.minHeight = `${el.scrollHeight}px`;
  }
};

const inputBlur = async (e) => {
  ({
    time() {
      const [hours, minutes] = e.target.value.replace(/ /g, '').split(':');
      (minutes || hours) && emits('update:modelValue', `${(hours ?? '').padStart(2, '0')} : ${(minutes ?? '').padStart(2, '0')}`);
    },
    number() {
      (e.target.value[0] === '0' && e.target.value[1] && e.target.value[1] !== ',') && (e.target.value = `${e.target.value[0]},${e.target.value.substring(1)}`);
      const [integers, fractions] = e.target.value.replace(/ /g, '').split(',');
      const resultFractions = cleanZeros(fractions);
      emits('update:modelValue', (integers || resultFractions) && e.target.value ? `${integers || 0}${resultFractions ? `,${resultFractions}` : ''}` : '');
    },
  })[props.mask]?.();
  if (props.tag === 'textarea') {
    emits('update:modelValue', normalizeLineBreaks(e.target.value));
    await nextTick();
    changeTextAreaHeight(e.target);
  }
  emits('blur');
};

const inputRenderModel = computed(() => {
  const { modelValue, itemName } = props;

  if (typeof modelValue === 'string' || typeof modelValue === 'number') {
    return modelValue;
  }

  if (!modelValue) return '';

  if (!Array.isArray(modelValue)) {
    return modelValue[itemName];
  }

  if (props.showNumberSelected && modelValue.length > 1) {
    return `Выбрано ${modelValue.length} ${numWord(modelValue.length, props.numWords)}`;
  }

  return [...modelValue].map((option) => option[itemName] || option).join(', ');
  // object case
});

const isEmpty = computed(() => typeof inputRenderModel.value !== 'number' && !inputRenderModel.value);

const acceptInputHandler = (detail) => {
  emits('update:modelValue', detail);
};

onMounted(() => {
  textarea.value ? changeTextAreaHeight(textarea.value) : null;
  if (props.inputFocus && !props.loading) input.value.focus();
});

onUpdated(async () => {
  if (!props.loading) {
    if (props.inputFocus && !props.focusOnce) input.value.focus();
  }
});

const inputHandler = (e) => {
  changeTextAreaHeight(e.target);

  if (props.mask) {
    return;
  }

  emits('update:modelValue', e.target.value);
};

const normalizeValue = (evt) => {
  if (!evt.target.value || props.min === undefined && props.max === undefined) {
    return;
  }

  const numericValue = toNormalNumber(evt.target.value);

  if (numericValue < props.min) {
    emits('update:modelValue', formatNumber(props.min));
  } else if (numericValue > props.max) {
    emits('update:modelValue', formatNumber(props.max));
  }
};

const clearableInput = () => {
  emits('update:modelValue', '');
  emits('clearInput', '');

  setTimeout(() => {
    input.value.focus();
  }, 0);
};

defineExpose({
  input,
});

const inputClasses = computed(() => ({
  'input--primary': props.primary,
  'input--secondary': props.secondary,
  'input--error': props.error && !props.errorAsTooltip,
  'input--empty': isEmpty.value,
  'input--readonly': props.readonly,
  '!pr-[80px]': props.clearable && props.selectReadonly,
  'input--select-readonly': props.selectReadonly,
  'input--search': props.search,
  'input--double-icon-end': props.afterIcon && props.error,
  'input--with-border': props.withBorder,
  'input--label-placeholder': props.placeholder && props.label,
  'input--optional': props.attrOptional,
}));
</script>

<style lang="scss" scoped>
.input {
  width: 100%;
  height: 100%;
  border: 1px solid transparent;
  border-bottom: 1px solid theme("colors.additional.300");
  font-weight: 400;
  font-size: 16px;
  outline: none !important;
  box-shadow: none !important;
  transition: background-color 0.2s ease-in-out, border 0.2s ease-in-out;
  padding-left: 2px;
  padding-right: 16px;
  padding-bottom: 2px !important;
  white-space: pre-line;

  $root: &;

  &--optional::placeholder::after {
    content: var(--optional-content);
    margin-left: 0.5ch;
  }

  &__wrapper {
    height: 48px;
    position: relative;
    --optional-content: '(необяз.)';

    &.textarea {
      min-height: 48px;
      height: auto;
      padding-top: 1.2em;
      border-radius: 4px;
      #{$root}--label {
        top: 3px !important;
      }
    }

    &--error {
      #{$root}--empty:not(#{$root}--focus) + #{$root}--label {
        color: theme("colors.negative.DEFAULT");
      }
    }

    &:focus-within {
      .input__icon {
        color: theme("colors.additional.300");
      }
    }

    #{$root}--label {
      top: -3px !important;

      &__optional::after {
        content: var(--optional-content);
        margin-left: 0.5ch;
      }
    }

    #{$root}--label-placeholder+label {
      position: absolute;
      top: 3px !important;
      font-size: 12px;
    }

    #{$root}--label-placeholder {
      padding-top: 21px;
      padding-bottom: 5px;
    }

    &--sm {
      height: 40px !important;
      &.textarea {
        height: auto;
        &:not(#{$root}--empty):not(.input--label-placeholder) + #{$root}--label {
          top: 3px !important;
        }
      }

      #{$root} {
        font-size: 14px !important;

        &:not(#{$root}--empty):not(.input--label-placeholder) + #{$root}--label {
          top: -5px !important;
        }
      }

      #{$root}--label {
        top: calc(50% - 0.7em) !important;
        padding-left: 2px !important;
        font-size: 14px;
      }

      #{$root}__icon_wrapper {
        right: 12px;
      }

      #{$root}--label-placeholder {
        padding-bottom: 7px;
      }

      #{$root}--label-placeholder+label {
        top: 2px !important;
        font-size: 12px !important;
      }
    }
  }

  &--select-readonly {
    padding-right: 40px;
    cursor: pointer;
  }

  &--readonly {
    padding-right: 16px;
  }

  &:focus:not(#{$root}--readonly),
  &--with-border {
    background-color: theme("colors.white") !important;

    & + #{$root}--label {
      padding-left: 2px !important;
      color: theme("colors.additional.DEFAULT");
    }
  }

  &:focus:not(#{$root}--select-readonly):not(.textarea):not(#{$root}--readonly):not(.input--label-placeholder)
    + #{$root}--label,
  &--select-readonly:not(#{$root}--empty) + #{$root}--label {
    margin-top: 1px;

    top: -5px !important;
  }

  // &:hover:not([readonly]),
  // &--select-readonly:hover:not(#{$root}--readonly) {
  //   border: 1px solid theme("colors.additional.300");
  // }

  &--readonly#{$root}--empty + #{$root}--label,
  &--select-readonly#{$root}--empty + #{$root}--label {
    transform: none;
  }

  &--empty {
    user-select: none;
  }

  &--primary {
    background-color: theme("colors.white");
  }

  &--error {
    border-bottom: 1px solid theme("colors.negative.DEFAULT") !important;
    padding-right: 70px !important;

    &#{$root}--empty {
      background-color: theme("colors.white");
    }

    &:focus {
      background-color: theme("colors.white") !important;
      border-bottom: 1px solid theme("colors.negative.DEFAULT") !important;
    }

    &:hover {
      border-bottom: 1px solid theme("colors.additional.300") !important;
    }
  }

  &--label {
    opacity: 1 !important;
    padding-left: 2px !important;
    color: theme("colors.additional.300");
    transition: all 0.2s ease-in-out;
  }

  &--search {
    padding-left: 52px !important;
    padding-right: 56px !important;

    & + #{$root}--label {
      padding-left: 60px !important;
    }
    &:focus {
      & + #{$root}--label {
        padding-left: 60px !important;
      }
    }
  }

  &__icon {
    transition: all 0.2s ease-in-out;
    color: theme("colors.additional.300");

    &--search {
      position: absolute;
      left: 16px;
      top: 50%;
      transform: translateY(-50%);
    }

    &--error {
      color: theme("colors.negative.DEFAULT") !important;
      margin-left: 8px;
    }

    &_wrapper {
      position: absolute;
      right: 16px;
      top: 50%;
      transform: translateY(-50%);
      max-width: 61px;
      justify-content: flex-end;
      display: flex;
    }
  }

  &[disabled] {
    border-bottom-color: theme("colors.main.50");
    background-color: theme("colors.main.50");
    color: theme("colors.additional.DEFAULT");
    opacity: 0.5;

    & + #{$root}--label {
      opacity: 0.5 !important;
      color: theme("colors.additional.DEFAULT");
    }
  }

  &--double-icon-end {
    padding-right: 84px !important;
  }

  &_error-annotation {
    position: absolute;
    color: theme("colors.negative.DEFAULT");
    font-weight: 400;
    font-size: 14px;
    line-height: 20px;
    padding-left: 2px;
  }
}

textarea {
  resize: none;
  overflow: hidden;
  min-height: 94px;
  &.input {
    border: 1px solid theme("colors.additional.300");
    margin-top: 10px;
    border-radius: 8px;
    padding: 10px 15px;
  }
}
</style>

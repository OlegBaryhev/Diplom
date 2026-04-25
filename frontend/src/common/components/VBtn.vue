<template>
  <Component
    :is="tag"
    v-bind="mergedAttrs"
    ref="buttonRef"
    class="btn"
    :class="{
      'btn--has-text': hasText,
      'btn--small': small,
      'btn--extra-small': extraSmall,
      'btn--outlined': outlined,
      'btn--ghost': ghost,
      'btn--has-icon': icon,
      'btn--reversed': reversed,
      'pointer-events-none': loading,
    }"
    :disabled="disabled"
  >
    <span
      v-if="hasText"
      class="btn__text"
      :class="{ 'invisible': loading }"
    >
      <slot>{{ text }}</slot>
    </span>

    <VIcon
      v-if="icon"
      :name="icon"
      class="btn__icon ease-in-out duration-300"
      :class="{
        'invisible': loading,
        ...(props.rotateArrow ? {
          'rotate-180': !rotateArrow,
          'rotate-0': rotateArrow,
        } : {}),
      }"
      :style="{
        'transform': iconScale ? `scale(${iconScale})` : null,
      }"
    />

    <div
      v-if="loading"
      class="btn__loader-wrap"
    >
      <VLoader small />
    </div>
  </Component>
</template>

<script lang="ts" setup>
import { defineComponent, defineAsyncComponent } from 'vue';

const props = withDefaults(defineProps<{
  text?: string;
  small?: boolean;
  extraSmall?:boolean;
  outlined?: boolean;
  ghost?: boolean;
  icon?: string;
  reversed?: boolean;
  tag?: string | ReturnType<typeof defineComponent> | ReturnType<typeof defineAsyncComponent>;
  loading?: boolean;
  disabled?: boolean;
  rotateArrow?: boolean;
  iconScale?: number | string;
}>(), {
  text: '',
  small: false,
  extraSmall: false,
  outlined: false,
  ghost: false,
  icon: '',
  reversed: false,
  tag: 'button',
  loading: false,
  disabled: undefined,
  rotateArrow: false,
});

const attrs = useAttrs();
const slots = useSlots();
const rotateArrow = ref(props.rotateArrow);
const buttonRef = ref(null);

const mergedAttrs = computed<ReturnType<typeof useAttrs>>(() => ({
  type: props.tag === 'button' ? 'button' : undefined,
  ...attrs,
}));

const hasText = computed(() => Boolean(slots.default ?? props.text));
</script>

<script lang="ts">
export default defineComponent({
  inheritAttrs: false,
});
</script>

<style lang="scss" scoped>
.btn {
  @apply text-base-regular;

  border-radius: 8px;
  outline: 4px solid transparent;
  border: 1px solid theme('colors.main.400');
  stroke: theme('colors.white');
  padding: 10px 24px;
  min-width: 48px;
  min-height: 48px;
  color: theme('colors.main.50');
  background-color: theme('colors.main.400');
  display: inline-flex;
  justify-content: center;
  align-items: center;
  vertical-align: middle;
  user-select: none;
  position: relative;
  transition-property: outline-color, border-color, stroke, color, background-color;
  transition-duration: 0.15s;

  &__loader-wrap {
    width: 100%;
    height: 100%;
    position: absolute;
    display: flex;
    justify-content: center;
    align-items: center;
  }

  &:hover {
    stroke: theme('colors.additional.200');
    border-color: theme('colors.main.200');
    background-color: theme('colors.main.500');
  }

  &:focus-visible {
    outline-color: theme('colors.main.200');
  }

  &:active {
    stroke: theme('colors.additional.300');
    border-color: theme('colors.main.DEFAULT');
    background-color: theme('colors.main.DEFAULT');
  }

  &:disabled {
    stroke: theme('colors.additional.200');
    border-color: theme('colors.additional.200');
    color: theme('colors.white');
    background-color: theme('colors.additional.200');
  }

  $btn: &;

  &--small {
    padding-top: 6px;
    padding-bottom: 6px;
    min-width: 40px;
    min-height: 40px;
  }

  &--outlined {
    outline-width: 1px;
    stroke: theme('colors.main.200');
    border-color: theme('colors.main.200');
    color: theme('colors.main.400');
    background-color: theme('colors.white');

    &:hover {
      stroke: theme('colors.main.400');
      border-color: theme('colors.main.200');
      background-color: theme('colors.white');
    }

    &:focus-visible {
      stroke: theme('colors.main.400');
      outline-color: theme('colors.main.400');
      border-color: theme('colors.main.200');
    }

    &:active {
      stroke: theme('colors.main.400');
      border-color: theme('colors.main.200');
      color: theme('colors.main.500');
      background-color: theme('colors.main.50');
    }

    &:disabled {
      stroke: theme('colors.additional.200');
      border-color: theme('colors.additional.200');
      color: theme('colors.additional.200');
      background-color: theme('colors.white');
    }
  }

  &--ghost {
    background-color: theme('colors.white');
    border: none;
    color: theme('colors.main.400');

    &:hover,
    &:focus-visible {
      color: theme('colors.main.DEFAULT');
      background-color: theme('colors.white');
      border: none;
    }

    &:active {
      color: theme('colors.black');
      background-color: theme('colors.white');
      border: none;
    }

    &:disabled {
      color: theme('colors.additional.300');
      background-color: theme('colors.white');
      border: none;
    }
  }

  &--has-icon:where(#{&}--has-text) {
    padding-right: 16px;

    #{$btn}__text {
      margin-right: 8px;
    }

    &:where(#{$btn}--reversed) {
      padding-right: 24px;
      padding-left: 16px;

      #{$btn}__text {
        order: 1;
        margin-right: 0;
        margin-left: 8px;
      }
    }
  }

  &--has-icon:not(&--has-text) {
    padding-left: 0;
    padding-right: 0;
  }

  &--extra-small {
    padding-top: 0;
    padding-bottom: 0;
    padding-right: 6px;
    padding-left: 6px;
    min-width: 40px;
    min-height: 22px;

    #{$btn}__text {
      font-size: 16px;
      line-height: 22px;
    }
    #{$btn}__icon {
        height: 16px;
        width: 16px;
    }
  }
}
</style>

<template>
  <Component
    :is="tag"
    class="skeleton-item"
    :class="{
      'skeleton-item--circle': circle,
      'skeleton-item--square': square,
      'skeleton-item--not-animated': notAnimated,
    }"
  >
    <slot />
  </Component>
</template>

<script lang="ts" setup>
withDefaults(defineProps<{
  tag?: string;
  circle?: boolean;
  square?: boolean;
  notAnimated?: boolean;
}>(), {
  tag: 'div',
  circle: false,
  square: false,
  notAnimated: false,
});
</script>

<style lang="scss" scoped>
@keyframes translate-x-skeleton {
  to {
    transform: translateX(100%);
  }
}

.skeleton-item {
  border-radius: 8px;
  background-color: theme('colors.additional.100');

  &--circle {
    border-radius: 50%;
  }

  &--square {
    border-radius: 0;
  }

  &:not(&--not-animated) {
    overflow: hidden;
    position: relative;

    // highlight
    &::after {
      @apply inset-0;

      content: '';
      position: absolute;
      transform: translateX(-100%);
      animation: translate-x-skeleton 1.4s infinite;
      background: linear-gradient(to right , rgba(0, 0, 0, 0), hsla(0, 0%, 100%, 0.4), rgba(0, 0, 0, 0));
    }
  }
}
</style>

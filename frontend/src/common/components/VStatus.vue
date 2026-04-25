<template>
  <div
    :class="`chip__status--${value}`"
    class="chip__status select-none"
  >
    <slot />
  </div>
</template>

<script lang="ts" setup>
defineProps<{ value: string }>();
</script>

<style scoped lang="scss">
@keyframes gradientShift {
  0% {
    background-position: 0 0;
  }
  100% {
    background-position: -200% 0;
  }
}

.chip__status {
  padding-left: 8px;
  padding-right: 8px;
  border-radius: 50px;
  height: 26px;
  font-size: 14px;
  line-height: 26px;
  display: inline-block;
  &--active, &--ready {
    background-color: theme('colors.positive.light');
    color: theme('colors.positive.DEFAULT');
  }

  &--completed {
    background-color: theme('colors.lime.700');
    color: theme('colors.lime.200');
  }

  &--cancelled {
    background-color: theme('colors.gray.300');
    color: theme('colors.gray.500');
  }

  &--not_activated {
    background-color: theme('colors.main.200');
    color: theme('colors.main.DEFAULT');
  }

  &--pending {
    background: linear-gradient(to right, theme('colors.lime.600'), theme('colors.lime.500'), theme('colors.lime.600'));
    background-size: 200% 100%;
    animation: gradientShift 3s linear infinite;
    color: theme('colors.white');
  }
}
</style>

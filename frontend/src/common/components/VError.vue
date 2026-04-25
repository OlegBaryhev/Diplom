<template>
  <div class="error">
    <Component
      :is="iconComponent"
      class="error__icon"
      :class="`w-${iconSize} h-${iconSize}`"
    />
    <p class="error__text">
      <b>Произошла ошибка загрузки данных.</b>
      <br>
      Обновите страницу
    </p>
  </div>
</template>

<script lang="ts" setup>
import ErrorIcon from '@/assets/svg/presentation/error.svg?component';
import type { IconComponent } from '@/common/types';

withDefaults(defineProps<{
  iconComponent?: IconComponent;
  buttonText?: string;
  iconSize: string | number;
}>(), {
  iconComponent: ErrorIcon,
  buttonText: '',
  iconSize: 14,
});

// eslint-disable-next-line no-spaced-func, func-call-spacing
defineEmits<{ (evt: 'handleButtonClick'): void }>();
</script>

<style lang="scss" scoped>
.error {
  border-radius: 16px;
  flex: 1 1 0;
  text-align: center;
  background-color: theme('colors.main.50');
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;

  &__icon {
    margin-bottom: 12px;
  }

  &__text {
    @apply text-base-regular;

    color: theme('colors.additional.300');
  }
}
</style>

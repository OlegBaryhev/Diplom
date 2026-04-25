<template>
  <div class="no-data">
    <Component
      :is="iconComponent"
      class="no-data__icon"
      :class="`w-${iconSize} h-${iconSize}`"
    />

    <slot name="content">
      <p class="no-data__text">
        <slot>
          <b>Нет данных</b>
        </slot>
      </p>

      <VBtn
        v-if="buttonText"
        class="no-data__button"
        :text="buttonText"
        outlined
        small
        data-test="no-data-button"
        @click="$emit('handleButtonClick')"
      />
    </slot>
  </div>
</template>

<script lang="ts" setup>
import DefaultIcon from '@/assets/svg/presentation/no-data.svg?component';
import type { IconComponent } from '@/common/types';

withDefaults(defineProps<{
  iconComponent?: IconComponent;
  buttonText?: string;
  iconSize?: string | number;
}>(), {
  iconComponent: DefaultIcon,
  buttonText: '',
  iconSize: 32,
});

// eslint-disable-next-line no-spaced-func, func-call-spacing
defineEmits<{ (evt: 'handleButtonClick'): void }>();
</script>

<style lang="scss" scoped>
.no-data {
  border-radius: 16px;
  flex: 1 1 0;
  text-align: center;
  background-color: theme('colors.main.50');
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  padding: 12px 0;

  &__icon {
    margin-bottom: 12px;
  }

  &__text {
    @apply text-base-regular;

    color: theme('colors.additional.300');
  }

  &__button {
    margin-top: 16px;
  }
}
</style>

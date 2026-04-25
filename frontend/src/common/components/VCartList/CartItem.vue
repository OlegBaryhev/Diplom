<template>
  <div class="cart-item flex h-[60px] w-full px-1">
    <div class="cart-item__wrapper h-full  w-full flex items-center justify-between">
      <span class="cart-item__name text-base-regular select-none text-additional px-3 max-w-full">{{ item?.product?.name }}</span>
      <div class="ml-auto mr-4 flex gap-3 items-center min-w-max">
        <VIcon
          name="minus"
          class="actions-styles h-[20px] w-[20px] text-main-300 cursor-pointer"
          tabindex="1"
          role="button"
          @click="setValue(-1)"
        />

        <VInput
          v-model="newValue"
          placeholder="Кол-во"
          mask="number-int"
          class="w-[65px] px-[0px]"
          secondary
          sm
          @blur="newValue === '0' && emit('delete', item)"
        />

        <VIcon
          name="plus"
          class="actions-styles h-[20px] w-[20px] text-main-300 cursor-pointer"
          tabindex="1"
          role="button"
          @click="setValue(1)"
        />
      </div>
      <VIcon
        name="trash"
        class="actions-styles h-[25px] w-[25px] text-red-500 cursor-pointer ml-2 mr-3"
        tabindex="1"
        role="button"
        @click="emits('delete', item)"
      />
    </div>
  </div>
</template>

<script lang="ts" setup>
import { debounce } from 'lodash';

const props = withDefaults(defineProps<{
  item: any,
}>(), {
  item: null,
});

const newValue = ref<number | string>(props.item?.quantity ?? '');
// eslint-disable-next-line func-call-spacing, no-spaced-func
const emits = defineEmits<{
  (evt: 'set-value', result: any): void;
  (evt: 'delete', item: any): void;
}>();

const setValue = (value: number) => {
  const num = Number.isNaN(Number(newValue.value)) ? 0 : Number(newValue.value);
  newValue.value = Math.max(0, num + value);
};

watch(
  () => newValue.value,
  debounce(() => emits('set-value', { item: props.item, value: newValue.value }), 1000),
);
</script>

<style lang="scss" scoped>
.cart-item {
  &__wrapper {
    border-bottom: 1px solid theme('colors.additional.100');
  }
  .actions-styles {
    transition: transform, filter 0.3s ease-in-out;
    &:hover { transform: scale(1.05); }
    &:hover:active {transform: scale(0.95); }
  }
}
</style>

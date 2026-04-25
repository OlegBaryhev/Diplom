<template>
  <div
    class="flex text-additional-300 text-sm-regular h-10"
    :class="{
      'text-sm-regular': primary,
      'w-fit rounded-lg text-xs-regular bg-main-50': secondary,
      'opacity-50 pointer-events-none': disabled,
    }"
  >
    <div
      v-for="tab in tabs"
      :key="tab?.id ?? tab?.value"
      class="tab cursor-pointer min-w-fit text-nowrap select-none transition duration-300 focus-element flex"
      :class="{
        'border-b-2 border-transparent pb-1.5 hover:text-black pt-2 primary': primary,
        '!border-main-500 hover:!text-main-400 text-main-400': primary && modelValue.id === tab.id,
        'p-3 hover:text-main-500 first:rounded-l-lg last:rounded-r-lg secondary': secondary,
        'bg-main-200 text-main-500': secondary && modelValue.id === tab.id,
        'pointer-events-none': loading || modelValue.id === tab.id
      }"
      :tabindex="disabled ? -1: 0"
      role="button"
      @keydown.enter="modelValue.id !== tab.id && $emit('update:modelValue', tab)"
      @click="modelValue.id !== tab.id && $emit('update:modelValue', tab);"
    >
      {{ tab.text }}
      <span
        v-if="totalIsOptional || tab?.number || tab?.total || tab?.number === 0 || tab?.total === 0"
        class="text-center flex items-start mt-[1px] ml-1"
      >
        <VIcon
          v-if="tab.id === 'increase' || tab?.isIncrease"
          class="w-[6px] h-[6px] ml-1"
          style="color:#2fa749"
          name="arrow-up"
        />

        <VIcon
          v-if="tab.id === 'decrease' || tab?.idDecrease"
          class="w-[6px] h-[6px] ml-1"
          style="color:#bc4442"
          name="arrow-down"
        />

        {{ tab.number || tab.total }}
      </span>

      <VIcon
        v-if="tab?.icon"
        class="w-2 h-2"
        :style="`color:${tab.icon.color}`"
        :name="tab.icon.name"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import type { Tab } from '@/common/types';

withDefaults(defineProps<{
  modelValue?: Tab;
  tabs?: Tab[];
  primary?: boolean;
  secondary?: boolean;
  loading?: boolean;
  disabled?: boolean;
  totalIsOptional?: boolean;
}>(), {
  modelValue: () => ({}) as Tab,
  tabs: () => [],
  totalIsOptional: true,
});

defineEmits(['update:modelValue']);
</script>

<style lang="scss" scoped>
.tab.primary + .tab.primary {
  margin-left: 24px;
}
</style>

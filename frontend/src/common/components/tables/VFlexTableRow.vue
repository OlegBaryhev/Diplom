<template>
  <Component
    :is="tag"
    :class="{'flex-table-row--with-dividing-line': hasDividingLine}"
    class="flex-table-row"
    role="row"
  >
    <slot />
  </Component>
</template>

<script lang="ts" setup>
const props = withDefaults(defineProps<{
  tag?: string;
  rowHeight?: number;
  hasDividingLine?: boolean;
}>(), {
  tag: 'div',
  rowHeight: 48,
  hasDividingLine: false,
});

const rowHeightWithPx = computed(() => `${props.rowHeight}px`);
</script>

<style lang="scss" scoped>
.flex-table-row {
  min-height: v-bind(rowHeightWithPx);
  display: flex;

  &::after {
    position: absolute;
    content: "";
    bottom: 0;
    width: 100%;
    border-bottom: 1px solid transparent;
    transition-duration: .4s;
  }

  &--with-dividing-line::after {
    border-color: #C9DEFF;
  }
}
</style>

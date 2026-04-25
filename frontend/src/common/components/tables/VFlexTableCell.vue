<template>
  <div
    class="flex-table-cell"
    :class="{
      'flex-table-cell--no-text-overflow--single-line': noTextOverflowNumber === 1,
      'flex-table-cell--no-text-overflow--multiline': noTextOverflowNumber > 1,
      'flex-table-cell--skeleton': skeleton,
    }"
    :role="isColumnheader ? 'columnheader': 'gridcell'"
  >
    <div
      class="flex-table-cell__inner"
      :class="{
        'fill-empty': isFillEmptyValue,
        'letter-break': useLetterBreak,
      }"
      :style="{
        '-webkit-line-clamp': noTextOverflowNumber > 1 ? noTextOverflowNumber : undefined,
      }"
      :title="noTextOverflow && content ? String(content) : undefined"
    >
      <slot>{{ content }}</slot>
    </div>
  </div>
</template>

<script lang="ts" setup>
const props = withDefaults(defineProps<{
  content?: string | number | null;
  noTextOverflow?: boolean | number;
  isColumnheader?: boolean;
  skeleton?: boolean;
  useLetterBreak?: boolean;
  isFillEmptyValue?: boolean;
}>(), {
  noTextOverflow: false,
  isColumnheader: false,
  skeleton: false,
  isFillEmptyValue: true,
  useLetterBreak: true,
});

const noTextOverflowNumber = computed(() => Number(props.noTextOverflow));
</script>

<style lang="scss" scoped>
.flex-table-cell {
  position: relative;
  padding: 8px 12px;
  display: flex;
  align-items: center;

  $cell: &;

  &:first-child {
    padding-left: 16px;
  }

  &:last-child {
    padding-right: 16px;
  }

  &--no-text-overflow {
    &--single-line #{$cell}__inner {
      @apply truncate;
    }

    &--multiline #{$cell}__inner {
      display: -webkit-box;
      -webkit-box-orient: vertical;
      word-break: break-word;
      overflow: hidden;
    }
  }

  &__inner {
    &.letter-break{
      white-space: pre-wrap;
      overflow-wrap: break-word;
    }
    width: 100%;
  }

  &:not(&--skeleton):not([role="columnheader"]) &__inner.fill-empty {
    :deep() > *:empty::after,
    &:empty::after {
      content: '-';
      display: inline-block;
    }
  }
}
</style>

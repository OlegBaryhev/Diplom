<template>
  <div>
    <RecycleScroller
      v-if="grid > 0 && items.length"
      v-slot="{ item, index }"
      list-class="card-list-scroller"
      item-class="card-list-item"
      :items="items"
      :item-size="rowHeight"
      :item-secondary-size="cardsWidth + horizontalMargin * 2"
      :grid-items="grid"
      :key-field="keyField"
      :buffer="buffer"
      emit-update
      page-mode
      @scroll-end="emit('scroll-end')"
    >
      <slot
        :item="item"
        :index="index"
      />
    </RecycleScroller>
  </div>
</template>

<script setup lang="ts">
import { useGrid } from '@/common/composables/use-grid';

const CARD_TITLE_LINE_HEIGHT = 26;

const emit = defineEmits<{(evt: 'scroll-end'): void;}>();

const CONTAINER_PADDING = 32;

const props = withDefaults(defineProps<{
  items: any[];
  buffer?: number;
  keyField?: string;
  cardsHeight?: number;
  cardsWidth?: number;
  verticalMargin?: number;
  horizontalMargin?: number;
  titleLinesCount?: number;
  filterPanelWidth?: number;
}>(), {
  buffer: 680,
  keyField: 'id',
  cardsHeight: 200,
  cardsWidth: 400,
  verticalMargin: 8,
  horizontalMargin: 8,
  titleLinesCount: 1,
  filterPanelWidth: 0,
});

const offset = computed(() => props.filterPanelWidth + CONTAINER_PADDING);
const grid = useGrid(offset, props.cardsWidth, props.horizontalMargin * 2);

const rowHeight = computed(() =>
  CARD_TITLE_LINE_HEIGHT * (props.titleLinesCount - 1) + props.cardsHeight + props.verticalMargin * 2);
</script>

<style lang="scss" scoped>
:deep() {
  .card-list-item {
    &:hover {
      z-index: 10;
    }
  }
}
</style>

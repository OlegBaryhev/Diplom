import type { Ref } from 'vue';

export const useGrid = (containerRef: Ref<HTMLElement | null>, cardWidth = 400, gap = 16) => {
  const gridColumns = ref(1);

  const update = () => {
    if (!containerRef.value) return;
    const w = containerRef.value.offsetWidth;
    gridColumns.value = Math.max(1, Math.floor(w / (cardWidth + gap)));
  };

  useResizeObserver(containerRef, update);

  onMounted(() => nextTick(update));

  return gridColumns;
};

import type { Ref } from 'vue';

export const useGrid = (offsetRef?: Ref<number>, cardWidth:number = 400, gap:number = 16) => {
  const sidebarWidth = 88;
  const gridColumns = ref(0);

  const updateGrid = () => {
    const offset = offsetRef?.value ?? 0;
    const containerWidth = document.body.offsetWidth - sidebarWidth - offset;
    gridColumns.value = Math.max(1, Math.floor(containerWidth / (cardWidth + gap)));
  };

  if (offsetRef) {
    watch(offsetRef, updateGrid);
  }

  onMounted(() => {
    updateGrid();
    window.addEventListener('resize', updateGrid);
  });

  onUnmounted(() => {
    window.removeEventListener('resize', updateGrid);
  });

  return gridColumns;
};

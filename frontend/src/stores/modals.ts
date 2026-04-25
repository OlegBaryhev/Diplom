export const useModals = defineStore('modals', () => {
  const activeModals = ref<string[]>([]);

  const open = (modalId: string): void => {
    activeModals.value.push(modalId);
  };

  const close = (modalId: string): void => {
    activeModals.value = activeModals.value.filter((modalItem) => modalItem !== modalId);
  };

  return { activeModals, open, close };
});

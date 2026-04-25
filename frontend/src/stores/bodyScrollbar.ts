import { OverlayScrollbars } from 'overlayscrollbars';

export const useBodyScrollbar = defineStore('scrollbar', () => {
  const bodyOverlayScrollbar = ref<ReturnType<typeof OverlayScrollbars>>();

  const initBodyOverlayScrollbar = () => { bodyOverlayScrollbar.value = OverlayScrollbars(document.body, {}); };

  return { bodyOverlayScrollbar, initBodyOverlayScrollbar };
});

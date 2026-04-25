import type { Directive } from 'vue';
import { useBodyScrollbar } from '@/stores/bodyScrollbar';
import { useScrollCount } from '@/stores/scrollCount';

export default <Directive<Element, boolean>>{
  mounted() {
    nextTick(() => {
      !useScrollCount().hasLock && useBodyScrollbar().bodyOverlayScrollbar!.options({ overflow: { y: 'hidden' } });
    });
  },

  updated() {
    nextTick(() => {
      useBodyScrollbar().bodyOverlayScrollbar!.options({ overflow: { y: useScrollCount().hasLock ? 'scroll' : 'hidden' } });
    });
  },

  beforeUnmount() {
    nextTick(() => {
      useScrollCount().hasLock && useBodyScrollbar().bodyOverlayScrollbar!.options({ overflow: { y: 'scroll' } });
    });
  },
};

import type { Plugin } from 'vue';
import VScrollLock from '@/directives/v-scroll-lock';

export default <Plugin>{
  install(app) {
    app.directive('scroll-lock', VScrollLock);
  },
};

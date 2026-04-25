import Toast from 'vue-toastification';
import VueClickAway from 'vue3-click-away';
import VueVirtualScroller from 'vue-virtual-scroller';

import App from './App.vue';
import router from './router';
import pinia from './pinia';

import VScrollLockPlugin from './plugins/v-scroll-lock';
import './plugins/floating-vue';

import './assets/main.scss';
import 'vue-toastification/dist/index.css';
import 'overlayscrollbars/overlayscrollbars.css';
import 'vue-virtual-scroller/dist/vue-virtual-scroller.css';
import 'floating-vue/dist/style.css';

import 'tw-elements';

createApp(App)
  .use(router)
  .use(pinia)
  .use(Toast, {
    transition: 'Vue-Toastification__fade',
    maxToasts: 6,
    newestOnTop: true,
    onMounted(_:ComponentPublicInstance, toastApp:any) {
      toastApp.use(router);
    },
  })
  .use(VueClickAway)
  .use(VueVirtualScroller)
  .use(VScrollLockPlugin)
  // .use(FloatingVue)
  .mount('#app');

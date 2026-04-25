import router from '@/router';

const pinia = createPinia();

pinia.use(({ store }) => {
  store.router = markRaw(router);
});

export default pinia;

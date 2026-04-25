export const useScrollCount = defineStore('scrollCount', () => {
  const scrollCount = ref<number>(0);
  const hasLock = computed(() => scrollCount.value === 0);

  const increase = (step = 1) => {
    scrollCount.value += step;
  };

  const decrease = (step = 1) => {
    scrollCount.value -= step;
  };

  return {
    scrollCount,
    hasLock,
    increase,
    decrease,
  };
});

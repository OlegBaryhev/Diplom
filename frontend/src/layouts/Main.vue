<template>
  <div class="main-layout flex justify-start min-h-screen min-w-[1024px] relative">
    <VSideBar
      :blured-style="isHomeRoute"
    />
    <div class="main-layout__wrapper flex items-start flex-col min-h-full w-full min-w-max">
      <RouterView />
    </div>
  </div>
</template>

<script lang="ts" setup>
const route = useRoute();
const isHomeRoute = computed(() => {
  const path = route?.path;
  return path === '/home' || path.startsWith('/home/');
});
</script>

<style lang="scss" scoped>
.main-layout {
  width: 100vw;
  min-height: 100vh;

  &__wrapper {
    margin-left: 88px;
    width: calc(100vw - 88px);
  }
}
</style>

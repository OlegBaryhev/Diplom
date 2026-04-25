<template>
  <div class="main-layout flex justify-start min-h-screen min-w-[1024px] relative">
    <VSideBar />
    <div class="main-layout__wrapper flex items-start flex-col min-h-full w-full min-w-max">
      <RouterView />
    </div>
  </div>
</template>

<style lang="scss">
.main-layout {
  width: 100vw;
  min-height: 100vh;

  &__wrapper {
    margin-left: 88px;
    width: calc(100vw - 88px);
  }
}
</style>

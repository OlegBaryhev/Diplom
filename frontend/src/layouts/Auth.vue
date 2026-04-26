<template>
  <main class="auth-layout flex items-center flex-col h-[100vh] relative justify-center items-center">
    <header class="h-[80px] min-h-[80px] w-full flex items-center justify-start px-6">
      <span
        class="h-min flex select-none"
        role="button"
        tabindex="1"
        @click="router.push({ name: isLogin ? 'register' : 'login' })"
      >
        <VIcon name="left" />
        {{ isLogin ? 'Регистрация' : 'Авторизация' }}
      </span>
    </header>
    <div class="auth-layout__viewport flex flex-wrap h-full">
      <RouterView v-slot="{ Component }">
        <Transition :name="isLogin ? 'slide-left' : 'slide-right'">
          <Component
            :is="Component"
            :key="isLogin ? 1 : 2"
          />
        </Transition>
      </RouterView>
    </div>
  </main>
</template>

<script lang="ts" setup>
const router = useRouter();
const isLogin = computed(() => router.currentRoute.value.name === 'login');
</script>

<style lang="scss" scoped>
.auth-layout {
  &_viewport {
    height: min-content;
  }
}

@media screen and (max-width: 1200px) {
  .auth-layout :deep() {
    .auth-wrapper {
      flex-direction: column;
      &__title {
        text-align: center;
      }

      &__info {
        margin-top: 6px;
        margin-bottom: 10px;
      }

      &__form {
        align-items: center !important;
      }
    }
  }
}

.slide-left-enter-active,
.slide-left-leave-active,
.slide-right-enter-active,
.slide-right-leave-active {
  top: 36px;
  transition: all 0.5s ease-out;
}

.slide-left-enter-to {
  position: absolute;
  right: 0;
  opacity: 1;
}

.slide-left-enter-from {
  position: absolute;
  right: -50%;
  opacity: 0;
}

.slide-left-leave-to {
  position: absolute;
  left: -50%;
  opacity: 0;
}

.slide-left-leave-from {
  position: absolute;
  left: 0;
  opacity: 1;
}

// right animation

.slide-right-enter-to {
  position: absolute;
  left: 0;
  opacity: 1;
}

.slide-right-enter-from {
  position: absolute;
  left: -50%;
  opacity: 0;
}

.slide-right-leave-to {
  position: absolute;
  right: -50%;
  opacity: 0;
}

.slide-right-leave-from {
  position: absolute;
  right: 0;
  opacity: 1;
}
</style>

<template>
  <main>
    <div class="flex flex-col min-h-full items-center justify-center py-[181px] px-4 sm:px-6 lg:px-8">
      <RouterView v-slot="{ Component }">
        <Transition
          name="fade"
          mode="out-in"
        >
          <Component :is="Component" />
        </Transition>
      </RouterView>
    </div>
  </main>
</template>

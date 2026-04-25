<template>
  <div
    class="loader"
    :class="{ 'loader--small': small }"
  >
    <Transition
      name="fade"
    >
      <div
        v-if="visible"
        class="loader__spinner"
      >
        <svg
          viewBox="25 25 50 50"
        >
          <circle
            class="loader__circle"
            cx="50"
            cy="50"
            r="22"
          ></circle>
        </svg>
      </div>
    </Transition>
  </div>
</template>

<script lang="ts" setup>

withDefaults(defineProps<{
  small?: boolean;
}>(), {
  small: false,
});

const visible = ref(false);

onMounted(() => {
  visible.value = true;
});

onBeforeUnmount(() => {
  visible.value = false;
});
</script>

<style lang="scss" scoped>
@keyframes spin {
  100% {
    rotate: 360deg;
  }
}

@keyframes stroke-animation {
  0% {
    stroke-dasharray: 1, 200;
    stroke-dashoffset: 0;
  }
  50% {
    stroke-dasharray: 89, 200;
    stroke-dashoffset: -35;
  }
  100% {
    stroke-dasharray: 89, 200;
    stroke-dashoffset: -124;
  }
}

.loader {
  display: inline-block;
  height: 96px;
  position: relative;
  aspect-ratio: 1;
  $loader-speed: 1.5s;
  $spin-speed: 1.5s;
  $loader: &;

  &__spinner {
    animation: spin $spin-speed linear infinite;
  }

  &__circle{
    fill: none;
    stroke-width: 3px;
    animation: stroke-animation $loader-speed linear infinite;
    stroke-linecap: round;
    stroke: theme('colors.main.400');
  }

  &--small {
    height: 24px;
    #{$loader}__circle {
      stroke-width: 3px;
    }
  }

}
</style>

<template>
  <div
    ref="cursorLevelContainer"
    class="cursor-level"
  >
    <div
      class="cursor-level__cursor"
      :class="{'is-black': isBlack}"
    />
    <div class="cursor-level__wrapper">
      <div
        v-for="num in sticksCount"
        :key="num"
        class="cursor-level__stick"
        :class="{
          'cursor-level__stick--middle': num % 5 === 0 && num % 10 !== 0,
          'cursor-level__stick--large': num === 1 || num === sticksCount || num % 10 === 0,
          'is-black': isBlack,
        }"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
const containerObserver = ref<null | ResizeObserver>(null);

const cursorLevelContainer = ref();

const props = withDefaults(defineProps<{
  stickGap?: number,
  cursorSize?: number,
  isBlack?: boolean,
}>(), {
  stickGap: 4,
  isBlack: false,
  cursorSize: 6,
});

const sticksCount = ref<number>(0);
const cursorPosition = ref<number>();

const onResize = (): void => {
  if (!cursorLevelContainer.value) return;
  const { height: containerHeight } = cursorLevelContainer.value.getBoundingClientRect();
  const fullCount = Math.floor(containerHeight / (props.stickGap + 1));
  sticksCount.value = fullCount;
};

const onCursorMouseMove = (e: MouseEvent):void => {
  const { top: containerTop, height: containerHeight } = cursorLevelContainer.value.getBoundingClientRect();
  const cursorHalf = Math.floor(props.cursorSize / 2);
  cursorPosition.value = e.clientY <= (containerTop - cursorHalf) ? (0 - cursorHalf)
    : e.clientY >= containerTop + containerHeight + cursorHalf ? containerHeight + cursorHalf
      : (e.clientY - cursorHalf) - containerTop;
};

const init = (): void => {
  if (!cursorLevelContainer.value) return;
  containerObserver.value = new ResizeObserver(() => onResize());
  containerObserver.value.observe(cursorLevelContainer.value);
  onResize();
  window.addEventListener('mousemove', onCursorMouseMove);
};

onMounted(() => init());
onUnmounted(
  () => {
    window.removeEventListener('mousemove', onCursorMouseMove);
  },
);
</script>

<style scoped lang="scss">
.cursor-level {
  --stick-gap: v-bind('stickGap + "px"');
  --cursor-position:  v-bind('cursorPosition + "px"');
  --cursor-size: v-bind('cursorSize + "px"');

  position: relative;

  &__cursor {
    position: absolute;
    top: var(--cursor-position);
    height: var(--cursor-size);
    width: var(--cursor-size);
    clip-path: polygon(0 0, 0% 100%, 100% 50%);
    background: theme('colors.white');
    transform: translateX(-100%);
    &.is-black {
      background: theme('colors.black');
    }
  }

  &__wrapper {
    display: flex;
    flex-direction: column;
    gap: var(--stick-gap);
  }

  &__stick {
    height: 1px;
    width: 3px;

    background: theme('colors.white');
    &.is-black {
      background: theme('colors.black');
    }
    &--middle {
      height: 1px;
      width: 4px;
    }

    &--large {
      height: 2px;
      width: 6px;
    }
  }
}
</style>

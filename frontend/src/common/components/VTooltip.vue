<template>
  <div
    ref="wrapTooltip"
    class="vtooltip group relative inline-flex"
    @mousemove="mouseMove"
    @mouseover="mouseOver"
  >
    <slot />
    <div
      v-show="content || $slots.content"
      ref="currentTooltip"
      class="vtooltip__content"
      :class="[
        hoverTooltip ? '' : 'hover:!invisible hover:!opacity-0',
        trail ? 'fixed trail' : 'absolute delay-200',
        show ? '' : 'hidden',
        showAlways ? '!visible !opacity-100' : '',
        top ? 'vtooltip__content-top' : 'vtooltip__content-bottom',
        center ? 'vtooltip__content-center' : right ? 'vtooltip__content-right' : 'vtooltip__content-left',
        positionLeft ? '!left-3.5' : '',
        positionRight ? '!right-3.5 !left-auto' : '',
        positionCenter ? '!right-auto' : '',
        tooltipClasses,
      ]"
      :style="`
        max-width: ${maxWidth}px;
      `"
    >
      <slot name="content">
        {{ content }}
      </slot>
    </div>
  </div>
</template>

<script lang="ts" setup>
const props = withDefaults(defineProps<{
  content?: string,
  hoverTooltip?: boolean,
  tooltipClasses?: string,
  top?: boolean,
  right?: boolean,
  center?: boolean,
  trail?: boolean,
  show?: boolean,
  showAlways?: boolean,
  margin?: number,
  positionLeft?: boolean,
  positionCenter?: boolean,
  positionRight?: boolean,
  maxWidth?: number,
}>(), {
  content: '',
  tooltipClasses: '',
  show: true,
  margin: 10,
  maxWidth: 296,
});

const currentTooltip = ref();
const wrapTooltip = ref();
const top = ref(props.top);
const right = ref(props.right);

const mouseMove = (e: MouseEvent) => {
  if (!props.trail) return;

  const coordsTooltip = currentTooltip.value?.getBoundingClientRect();
  const { height: tooltipHeight, width: tooltipWidth } = coordsTooltip;
  const { clientWidth, clientHeight } = document.documentElement;

  const isOutOfBoundsRight = tooltipWidth > clientWidth - e.clientX - props.margin;
  const isOutOfBoundsLeft = tooltipWidth > e.clientX + props.margin;

  if (props.right) {
    right.value = isOutOfBoundsLeft;
    currentTooltip.value.style.left = right.value
      ? `${e.clientX - tooltipWidth + 2}px`
      : `${e.clientX}px`;
  } else {
    right.value = isOutOfBoundsRight;
    currentTooltip.value.style.left = right.value
      ? `${e.clientX - tooltipWidth}px`
      : `${e.clientX}px`;
  }

  const isOutOfBoundsBottom = clientHeight - e.clientY - 15 < tooltipHeight + props.margin + 15;
  const isOutOfBoundsTop = e.clientY < tooltipHeight + props.margin;

  if (props.top) {
    top.value = isOutOfBoundsTop;
    currentTooltip.value.style.top = top.value
      ? `${e.clientY - tooltipHeight - 15}px`
      : `${e.clientY + 30}px`;
  } else {
    top.value = isOutOfBoundsBottom;
    currentTooltip.value.style.top = top.value
      ? `${e.clientY - tooltipHeight - 15}px`
      : `${e.clientY + 30}px`;
  }
};

const mouseOver = () => {
  if (props.trail) return;

  const coordsTooltip = currentTooltip.value?.getBoundingClientRect();
  const coordsWrapTooltip = wrapTooltip.value?.getBoundingClientRect();

  const isOutOfBoundsWrapTop = coordsWrapTooltip.top - props.margin < coordsTooltip.height;
  const isOutOfBoundsWrapBottom = document.documentElement.clientHeight - coordsWrapTooltip.bottom - props.margin < coordsTooltip.height;

  top.value = props.top ? isOutOfBoundsWrapTop : isOutOfBoundsWrapBottom;

  const isOutOfBoundsWrapRight = coordsTooltip.width <= coordsWrapTooltip.left - props.margin + coordsWrapTooltip.width / 2;
  const isOutOfBoundsWrapLeft = coordsTooltip.width > document.documentElement.clientWidth - (coordsWrapTooltip.left + props.margin + coordsWrapTooltip.width / 2);

  right.value = props.right ? isOutOfBoundsWrapRight : isOutOfBoundsWrapLeft;
};

onMounted(() => {
  mouseOver();
});

</script>

<style lang="scss" scoped>
.vtooltip {
  &__content {
    @apply group-hover:visible group-hover:delay-1000 group-hover:opacity-100 text-base-medium w-max;
    visibility: hidden;
    opacity: 0;
    font-size: 16px;
    background-color: theme('colors.additional.DEFAULT');
    color: theme('colors.main.50');
    padding: 4px 8px;
    border-radius: 8px;
    z-index: 100;
    transition: opacity 0.3s;

    &:before {
      @apply content-[''] absolute z-0 w-2.5 h-2.5 rotate-45 bg-additional;
    }

    &-top {
      @apply before:-bottom-1;

      &:not(.trail) {
        @apply bottom-[calc(100%+10px)];
      }
    }

    &-bottom {
      @apply top-[calc(100%+10px)] before:-top-1;
    }

    &-right {
      @apply before:right-2 right-1/2 translate-x-[16px];
    }

    &-center {
      @apply before:right-[calc(50%-10px)] left-1/2 -translate-x-[calc(50%+16px)];
    }

    &-left {
      @apply left-1/2 -translate-x-[10px];
    }
  }
}
</style>

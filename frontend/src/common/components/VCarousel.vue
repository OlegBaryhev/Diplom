<template>
  <div
    ref="rootRef"
    class="v-carousel"
    :class="{ 'v-carousel--single': images.length <= 1 }"
    tabindex="0"
    @keydown.left.prevent="prev"
    @keydown.right.prevent="next"
  >
    <!-- Empty state -->
    <div
      v-if="!images.length"
      class="v-carousel__empty"
    >
      <VIcon
        name="photo"
        class="v-carousel__empty-icon"
      />
      <span>Нет изображений</span>
    </div>

    <template v-else>
      <!-- Track -->
      <div
        class="v-carousel__track-wrapper"
        @pointerdown="onPointerDown"
        @pointermove="onPointerMove"
        @pointerup="onPointerUp"
        @pointercancel="onPointerUp"
      >
        <div
          class="v-carousel__track"
          :style="trackStyle"
        >
          <div
            v-for="(image, i) in images"
            :key="image.id"
            class="v-carousel__slide"
          >
            <img
              :src="fullUrl(image.url)"
              :alt="`Изображение ${i + 1}`"
              class="v-carousel__image"
              draggable="false"
              @error="onImgError(i)"
            >
            <div
              v-if="imgErrors.has(i)"
              class="v-carousel__img-fallback"
            >
              <VIcon
                name="photo"
                class="v-carousel__empty-icon"
              />
            </div>
          </div>
        </div>
      </div>

      <!-- Arrows (hidden for single image) -->
      <template v-if="images.length > 1">
        <button
          class="v-carousel__arrow v-carousel__arrow--prev"
          :disabled="currentIndex === 0"
          @click.stop="prev"
        >
          <VIcon
            name="left"
            class="v-carousel__arrow-icon"
          />
        </button>
        <button
          class="v-carousel__arrow v-carousel__arrow--next"
          :disabled="currentIndex === images.length - 1"
          @click.stop="next"
        >
          <VIcon
            name="right"
            class="v-carousel__arrow-icon"
          />
        </button>
      </template>

      <!-- Indicators -->
      <div
        v-if="images.length > 1"
        class="v-carousel__indicators"
      >
        <button
          v-for="(_, i) in images"
          :key="i"
          class="v-carousel__dot"
          :class="{ 'v-carousel__dot--active': i === currentIndex }"
          @click.stop="goTo(i)"
        />
      </div>
    </template>
  </div>
</template>

<script lang="ts" setup>
import type { CSSProperties } from 'vue';
import type { ProductImage } from '@/modules/products/types';
import { REMOTE_SERVER_URL } from '@/consts';

const props = defineProps<{
  images: ProductImage[];
}>();

const currentIndex = ref(0);
const dragStartX = ref(0);
const dragDeltaX = ref(0);
const isDragging = ref(false);
const pointerId = ref<number | null>(null);
const imgErrors = ref<Set<number>>(new Set());
const rootRef = ref<HTMLElement | null>(null);

const DRAG_THRESHOLD = 50;

const fullUrl = (url: string) => {
  if (url.startsWith('http')) return url;
  return `${REMOTE_SERVER_URL}${url}`;
};

const onImgError = (i: number) => {
  imgErrors.value = new Set([...imgErrors.value, i]);
};

const trackStyle = computed<CSSProperties>(() => ({
  transform: `translateX(calc(-${currentIndex.value * 100}% + ${isDragging.value ? dragDeltaX.value : 0}px))`,
  transition: isDragging.value ? 'none' : 'transform 0.3s ease',
}));

const goTo = (index: number) => {
  currentIndex.value = Math.max(0, Math.min(index, props.images.length - 1));
};

const prev = () => goTo(currentIndex.value - 1);
const next = () => goTo(currentIndex.value + 1);

const onPointerDown = (e: PointerEvent) => {
  if (props.images.length <= 1) return;
  isDragging.value = true;
  dragStartX.value = e.clientX;
  dragDeltaX.value = 0;
  pointerId.value = e.pointerId;
  (e.currentTarget as HTMLElement).setPointerCapture(e.pointerId);
};

const onPointerMove = (e: PointerEvent) => {
  if (!isDragging.value || e.pointerId !== pointerId.value) return;
  dragDeltaX.value = e.clientX - dragStartX.value;
};

const onPointerUp = (e: PointerEvent) => {
  if (!isDragging.value || e.pointerId !== pointerId.value) return;
  isDragging.value = false;
  const delta = dragDeltaX.value;
  dragDeltaX.value = 0;
  pointerId.value = null;

  if (delta < -DRAG_THRESHOLD) next();
  else if (delta > DRAG_THRESHOLD) prev();
};

watch(() => props.images, () => {
  currentIndex.value = 0;
  imgErrors.value = new Set();
});
</script>

<style lang="scss" scoped>
.v-carousel {
  position: relative;
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  background: theme('colors.main.50');
  border-radius: 8px;
  overflow: hidden;
  outline: none;

  &__track-wrapper {
    flex: 1;
    overflow: hidden;
    position: relative;
    cursor: grab;

    &:active {
      cursor: grabbing;
    }
  }

  &__track {
    display: flex;
    height: 100%;
    will-change: transform;
  }

  &__slide {
    flex: 0 0 100%;
    width: 100%;
    height: 100%;
    position: relative;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  &__image {
    max-width: 100%;
    max-height: 100%;
    object-fit: contain;
    user-select: none;
    pointer-events: none;
  }

  &__img-fallback {
    position: absolute;
    inset: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    background: theme('colors.main.100');
  }

  &__empty {
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 8px;
    color: theme('colors.additional.300');
    font-size: 13px;
  }

  &__empty-icon {
    width: 32px;
    height: 32px;
    color: theme('colors.additional.200');
  }

  &__arrow {
    position: absolute;
    top: 50%;
    transform: translateY(-50%);
    width: 28px;
    height: 28px;
    border-radius: 50%;
    background: rgba(255, 255, 255, 0.85);
    border: 1px solid rgba(0, 0, 0, 0.08);
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    transition: background 0.15s, opacity 0.15s;
    z-index: 2;

    &:disabled {
      opacity: 0.3;
      cursor: default;
    }

    &:not(:disabled):hover {
      background: white;
    }

    &--prev { left: 6px; }
    &--next { right: 6px; }

    &-icon {
      width: 14px;
      height: 14px;
      color: theme('colors.main.400');
    }
  }

  &__indicators {
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 6px;
    padding: 6px 0;
    flex-shrink: 0;
    background: rgba(255, 255, 255, 0.9);
  }

  &__dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: theme('colors.additional.200');
    border: none;
    cursor: pointer;
    transition: background 0.2s, transform 0.2s;
    padding: 0;

    &--active {
      background: theme('colors.main.400');
      transform: scale(1.25);
    }

    &:hover:not(&--active) {
      background: theme('colors.additional.300');
    }
  }

  &--single .v-carousel__track-wrapper {
    cursor: default;
  }
}
</style>

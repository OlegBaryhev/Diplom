<template>
  <div
    ref="triggerRef"
    class="v-expanded-photo"
    @mouseenter="onTriggerEnter"
    @mouseleave="onTriggerLeave"
  >
    <slot />
  </div>

  <Teleport to="body">
    <Transition name="v-expanded-photo-fade">
      <div
        v-if="isVisible"
        class="v-expanded-photo-preview"
        :style="previewStyle"
        @mouseenter="onPreviewEnter"
        @mouseleave="onPreviewLeave"
      >
        <VCarousel
          :images="images"
          class="v-expanded-photo-preview__carousel"
        />
      </div>
    </Transition>
  </Teleport>
</template>

<script lang="ts" setup>
import type { CSSProperties } from 'vue';
import type { ProductImage } from '@/modules/products/types';
import { activePreviewId } from '@/common/composables/usePhotoPreview';
import VCarousel from './VCarousel.vue';

// Each instance has a unique id; activePreviewId is module-level singleton
const _instanceId = Math.random().toString(36).slice(2);

const props = withDefaults(defineProps<{
  images: ProductImage[];
  delay?: number;
}>(), {
  delay: 1000,
});

const triggerRef = ref<HTMLElement | null>(null);
const previewStyle = ref<CSSProperties>({});
const isHoveringTrigger = ref(false);
const isHoveringPreview = ref(false);
let openTimer: ReturnType<typeof setTimeout> | null = null;

const isVisible = computed(() => activePreviewId.value === _instanceId);

const PREVIEW_WIDTH = 320;
const PREVIEW_HEIGHT = 240;
const GAP = 10;

const calcPosition = () => {
  const rect = triggerRef.value?.getBoundingClientRect();
  if (!rect) return;

  let left = rect.right + GAP;
  let { top } = rect;

  if (left + PREVIEW_WIDTH > window.innerWidth - GAP) {
    left = rect.left - PREVIEW_WIDTH - GAP;
  }
  if (top + PREVIEW_HEIGHT > window.innerHeight - GAP) {
    top = window.innerHeight - PREVIEW_HEIGHT - GAP;
  }
  top = Math.max(GAP, top);

  previewStyle.value = {
    position: 'fixed',
    left: `${Math.round(left)}px`,
    top: `${Math.round(top)}px`,
    width: `${PREVIEW_WIDTH}px`,
    zIndex: 9999,
  };
};

const open = () => {
  if (!props.images.length) return;
  calcPosition();
  activePreviewId.value = _instanceId;
};

const close = () => {
  if (activePreviewId.value === _instanceId) {
    activePreviewId.value = null;
  }
};

const scheduleClose = () => {
  setTimeout(() => {
    if (!isHoveringTrigger.value && !isHoveringPreview.value) {
      close();
    }
  }, 80);
};

const onTriggerEnter = () => {
  isHoveringTrigger.value = true;
  if (!openTimer) {
    openTimer = setTimeout(open, props.delay);
  }
};

const onTriggerLeave = () => {
  isHoveringTrigger.value = false;
  if (openTimer) {
    clearTimeout(openTimer);
    openTimer = null;
  }
  scheduleClose();
};

const onPreviewEnter = () => { isHoveringPreview.value = true; };
const onPreviewLeave = () => {
  isHoveringPreview.value = false;
  scheduleClose();
};

const onResize = () => { if (isVisible.value) close(); };

onMounted(() => window.addEventListener('resize', onResize));
onUnmounted(() => {
  window.removeEventListener('resize', onResize);
  if (openTimer) clearTimeout(openTimer);
  if (activePreviewId.value === _instanceId) activePreviewId.value = null;
});
</script>

<style lang="scss" scoped>
.v-expanded-photo {
  display: inline-flex;
  align-items: center;
  cursor: default;
}

.v-expanded-photo-preview {
  background: white;
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.18), 0 2px 8px rgba(0, 0, 0, 0.1);
  overflow: hidden;

  &__carousel {
    width: 100%;
    height: 240px;
  }
}

.v-expanded-photo-fade-enter-active,
.v-expanded-photo-fade-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}

.v-expanded-photo-fade-enter-from,
.v-expanded-photo-fade-leave-to {
  opacity: 0;
  transform: scale(0.95) translateY(-4px);
}
</style>

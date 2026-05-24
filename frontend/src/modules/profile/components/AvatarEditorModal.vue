<template>
  <VModalWrap
    :modal-id="modalId"
    title="Редактирование аватара"
    @closed="closeModal"
  >
    <template #modal-body>
      <div class="flex flex-col gap-4">
        <div class="relative flex justify-center">
          <div class="avatar-canvas-container">
            <canvas
              ref="canvasRef"
              class="avatar-canvas"
              :width="canvasSize"
              :height="canvasSize"
              @pointerdown="startDrag"
              @pointermove="onDrag"
              @pointerup="stopDrag"
              @pointercancel="stopDrag"
              @pointerleave="stopDrag"
              @wheel="handleWheel"
            ></canvas>
          </div>
        </div>

        <div class="flex flex-col gap-3">
          <label class="cursor-pointer select-none text-center text-main-400 text-sm-medium hover:text-main-500 transition">
            <span>Выбрать изображение</span>
            <input
              type="file"
              accept="image/jpeg,image/png,image/webp"
              class="hidden"
              @change="onFileSelect"
            />
          </label>

          <div
            v-if="imageSelected"
            class="flex select-none items-center gap-2"
          >
            <span class="text-xs text-additional-300">Масштаб</span>
            <input
              v-model.number="zoom"
              type="range"
              :min="minZoom"
              :max="maxZoom"
              step="0.01"
              class="flex-1"
            />
          </div>

          <p class="text-xs select-none text-additional-200 text-center">
            Перемещайте изображение мышью, масштабируйте колёсиком
          </p>
        </div>
      </div>
    </template>

    <template #modal-footer>
      <div class="space-x-4">
        <VBtn
          text="Отменить"
          outlined
          small
          @click="closeModal"
        />
        <VBtn
          text="Сохранить"
          small
          :loading="isSaving"
          @click="saveAvatar"
        />
      </div>
    </template>
  </VModalWrap>
</template>

<script lang="ts" setup>
import { useModals } from '@/stores/modals';
import { uploadAvatar } from '../api';

const props = withDefaults(
  defineProps<{
    modalId: string;
    currentAvatarUrl?: string | null;
  }>(),
  {
    currentAvatarUrl: null,
  },
);

const emit = defineEmits<{(e: 'saved', newUrl: string): void;}>();

const modalStore = useModals();
const canvasRef = ref<HTMLCanvasElement | null>(null);
const isSaving = ref(false);
const imageSelected = ref(false);
const imgLoaded = ref(false);

const canvasSize = 300;
const minZoom = 1;
const maxZoom = 3;

let imgElement: HTMLImageElement | null = null;
let baseScale = 1;

const offsetX = ref(0);
const offsetY = ref(0);
const zoom = ref(1);

let isDragging = false;
let dragPointerId: number | null = null;
let dragStart = { x: 0, y: 0 };
let startOffset = { x: 0, y: 0 };

const getImageMetrics = () => {
  if (!imgElement) {
    return null;
  }

  const imgW = imgElement.naturalWidth || imgElement.width;
  const imgH = imgElement.naturalHeight || imgElement.height;

  return { imgW, imgH };
};

const getCurrentScale = () => baseScale * zoom.value;

const clampOffset = (x: number, y: number, imgW: number, imgH: number, currentScale: number) => {
  const renderedW = imgW * currentScale;
  const renderedH = imgH * currentScale;
  const maxX = Math.max(0, (renderedW - canvasSize) / 2);
  const maxY = Math.max(0, (renderedH - canvasSize) / 2);

  return {
    x: Math.min(maxX, Math.max(-maxX, x)),
    y: Math.min(maxY, Math.max(-maxY, y)),
  };
};

const drawPlaceholder = () => {
  const canvas = canvasRef.value;
  if (!canvas) return;

  const ctx = canvas.getContext('2d');
  if (!ctx) return;

  ctx.clearRect(0, 0, canvasSize, canvasSize);

  ctx.save();
  ctx.beginPath();
  ctx.arc(canvasSize / 2, canvasSize / 2, canvasSize / 2, 0, Math.PI * 2);
  ctx.clip();

  ctx.fillStyle = '#e2e8f0';
  ctx.fillRect(0, 0, canvasSize, canvasSize);

  ctx.fillStyle = '#94a3b8';
  ctx.font = '24px sans-serif';
  ctx.textAlign = 'center';
  ctx.textBaseline = 'middle';
  ctx.fillText('No photo', canvasSize / 2, canvasSize / 2);

  ctx.restore();

  ctx.beginPath();
  ctx.arc(canvasSize / 2, canvasSize / 2, canvasSize / 2, 0, Math.PI * 2);
  ctx.strokeStyle = '#ccc';
  ctx.lineWidth = 2;
  ctx.stroke();
};

const drawImage = () => {
  if (!canvasRef.value) return;

  if (!imageSelected.value || !imgElement || !imgLoaded.value) {
    drawPlaceholder();
    return;
  }

  const canvas = canvasRef.value;
  const ctx = canvas.getContext('2d');
  if (!ctx) return;

  const metrics = getImageMetrics();
  if (!metrics) return;

  const currentScale = getCurrentScale();
  const { imgW, imgH } = metrics;
  const renderedW = imgW * currentScale;
  const renderedH = imgH * currentScale;

  const clamped = clampOffset(offsetX.value, offsetY.value, imgW, imgH, currentScale);
  offsetX.value = clamped.x;
  offsetY.value = clamped.y;

  const drawX = (canvasSize - renderedW) / 2 + offsetX.value;
  const drawY = (canvasSize - renderedH) / 2 + offsetY.value;

  ctx.clearRect(0, 0, canvasSize, canvasSize);

  ctx.save();
  ctx.beginPath();
  ctx.arc(canvasSize / 2, canvasSize / 2, canvasSize / 2, 0, Math.PI * 2);
  ctx.clip();
  ctx.drawImage(imgElement, drawX, drawY, renderedW, renderedH);
  ctx.restore();

  ctx.beginPath();
  ctx.arc(canvasSize / 2, canvasSize / 2, canvasSize / 2, 0, Math.PI * 2);
  ctx.strokeStyle = '#ccc';
  ctx.lineWidth = 2;
  ctx.stroke();
};

const fitImageToCircle = () => {
  if (!imgElement) return;

  const metrics = getImageMetrics();
  if (!metrics) return;

  const { imgW, imgH } = metrics;
  baseScale = Math.max(canvasSize / imgW, canvasSize / imgH);
  zoom.value = 1;
  offsetX.value = 0;
  offsetY.value = 0;
  imgLoaded.value = true;
  drawImage();
};

const loadImage = (url: string) => {
  imageSelected.value = true;
  imgLoaded.value = false;

  const img = new Image();
  img.crossOrigin = 'anonymous';
  img.onload = () => {
    imgElement = img;
    fitImageToCircle();
  };
  img.src = url;
};

const resetState = () => {
  imgElement = null;
  imgLoaded.value = false;
  imageSelected.value = false;
  baseScale = 1;
  offsetX.value = 0;
  offsetY.value = 0;
  zoom.value = 1;
  isDragging = false;
  dragPointerId = null;
  drawPlaceholder();
};

const closeModal = () => {
  modalStore.close(props.modalId);
  resetState();
};

const onFileSelect = (e: Event) => {
  const input = e.target as HTMLInputElement;
  if (!input.files?.length) return;

  const file = input.files[0];
  const reader = new FileReader();

  reader.onload = (ev) => {
    if (ev.target?.result) {
      loadImage(ev.target.result as string);
    }
  };

  reader.readAsDataURL(file);
};

const startDrag = (e: PointerEvent) => {
  if (!imgLoaded.value || !canvasRef.value) return;

  e.preventDefault();
  canvasRef.value.setPointerCapture(e.pointerId);
  isDragging = true;
  dragPointerId = e.pointerId;
  dragStart = { x: e.clientX, y: e.clientY };
  startOffset = { x: offsetX.value, y: offsetY.value };
};

const onDrag = (e: PointerEvent) => {
  if (!isDragging || dragPointerId !== e.pointerId || !imgElement) return;

  const dx = e.clientX - dragStart.x;
  const dy = e.clientY - dragStart.y;
  const metrics = getImageMetrics();
  if (!metrics) return;

  const currentScale = getCurrentScale();
  const nextX = startOffset.x + dx;
  const nextY = startOffset.y + dy;
  const clamped = clampOffset(nextX, nextY, metrics.imgW, metrics.imgH, currentScale);

  offsetX.value = clamped.x;
  offsetY.value = clamped.y;
};

const stopDrag = (e?: PointerEvent) => {
  if (!isDragging) return;

  if (e && dragPointerId !== null && canvasRef.value?.hasPointerCapture(dragPointerId)) {
    try {
      canvasRef.value.releasePointerCapture(dragPointerId);
    } catch (error) {
      console.error(error);
    }
  }

  isDragging = false;
  dragPointerId = null;
};

const handleWheel = (e: WheelEvent) => {
  if (!imgLoaded.value || !imgElement) return;

  e.preventDefault();

  const zoomStep = 0.08;
  const direction = e.deltaY > 0 ? -1 : 1;
  const nextZoom = Math.min(maxZoom, Math.max(minZoom, zoom.value + direction * zoomStep));

  if (nextZoom === zoom.value) return;

  zoom.value = nextZoom;

  const metrics = getImageMetrics();
  if (!metrics) return;

  const currentScale = getCurrentScale();
  const clamped = clampOffset(offsetX.value, offsetY.value, metrics.imgW, metrics.imgH, currentScale);
  offsetX.value = clamped.x;
  offsetY.value = clamped.y;
};

const getCroppedBlob = (): Promise<Blob> =>
  new Promise((resolve, reject) => {
    if (!canvasRef.value || !imgElement || !imgLoaded.value) {
      reject(new Error('Нет изображения'));
      return;
    }

    const cropCanvas = document.createElement('canvas');
    cropCanvas.width = canvasSize;
    cropCanvas.height = canvasSize;

    const cropCtx = cropCanvas.getContext('2d');
    if (!cropCtx) {
      reject(new Error('Cannot create crop context'));
      return;
    }

    cropCtx.clearRect(0, 0, canvasSize, canvasSize);
    cropCtx.save();
    cropCtx.beginPath();
    cropCtx.arc(canvasSize / 2, canvasSize / 2, canvasSize / 2, 0, Math.PI * 2);
    cropCtx.clip();
    cropCtx.drawImage(canvasRef.value, 0, 0);
    cropCtx.restore();

    cropCanvas.toBlob((blob) => {
      if (blob) resolve(blob);
      else reject(new Error('Ошибка создания Blob'));
    }, 'image/png');
  });

const saveAvatar = async () => {
  if (!imgLoaded.value) return;

  isSaving.value = true;

  try {
    const blob = await getCroppedBlob();
    const file = new File([blob], 'avatar.png', { type: 'image/png' });
    const formData = new FormData();
    formData.append('avatar', file);

    const response = await uploadAvatar(formData);
    const newUrl = response.avatar_url;

    emit('saved', newUrl);
    closeModal();
  } catch (error) {
    console.error('Ошибка сохранения аватара', error);
  } finally {
    isSaving.value = false;
  }
};

watch([zoom, offsetX, offsetY], () => {
  drawImage();
});

watch(
  () => props.currentAvatarUrl,
  (url) => {
    resetState();

    if (url) {
      loadImage(url);
    } else {
      drawPlaceholder();
    }
  },
  { immediate: true },
);

onMounted(() => {
  drawPlaceholder();
});

onBeforeUnmount(() => {
  stopDrag();
});
</script>

<style lang="scss" scoped>
.avatar-canvas-container {
  background: #f1f5f9;
  border-radius: 50%;
  display: inline-flex;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.avatar-canvas {
  border-radius: 50%;
  cursor: grab;
  display: block;
  user-select: none;
  touch-action: none;
}

.avatar-canvas:active {
  cursor: grabbing;
}
</style>

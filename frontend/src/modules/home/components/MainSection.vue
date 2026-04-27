<template>
  <article
    class="main-section flex-col"
  >
    <div
      ref="canvasWrapper"
      class="main-section__canvas-wrapper"
      @mousemove="parallax"
    >
      <canvas
        ref="mainCanvas"
        class="main-section__canvas"
        :style="{
          '--hue': hueSaturation,
          '--parallax-position': parallaxPosition,
        }"
      />
    </div>

    <div class="main-section__fixed-layer fixed w-full h-screen">
      <div class="main-section__cursor h-screen ml-[100px] flex flex-col  justify-center">
        <VCursorLevel class="h-[60%] ml-[5vw]" />
      </div>
    </div>

    <div
      v-scroll
      class="main-section__front-layer flex flex-col"
    >
      <section
        class="main-section__section flex w-full h-[100vh] min-h-[100vh] mandatory-scroll-snapping"
        :class="{ 'opacity-0' : selectedSectionIndex !== 0 }"
      >
        <article
          class="text-white flex flex-col h-full w-full"
        >
          <div class="main-section__content h-full w-full flex items-center justify-center pr-[100px]">
            <h1 class="main-section__main-title flex flex-col justify-center gap-0 text-center select-none text-[80px]">
              <span
                class="leading-[70px] mb-3 wow fadeInDown"
                data-wow-duration="2s"
                data-wow-delay="5s"
              >Система ценообразования</span>
              <strong class="leading-[110px] text-[120px] uppercase">"Doge Devices"</strong>
            </h1>
          </div>

          <div
            class="main-section__news ml-auto flex mt-auto w-full justify-end p-9 mr-5"
          >
            <div class="flex gap-8">
              <div
                v-for="(item, index) in newsMocks"
                :key="index"
                class="main-section__news-item cursor-pointer z-10"
              >
                <h4 class="w-full py-2 border-b-[1px] border-white select-none">
                  {{ item.title }}
                </h4>
                <p class="mt-2 select-none">
                  {{ item.text }}
                </p>
              </div>
            </div>
          </div>
        </article>
      </section>
      <section class="main-section__links h-[100vh] w-full min-h-[100vh] mandatory-scroll-snapping">
        <div
          class="flex w-full h-full justify-center items-center"
        >
          <Links />
        </div>
      </section>
    </div>
  </article>
</template>

<script lang="ts" setup>
import WOW from 'wowjs';
import { OverlayScrollbars } from 'overlayscrollbars';
import { newsMocks } from '../mock';
import useMainSectionShader from '@/common/composables/glsl/main-section';
import Links from '@/modules/home/components/Links.vue';

interface ISubSection {
  title: string,
  subtitle?: string,
  tags?: string[],
  img?: string,
}

const PARALLAX_PADDING = 100;
const scrollTop = ref<number>(0);
const hueSaturation = ref<number>();

const SECTIONS_CONTENT: ISubSection[] = [
  {
    title: '',
    subtitle: '',
    tags: [''],
    img: '',
  },
];

const inertiaFactor = 0.05;
const selectedSectionIndex = ref<number>(0);

const fetchedNews = ref([]);

const fetchNews = () => {
  fetchedNews.value = newsMocks;
  //
};

const sectionsCount = computed(() => SECTIONS_CONTENT.length + 1);

onMounted(() => {
  new WOW.WOW({
    live: true,
  }).init();
});

const parallaxPosition = ref<string | null>('none');
const mainCanvas = ref(null);
const canvasWrapper = ref();
const shader = ref(null);

const parallax = (e: MouseEvent) => {
  if (!canvasWrapper.value) return;

  const rect = canvasWrapper.value.getBoundingClientRect();
  const containerCenterX = rect.left + rect.width / 2;
  const containerCenterY = rect.top + rect.height / 2;

  const mouseX = e.clientX;
  const mouseY = e.clientY;

  const deltaX = mouseX - containerCenterX;
  const deltaY = mouseY - containerCenterY;

  const maxMoveX = (rect.width / 2) + (PARALLAX_PADDING / 2);
  const maxMoveY = (rect.height / 2) + (PARALLAX_PADDING / 2);

  const normalizedX = Math.max(-1, Math.min(1, deltaX / maxMoveX));
  const normalizedY = Math.max(-1, Math.min(1, deltaY / maxMoveY));

  const offsetX = normalizedX * maxMoveX * inertiaFactor;
  const offsetY = normalizedY * maxMoveY * inertiaFactor;

  parallaxPosition.value = `${offsetX / 2}px, ${offsetY / 2}px`;
};

const vScroll = {
  mounted: (el: HTMLElement) => {
    OverlayScrollbars(el, {
      overflow: {
        x: 'visible',
      },
      scrollbars: {
        visibility: 'auto',
      },
    }, {
      scroll(e) {
        const { scrollTop: elementScrollTop, scrollHeight } = e.elements().content;
        const sectionHeight = scrollHeight / sectionsCount.value;
        scrollTop.value = elementScrollTop;
        selectedSectionIndex.value = Math.floor(elementScrollTop / (sectionHeight * 0.5));
        hueSaturation.value = Math.max(0, Math.min(Math.floor((elementScrollTop / sectionHeight) * (360 / sectionsCount.value)), 360));
        shader.value?.onScroll(e);
      },
    });
  },
};

watch(
  () => selectedSectionIndex.value,
  (val) => val === 0 && fetchNews(),
  { immediate: true },
);

onMounted(
  () => {
    shader.value = useMainSectionShader(canvasWrapper.value, mainCanvas.value, { containerScrollTop: scrollTop });
    shader.value.startDraw();
  },
);

onUnmounted(() => {
  shader.value.eliminateEvents();
});

</script>

<style lang="scss" scoped>
.main-section {
  --parallax-padding: v-bind('PARALLAX_PADDING + "px"');
  --sections-count: v-bind(sectionsCount);

  min-height: 100vh;
  width: 100vw;
  display: flex;
  position: absolute;
  left: 0;
  flex-direction: column;

  &__canvas-wrapper{
    display: flex;
    width: 100vw;
    z-index: -1;
    position: fixed;
    justify-content: center;
    align-content: center;
    height: 100vh;
    overflow: hidden;
  }

  &__front-layer {
    z-index: 5;
    height: 100vh;
    display: flex;
    flex-direction: column;
    position: relative;
    width: 100%;
    overflow: auto;
    :deep() [data-overlayscrollbars-viewport] {
      scroll-snap-type: y proximity;
    }
  }

  &__news-item {
    cursor: pointer;
    padding: 6px;
    border-radius: 8px 12px;
    pointer-events: all;
    background: transparent;
    transition: all 0.2s ease-in;
    &:hover {
      transform: scale(102%);
    }
  }

  &__canvas {
    --hue: 0;
    --parallax-position: 0;
    position: absolute;
    top: calc(var(--parallax-padding) * -0.25);
    left: calc(var(--parallax-padding) * -0.5);
    filter: hue-rotate(calc(var(--hue) * 1deg));
    transform: translate(var(--parallax-position));
    transition: filter 0.3s linear, transform 0.2s ease-out;
    min-height: calc(100% + var(--parallax-padding));
    min-width: calc(100% + var(--parallax-padding));
  }

  .mandatory-scroll-snapping {
    scroll-margin-top: 30px;
    scroll-snap-align: center;
    transition: opacity 0.2s ease-in;
  }
}
</style>

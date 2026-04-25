<template>
  <Teleport to="body">
    <div
      ref="sidePanel"
      v-scroll-lock
      v-bind="{ ...$attrs, ...scopeAttrs }"
      :class="[CLASS_NAME, { [`${CLASS_NAME}--left`]: left }]"
      tabindex="0"
      @keydown.esc="close"
    >
      <Transition
        name="side-panel__overlay"
        appear
        @after-leave="emitClose"
      >
        <div
          v-if="isVisible"
          class="side-panel__overlay"
          data-test="close"
          @click="close"
        />
      </Transition>

      <Transition
        name="side-panel__base"
        appear
      >
        <div
          v-if="isVisible"
          class="side-panel__base"
        >
          <div
            class="side-panel__head"
            :class="{
              'show-shadow': !isZeroPosition && showShadow,
            }"
          >
            <div class="side-panel__head-wrapper">
              <slot name="title">
                <h3
                  v-if="title"
                  class="side-panel__title"
                >
                  {{ title }}
                </h3>
              </slot>
              <slot
                name="head"
                :on-close="close"
              />
            </div>
          </div>

          <div
            v-scroll
            class="side-panel__content"
          >
            <TransitionGroup
              name="content"
            >
              <slot
                v-if="!loading"
                :on-close="close"
              />

              <div
                v-else
                class="w-full h-full flex justify-center items-center"
              >
                <VLoader />
              </div>
            </TransitionGroup>
          </div>

          <Transition
            name="fade"
            mode="out-in"
          >
            <div
              v-if="!loading && (userHasPermission(Permissions.Delete) || userHasPermission(Permissions.Edit))"
              class="side-panel__foot"
            >
              <slot
                name="foot"
                :on-close="close"
              />
            </div>
          </Transition>

          <button
            v-if="!hideCloseButton"
            class="side-panel__close"
            type="button"
            data-test="close"
            @click="close"
          >
            <VIcon
              class="side-panel__close-icon"
              name="close"
            />
          </button>
        </div>
      </Transition>
    </div>
  </Teleport>
</template>

<script lang="ts" setup>
import { OverlayScrollbars } from 'overlayscrollbars';
import { Permissions } from '@/common/types/permissions';
import { userHasPermission } from '@/common/utils/permissions';
import { getFocusableElement } from '@/common/utils/focus';
import { useScrollCount } from '@/stores/scrollCount';

const CLASS_NAME = 'side-panel';

const instance = getCurrentInstance();

const scopeId = instance?.vnode.scopeId;
const scopeAttrs = scopeId ? { [scopeId]: '' } : {};

const props = withDefaults(defineProps<{
  title?: string;
  left?: boolean;
  hideCloseButton?: boolean;
  focusOnDescendants?: boolean;
  loading?: boolean;
  allowScrollEvent?: boolean;
  showShadow?: boolean;
}>(), {
  left: false,
  hideCloseButton: false,
  focusOnDescendants: false,
  loading: false,
  allowScrollEvent: false,
  showShadow: true,
});

const storeScrollCount = useScrollCount();

const sidePanel = ref<HTMLElement | null>(null);
const isVisible = ref(true);
const emit = defineEmits<{(evt: 'close'): void, (evt: 'os-scroll', arg: any): void}>();
const isZeroPosition = ref(true);

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
        props.allowScrollEvent && emit('os-scroll', e);
        isZeroPosition.value = e.elements().content.scrollTop === 0;
      },
    });
  },
};

const close = (): void => {
  isVisible.value = false;
};

const focusIn = (sidePanelElement: HTMLElement): void => {
  const focusableElement = getFocusableElement(sidePanelElement);

  if (props.focusOnDescendants && focusableElement) {
    focusableElement.focus();
  } else {
    sidePanelElement.focus();
  }
};

const emitClose = (): void => {
  const sidePanelElements = document.getElementsByClassName(CLASS_NAME);
  const currentSidePanelElement = sidePanelElements[sidePanelElements.length - 2] as HTMLElement | undefined;
  nextTick(() => {
    emit('close');

    if (currentSidePanelElement) {
      nextTick(() => { focusIn(currentSidePanelElement); });
    }
  });
};

onMounted(() => {
  storeScrollCount.increase();
  nextTick(() => {
    focusIn(sidePanel.value!);
  });
});

onUnmounted(() => {
  storeScrollCount.decrease();
});

defineExpose({ close });
</script>

<script lang="ts">
export default defineComponent({
  name: 'VSidePanel',
  inheritAttrs: false,
});
</script>

<style lang="scss" scoped>
.side-panel {
  width: 100%;
  height: 100%;
  position: fixed;
  top: 0;
  left: 0;
  z-index: 999;
  display: flex;
  justify-content: flex-end;

  $side-panel: &;

  &__overlay {
    @apply inset-0 bg-black/40;

    position: absolute;

    &-enter-active,
    &-leave-active {
      transition: opacity 0.3s ease-out;
    }

    &-enter-from,
    &-leave-to {
      opacity: 0;
    }
  }

  &__base {
    border-radius: 8px 0 0 8px;
    padding: 20px 0 24px 0;
    width: 90%;
    max-width: 600px;
    background-color: theme('colors.white');
    display: flex;
    flex-direction: column;
    position: relative;

    &-enter-active,
    &-leave-active {
      transition: transform 0.3s ease-out;
    }

    &-enter-from,
    &-leave-to {
      transform: translateX(100%);
    }
  }

  &__head-wrapper,
  &__content,
  &__foot {
    padding: 0 24px;
  }
  &__content {
    margin-bottom: 16px;
  }

  &__head {
    &-wrapper{
      position: relative;
      width: 100%;
      padding-bottom: 16px;
      &::after{
        content: '';
        left: 0;
        top: 100%;
        width: 100%;
        pointer-events: none;
        height: 20px;
        position: absolute;
        transition: 0.1s ease transform;
        background: linear-gradient(rgba(57, 80, 105, 0.15) 0%, #0000 100%);
        transform-origin: top;
        transform: scale(100%, 0);
      }
    }
    &.show-shadow{
      .side-panel__head-wrapper::after{
        transform: scale(100%, 100%);
      }
    }
  }
  &__title {
    @apply text-2xl-semibold;

    margin: 0 24px 14px 0;
    color: theme('colors.additional.DEFAULT');
  }

  &__content {
    flex: 1;
    overflow-y: auto;
    overflow-x: hidden;
    :deep(){
      .content-move,
      .content-enter-active,
      .content-leave-active {
        transition: 0.2s ease opacity;
      }

      .content-enter-active {
        transition-delay: 0.2s;
      }

      .content-enter-from,
      .content-leave-to {
        opacity: 0;
      }
    }
  }

  &__close {
    @apply transition-colors;

    position: absolute;
    top: 24px;
    right: 24px;
    color: theme('colors.additional.DEFAULT');

    &:hover,
    &:focus-visible {
      color: theme('colors.black');
    }
  }

  &--left {
    justify-content: flex-start;

    #{$side-panel}__base {
      border-radius: 0 8px 8px 0;

      &-enter-from,
      &-leave-to {
        transform: translateX(-100%);
      }
    }
  }
}
</style>

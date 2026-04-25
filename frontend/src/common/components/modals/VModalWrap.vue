<template>
  <Teleport to="body">
    <Transition
      name="modal__overlay"
      appear
    >
      <div
        v-if="show"
        v-scroll-lock="show"
        class="modal modal__overlay bg-black bg-opacity-40 fixed top-0 left-0 w-full h-full outline-none overflow-x-hidden overflow-y-auto flex justify-center items-center"
        tabindex="-1"
        role="dialog"
        data-test="close"
        @click="store.close(modalId)"
      >
        <div
          class="modal-dialog max-w-150 modal-dialog-centered relative w-auto pointer-events-none"
          @click.stop
        >
          <div class="modal-content rounded-xl p-8 border-none shadow-lg relative flex flex-col w-full pointer-events-auto bg-white bg-clip-padding outline-none text-current">
            <div class="modal-header mb-4">
              <h5 class="text-xl-semibold break-words text-black">
                <slot name="modal-header">
                  {{ title }}
                </slot>
              </h5>
            </div>

            <div class="modal-body text-base-regular mb-6">
              <slot name="modal-body" />
            </div>

            <div class="modal-footer flex flex-shrink-0 flex-wrap items-center justify-end">
              <slot name="modal-footer" />
            </div>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script lang="ts" setup>
import { useModals } from '@/stores/modals';
import { useScrollCount } from '@/stores/scrollCount';

const props = withDefaults(defineProps<{
  modalId?: string;
  title?: string;
}>(), {
  modalId: '',
});

const emit = defineEmits(['closed']);

const store = useModals();
const storeScrollCount = useScrollCount();

const show = computed(() => store.activeModals.includes(props.modalId));

watch(show, () => {
  if (!show.value) {
    emit('closed');
    storeScrollCount.decrease();
  } else storeScrollCount.increase();
});

onBeforeUnmount(() => show.value && storeScrollCount.decrease());
</script>

<script lang="ts">
export default defineComponent({
  inheritAttrs: false,
});
</script>

<style lang="scss" scoped>
@use '@/assets/mixins';

.modal {
  z-index: 99999;
  $scrollbar-size: 12px;
  @include mixins.scrollbar($scrollbar-size);

  &-content {
    box-shadow: 0px 0px 0px 1px rgba(0, 44, 94, 0.001), 0px 10px 20px -4px rgba(57, 80, 105, 0.15);
  }

  &__overlay {
    &-enter-active,
    &-leave-active {
      transition: opacity 0.3s ease;
    }

    &-enter-from,
    &-leave-to {
      opacity: 0;
    }
  }
}
</style>

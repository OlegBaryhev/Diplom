<template>
  <aside
    class="filter-panel p-6"
    :class="{'filter-panel__open': isOpen}"
  >
    <div class="filter-panel__wrapper">
      <div class="flex">
        <h3
          class="filter-panel__title h-[20px] mb-3 text-[16px] uppercase flex items-center gap-2 select-none"
          tabindex="1"
          role="button"
          @click="isOpen = !isOpen"
        >
          <VIcon
            name="filter"
            class="w-5 h-5 cursor-pointer"
          />
          <span v-show="isOpen">Фильтр</span>
        </h3>
      </div>

      <div v-show="isOpen">
        <div
          class="filter-panel__content gap-3 flex flex-col"
        >
          <slot></slot>
        </div>

        <div
          class="filter-panel__footer mt-4 flex gap-2 items-center">
          <VTooltip
            content="Очистить"
            hover-tooltip
            center
          >
            <VBtn
              outlined
              icon="close"
              :disabled="disableClearButton"
              data-test="clear-button"
              @click="emits('clear-filter')"
            />
          </VTooltip>

          <VBtn
            text="Применить"
            outlined
            icon="arrow-right"
            type="submit"
            class="w-full"
            icon-scale="0.7"
            :disabled="localLoading || disableFilterButton"
            @click="acceptFilter()"
          />
        </div>
      </div>
    </div>
  </aside>
</template>

<script lang="ts" setup>
const saveChangesLoading = ref<boolean>(false);

const props = withDefaults(defineProps<{
  loading?: boolean;
  disableFilterButton?: boolean;
  disableClearButton?: boolean;
  isOpen?: boolean;
}>(), {
  loading: false,
  disableFilterButton: false,
  disableClearButton: false,
  isOpen: true,
});

const localLoading = computed(() => saveChangesLoading.value || props.loading);
const emits = defineEmits([
  'update:isOpen',
  'accept-filter',
  'clear-filter',
]);

const acceptFilter = () => {
  emits('accept-filter');
};
const isOpen = useVModel(props, 'isOpen', emits);
</script>

<style lang="scss" scoped>
.filter-panel {
  --panel-width: 350px;
  --panel-width-close: 70px;
  height: 100%;
  display: flex;
  overflow: hidden;
  flex-direction: column;
  gap: 3px;
  transition: 0.2s ease-in-out width;
  position: fixed;
  z-index: 60;
  background: theme('colors.white');
  border-right: 1px solid theme("colors.main.400");

  &__wrapper {
    width: calc(var(--panel-width) - 96px);
    min-width: calc(var(--panel-width) - 96px);
  }

  &:not(.filter-panel__open){
    width: var(--panel-width-close);
  }

  &__open {
    width: var(--panel-width);
  }

  &::after {
    content: '';
    height: 100%;
    width: 3px;
    top: 0;
    background: linear-gradient(90deg, rgba(0, 0, 0, 0.2), transparent);
    right: 0;
    transform: translateX(100%);
    position: absolute;
  }
}
</style>

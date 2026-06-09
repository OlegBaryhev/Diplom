<!-- eslint-disable no-spaced-func -->
<template>
  <header class="filter-header w-full flex-col flex min-h-[128px] justify-between min-w-fit">
    <div
      v-if="title"
      class="filter-header__title-wrapper min-h-[70px] h-full flex items-center"
    >
      <h2 class="filter-header__title font-medium text-lg text-additional h-full flex items-center">
        {{ title }}
      </h2>

      <div class="filter-header__right ml-auto gap-5 flex items-center h-full">
        <slot name="actions" />
      </div>
    </div>

    <div class="w-full flex min-h-[70px] flex-end justify-between min-w-fit pb-5">
      <div class="filter-header__left h-full flex items-center mr-2">
        <VSearch
          v-model="searchQuery"
          class="filter-header__search min-w-max mr-6"
          :placeholder="searchPlaceholder"
          :min-length="0"
          input-focus
          :loading="loading"
          sm
          debounced
          :disabled="skeleton || disableSearch"
        />

        <span
          v-if="showTotal && typeof total === 'number'"
          class="text-sm text-additional text-base-regular"
        >
          Всего строк: {{ total }}
        </span>
      </div>

      <div class="filter-header__right h-full gap-5 flex items-center min-w-max">
        <VMultiselect
          v-model="sorting"
          :options="sortingOptions"
          item-name="name"
          primary-key="value"
          sm
          class="min-w-max"
          label="Сортировка"
          data-test="sorting"
        />

        <!-- View mode switcher slot (right of sorting) -->
        <slot name="view-mode" />

        <div
          v-if="modesList?.length"
          class="filter-header__icons-container flex gap-1"
        >
          <VBtn
            v-for="(item, index) in modesList"
            :key="index"
            ghost
            small
            :icon="item.icon"
            :class="{ 'filter-header__button--selected': selectedItemType === index }"
            :title="item.hint"
            @click="onModeClick(index)"
          />
        </div>
      </div>
    </div>
  </header>
</template>

<script lang="ts" setup>
const props = withDefaults(defineProps<{
  title: string;
  selectedType?: number;
  searchPlaceholder?: string;
  disableSearch?: boolean;
  loading?: boolean;
  skeleton?: boolean;
  search?: string;
  items?: any[];
  sortingOptions?: any;
  sorting?: string;
  modesList?: any[];
  showTotal?: boolean;
  total?: number;
}>(), {
  selectedType: 0,
  skeleton: false,
  disableSearch: false,
  loading: false,
  showTotal: false,
  total: null,
  search: '',
  sortingOptions: [],
  searchPlaceholder: 'Поиск',
});

// eslint-disable-next-line func-call-spacing
const emit = defineEmits<{(evt: 'update:search', searchQuery: string): void;
  (evt: 'update:sorting', value: string): void;
  (evt: 'update:selectedType', value: number): void;
}>();

const searchQuery = useVModel(props, 'search', emit);
const sorting = useVModel(props, 'sorting', emit);
const selectedItemType = ref<number>(props.selectedType);

watch(() => props.selectedType, (v) => { selectedItemType.value = v; });

const onModeClick = (index: number) => {
  selectedItemType.value = index;
  emit('update:selectedType', index);
};
</script>

<style lang="scss" scoped>
.filter-header {
  &__button--selected {
    color: theme('colors.main.DEFAULT');
    position: relative;

    &::after {
      content: '';
      position: absolute;
      bottom: 0;
      left: 0;
      width: 100%;
      height: 2px;
      background: theme('colors.main.DEFAULT');
      border-radius: 1px;
    }
  }
}
</style>

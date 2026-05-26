<template>
  <div class="flex items-center h-screen w-full">
    <VFilterPanel
      v-if="!!slots?.filter?.()[0]?.children?.length"
      v-model:is-open="isOpen"
      :disable-filter-button="disableFilterButton"
      :disable-clear-button="disableClearButton"
      :loading="loading"
      @accept-filter="emits('accept-filter');"
      @clear-filter="emits('clear-filter')"
    >
      <template #default>
        <slot name="filter" />
      </template>
    </VFilterPanel>

    <div
      class="fixed-header-n-table"
      :class="{
        'fixed-header-n-table--open-filter': isOpen && !!slots?.filter?.()[0]?.children?.length,
        'fixed-header-n-table--closed-filter': !isOpen && !!slots?.filter?.()[0]?.children?.length,
      }"
    >
      <VFilterHeader
        v-model:search="searchQuery"
        v-model:sorting="sorting"
        :sorting-options="sortingOptions"
        :show-total="showTotal"
        :total="total"
        :title="title"
        :items="items"
      >
        <template #actions>
          <slot name="header-actions" />
        </template>
      </VFilterHeader>

      <VAdvancedFlexTable
        v-if="items?.length || loading"
        class="table"
        :class="{
          'table--pinned-header': isTableHeaderPinned,
          'table--reduced-header-top': isHeadCollapsed,
          'table--hide-header': hideHead && isHeadCollapsed,
        }"
        :column-headers="columnHeaders"
        :items="items"
        :item-id-key="itemIdKey"
        :get-item-additional-classes="getItemAdditionalClasses"
        :active-item="activeItem"
        :item-checking="itemChecking"
        :process-checked-items="processCheckedItems"
        :loading="loading"
        :fetching-more-items-func="fetchingMoreItemsFunc"
        :total="total"
        :page="page"
        :row-height="rowHeight"
        :header-row-height="headerRowHeight"
        :has-dividing-line="hasDividingLine"
        :actions-list="actionsList"
        @update:active-item="$emit('update:activeItem', $event)"
        @update:item-checking="$emit('update:itemChecking', $event)"
        @update:page="$emit('update:page', $event)"
        @action="$emit('action', $event);"
      >
        <template #default="{ item }: { item: any }">
          <slot :item="item" />
        </template>

        <template
          v-if="$slots.checkedItemsActions"
          #checkedItemsActions="checkedActions"
        >
          <slot
            name="checkedItemsActions"
            v-bind="checkedActions"
          />
        </template>
      </VAdvancedFlexTable>

      <VError
        v-else-if="error"
        class="no-data-block"
        :icon-component="ErrorIcon"
        icon-size="32"
      />

      <VNoData
        v-else
        class="no-data-block"
        :icon-component="noFiltering ? noDataIconComponent : NoSearchResults"
        :button-text="noDataButtonText"
        @handle-button-click="$emit('handleNoDataButtonClick')"
      >
        <template v-if="!noFiltering">
          <p class="no-data-block--text">
            <b>Запрос не найден.</b><br>
            Попробуйте ввести другой
          </p>
        </template>
        <template v-else-if="$slots.noDataText">
          <slot name="noDataText" />
        </template>
      </VNoData>
    </div>
  </div>
</template>

<script lang="ts" setup>
import NoDataIcon from '@/assets/svg/presentation/no-data.svg?component';
import NoSearchResults from '@/assets/svg/presentation/no-search-results.svg?component';
import ErrorIcon from '@/assets/svg/presentation/error3.svg?component';
import type { Breadcrumb, IconComponent } from '@/common/types';
import type {
  ColumnHeader, ItemChecking, ProcessCheckedItems,
} from '@/common/components/tables/types';

const MIN_SCROLL_Y_TO_COLLAPSE_HEAD = 69;
const LOADER_GAP = 128;

// eslint-disable-next-line no-spaced-func
const props = withDefaults(defineProps<{
  title?: string;
  subtitle?: string;
  breads?: Breadcrumb[];
  showHeaderInfo?: boolean;
  search: string;
  disableSearch?: boolean;
  searchPlaceholder?: string;
  showTotal?: boolean;
  total?: number;
  page?: number;
  hasTabs?: boolean;
  tabs?: any[];
  activeTab?: any;
  columnHeaders: ColumnHeader[];
  items: any[];
  itemIdKey?: string;
  totalLoading?: boolean;
  // eslint-disable-next-line func-call-spacing
  getItemAdditionalClasses?: (item: any) => any[];
  activeItem?: any;
  itemChecking?: ItemChecking;
  processCheckedItems?: ProcessCheckedItems;
  loading?: boolean;
  error?: boolean;
  fetchingMoreItemsFunc?: (...args: any[]) => Promise<any>;
  noDataIconComponent?: IconComponent;
  noDataButtonText?: string;
  rowHeight?: number;
  headerRowHeight?: number;
  noInit?: boolean;
  hideHead?: boolean;
  hasDividingLine?: boolean;
  noFiltering?: boolean;
  disableFilterButton?: boolean;
  disableClearButton?: boolean;
  sorting?: string;
  sortingOptions?: any;
  actionsList?: any;
}>(), {
  disableSearch: false,
  noFiltering: false,
  total: 0,
  page: 1,
  loading: false,
  noDataIconComponent: NoDataIcon,
  error: false,
  hideHead: false,
  itemIdKey: 'id',
  hasDividingLine: false,
  sortingOptions: [],
  disableFilterButton: false,
  disableClearButton: false,
  actionsList: [],
});

// eslint-disable-next-line func-call-spacing, no-spaced-func
const emits = defineEmits<{
  (evt: 'update:search', newSearch: string): void;
  (evt: 'update:activeTab', newActiveTab: any): void;
  (evt: 'update:itemChecking', newItemChecking: ItemChecking): void;
  (evt: 'update:activeItem', newActiveItem: any): void;
  (evt: 'update:page', newPage: number): void;
  (evt: 'update:sorting', sorting: any): void;
  (evt: 'accept-filter'): void;
  (evt: 'clear-filter'): void;
  (evt: 'handleNoDataButtonClick'): void;
  (evt: 'action', action: any): void;
}>();

const sorting = useVModel(props, 'sorting', emits);
const searchQuery = useVModel(props, 'search', emits);

const isOpen = ref<boolean>(true);
const slots = useSlots();

watch(
  () => [props.search, props.appliedFilterData, props.activeTab],
  () => {
    props.itemChecking && emits('update:itemChecking', { mode: 'include', ids: [] });
  },
  { immediate: true, deep: true },
);

const windowScroll = useWindowScroll();
const isHeadCollapsed = ref(false);

const isTableHeaderPinned = computed(() => windowScroll.y.value > 0);
watch(windowScroll.y, (newScrollY, oldScrollY) => {
  if (oldScrollY - newScrollY === LOADER_GAP) {
    return;
  }

  isHeadCollapsed.value = newScrollY >= MIN_SCROLL_Y_TO_COLLAPSE_HEAD && newScrollY > oldScrollY;
});
</script>

<style lang="scss" scoped>
.table {
  display: block;
  padding-top: 68px;

  :deep() .flex-table__header {
    position: sticky;
    top: 68px;
    z-index: 60;
    transition: top 0.2s;
  }

  &--pinned-header :deep() .flex-table__header {
    border-color: transparent;
    box-shadow: 0 20px 20px -20px #39506926;
  }

  &--reduced-header-top :deep() .flex-table__header {
    top: 0px;
  }

  &--hide-header :deep() .flex-table__header{
    top: -68px;
  }
}

.fixed-header-n-table {
  padding: 0px 16px 28px;
  min-width: 1272px;
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  margin-left: 0px;
  transition: margin-left 0.2s linear;

  &--open-filter {
    margin-left: 350px;
  }

  &--closed-filter {
    margin-left: 70px;
  }
}

.no-data-block {
  &--text b {
    font-size: 24px;
  }
}
</style>

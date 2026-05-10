<template>
  <Component
    :is="component"
    class="flex-table"
    :class="classObject"
    role="grid"
  >
    <div
      ref="header"
      class="flex-table__header"
      role="rowgroup"
    >
      <VFlexTableRow :row-height="headerRowHeight">
        <VFlexTableCell
          :class="{
            'invisible': !hasAnyPermission,
            'system-invisible': !itemChecking,
          }"
          is-columnheader
          :skeleton="skeleton"
        >
          <VSkeletonItem
            v-if="skeleton"
            class="flex-table__checkbox-skeleton"
            square
          />
          <VCheckbox
            v-else
            :model-value="allItemsCheckboxChecked"
            :indeterminate="allItemsCheckboxIndeterminate"
            data-test="check-all-items"
            @update:model-value="onAllItemsCheckboxUpdate"
          />
        </VFlexTableCell>

        <VFlexTableCell
          v-if="showIdComputed"
          :class="{ 'invisible': !hasAnyPermission }"
          is-columnheader
          :skeleton="skeleton"
        >
          <VSkeletonItem
            v-if="skeleton"
            class="flex-table__cell-skeleton"
            :class="{'flex-table__cell-skeleton--large': largeSkeleton}"
          />
          <template v-else>
            ID
          </template>
        </VFlexTableCell>

        <VFlexTableCell
          v-for="item in expandedColumnHeaders"
          :key="item.key"
          is-columnheader
          :skeleton="skeleton"
          :data-test="`column-header-${item.key}`"
        >
          <VSkeletonItem
            v-if="skeleton"
            class="flex-table__cell-skeleton"
            :class="{ 'flex-table__cell-skeleton--large': largeSkeleton }"
          />

          <template v-else>
            <p class="flex-table__cell-header">
              {{ item.name }}
            </p>
          </template>
        </VFlexTableCell>

        <VFlexTableCell
          v-if="!!actionsList?.length"
          :class="{ 'invisible': !hasAnyPermission }"
          is-columnheader
          :skeleton="skeleton"
        >
          <VSkeletonItem
            v-if="skeleton"
            class="flex-table__cell-skeleton"
            :class="{'flex-table__cell-skeleton--large': largeSkeleton}"
          />
          <template v-else>
            Действия
          </template>
        </VFlexTableCell>
      </VFlexTableRow>
    </div>

    <div
      ref="body"
      v-scroll="disablePageMode"
      class="flex-table__body"
      role="rowgroup"
    >
      <DynamicScroller
        ref="scroller"
        :items="scrollerItems"
        :class="TABLE_SCROLLER_CLASS_NAME"
        :key-field="itemIdKey"
        :min-item-size="rowHeight"
        :buffer="scrollerBuffer"
        :page-mode="!disablePageMode"
        @scroll-end="!fetchMoreItemsLoading && !skeleton && $emit('scrollEnd')"
      >
        <template #default="{ item, index, active }">
          <DynamicScrollerItem
            :item="item"
            :active="active"
            :data-index="index"
            :size-dependencies="Object.keys(item)"
          >
            <VFlexTableRow
              :key="(itemIdKey && item[itemIdKey] ? item[itemIdKey] : item?.id) ?? index"
              class="flex-table__body-row"
              :class="{
                ...getItemAdditionalClasses(item, index),
                'temporary': item.isTemporary,
              }"
              v-bind="skeleton ? null : getItemAdditionalProps(item)"
              draggable="false"
              :row-height="rowHeight"
              :data-test="skeleton ? 'item-skeleton' : `item-${itemIdKey}-${item[itemIdKey]}`"
              :has-dividing-line="isShowDividingLine(item, index) ? hasDividingLine : false"
              v-on="skeleton ? {} : getItemAdditionalListeners(item)"
              @mouseover.stop="currentHoveredItem = index"
              @mouseleave="currentHoveredItem = null"
              @animationend="onAnimationEnd"
            >
              <VFlexTableCell
                :class="{
                  'invisible': !hasAnyPermission,
                  'system-invisible': !itemChecking,
                }"
                :skeleton="skeleton"
                @click.stop
                @click.self.prevent
              >
                <VSkeletonItem
                  v-if="skeleton"
                  class="flex-table__checkbox-skeleton"
                  :class="{'flex-table__checkbox-skeleton--large': largeSkeleton}"
                  square
                />

                <VCheckbox
                  v-else
                  :model-value="isItemChecked(item)"
                  :value="item[itemIdKey]"
                  data-test="check-item"
                  @update:model-value="onItemCheckboxUpdate($event, item)"
                />
              </VFlexTableCell>

              <VFlexTableCell
                v-if="showIdComputed"
                :class="{ 'invisible': !hasAnyPermission }"
                :skeleton="skeleton"
              >
                <VSkeletonItem
                  v-if="skeleton"
                  class="flex-table__cell-skeleton"
                  :class="{'flex-table__cell-skeleton--large': largeSkeleton}"
                />

                <template v-else>
                  {{ item[itemIdKey] }}
                </template>
              </VFlexTableCell>

              <template v-if="skeleton">
                <VFlexTableCell
                  v-for="{ key } in columnHeaders"
                  :key="key"
                  skeleton
                >
                  <VSkeletonItem
                    class="flex-table__cell-skeleton"
                    :class="{'flex-table__cell-skeleton--large': largeSkeleton}"
                  />
                </VFlexTableCell>
              </template>

              <slot
                v-else
                :item="item"
              />

              <VFlexTableCell
                v-if="!!actionsList?.length"
                :class="{ 'invisible': !hasAnyPermission }"
                :skeleton="skeleton"
                @click.stop
                @click.self.prevent
              >
                <VSkeletonItem
                  v-if="skeleton"
                  class="flex-table__cell-skeleton"
                  :class="{'flex-table__cell-skeleton--large': largeSkeleton}"
                />

                <div
                  v-else
                  class="flex w-full justify-center"
                >
                  <VIcon
                    v-for="(action, actionIndex) in actionsList"
                    :key="action?.emit ?? actionIndex"
                    :data-test="`action-${actionIndex}`"
                    :name="action?.icon"
                    class="actions-styles cursor-pointer h-[20px] w-[20px] text-main-300"
                    tabindex="1"
                    role="button"
                    @click="$emit('action', { action, item })"
                  />
                </div>
              </VFlexTableCell>
            </VFlexTableRow>
          </DynamicScrollerItem>
        </template>
      </DynamicScroller>
    </div>
  </Component>
</template>

<script lang="ts" setup>
import type { ComponentCustomProps } from 'vue';
import { debounce } from 'lodash';
import { OverlayScrollbars } from 'overlayscrollbars';
import VSkeleton from '@/common/components/VSkeleton/index.vue';
import {
  TABLE_SCROLLER_CLASS_NAME,
  TABLE_MIN_HEIGHT,
  TABLE_MIN_HEIGHT_WITH_FOOTER_BUTTONS,
} from './consts';
import type { CheckboxChecked } from '@/common/types';
import type { ColumnHeader, ItemChecking } from './types';
import { userHasPermission } from '@/common/utils/permissions';
import { Permissions } from '@/common/types/permissions';

// eslint-disable-next-line no-spaced-func
const props = withDefaults(defineProps<{
  columnHeaders: ColumnHeader[];
  items: any[];
  itemIdKey?: string;
  // eslint-disable-next-line func-call-spacing
  getItemAdditionalProps?: (item: any) => ComponentCustomProps;
  // eslint-disable-next-line @typescript-eslint/ban-types
  getItemAdditionalListeners?: (item: any) => Record<string, Function>;
  itemChecking?: ItemChecking;
  loading?: boolean;
  skeletonBodyRowCount?: number;
  scrollerBuffer?: number;
  disablePageMode?: boolean;
  rowHeight?: number;
  headerRowHeight?: number;
  hasDividingLine?: boolean;
  customScroll?: boolean;
  hasFooterButtons?: boolean;
  fetchMoreItemsLoading?: boolean;
  largeSkeleton?: boolean;
  showId?: boolean;
  actionsList?: any;
}>(), {
  itemIdKey: 'id',
  getItemAdditionalProps: () => ({}),
  getItemAdditionalListeners: () => ({}),
  loading: false,
  skeletonBodyRowCount: 14,
  scrollerBuffer: 1600,
  disablePageMode: false,
  rowHeight: 48,
  hasDividingLine: false,
  customScroll: false,
  hasFooterButtons: false,
  fetchMoreItemsLoading: false,
  largeSkeleton: false,
  showId: true,
  actionsList: [],
});

const showIdComputed = computed(() => props?.showId && (userHasPermission(Permissions.Write) || userHasPermission(Permissions.Edit) || userHasPermission(Permissions.Delete)));

// eslint-disable-next-line func-call-spacing, no-spaced-func
const emit = defineEmits<{
  (evt: 'update:itemChecking', newItemChecking: ItemChecking): void;
  (evt: 'action', action: any): void;
  (evt: 'scrollEnd'): void;
}>();

const disableTemporaryItems = inject<(ids?: string[]) => void | null>('disableTemporaryItems', () => null);

const onAnimationEnd = debounce((event: AnimationEvent) => {
  if (event.animationName.startsWith('pulse') && disableTemporaryItems) {
    disableTemporaryItems();
  }
}, 1000);
const scroller = ref(null);

const minTableHeight = computed(() => props.hasFooterButtons ? TABLE_MIN_HEIGHT_WITH_FOOTER_BUTTONS : TABLE_MIN_HEIGHT);

const vScroll = {
  mounted: (el: HTMLElement) => {
    OverlayScrollbars({
      target: el,
      elements: {
        viewport: scroller.value.$el,
      },
    }, {
      overflow: {
        x: 'visible',
      },
      scrollbars: {
        visibility: 'auto',
      },
    });
  },
};

const skeleton = computed(() => props.loading && !props.items?.length);
const component = computed(() => skeleton.value ? VSkeleton : 'div');

const isScrollerOverflowed = ref(false);

const expandedColumnHeaders = computed(() => props.columnHeaders);

const classObject = computed(() => ({
  'flex-table--checkable': props.itemChecking,
  'flex-table--skeleton': skeleton.value,
  'flex-table--loading': props.loading,
  'flex-table--disabled-page-mode': props.disablePageMode,
  'flex-table--overflowed-scroller': isScrollerOverflowed.value,
}));

const skeletonBodyRows = computed(() => new Array(props.skeletonBodyRowCount).fill(null).map((_, index) => ({
  [props.itemIdKey]: index,
})));

const scrollerItems = computed(() => skeleton.value ? skeletonBodyRows.value : props.items ?? []);

const hasAnyPermission = computed(() => userHasPermission(Permissions.Delete));

const allItemsCheckboxChecked = computed(() => {
  if (!props.itemChecking) {
    return false;
  }

  return props.itemChecking.mode === 'include'
    ? props.itemChecking.ids.length === props.items?.length
    : !props.itemChecking.ids.length;
});

const allItemsCheckboxIndeterminate = computed(() => Boolean(props.itemChecking?.ids.length) && props.itemChecking?.ids.length !== props.items?.length);

const onAllItemsCheckboxUpdate = (checked: CheckboxChecked): void => {
  const newMode = checked ? 'exclude' : 'include';
  emit('update:itemChecking', { mode: newMode, ids: [] });
};

const isItemChecked = (item: any): boolean => {
  if (!props.itemChecking) {
    return false;
  }

  const hasBeenAddedToIds = props.itemChecking.ids.includes(item[props.itemIdKey]);
  return props.itemChecking.mode === 'include' ? hasBeenAddedToIds : !hasBeenAddedToIds;
};

const onItemCheckboxUpdate = (checked: CheckboxChecked, item: any): void => {
  if (!props.itemChecking) {
    return;
  }

  const newIds = props.itemChecking.mode === 'include' && checked || props.itemChecking.mode === 'exclude' && !checked
    ? [...props.itemChecking.ids, item[props.itemIdKey]]
    : props.itemChecking.ids.filter((id) => id !== item[props.itemIdKey]);

  emit('update:itemChecking', { ...props.itemChecking, ids: newIds });
};

const currentHoveredItem = ref(null);

const isShowDividingLine = (item: any, index: number) => {
  const isCurrentItemChecked = isItemChecked(item);

  const nextItem = props.items?.[index + 1];
  const isNextItemChecked = nextItem ? isItemChecked(nextItem) : false;

  const isNextItemHovered = index + 1 === currentHoveredItem.value;
  const isCurrentItemHovered = index === currentHoveredItem.value;

  if (skeleton.value) return true;
  if (isNextItemHovered || isCurrentItemHovered) return false;
  if (isCurrentItemChecked && !isNextItemChecked) return false;
  if (!isCurrentItemChecked && isNextItemChecked) return false;
  return true;
};

const scrollbarOverflowValue = computed(() => {
  if (props.items?.length > 6) return 'hidden';
  return 'visible';
});

const getItemAdditionalClasses = (item: any, index: number): any => {
  const isCurrentItemChecked = isItemChecked(item);

  if (!isCurrentItemChecked) {
    return null;
  }

  const previousItem = props.items[index - 1];
  const isPreviousItemChecked = previousItem ? isItemChecked(previousItem) : false;
  const nextItem = props.items[index + 1];
  const isNextItemChecked = nextItem ? isItemChecked(nextItem) : false;

  return {
    'flex-table__body-row--checked': true,
    'flex-table__body-row--rect--top': isPreviousItemChecked,
    'flex-table__body-row--rect--bottom': isNextItemChecked,
  };
};
</script>

<style lang="scss" scoped>
@use '@/assets/mixins';

$tile-bg: #cfcfdf;

@keyframes pulse {
  0% {
    background: theme('colors.main.100');
  }
  50% {
    background: theme('colors.main.200');
  }
}
.system-invisible {
  @apply invisible;
  width: 0 !important;
  max-width: 0 !important;
  min-width: 0 !important;
  padding: 0 !important;
}

.flex-table {
  --local-height-correction: 0px;
  position: relative;

  $table: &;

  &__header {
    @apply text-xs-medium;

    margin-bottom: 4px;
    border-bottom: 1px solid theme('colors.main.200');
    color: theme('colors.additional.300');
    background-color: theme('colors.white');
  }

  &__checkbox-skeleton {
    margin: 0 auto;
    width: 20px;
    height: 20px;
  }

  &__cell-skeleton {
    width: 100%;
    height: 8px;
    &--large {
      height: 20px;
    }
  }

  &__cell-header {
    display: inline;
    position: relative;
  }

  &__body {
    :deep(){
      .os-scrollbar.os-scrollbar-vertical{
        z-index: 15;
      }
    }

    &-scroller {
      @apply transition-opacity duration-200;

      :deep() {
        -ms-overflow-style: none;
        scrollbar-width: none;
        min-height: calc(v-bind(minTableHeight) + var(--local-height-correction));
        &::-webkit-scrollbar {
          display: none;
        }

        .vue-recycle-scroller__item-view.hover {
          z-index: 10;
        }

        .vue-recycle-scroller__item-wrapper {
          overflow: v-bind(scrollbarOverflowValue) !important;
        }

        // .vue-recycle-scroller__item-wrapper {
        //   overflow: visible;
        //   min-height: auto !important;
        // }
      }
    }

    &-row {
      &.temporary {
        animation: 1s pulse forwards ease-in-out;
      }

      @apply text-sm-regular;

      border-radius: 8px;
      transition-property: border-radius, color, background-color;
      transition-duration: 0.4s, 0.2s, 0.2s;

      &:hover {
        background-color: theme('colors.main.50');
      }

      &--checked {
        @apply bg-main-200/40;

        color: theme('colors.main.DEFAULT');

        &:hover {
          @apply bg-main-200/70;

          color: theme('colors.black');
        }
      }

      &--rect {
        &--top {
          border-top-left-radius: 0;
          border-top-right-radius: 0;
        }

        &--bottom {
          border-bottom-left-radius: 0;
          border-bottom-right-radius: 0;
        }
      }
    }
  }

  &--checkable :deep() .flex-table-cell:first-child {
    padding-right: 24px;
    width: 24px + 40px;
    justify-content: center;
    cursor: default;
  }

  &--skeleton {
    .flex-table__header {
      border-color: theme('colors.additional.200');
    }

    .flex-table__body-row:hover {
      background-color: transparent;
    }

    :deep() .flex-table-cell__inner {
      width: 100%;
    }
  }

  &--loading:not(&--skeleton) &__body {
    cursor: wait;

    &-scroller {
      opacity: 0.5;
      pointer-events: none;
    }
  }
}

.actions-styles {
  transition: transform, filter 0.3s ease-in-out;
  &:hover { transform: scale(1.05); }
  &:hover:active {transform: scale(0.95); }
}
</style>

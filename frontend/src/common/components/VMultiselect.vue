<template>
  <div
    v-click-away="close"
    class="relative !cursor-pointer"
    :style="{ overflow: isCalculatingDirection ? 'hidden' : 'unset' }"
  >
    <VInput
      ref="parentInput"
      select
      :primary="primary"
      :secondary="secondary"
      select-readonly
      :readonly="readonly"
      :input-focus="isFocus"
      :disabled="disabled"
      :sm="sm"
      class="select-input !cursor-pointer"
      :error="error"
      :model-value="formattedModelValue"
      :label="labelToShow"
      :placeholder="placeholder"
      :show-number-selected="showNumberSelected"
      :num-words="numWords"
      :item-name="itemName"
      :clearable="clearable && !showClearButton"
      :with-border="withBorder"
      :attr-optional="attrOptional"
      :hint="hint"
      data-test="toggleShowMenu"
      @click="toggleShowMenu"
      @clear-input="clearHandler"
    />
    <Teleport
      to="body"
      :disabled="!preventScrollClipping"
    >
      <Transition>
        <div
          v-if="showMenu && !readonly"
          ref="searchFilter"
          class="menu"
          :style="{
            visibility: isCalculatingDirection ? 'hidden' : 'visible',
            width: preventScrollClipping && `${listDimensions.width}px`,
            left: preventScrollClipping && `${listDimensions.left}px`,
            top: preventScrollClipping && `${listDimensions.top}px`,
          }"
          :class="{
            'menu--enlarged-top': error && typeof error === 'string',
            'floating-top': (floatingTop || dropAlwaysTop) && !preventScrollClipping,
            'is-new-filter': isUseNewFilter,
          }"
        >
          <VSearchFilterWithWorker
            v-if="isUseNewFilter"
            class="max-h-[352px] max-w-full"
            :model-value="adjustedModelValue"
            :multi="multi"
            input-focus
            secondary
            :item-name="itemName"
            :primary-key="primaryKey"
            :options="options"
            :paginated-options-url="paginatedOptionsUrl"
            @update:modelValue="selectHandler"
            @update:search="$emit('update:search', $event)"
            @close="close"
            @click.stop
          />

          <VSearchFilter
            v-else
            input-focus
            :model-value="adjustedModelValue"
            :multi="multi"
            :item-name="itemName"
            :options="options"
            :loading="loading"
            :num-words="numWords"
            class="max-h-[352px]"
            :primary-key="primaryKey"
            :clearable="optional"
            :off-sort="offSort"
            :off-shift="offShift"
            :async-search="asyncSearch"
            :records-name="recordsName"
            :show-clear-button="showClearButton"
            :paginated-options-url="paginatedOptionsUrl"
            @update:modelValue="selectHandler"
            @update:search="$emit('update:search', $event)"
            @close="close"
            @list-ready="recalculateUpdateListPosition"
            @click.stop
          >
            <template #option="{ option }">
              <slot
                name="option"
                :option="option"
              />
            </template>
          </VSearchFilter>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<script lang="ts" setup>
import { useElementBounding } from '@vueuse/core';
import type { GlobalComponents } from 'vue';

const props = withDefaults(defineProps<{
  modelValue?: object | string | number | any[] | null;
  recordsName?: object | string;
  options?: any[];
  multi?: boolean;
  auto?: boolean;
  error?: string | boolean;
  label?: string;
  placeholder?: string;
  sm?: boolean;
  primary?: boolean;
  secondary?: boolean;
  withBorder?: boolean;
  itemName?: string;
  selectReadonly?: boolean;
  readonly?: boolean;
  loading?: boolean;
  primaryKey?: string;
  clearable?: boolean;
  optional?: boolean;
  attrOptional?: boolean;
  shortOptionalPostfix?: boolean;
  disabled?: boolean;
  showClearButton?: boolean;
  numWords?: any[];
  showNumberSelected?: boolean;
  asyncSearch?: boolean;
  paginatedOptionsUrl?: string | null;
  offSort?: boolean;
  offShift?: boolean;
  inputValue?: string;
  hint?: string | null;
  isNewFilter?: boolean;
  floatingOptionsParentId?: string | null;
   /** Для использования Teleport(-а) */
  preventScrollClipping?: boolean;
  deepRecalculating?: boolean;
  /** Для случаев, когда список нужно отображать сверху */
  dropAlwaysTop?: boolean;
}>(), {
  modelValue: null,
  itemName: 'name',
  loading: false,
  primaryKey: 'value',
  clearable: false,
  numWords: () => [],
  showNumberSelected: false,
  asyncSearch: false,
  paginatedOptionsUrl: null,
  offSort: false,
  offShift: false,
  inputValue: '',
  floatingOptionsParentId: null,
  preventScrollClipping: false,
  deepRecalculating: false,
  dropAlwaysTop: false,
  attrOptional: false,
  isNewFilter: true,
});

const showMenu = ref<boolean>(false);

const getAdjustedFilterItemData = (data: any) => Array.isArray(data)
  ? data
  : data instanceof Object
    ? Object.values(data).reduce((acc:any, value:any) => acc.concat(value), [])
    : [];

const isUseNewFilter = computed(() => props.isNewFilter && props.multi);
const adjustedModelValue = computed(() => !props.isNewFilter && props.multi ? props.modelValue : getAdjustedFilterItemData(props.modelValue));

const parentInput = ref<InstanceType<GlobalComponents['VInput']> | null>(null);
const deepRecalculatingCondition = computed<number | null>(() => {
  const { x: positionX, y: positionY } = useElementBounding(parentInput.value?.$el);
  return props.deepRecalculating && parentInput?.value
    ? { positionX: positionX.value, positionY: positionY.value }
    : null;
});

const searchFilter = ref<HTMLDivElement | null>(null);
const selectPlaceCalculatingParent = computed(() => props.floatingOptionsParentId
  ? document.getElementById(props.floatingOptionsParentId)
  : null);

const DROPDOWN_MARGIN_SIZE = 8;

const emits = defineEmits([
  'update:modelValue',
  'update:search',
  'close',
]);

const formattedModelValue = computed(() => {
  if (props.modelValue === null) {
    return '';
  }

  if (props.inputValue) {
    return props.inputValue;
  }

  if (Array.isArray(props.modelValue)) {
    return props.modelValue.map((item) => item[props.itemName] ?? item).join(', ');
  }

  return String(props.modelValue[props.itemName] ?? props.modelValue);
});

const labelToShow = computed<string>(() => {
  if (!props.label) {
    return props.multi ? 'Выберите значения' : 'Выберите значение';
  }

  const postfix = props.attrOptional ? '' : props.optional ? ` (${props.shortOptionalPostfix ? 'необяз.' : 'необязательно'})` : '';

  return `${props.label}${postfix}`;
});

const isFocus = computed(() => !props.readonly ? showMenu.value : false);
function selectHandler(option: null | any) {
  if (!props.multi) {
    showMenu.value = false;
  }
  emits('update:modelValue', option);
}

function close() {
  if (showMenu.value) {
    showMenu.value = false;
  }

  emits('close');
}

const floatingTop = ref<boolean>(false);
// eslint-disable-next-line no-unneeded-ternary
const isCalculatingDirection = ref(props.floatingOptionsParentId ? true : false);

const listDimensions = reactive({
  top: 0,
  width: 0,
  left: 0,
});

const updateListPosition = ():void => {
  if (!selectPlaceCalculatingParent.value && !props.preventScrollClipping) {
    isCalculatingDirection.value = false;
    return;
  }

  try {
    const {
      top: containerTop,
      height: containerHeight,
    } = useElementBounding(selectPlaceCalculatingParent.value);

    const parentTop = containerTop ?? 0;
    const parentHeight = selectPlaceCalculatingParent.value
      ? Math.min(containerHeight.value, window.innerHeight) ?? window.innerHeight
      : window.innerHeight;

    const {
      height: listHeight,
    } = useElementBounding(searchFilter);

    const {
      top: inputTop,
      height: inputHeight,
      width: inputWidth,
      left: inputLeft,
    } = useElementBounding(parentInput);

    if (!props.dropAlwaysTop) {
      const distanceFromTopToList = Math.round(inputTop.value + inputHeight.value + DROPDOWN_MARGIN_SIZE + window.scrollY);
      const distanceFromTopToParent = Math.round(parentTop.value + window.scrollY);

      const potentialSpaceForListAtTop = distanceFromTopToList - distanceFromTopToParent - 48 - DROPDOWN_MARGIN_SIZE * 2;
      const potentialSpaceForListAtBottom = parentHeight - (inputTop.value + window.scrollY - distanceFromTopToParent) - 48 - DROPDOWN_MARGIN_SIZE;

      floatingTop.value = potentialSpaceForListAtBottom < listHeight.value
        && potentialSpaceForListAtTop >= listHeight.value;
    }

    listDimensions.width = inputWidth.value;

    listDimensions.left = inputLeft.value + window.scrollX;
    listDimensions.top = Math.round((props.dropAlwaysTop || floatingTop.value)
      ? inputTop.value + window.scrollY - listHeight.value - DROPDOWN_MARGIN_SIZE
      : inputTop.value + inputHeight.value + window.scrollY + DROPDOWN_MARGIN_SIZE);
  } catch (e) {
    console.error(e);
  } finally {
    isCalculatingDirection.value = false;
  }
};

const recalculateUpdateListPosition = (): void => {
  if (!showMenu.value) return;
  updateListPosition();
};

const toggleShowMenu = () => {
  if (!props.disabled) {
    showMenu.value = !showMenu.value;
    recalculateUpdateListPosition();
  }
};

const clearHandler = (): void => {
  emits('update:modelValue', '');
};

watch(showMenu, (newValue) => {
  if (!newValue) {
    parentInput.value.input.blur();
  }
});

watch(
  () => deepRecalculatingCondition.value,
  () => recalculateUpdateListPosition(),
  { deep: true },
);

</script>

<style scoped lang="scss">

.menu {
  background-color: theme('colors.white');
  border-radius: 8px;
  z-index: 99999;
  padding: 4px 0;
  position: absolute;
  top: calc(100% + v-bind('DROPDOWN_MARGIN_SIZE + "px"'));
  width: 100%;
  height: fit-content;
  left: 0;
  max-height: 384px;
  box-shadow: 0px 2px 2px rgba(46, 62, 80, 0.1),
              0px 0px 2px rgba(111, 146, 185, 0.25),
              0px 3px 18px -1px rgba(120, 138, 159, 0.2);

  &::after {
    display: block;
    content: '';
    height: 18px;
    position: absolute;
    bottom: -18px;
    width: 100%;
  }

  &.floating-top {
    bottom: calc(100% + v-bind('DROPDOWN_MARGIN_SIZE + "px"'));
    top: unset;
  }

  &--enlarged-top {
    top: calc(100% + 24px);
  }

  :deep() .search-filter {
    &__input {
      margin-top: 12px;
    }

    &__head {
      padding: 0 16px;
    }

    &__item:not(.new-filter-master-checkbox) {
      padding-left: 24px;
      padding-right: 24px;
    }

    &--headless .search-filter__item {
      padding-left: 16px;
      padding-right: 16px;
    }
  }
}

:deep() .input {
  display: block;
  overflow: hidden!important;
  white-space: nowrap;
  text-overflow: ellipsis;
}

:deep() label {
  font-size: 16px;
}

.v-enter-active,
.v-leave-active {
  transition: opacity 0.3s ease-in-out;
}

.v-enter-from,
.v-leave-to {
  opacity: 0;
}
</style>

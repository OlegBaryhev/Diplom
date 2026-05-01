<template>
  <div
    class="search-filter"
    :class="{ 'search-filter--headless': !isHeadVisible }"
  >
    <div
      v-if="isHeadVisible"
      class="search-filter__head"
      :class="{
        'search-filter__head--shadowed': !multi && scrollTop,
        'search-filter__head--flex': isCheckDoublesActive && items && isSearchable
      }"
    >
      <VTabs
        v-if="areTabsVisible"
        v-model="activeTab"
        class="search-filter__tabs"
        primary
        :tabs="tabs"
        @update:model-value="tabChangedHandler"
      />

      <VBtn
        v-if="isCheckDoublesActive && items && !isSearchable"
        class="ml-4 check__doubles__btn"
        outlined
        small
        @click="toggleDoubles"
      >
        Проверка дубликатов
      </VBtn>

      <VSearch
        v-if="isSearchable"
        ref="search"
        v-model="searchQuery"
        :debounced="asyncSearch"
        :input-focus="inputFocus"
        secondary
        sm
        class="search-filter__input"
        :class="{ 'search-filter__input--reduced-margin': isClearButtonVisible || withAddingOnCurrentTab }"
      />
      <button
        v-if="isClearButtonVisible"
        class="search-filter__button"
        type="button"
        @click="clear"
      >
        <span>Очистить поле</span>
      </button>
      <button
        v-if="withAddingOnCurrentTab"
        class="search-filter__button"
        type="button"
        @click="emit('add-new', activeTab)"
      >
        <VIcon
          name="plus"
          class="mr-1 w-[22px] h-[22px]"
        /> <span>Создать новый</span>
      </button>

      <VBtn
        v-if="isCheckDoublesActive && items && isSearchable"
        class="ml-4 check__doubles__btn"
        outlined
        small
        icon="link"
        @click="toggleDoubles"
      />
    </div>

    <div
      v-if="isMenuVisible"
      class="search-filter__menu"
    >
      <DynamicScroller
        ref="scroller"
        :items="items"
        :min-item-size="48"
        class="search-filter__menu-scroller"
        :buffer="300"
        :key-field="primaryKey"
        :[!isPrimitive&&`key`]="primaryKey"
        @visible="emit('list-ready')"
        @[!loading&&`scroll-end`]="getNextPage"
      >
        <template #default="{ item, index, active }">
          <DynamicScrollerItem
            :item="item"
            :active="!!active"
            :size-dependencies="[
              isPrimitive ? item : item[itemName],
            ]"
            :data-index="index"
            :data-active="!!active"
          >
            <div
              class="search-filter__item search-filter__menu-item"
              :class="{
                'search-filter__menu-item--one-selected': !multi && checkMode(isOptionSelected(item)),
                'disabled': getAdditionalData(item)?.disabled,
              }"
              @click="internalModelValue = item"
            >
              <VTooltip
                :show="!!(getAdditionalData(item)?.disabled && getAdditionalData(item)?.tooltipContent)"
                :max-width="getAdditionalData(item)?.tooltipMaxWidth"
                :allow-capturing="true"
                left
                class="items-center w-full"
              >
                <template #default>
                  <span> {{ String(isPrimitive ? item : item[itemName]) }} </span>
                </template>

                <template #content>
                  <div v-html="getAdditionalData(item)?.tooltipContent" />
                </template>
              </VTooltip>
            </div>
          </DynamicScrollerItem>
        </template>
      </DynamicScroller>
    </div>
    <div
      v-if="loading"
      class="search-filter__item justify-center"
    >
      <VLoader small />
    </div>
    <div
      v-else-if="!isMenuVisible && !loading"
      class="search-filter__item"
    >
      <span>Ничего не найдено</span>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { cloneDeep } from 'lodash';

import { api } from '@/api';
import { SAME_MEANING_WORDS_GROUPS } from '@/consts/same-meaning-words-group';
import { OPTION_COUNT_TO_SEARCH } from '@/consts';
import VSearch from '@/common/components/VSearch.vue';

const props = withDefaults(defineProps<{
  modelValue: Record<string, any> | string | number | any[] | null,
  options: any[],
  additionalOptionsData?: any[] | null,
  multi?: boolean,
  mode?: 'include' | 'exclude',
  hasTabs?: boolean,
  filterType?: string,
  prerenderRowsCount?: number,
  loading?: boolean,
  primaryKey?: string,
  showClearButton?: boolean,
  recordsName?: Record<string, any> | string,
  itemName?: string,
  numWords?: any[],
  withAdding?: boolean | any[],
  asyncSearch?: boolean,
  paginatedOptionsUrl?: string | null,
  paginatedSearchPageSize?: number,
  clearable?: boolean,
  offSort?: boolean,
  offShift?: boolean,
  searchValue?: string,
  activeTabOuter?: null | Record<string, any>,
  inputFocus?: boolean,
  category?: string,
}>(), {
  modelValue: null,
  options: () => [],
  additionalOptionsData: () => [],
  mode: 'include',
  prerenderRowsCount: 20,
  loading: false,
  primaryKey: 'value',
  additionalSearchField: '',
  itemName: 'name',
  numWords: () => [],
  withAdding: false,
  paginatedOptionsUrl: null,
  paginatedSearchPageSize: 100,
  offSort: false,
  offShift: false,
  searchValue: '',
  activeTabOuter: null,
});

const search = ref<InstanceType<typeof VSearch> | null>(null);
const serverTotal = ref(0);
const asyncSearchLoading = ref(false);
const asyncMode = ref(props.mode);
const loading = computed(() => props.loading || asyncSearchLoading.value);
const emit = defineEmits([
  'update:modelValue',
  'update:activeTab',
  'update:search',
  'update:mode',
  'update:total',
  'close',
  'add-new',
  'list-ready',
]);
const checkIsAsyncList = computed(() => props.category === 'SearchListAsync');

// eslint-disable-next-line no-bitwise
const checkMode = (value: boolean, mode = 'exclude') => checkIsAsyncList.value ? Boolean(asyncMode.value === mode ^ value) : value;
const internalModelValue = useVModel(props, 'modelValue', emit);

const searchQuery = ref(toRaw(props.searchValue));

const scroller = ref(null);
const { y: scrollTop } = useScroll(scroller);

const isPrimitive = computed(() => {
  const firstOption = props.options?.[0];
  return typeof firstOption === 'string' || typeof firstOption === 'number';
});

const tabChangedHandler = () => {
  search.value.input.input.focus();
};

const isOptionSelected = (option) => {
  if (!props.modelValue) return false;

  if (Array.isArray(props.modelValue)) {
    return props.modelValue.some((item) => isPrimitive.value
      ? item === option
      : item?.[props.primaryKey] === option?.[props.primaryKey]);
  }

  return isPrimitive.value
    ? props.modelValue === option
    : props.modelValue?.[props.primaryKey] === option?.[props.primaryKey];
};

const tabs = computed(() => props.hasTabs && props.options ? props.options.map((option) => ({
  text: option.tabName,
  id: option.tabValue,
})) : null);

const areTabsVisible = computed(() => props.hasTabs && Boolean(tabs.value?.length));

const clear = () => {
  emit('update:modelValue', null);
  internalModelValue.value = Array.isArray(props.modelValue) ? [] : (typeof props.modelValue === 'string' ? '' : null);
};

const getUnshiftedSortedItems = (items) => {
  if (!items) return [];
  const internalItems = [...items];

  if (!props.offSort) {
    internalItems.sort((optionA, optionB) => {
      const optionAText = isPrimitive.value ? optionA : optionA[props.itemName];
      const optionBText = isPrimitive.value ? optionB : optionB[props.itemName];
      if (!optionAText) return;
      return typeof optionAText === 'number'
        ? optionAText > optionBText
        : optionAText.localeCompare(optionBText);
    });
  }

  if (!props.offShift) {
    const itemsToUnshift = [];

    for (let index = 0; index < internalItems.length; index++) {
      const option = internalItems[index];

      if (checkMode(isOptionSelected(option))) {
        itemsToUnshift.push(option);
        internalItems.splice(index--, 1);
      }
    }

    return [...itemsToUnshift, ...internalItems];
  }

  return internalItems;
};

const calculateSortedOptions = () => tabs.value
  ? props.options.map((option) => ({
    ...option,
    items: getUnshiftedSortedItems(option.items),
  }))
  : getUnshiftedSortedItems(props.options);

const sortedOptions = ref();

const activeTab = ref(props.activeTabOuter ?? tabs.value?.[0] ?? null);

watch(() => cloneDeep(props.options), () => {
  sortedOptions.value = calculateSortedOptions();
}, { immediate: true });

watch(() => props.hasTabs, () => {
  sortedOptions.value = calculateSortedOptions();
});

watch(
  () => activeTab.value?.id,
  () => {
    emit('update:activeTab', activeTab.value);

    nextTick(() => {
      props.asyncSearch && emit('update:search', searchQuery.value);
    });
  },
);

const getAdditionalData = (option) =>
  props.additionalOptionsData?.find(
    (additionalOptionsDataItem) =>
      additionalOptionsDataItem?.[props.primaryKey] === option?.[props.primaryKey],
  );

const activeOptions = computed({
  // eslint-disable-next-line arrow-body-style
  get: () => {
    if (!props.hasTabs) return sortedOptions.value;

    if (!activeTab.value) return [];

    const activeTabValue = activeTab.value.id;

    return sortedOptions.value.find((option) => option.tabValue === activeTabValue).items;
  },

  set: (activeOption) => {
    emit('update:activeTab', activeOption);
  },
});

const isSearchable = computed(() => activeOptions.value?.length >= OPTION_COUNT_TO_SEARCH || searchQuery.value);

const toExpandTokens = (tokens) => tokens.map((token) => {
  const sameMeaningWordsGroupsTokenIndex = SAME_MEANING_WORDS_GROUPS
    .findIndex((group) => group
      .includes(token));

  if (sameMeaningWordsGroupsTokenIndex !== -1) {
    return SAME_MEANING_WORDS_GROUPS[sameMeaningWordsGroupsTokenIndex];
  }

  return token;
});

const searchResults = computed(() => {
  if (!isSearchable.value || !searchQuery.value) {
    return null;
  }

  if (props.asyncSearch || props.paginatedOptionsUrl) return activeOptions.value;

  return activeOptions.value.filter((option) => {
    const query = searchQuery.value.trim().toLowerCase();

    const tokens = query
      .replaceAll(/[.,;]/g, ' ')
      .split(/\s+/)
      .map((token) => token
        .trim()
        .toLowerCase())
      .filter(Boolean);

    const expandedTokens = toExpandTokens(tokens);

    if (isPrimitive.value) {
      return expandedTokens.every((token) => Array.isArray(token)
        ? token.some((tokenItem) => String(option).toLowerCase().includes(tokenItem))
        : String(option).toLowerCase().includes(token));
    }

    const nameField = String(option[props.itemName]).toLowerCase();

    return expandedTokens.every((token) => Array.isArray(token)
      ? token.some((tokenItem) => `${nameField}`.includes(tokenItem))
      : `${nameField}`.includes(token));
  });
});

const availableOptions = computed(() => {
  let target;
  Array.isArray(searchResults.value) ? target = searchResults : target = activeOptions;

  return target.value?.filter((option) => !getAdditionalData(option)?.disabled);
});

const items = computed(() => {
  if (props.paginatedOptionsUrl) return activeOptions.value;
  return searchResults.value ?? activeOptions.value;
});

watch([searchResults, activeOptions], () => { scroller.value?.$el.scrollTo({ top: 0 }); });

// eslint-disable-next-line no-bitwise
const isMenuVisible = computed(() => Boolean((props.multi && props.paginatedOptionsUrl) ^ (searchResults.value ?? items.value)?.length));

const allItemsCheckboxChecked = computed(() => availableOptions.value?.every(isOptionSelected));

const withAddingOnCurrentTab = computed(
  () => (props.withAdding === true) || (Array.isArray(props.withAdding) && props.withAdding.includes(activeTab.value.id)),
);

const doesModelValueExist = computed(() => {
  if (Array.isArray(props.modelValue)) {
    return Boolean(props.modelValue.length);
  }

  return typeof props.modelValue === 'number' ? true : Boolean(props.modelValue);
});

const isClearButtonVisible = computed(() => (!props.multi && props.clearable || props.showClearButton) && doesModelValueExist.value);

const isHeadVisible = computed(() => areTabsVisible.value || isSearchable.value
  || withAddingOnCurrentTab.value || isClearButtonVisible.value);

const coincidences = (arr1, arr2, method = 'filter', flag = false) => {
  const strObject = arr1.map((el) => JSON.stringify(el));
  // eslint-disable-next-line no-bitwise
  return arr2?.[method]((obj1) => !!(flag ^ !!(strObject.indexOf(JSON.stringify(obj1)) + 1)));
};

const page = ref(1);
const getNextPage = async () => {
  if (props.paginatedOptionsUrl) {
    if ((page.value - 1) * props.paginatedSearchPageSize > serverTotal.value) return false;
    try {
      asyncSearchLoading.value = true;
      const { data } = await api.post(
        `${window.location.hostname === 'localhost' ? 'https:' : window.location.protocol}//${props.paginatedOptionsUrl}?page=${page.value}&size=${props.paginatedSearchPageSize}`,
        { fulltext: searchQuery.value },
      );
      if (!data || !data.items || data.items?.length === 0) return;
      if (searchQuery.value) {
        emit('update:modelValue', coincidences(props.modelValue, data.items));
      }
      sortedOptions.value.push(...data.items);
      serverTotal.value = data.total;
      page.value++;
    } finally {
      asyncSearchLoading.value = false;
      emit('update:total', serverTotal.value);
    }
  }
};

const setModeValue = (value) => {
  if (!props.paginatedOptionsUrl) return;
  !checkIsAsyncList.value && (asyncMode.value = value ? 'exclude' : 'include');
  emit('update:mode', asyncMode.value);
};

watch(
  searchQuery,
  async () => {
    emit('update:search', searchQuery.value);
    if (props.paginatedOptionsUrl) {
      sortedOptions.value = [];
      page.value = 1;
      await getNextPage();
    }
  },
);

watch(
  allItemsCheckboxChecked,
  setModeValue,
);

watch(
  () => props.mode,
  () => {
    asyncMode.value = props.mode;
  },
  { immediate: true },
);

const total = computed(() => props.paginatedOptionsUrl
  ? serverTotal.value
  : items.value.filter((item) => !getAdditionalData(item)?.disabled).length);

watch(serverTotal, (newVal) => {
  if (!props.paginatedOptionsUrl) return;
  emit('update:total', newVal);
});

getNextPage();

const isCheckDoublesActive = localStorage.getItem('checkDoubles');
</script>

<style scoped lang="scss">
@use '@/assets/mixins';
.search-filter {
  @apply flex flex-col;
  &__head {
    @apply transition-shadow duration-300;
    margin-bottom: 4px;
    &--shadowed {
      box-shadow: 0 9px 6px -6px #6F92B926;
    }
  }

  &__head--flex {
    display: flex;
    align-items: center;
    justify-content: space-between;
    .input__container {
      width: 100%;
    }
  }

  &__tabs {
    margin-bottom: 12px;
    padding: 0 8px;
    flex-shrink: 0;
  }

  &__input {
    margin-bottom: 12px;
    &--reduced-margin {
      margin-bottom: 8px;
    }
  }

  &__button {
    @apply text-base-regular transition-colors;
    height: 48px;
    width: 100%;
    color: theme('colors.main.400');
    display: flex;
    align-items: center;
    &:hover,
    &:focus-visible {
      color: theme('colors.main.500');
    }
  }

  &__item {
    padding: 0 8px;
    min-height: 40px;
    display: flex;
    align-items: center;
    width: 100%;
  }

  &__menu {
    overflow: hidden;
    display: flex;
    flex-direction: column;
    &-scroller {
      @include mixins.scrollbar;
      overscroll-behavior: contain;
    }
    &-item {
      content-visibility: auto;
      color: theme('colors.additional.DEFAULT');
      cursor: pointer;
      user-select: none;
      transition: color .3s ease-in-out;
      &.disabled {
        cursor: default;
      }
      &--one-selected {
        background-color: theme('colors.main.50');
      }
      &:hover {
        &:not(.disabled) {
          color: theme('colors.main.400') !important;
        }
      }
      &:active:not(.disabled) {
        background-color: theme('colors.main.50');
      }
      .checkbox {
        margin: 0 -8px;
        padding: 8px;
        width: calc(100% + 16px);
      }
    }
  }

  .check__doubles__btn {
    background: #fff;
    transition: all 0.3s ease;
    box-shadow: 0px -5px 9px 4px rgb(255 0 174 / 18%), 0px 5px 9px 5px rgb(0 25 255 / 18%);
    margin: 0px 8px 12px;
  }
}
</style>

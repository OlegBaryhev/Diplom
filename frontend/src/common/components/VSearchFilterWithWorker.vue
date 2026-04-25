<template>
  <div
    class="search-filter"
    :class="{ 'search-filter--headless': !isSearchable }"
  >
    <div
      v-if="isSearchable"
      class="search-filter__head"
      :class="{
        'search-filter__head--shadowed': scrollTop && !loading && (searchResults ?? optionsWithSelection)?.length > 0,
        'search-filter__head--flex': isCheckDoublesActive && items && isSearchable
      }"
    >
      <VSearch
        ref="search"
        v-model="searchQuery"
        debounced
        :input-focus="inputFocus"
        secondary
        sm
        class="search-filter__input"
      />

      <div
        v-show="!loading && (searchResults ?? optionsWithSelection)?.length >= OPTION_COUNT_TO_SHOW_MASTER_CHECKBOX"
        class="search-filter__item search-filter__menu-item new-filter-master-checkbox"
      >
        <VCheckbox
          class="search-filter--new__checkbox"
          :model-value="allItemsCheckboxStates.checked"
          :indeterminate="allItemsCheckboxStates.indeterminate"
          :label="`Выбрать все (${total})`"
          :readonly="isSelectAllLoading || setItemsStateLoading"
          :loading="isSelectAllLoading"
          data-test="select-all"
          @update:model-value="!!searchResults ? setStatesToAll($event) : cacheAllStates($event); searchResults && (searchResultToUpdate = true)"
        />
      </div>
    </div>

    <div
      class="search-filter__menu"
    >
      <div
        v-if="asyncSearchLoading || loading"
        class="search-filter__item justify-center"
      >
        <VLoader small />
      </div>
      <div
        v-else-if="(searchResults ?? optionsWithSelection)?.length > 0"
        v-scroll
        class="search-filter__wrapper relative h-full"
        :class="{ 'pointer-events-none': isSelectAllLoading || setItemsStateLoading }"
      >
        <VirtualList
          ref="scroller"
          :items="searchResults ?? optionsWithSelection ?? []"
          :item-size="itemsMinHeight"
          :default-scroll-key="primaryKey"
          item-resizable
          class="search-filter__menu-scroller"
          @scroll="onScroll"
        >
          <template #default="{ item }">
            <div
              class="search-filter__item search-filter__menu-item"
            >
              <VCheckbox
                v-model="item.selected"
                @update:model-value="handleOptionClick($event, item)"
              >
                <template #default>
                  <span class="search-filter__item-label">{{ isPrimitive ? item : item[itemName] }}</span>
                </template>
              </VCheckbox>
            </div>
          </template>
        </VirtualList>
        <div
          v-if="setItemsStateLoading"
          class="search-filter__item absolute w-full h-40px z-10 bottom-0 bg-white justify-center"
        >
          <VLoader small />
        </div>
      </div>
      <div
        v-else
        class="search-filter__item"
      >
        <span>Ничего не найдено</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { cloneDeep, omit, debounce } from 'lodash';
import { VirtualList } from 'vueuc';
import { OverlayScrollbars } from 'overlayscrollbars';
import {
  OPTION_COUNT_TO_SHOW_MASTER_CHECKBOX,
  OPTION_COUNT_TO_SEARCH,
} from '@/consts';
import { SAME_MEANING_WORDS_GROUPS } from '@/consts/same-meaning-words-group';
import { api } from '@/api';

interface IMasterCheckbox {
  checked: boolean,
  indeterminate: boolean,
}

const worker = new Worker(new URL('@/common/workers/filter.worker.ts', import.meta.url), { type: 'module' });

const props = withDefaults(defineProps<{
  modelValue?: object | string | number | any[] | null;
  options?: any[];
  loading?: boolean;
  primaryKey?: string;
  itemName?: string;
  searchValue?: string;
  inputFocus?: boolean;
  itemsMinHeight?: number;
  symbolsToSearch?: number;
  paginatedSearchPageSize?: number,
  paginatedOptionsUrl?: string | null,
}>(), {
  modelValue: null,
  options: () => [],
  loading: false,
  primaryKey: 'value',
  itemName: 'name',
  searchValue: '',
  inputFocus: false,
  itemsMinHeight: 40,
  paginatedSearchPageSize: 1_000_000_000,
  symbolsToSearch: 1, // SYMBOLS_COUNT_TO_SEARCH
  paginatedOptionsUrl: null,
});

const scroller = ref();

const search = ref(null);
const serverTotal = ref<number>(0);
const abortController = ref<AbortController | null>(null);

const scrollTop = ref<number>(0);

const onScroll = () => {
  if (!scroller.value) return;
  scrollTop.value = scroller.value?.listElRef?.scrollTop;
};

const setItemsStateLoading = ref<boolean>(false);
const isSelectAllLoading = ref<boolean>(false);

const vScroll = {
  mounted: (el: HTMLElement) => {
    OverlayScrollbars({
      target: el,
      elements: {
        viewport: scroller.value.$el.nextSibling,
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

const emit = defineEmits([
  'update:modelValue',
  'update:search',
  'update:total',
  'close',
  'list-ready',
]);

const searchQuery = ref<string>(unref(props.searchValue));
const searchLoading = ref<boolean>(false);

const asyncSearchLoading = ref<boolean>(false);
const asyncOptions = ref<any[] | null>(null);
const currentOptionsList = computed(() => props.paginatedOptionsUrl ? asyncOptions.value : props.options);

const isPrimitive = computed(() => ['string', 'number'].includes(typeof currentOptionsList.value?.[0]));

const searchResults = ref<null | any[]>(null);
const optionsWithSelection = ref([]);

const searchResultToUpdate = ref<boolean>(false);

const handleOptionClick = (isSelected: boolean, item: any) => {
  if (!(props.modelValue instanceof Array)) return;

  const newModelValue = isSelected
    ? [...props.modelValue, item]
    : props.modelValue.filter((option) => option.value !== item.value);

  if (searchResults.value && searchResults.value.length > 0) {
    searchResultToUpdate.value = true;
  }
  emit('update:modelValue', newModelValue);
};

const mapOptionsWithSelection = (isReload: boolean = false, options: null | any[] = currentOptionsList.value) => {
  if (props.modelValue?.length === 0) {
    optionsWithSelection.value = options;
  }

  if (isReload) searchLoading.value = true;
  else setItemsStateLoading.value = true;

  worker.postMessage({
    type: 'mapOptionsWithSelection',
    options: cloneDeep(unref(options)),
    modelValue: cloneDeep(props.modelValue),
    isSearch: isReload,
  });
};

const getAsyncOptionsList = async (): Promise<void> => {
  if (!props.paginatedOptionsUrl) return;

  asyncSearchLoading.value = true;
  try {
    if (abortController.value) {
      abortController.value?.abort();
    } else {
      abortController.value = new AbortController();
    }

    const request = await api.post(
      `${window.location.hostname === 'localhost' ? 'https:' : window.location.protocol}//${props.paginatedOptionsUrl}?page=1&size=${props.paginatedSearchPageSize}`,
      { fulltext: '' },
      {
        signal: abortController.value?.signal,
      },
    );

    if (!request || !request?.data) return;

    const { data } = request;

    if (!data?.items?.length) return;

    asyncOptions.value = data.items;
    mapOptionsWithSelection(true);
  } finally {
    asyncSearchLoading.value = false;
  }
};

const defaultOptionsInit = (): void => {
  props.paginatedOptionsUrl ? getAsyncOptionsList() : mapOptionsWithSelection(true);
};

defaultOptionsInit();

const isSearchable = computed(() => (searchResults.value ?? optionsWithSelection.value)?.length >= OPTION_COUNT_TO_SEARCH
  || searchLoading.value || searchQuery.value.length);

const startSearch = debounce(async (): Promise<void> => {
  searchLoading.value = true;

  worker.postMessage({
    type: 'simpleSearch',
    items: cloneDeep(unref(optionsWithSelection.value)),
    searchQuery: searchQuery.value,
    mapModelValue: cloneDeep(props.modelValue),
    synonyms: SAME_MEANING_WORDS_GROUPS,
    fieldToSearch: props.itemName,
  });
}, 100);

watch(
  () => searchQuery.value,
  async () => {
    emit('update:search', searchQuery.value);

    if (searchQuery.value.length >= props.symbolsToSearch) {
      startSearch();
      return;
    }

    if (searchResultToUpdate.value) {
      mapOptionsWithSelection(true);
      searchResultToUpdate.value = false;
      return;
    }

    searchResults.value = null;

    await nextTick();
    searchLoading.value = false;
  },
  { deep: true },
);

const allItemsCheckboxStates = computed<IMasterCheckbox>(() => {
  const listToCheck = searchResults.value ?? optionsWithSelection.value;

  const output = {
    checked: false,
    indeterminate: false,
  };

  let isException = false;
  // eslint-disable-next-line no-restricted-syntax
  for (const option of listToCheck) {
    if (isException && option?.selected) {
      output.checked = false;
      output.indeterminate = true;
      break;
    } else if (option?.selected) {
      output.checked = true;
      output.indeterminate = true;
    } else {
      output.checked = false;
      if (output.indeterminate) break;
      else isException = true;
    }
  }
  output.checked && (output.indeterminate = false);
  return output;
});

const cashedOptionsSelectionValues = ref<
  {
    allSelected: any[],
    allUnselected: any[],
  }
>({
  allSelected: [],
  allUnselected: [],
});

const setStatesToAll = (checked: boolean = true) => {
  isSelectAllLoading.value = true;

  worker.postMessage({
    type: 'setStatesToAll',
    flag: checked,
    modelValue: cloneDeep(props.modelValue),
    options: cloneDeep(searchResults.value),
  });
};

const setOptionsSelectedByFlag = async (checked: boolean = true, changeModelValue: boolean = true) => {
  const selectedValue = cashedOptionsSelectionValues.value?.[checked ? 'allSelected' : 'allUnselected'];
  if (!selectedValue?.length) return;
  optionsWithSelection.value = cloneDeep(selectedValue);
  changeModelValue && emit('update:modelValue', checked ? selectedValue : []);
  if (searchResults.value) {
    setStatesToAll(false);
    return;
  }

  await nextTick();
  setItemsStateLoading.value = false;
  isSelectAllLoading.value = false;
};

const cacheAllStates = (checked: boolean = true, isExternal: boolean = false) => {
  isExternal ? setItemsStateLoading.value = true : isSelectAllLoading.value = true;

  if (!cashedOptionsSelectionValues.value?.allSelected?.length
    && !cashedOptionsSelectionValues.value?.allUnselected?.length) {
    worker.postMessage({
      type: 'cacheAllStates',
      flag: checked,
      options: cloneDeep(optionsWithSelection.value),
    });
    return;
  }

  setOptionsSelectedByFlag(checked);
};

const modificateForModelValue = (arr: any[]) => arr && arr?.length ? arr?.reduce((acc, val) => {
  val.selected && acc.push(val);
  return acc;
}, []) : [];

const initWorkersEvents = async (): Promise<void> => {
  worker.onmessage = async (event): Promise<void> => {
    const { type, result } = event.data;

    const currentResult = result ?? [];

    if (type === 'cacheAllStates') {
      const omitedResult = omit(result, 'flag');
      cashedOptionsSelectionValues.value.allSelected = omitedResult.allSelected;
      cashedOptionsSelectionValues.value.allUnselected = omitedResult.allUnselected;
      setOptionsSelectedByFlag(currentResult.flag);

      await nextTick();
      isSelectAllLoading.value = false;
      setItemsStateLoading.value = false;

      return;
    }

    if (type === 'simpleSearch') {
      searchResultToUpdate.value = true; // @todo Добавить сравнение?
      searchResults.value = currentResult;

      await nextTick();
      searchLoading.value = false;

      return;
    }

    if (type === 'setStatesToAll') {
      searchResults.value = result.options;
      emit('update:modelValue', modificateForModelValue(result.modelValue));

      await nextTick();
      setItemsStateLoading.value = false;
      isSelectAllLoading.value = false;

      return;
    }

    if (type === 'mapOptionsWithSelection') {
      optionsWithSelection.value = result.options;
      emit('update:modelValue', modificateForModelValue(result.options));

      await nextTick();
      if (result.isSearch) {
        searchLoading.value = false;
        searchResults.value = null;
      } else setItemsStateLoading.value = false;

      return;
    }

    optionsWithSelection.value = currentResult;
    emit('update:modelValue', modificateForModelValue(currentResult));
    await nextTick();
    setItemsStateLoading.value = false;
    isSelectAllLoading.value = false;
  };

  worker.onerror = (err) => {
    console.error('Ошибка WebWorker:', err);
    setItemsStateLoading.value = false;
    searchLoading.value = false;
  };
};

initWorkersEvents();

const total = computed(() => (searchResults.value ?? optionsWithSelection.value)?.length);

watch(
  serverTotal,
  (newVal) => {
    emit('update:total', newVal);
  },
);

const clearFilterOptions = debounce(() => {
  cacheAllStates(false, true);
}, 250);

const loading = computed<boolean>(() => props.loading || searchLoading.value);

defineExpose({ clearFilterOptions });

const isCheckDoublesActive = localStorage.getItem('checkDoubles');

onUnmounted(() => {
  emit('update:search', '');
  abortController.value?.abort();
  worker.terminate();
});
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

    &__menu-scroller {
      & :deep() {
        .os-viewport  {
          overscroll-behavior: none;
        }
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

    &__item-label {
      position: relative;
      word-wrap: break-word;
      overflow-wrap: break-word;
      white-space: pre;
      overflow-wrap: anywhere;
      text-wrap: balance;
      max-width: min-content;
      width: min-content;
    }

    &__menu {
      overflow: hidden;
      display: flex;
      flex-direction: column;

      &-scroller{
        -ms-overflow-style: none;
        scrollbar-width: none;

        &::-webkit-scrollbar {
          display: none;
        }

        &:deep() .v-vl-visible-items {
          min-height: max(800px, 100%);
        }
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
          font-size: 10px;
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

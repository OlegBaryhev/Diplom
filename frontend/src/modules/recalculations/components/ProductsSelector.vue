<!-- eslint-disable no-lonely-if -->
<template>
  <div class="products-selector">
    <div class="products-selector__selection-type">
      <VRadio
        v-model="internalSelectionType"
        value="all"
        name="sel-type"
        label="Все товары"
        @update:model-value="onSelectionTypeChange"
      />
      <VRadio
        v-model="internalSelectionType"
        value="groups"
        name="sel-type"
        label="По группам"
        @update:model-value="onSelectionTypeChange"
      />
      <VRadio
        v-model="internalSelectionType"
        value="individual"
        name="sel-type"
        label="Точечно"
        @update:model-value="onSelectionTypeChange"
      />
    </div>

    <template v-if="internalSelectionType === 'all'">
      <p class="products-selector__all-notice">
        Перерасчет будет применён ко всем товарам в системе
      </p>
    </template>

    <template v-else-if="internalSelectionType === 'groups'">
      <div class="products-selector__tabs">
        <button
          v-for="tab in GROUP_TABS"
          :key="tab.value"
          class="products-selector__tab"
          :class="{ 'products-selector__tab--active': activeTab === tab.value }"
          type="button"
          @click="activeTab = tab.value"
        >
          {{ tab.label }}
        </button>
      </div>

      <div
        v-if="activeTab === 'categories'"
        class="products-selector__list"
      >
        <VInput
          v-model="categorySearch"
          label="Поиск"
          sm
          secondary
          class="mb-3"
        />
        <div class="products-selector__items">
          <label
            v-for="cat in filteredCategories"
            :key="cat.id"
            class="products-selector__item"
          >
            <input
              type="checkbox"
              class="products-selector__checkbox"
              :checked="selectedCategoryIds.has(cat.id)"
              @change="toggleCategory(cat.id)"
            >
            <span class="products-selector__item-name">{{ cat.name }}</span>
          </label>
          <p
            v-if="!filteredCategories.length && !loading"
            class="products-selector__empty"
          >
            Ничего не найдено
          </p>
        </div>
      </div>

      <div
        v-else-if="activeTab === 'brands'"
        class="products-selector__list"
      >
        <VInput
          v-model="brandSearch"
          label="Поиск"
          sm
          secondary
          class="mb-3"
        />
        <div class="products-selector__items">
          <label
            v-for="brand in filteredBrands"
            :key="brand.id"
            class="products-selector__item"
          >
            <input
              type="checkbox"
              class="products-selector__checkbox"
              :checked="selectedBrandIds.has(brand.id)"
              @change="toggleBrand(brand.id)"
            >
            <span class="products-selector__item-name">{{ brand.name }}</span>
          </label>
          <p
            v-if="!filteredBrands.length && !loading"
            class="products-selector__empty"
          >
            Ничего не найдено
          </p>
        </div>
      </div>
    </template>

    <template v-else-if="internalSelectionType === 'individual'">
      <div class="products-selector__list">
        <VInput
          v-model="productSearch"
          label="Поиск товаров"
          sm
          secondary
          class="mb-3"
        />

        <label class="products-selector__item products-selector__item--master">
          <input
            type="checkbox"
            class="products-selector__checkbox"
            :checked="masterState === 'all'"
            :indeterminate="masterState === 'partial'"
            @change="toggleMaster"
          >
          <span class="products-selector__item-name products-selector__item-name--bold">
            Выбрать все
          </span>
        </label>

        <div class="products-selector__divider" />

        <div class="products-selector__items">
          <label
            v-for="product in filteredProducts"
            :key="product.id"
            class="products-selector__item"
          >
            <input
              type="checkbox"
              class="products-selector__checkbox"
              :checked="isProductChecked(product.id)"
              @change="toggleProduct(product.id)"
            >
            <span class="products-selector__item-name">{{ product.name }}</span>
            <span
              v-if="product.category"
              class="products-selector__item-meta"
            >{{ product.category.name }}</span>
          </label>

          <p
            v-if="!filteredProducts.length && !loading"
            class="products-selector__empty"
          >
            Ничего не найдено
          </p>
        </div>
      </div>
    </template>
  </div>
</template>

<script lang="ts" setup>
import { getCategoriesRequest, getBrandsRequest, getProductsRequest } from '@/modules/products/api';
import type { ProductSelection, SelectionType } from '@/modules/recalculations/types';

const props = withDefaults(defineProps<{
  modelValue: ProductSelection;
}>(), {});

// eslint-disable-next-line func-call-spacing, no-spaced-func
const emit = defineEmits<{
  (evt: 'update:modelValue', val: ProductSelection): void;
}>();

const GROUP_TABS = [
  { value: 'categories', label: 'Категории' },
  { value: 'brands', label: 'Бренды' },
] as const;

type GroupTab = typeof GROUP_TABS[number]['value'];

const activeTab = ref<GroupTab>('categories');
const loading = ref(false);
const productSearch = ref('');
const categorySearch = ref('');
const brandSearch = ref('');

const allProducts = ref<any[]>([]);
const allCategories = ref<any[]>([]);
const allBrands = ref<any[]>([]);

const internalSelectionType = ref<SelectionType>(props.modelValue.selection_type ?? 'all');
const individualMode = ref<'include' | 'exclude'>(props.modelValue.mode ?? 'include');
const individualIds = ref<Set<number>>(new Set(props.modelValue.product_ids ?? []));
const selectedCategoryIds = ref<Set<number>>(new Set(props.modelValue.category_ids ?? []));
const selectedBrandIds = ref<Set<number>>(new Set(props.modelValue.brand_ids ?? []));

const fetchData = async () => {
  loading.value = true;
  try {
    const [catRes, brandRes, prodRes] = await Promise.all([
      getCategoriesRequest(),
      getBrandsRequest(),
      getProductsRequest({ page: 1, page_size: 500 }),
    ]);
    allCategories.value = catRes.data ?? [];
    allBrands.value = brandRes.data ?? [];
    allProducts.value = prodRes.data?.items ?? [];
  } catch (err) {
    console.error(err);
  } finally {
    loading.value = false;
  }
};

fetchData();

const filteredProducts = computed(() => allProducts.value.filter(
  (p) => !productSearch.value || p.name.toLowerCase().includes(productSearch.value.toLowerCase()),
));

const filteredCategories = computed(() => allCategories.value.filter(
  (c) => !categorySearch.value || c.name.toLowerCase().includes(categorySearch.value.toLowerCase()),
));

const filteredBrands = computed(() => allBrands.value.filter(
  (b) => !brandSearch.value || b.name.toLowerCase().includes(brandSearch.value.toLowerCase()),
));

const isProductChecked = (id: number): boolean => {
  if (individualMode.value === 'include') return individualIds.value.has(id);
  return !individualIds.value.has(id);
};

const masterState = computed((): 'all' | 'none' | 'partial' => {
  const ids = filteredProducts.value.map((p) => p.id);
  if (!ids.length) return 'none';
  if (ids.every((id) => isProductChecked(id))) return 'all';
  if (ids.every((id) => !isProductChecked(id))) return 'none';
  return 'partial';
});

const emitChange = () => {
  emit('update:modelValue', {
    selection_type: internalSelectionType.value,
    mode: individualMode.value,
    product_ids: Array.from(individualIds.value),
    category_ids: Array.from(selectedCategoryIds.value),
    brand_ids: Array.from(selectedBrandIds.value),
  });
};

const onSelectionTypeChange = (val: SelectionType) => {
  if (val === 'groups') {
    activeTab.value = 'categories';
  }
  emitChange();
};

const toggleProduct = (id: number) => {
  const allIds = filteredProducts.value.map((p) => p.id);
  const wasChecked = isProductChecked(id);

  if (individualMode.value === 'include') {
    if (wasChecked) {
      individualIds.value.delete(id);
    } else {
      individualIds.value.add(id);
      if (allIds.every((i) => individualIds.value.has(i))) {
        individualMode.value = 'exclude';
        individualIds.value = new Set();
      }
    }
  } else if (wasChecked) {
    individualIds.value.add(id);
    if (allIds.every((i) => individualIds.value.has(i))) {
      individualMode.value = 'include';
      individualIds.value = new Set();
    }
  } else {
    individualIds.value.delete(id);
  }

  emitChange();
};

const toggleMaster = () => {
  if (masterState.value === 'all') {
    individualMode.value = 'include';
    individualIds.value = new Set();
  } else {
    individualMode.value = 'exclude';
    individualIds.value = new Set();
  }
  emitChange();
};

const toggleCategory = (id: number) => {
  if (selectedCategoryIds.value.has(id)) {
    selectedCategoryIds.value.delete(id);
  } else {
    selectedCategoryIds.value.add(id);
  }
  emitChange();
};

const toggleBrand = (id: number) => {
  if (selectedBrandIds.value.has(id)) {
    selectedBrandIds.value.delete(id);
  } else {
    selectedBrandIds.value.add(id);
  }
  emitChange();
};

watch(
  () => props.modelValue,
  (val) => {
    internalSelectionType.value = val.selection_type ?? 'all';
    individualMode.value = val.mode ?? 'include';
    individualIds.value = new Set(val.product_ids ?? []);
    selectedCategoryIds.value = new Set(val.category_ids ?? []);
    selectedBrandIds.value = new Set(val.brand_ids ?? []);
  },
  { deep: true },
);
</script>

<style lang="scss" scoped>
.products-selector {
  display: flex;
  flex-direction: column;
  gap: 12px;

  &__selection-type {
    display: flex;
    gap: 16px;
    flex-wrap: wrap;
  }

  &__all-notice {
    @apply text-sm-regular;
    color: theme('colors.additional.300');
    padding: 8px 12px;
    background: theme('colors.main.50');
    border-radius: 6px;
  }

  &__tabs {
    display: flex;
    gap: 0;
    border-bottom: 1px solid theme('colors.main.100');
  }

  &__tab {
    @apply text-sm-medium;
    padding: 6px 14px;
    color: theme('colors.additional.300');
    border-bottom: 2px solid transparent;
    margin-bottom: -1px;
    background: none;
    cursor: pointer;
    transition: color 0.15s, border-color 0.15s;

    &--active {
      color: theme('colors.main.400');
      border-bottom-color: theme('colors.main.400');
    }
  }

  &__list {
    display: flex;
    flex-direction: column;
  }

  &__divider {
    height: 1px;
    background: theme('colors.main.100');
    margin: 4px 0;
  }

  &__items {
    max-height: 220px;
    overflow-y: auto;
    display: flex;
    flex-direction: column;
  }

  &__item {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 7px 4px;
    cursor: pointer;
    border-radius: 4px;
    transition: background 0.1s;

    &:hover {
      background: theme('colors.main.50');
    }

    &--master {
      padding: 6px 4px 8px;
    }
  }

  &__checkbox {
    width: 15px;
    height: 15px;
    flex-shrink: 0;
    cursor: pointer;
    accent-color: theme('colors.main.400');
  }

  &__item-name {
    @apply text-sm-regular;
    color: theme('colors.black');
    flex: 1;
    min-width: 0;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;

    &--bold {
      @apply text-sm-medium;
    }
  }

  &__item-meta {
    @apply text-xs-regular;
    color: theme('colors.additional.300');
    flex-shrink: 0;
  }

  &__empty {
    @apply text-sm-regular;
    color: theme('colors.additional.300');
    text-align: center;
    padding: 12px 0;
  }
}
</style>

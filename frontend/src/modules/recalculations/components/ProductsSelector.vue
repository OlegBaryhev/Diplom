<!-- eslint-disable no-lonely-if -->
<template>
  <div class="products-selector">
    <div class="products-selector__tabs">
      <button
        v-for="tab in TABS"
        :key="tab.value"
        class="products-selector__tab"
        :class="{ 'products-selector__tab--active': activeTab === tab.value }"
        type="button"
        @click="activeTab = tab.value"
      >
        {{ tab.label }}
      </button>
    </div>

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
      <div
        v-if="activeTab === 'categories'"
        class="products-selector__list"
      >
        <div class="products-selector__search">
          <VInput
            v-model="categorySearch"
            label="Поиск категорий"
            sm
            secondary
          />
        </div>
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
            <span>{{ cat.name }}</span>
          </label>
        </div>
      </div>

      <div
        v-else-if="activeTab === 'brands'"
        class="products-selector__list"
      >
        <div class="products-selector__search">
          <VInput
            v-model="brandSearch"
            label="Поиск брендов"
            sm
            secondary
          />
        </div>
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
            <span>{{ brand.name }}</span>
          </label>
        </div>
      </div>
    </template>

    <template v-else-if="internalSelectionType === 'individual'">
      <div class="products-selector__list">
        <div class="products-selector__search">
          <VInput
            v-model="productSearch"
            label="Поиск товаров"
            sm
            secondary
          />
        </div>

        <div class="products-selector__master-row">
          <button
            type="button"
            class="products-selector__master-checkbox-btn"
            :title="masterTitle"
            @click="toggleMaster"
          >
            <span
              class="products-selector__master-icon"
              :class="`products-selector__master-icon--${masterState}`"
            />
            <span class="products-selector__master-label">{{ masterTitle }}</span>
          </button>

          <span class="products-selector__mode-badge">
            {{ individualMode === 'include' ? 'include' : 'exclude' }}
          </span>
        </div>

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
            <span class="products-selector__product-name">{{ product.name }}</span>
            <span
              v-if="product.category"
              class="products-selector__product-meta"
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

const TABS = [
  { value: 'products', label: 'Товары' },
  { value: 'categories', label: 'Категории' },
  { value: 'brands', label: 'Бренды' },
] as const;

type TabValue = typeof TABS[number]['value'];

const activeTab = ref<TabValue>('products');
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

const filteredProducts = computed(() =>
  allProducts.value.filter((p) =>
    !productSearch.value || p.name.toLowerCase().includes(productSearch.value.toLowerCase())));

const filteredCategories = computed(() => allCategories.value.filter((c) => !categorySearch.value || c.name.toLowerCase().includes(categorySearch.value.toLowerCase())));

const filteredBrands = computed(() => allBrands.value.filter((b) => !brandSearch.value || b.name.toLowerCase().includes(brandSearch.value.toLowerCase())));

const isProductChecked = (id: number): boolean => {
  if (individualMode.value === 'include') return individualIds.value.has(id);
  return !individualIds.value.has(id);
};

const masterState = computed((): 'all' | 'none' | 'partial' => {
  const ids = filteredProducts.value.map((p) => p.id);
  if (!ids.length) return 'none';
  const allChecked = ids.every((id) => isProductChecked(id));
  if (allChecked) return 'all';
  const noneChecked = ids.every((id) => !isProductChecked(id));
  if (noneChecked) return 'none';
  return 'partial';
});

const masterTitle = computed(() => {
  if (masterState.value === 'all') return 'Все выбраны';
  if (masterState.value === 'none') return 'Ничего не выбрано';
  return 'Выбраны некоторые';
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

const onSelectionTypeChange = () => {
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
  } else {
    // eslint-disable-next-line no-lonely-if
    if (wasChecked) {
      individualIds.value.add(id);
      if (allIds.every((i) => individualIds.value.has(i))) {
        individualMode.value = 'include';
        individualIds.value = new Set();
      }
    } else {
      individualIds.value.delete(id);
    }
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

  &__tabs {
    display: flex;
    gap: 4px;
    border-bottom: 1px solid theme('colors.main.100');
  }

  &__tab {
    @apply text-sm-medium;
    padding: 6px 12px;
    color: theme('colors.additional.300');
    border-bottom: 2px solid transparent;
    transition: color 0.15s, border-color 0.15s;
    margin-bottom: -1px;
    background: none;
    cursor: pointer;

    &--active {
      color: theme('colors.main.400');
      border-bottom-color: theme('colors.main.400');
    }
  }

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

  &__list {
    display: flex;
    flex-direction: column;
    gap: 8px;
  }

  &__search {
    flex-shrink: 0;
  }

  &__master-row {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 6px 0;
    border-bottom: 1px solid theme('colors.main.100');
  }

  &__master-checkbox-btn {
    display: flex;
    align-items: center;
    gap: 6px;
    background: none;
    border: none;
    cursor: pointer;
    padding: 0;
  }

  &__master-icon {
    width: 16px;
    height: 16px;
    border: 2px solid theme('colors.main.300');
    border-radius: 3px;
    flex-shrink: 0;
    position: relative;

    &--all {
      background: theme('colors.main.400');
      border-color: theme('colors.main.400');

      &::after {
        content: '';
        position: absolute;
        left: 2px;
        top: -1px;
        width: 8px;
        height: 5px;
        border-left: 2px solid white;
        border-bottom: 2px solid white;
        transform: rotate(-45deg);
      }
    }

    &--partial {
      &::after {
        content: '';
        position: absolute;
        left: 2px;
        top: 5px;
        width: 8px;
        height: 2px;
        background: theme('colors.main.400');
      }
    }
  }

  &__master-label {
    @apply text-sm-medium;
    color: theme('colors.additional.DEFAULT');
  }

  &__mode-badge {
    @apply text-xs-medium;
    margin-left: auto;
    padding: 2px 8px;
    border-radius: 4px;
    background: theme('colors.main.50');
    color: theme('colors.main.400');
  }

  &__items {
    max-height: 240px;
    overflow-y: auto;
    display: flex;
    flex-direction: column;
    gap: 4px;
    padding-right: 4px;
  }

  &__item {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 6px 8px;
    border-radius: 4px;
    cursor: pointer;
    transition: background 0.1s;

    &:hover {
      background: theme('colors.main.50');
    }
  }

  &__checkbox {
    width: 16px;
    height: 16px;
    cursor: pointer;
    flex-shrink: 0;
    accent-color: theme('colors.main.400');
  }

  &__product-name {
    @apply text-sm-regular;
    color: theme('colors.black');
    flex: 1;
    min-width: 0;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  &__product-meta {
    @apply text-xs-regular;
    color: theme('colors.additional.300');
    flex-shrink: 0;
  }

  &__empty {
    @apply text-sm-regular;
    color: theme('colors.additional.300');
    text-align: center;
    padding: 16px 0;
  }
}
</style>

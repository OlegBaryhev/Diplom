<template>
  <!-- Фото -->
  <VTableCell data-test="product-image">
    <VExpandedPhoto :images="item.images ?? []">
      <div class="product-thumbnail">
        <img
          v-if="primaryImage && !thumbError"
          :src="fullUrl(primaryImage.url)"
          :alt="item.name"
          class="product-thumbnail__img"
          @error="thumbError = true"
        >
        <div
          v-else
          class="product-thumbnail__placeholder"
        >
          <VIcon
            name="photo"
            class="product-thumbnail__icon"
          />
        </div>
      </div>
    </VExpandedPhoto>
  </VTableCell>

  <!-- Наименование -->
  <VTableCell data-test="product-name">
    {{ item?.name }}
  </VTableCell>

  <!-- Описание -->
  <VTableCell data-test="product-description">
    {{ item?.description }}
  </VTableCell>

  <!-- Категория -->
  <VTableCell data-test="product-category">
    {{ item?.category?.name }}
  </VTableCell>

  <!-- Бренд -->
  <VTableCell data-test="product-brand">
    {{ item?.brand?.name }}
  </VTableCell>

  <!-- Скидка -->
  <VTableCell data-test="product-discount">
    <span
      v-if="item.discount > 0"
      class="discount-badge"
    >
      {{ item.discount }}%
    </span>
    <span
      v-else
      class="text-additional-300"
    >—</span>
  </VTableCell>

  <!-- Цена -->
  <VTableCell data-test="product-price">
    <template v-if="item.discount > 0">
      <div class="price-with-discount">
        <span class="price-with-discount__old">{{ formatMoney(item.price) }}</span>
        <span class="price-with-discount__new">{{ formatMoney(discountedPrice) }}</span>
      </div>
    </template>
    <template v-else>
      {{ formatMoney(item?.price) }}
    </template>
  </VTableCell>
</template>

<script lang="ts" setup>
import type { Product } from '../types';
import { formatMoney, calcDiscountedPrice } from '@/common/utils/format';
import { REMOTE_SERVER_URL } from '@/consts';
import VExpandedPhoto from '@/common/components/VExpandedPhoto.vue';

const props = defineProps<{ item: Product }>();

const thumbError = ref(false);

const primaryImage = computed(() => props.item.images?.find((img) => img.is_primary) ?? props.item.images?.[0] ?? null);

const discountedPrice = computed(() => calcDiscountedPrice(props.item.price, props.item.discount));

const fullUrl = (url: string) => (url.startsWith('http') ? url : `${REMOTE_SERVER_URL}${url}`);

watch(() => props.item.images, () => { thumbError.value = false; });
</script>

<style lang="scss" scoped>
.product-thumbnail {
  width: 36px;
  height: 36px;
  border-radius: 6px;
  overflow: hidden;
  flex-shrink: 0;

  &__img {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }

  &__placeholder {
    width: 100%;
    height: 100%;
    background: theme('colors.main.100');
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 6px;
  }

  &__icon {
    width: 18px;
    height: 18px;
    color: theme('colors.additional.200');
  }
}

.discount-badge {
  display: inline-block;
  background: #FFF3C4;
  color: #7A5F00;
  border-radius: 6px;
  padding: 2px 8px;
  font-size: 12px;
  font-weight: 500;
}

.price-with-discount {
  display: flex;
  flex-direction: column;
  gap: 1px;

  &__old {
    font-size: 11px;
    color: theme('colors.additional.300');
    text-decoration: line-through;
    text-decoration-color: #dc2626;
    line-height: 1.3;
  }

  &__new {
    font-size: 13px;
    font-weight: 500;
    background: #FFF3C4;
    color: #7A5F00;
    border-radius: 5px;
    padding: 1px 6px;
    display: inline-block;
  }
}
</style>

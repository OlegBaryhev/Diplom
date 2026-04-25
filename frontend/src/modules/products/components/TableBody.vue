<template>
  <VTableCell data-test="product-name">
    {{ item?.name }}
  </VTableCell>

  <VTableCell data-test="product-description">
    {{ item?.description }}
  </VTableCell>

  <VTableCell data-test="product-category">
    {{ item?.category?.name }}
  </VTableCell>

  <VTableCell data-test="product-brand">
    {{ item?.brand?.name }}
  </VTableCell>

  <VTableCell data-test="product-price">
    {{ formatMoney(item?.price) }}
  </VTableCell>
</template>

<script lang="ts" setup>
import type { Product } from '../types';
import { formatMoney } from '@/common/utils/format';

/**
 * @oaram id
 * @oaram name
 * @oaram description
 * @oaram price
 * @oaram category
 * @oaram brand
 */
// eslint-disable-next-line @typescript-eslint/no-unused-vars
const props = defineProps<{ item: Product }>();
</script>

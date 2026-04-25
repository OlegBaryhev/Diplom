<template>
  <VTableCell data-test="analog-name">
    {{ item?.name }}
  </VTableCell>

  <VTableCell data-test="analog-description">
    {{ item?.description }}
  </VTableCell>

  <VTableCell data-test="analog-category">
    {{ item?.category?.name }}
  </VTableCell>

  <VTableCell data-test="analog-brand">
    {{ item?.brand?.name }}
  </VTableCell>

  <VTableCell data-test="analog-price">
    {{ formatMoney(item?.price) }}
  </VTableCell>
</template>

<script lang="ts" setup>
import type { Analog } from '../types';
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
const props = defineProps<{ item: Analog }>();
</script>

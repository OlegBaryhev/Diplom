<template>
  <VTableCell data-test="cart-user">
    {{ `${item?.user?.name}${item?.user?.surname ? ' ' + item?.user?.surname : ''}` || 'Пользователь' }}
  </VTableCell>

  <VTableCell data-test="cart-products_types">
    {{ item?.products_types }}
  </VTableCell>

  <VTableCell data-test="cart-total">
    {{ item?.products_total }}
  </VTableCell>

  <VTableCell data-test="cart-price">
    {{ formatMoney(item?.total_price) }}
  </VTableCell>
</template>

<script lang="ts" setup>
import type { CartSearchItem } from '../types';
import { formatMoney } from '@/common/utils/format';

/**
 */

// eslint-disable-next-line @typescript-eslint/no-unused-vars
const props = defineProps<{ item: CartSearchItem }>();
</script>

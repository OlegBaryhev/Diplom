<template>
  <VTableCell data-test="cart-pickup_code">
    {{ item?.pickup_code }}
  </VTableCell>

  <VTableCell data-test="cart-user">
    {{ `${item?.user?.name}${item?.user?.surname ? ' ' + item?.user?.surname : ''}` || 'Пользователь' }}
  </VTableCell>

  <VTableCell data-test="cart-items-total">
    {{ item?.total_product_varieties }}
  </VTableCell>

  <VTableCell data-test="cart-items-total">
    {{ item?.total_product_quantity }}
  </VTableCell>

  <VTableCell data-test="cart-created_at">
    <div class="w-full flex justify-center items-center">
      <VStatus :value="item?.status">
        {{ ORDER_STATUS?.[item?.status] }}
      </VStatus>
    </div>
  </VTableCell>

  <VTableCell data-test="cart-created_at">
    {{ formatDate(item?.created_at, 'dd.MM.yy HH:mm') }}
  </VTableCell>
</template>

<script lang="ts" setup>
import type { OrderRead } from '../types';
import { ORDER_STATUS } from '@/modules/orders/const';
import { formatDate } from '@/common/utils/format';

// eslint-disable-next-line @typescript-eslint/no-unused-vars
const props = defineProps<{ item: OrderRead }>();
</script>

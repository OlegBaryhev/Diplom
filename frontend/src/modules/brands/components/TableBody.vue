<template>
  <VTableCell data-test="brand-name">
    {{ item?.name }}
  </VTableCell>

  <VTableCell data-test="brand-description">
    {{ item?.description }}
  </VTableCell>

  <VTableCell data-test="brand-created_at">
    {{ formatDate(item?.created_at, 'dd.MM.yy HH:mm') }}
  </VTableCell>
</template>

<script lang="ts" setup>
import type { Brand } from '../types';
import { formatDate } from '@/common/utils/format';

/**
 * @oaram id
 * @oaram name
 * @oaram description
 */

// eslint-disable-next-line @typescript-eslint/no-unused-vars
const props = defineProps<{ item: Brand }>();
</script>

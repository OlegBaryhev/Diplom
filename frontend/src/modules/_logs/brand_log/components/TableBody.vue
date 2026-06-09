<template>
  <VTableCell data-test="log-operation">
    {{ item?.operation }}
  </VTableCell>

  <VTableCell data-test="log-row">
    {{ JSON.stringify(item?.row_data) }}
  </VTableCell>

  <VTableCell data-test="log-changed_at">
    {{ formatDate(item?.changed_at, 'dd.MM.yy HH:mm') }}
  </VTableCell>
</template>

<script lang="ts" setup>
import type { ILogData } from '@/modules/_logs/types';
import { formatDate } from '@/common/utils/format';

/**
 * @oaram id
 * @oaram name
 * @oaram description
 */

// eslint-disable-next-line @typescript-eslint/no-unused-vars
const props = defineProps<{ item: ILogData }>();
</script>

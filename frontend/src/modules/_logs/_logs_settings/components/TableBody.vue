<template>
  <VTableCell data-test="settings-table-name">
    {{ item?.table_name }}
  </VTableCell>

  <VTableCell data-test="settings-time-retention">
    {{ item?.time_retention_minutes }}
  </VTableCell>

  <VTableCell data-test="settings-count-retention">
    {{ item?.count_retention_limit }}
  </VTableCell>
</template>

<script lang="ts" setup>
import type { ILogSettings } from '@/modules/_logs/types';

// eslint-disable-next-line @typescript-eslint/no-unused-vars
const props = defineProps<{ item: ILogSettings }>();
</script>

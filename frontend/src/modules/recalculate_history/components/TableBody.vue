<template>
  <VTableCell data-test="history-name">
    <span class="font-medium">{{ item?.name }}</span>
  </VTableCell>

  <VTableCell data-test="history-type">
    <span
      v-if="item?.recalculation_type"
      class="type-chip"
    >
      {{ RECALCULATION_TYPE_LABELS[item.recalculation_type] ?? `Тип ${item.recalculation_type}` }}
    </span>
    <span
      v-else
      class="text-additional-300"
    >—</span>
  </VTableCell>

  <VTableCell data-test="history-trigger">
    {{ TRIGGER_TYPE_LABELS[item?.trigger_type] ?? item?.trigger_type ?? '—' }}
  </VTableCell>

  <VTableCell data-test="history-by">
    {{ item?.recalculated_by ?? '—' }}
  </VTableCell>

  <VTableCell data-test="history-affected">
    {{ item?.products_affected_count ?? '—' }}
  </VTableCell>

  <VTableCell data-test="history-exec-time">
    {{ item?.execution_time_ms !== null ? `${item.execution_time_ms} мс` : '—' }}
  </VTableCell>

  <VTableCell data-test="history-date">
    {{ formatDate(item?.recalculated_at) }}
  </VTableCell>
</template>

<script lang="ts" setup>
import { format, parseISO } from 'date-fns';
import { RECALCULATION_TYPE_LABELS, TRIGGER_TYPE_LABELS } from '@/modules/recalculations/types';

const props = defineProps<{ item: any }>();

const formatDate = (dateStr: string | null | undefined): string => {
  if (!dateStr) return '—';
  try {
    return format(parseISO(dateStr), 'dd.MM.yyyy HH:mm');
  } catch {
    return dateStr;
  }
};
</script>

<style lang="scss" scoped>
.type-chip {
  @apply text-xs-medium;
  display: inline-block;
  padding: 2px 7px;
  border-radius: 4px;
  background: theme('colors.main.50');
  color: theme('colors.main.400');
  white-space: nowrap;
}
</style>

<template>
  <VTableCell data-test="recalculation-name">
    <span class="font-medium text-black">{{ item?.name }}</span>
  </VTableCell>

  <VTableCell data-test="recalculation-type">
    <span class="type-badge">{{ RECALCULATION_TYPE_LABELS[item?.recalculation_type] ?? '—' }}</span>
  </VTableCell>

  <VTableCell data-test="recalculation-trigger">
    {{ TRIGGER_TYPE_LABELS[item?.trigger_type] ?? '—' }}
  </VTableCell>

  <VTableCell data-test="recalculation-priority">
    {{ item?.priority ?? 0 }}
  </VTableCell>

  <VTableCell data-test="recalculation-active">
    <span
      class="status-badge"
      :class="item?.is_active ? 'status-badge--active' : 'status-badge--inactive'"
    >
      {{ item?.is_active ? 'Активен' : 'Отключен' }}
    </span>
  </VTableCell>

  <VTableCell data-test="recalculation-updated">
    {{ formatDate(item?.updated_at) }}
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
.type-badge {
  @apply text-xs-medium;
  display: inline-block;
  padding: 2px 8px;
  border-radius: 4px;
  background: theme('colors.main.50');
  color: theme('colors.main.400');
  white-space: nowrap;
}

.status-badge {
  @apply text-xs-medium;
  display: inline-block;
  padding: 2px 8px;
  border-radius: 4px;
  white-space: nowrap;

  &--active {
    background: #dcfce7;
    color: #16a34a;
  }

  &--inactive {
    background: #f3f4f6;
    color: theme('colors.additional.300');
  }
}
</style>

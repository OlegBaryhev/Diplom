<template>
  <VSidePanel
    class="item-side-panel"
    title="История перерасчета"
    data-test="item-side-panel"
    @close="$emit('close')"
  >
    <template #head>
      <VSidePanelInfoItem
        caption="ID"
        :value="item?.id"
        is-head
      />
    </template>

    <template #default>
      <div class="content">
        <VSidePanelInfoItem
          class="mb-4"
          caption="Наименование"
          :value="item?.name"
        />

        <VSidePanelInfoItem
          class="mb-4"
          caption="Описание"
          :value="item?.description"
        />

        <VSidePanelInfoItem
          class="mb-4"
          caption="Тип перерасчета"
          :value="typeLabel"
        />

        <VSidePanelInfoItem
          class="mb-4"
          caption="Инициатор"
          :value="triggerLabel"
        />

        <VSidePanelInfoItem
          class="mb-4"
          caption="Выполнил"
          :value="item?.recalculated_by"
        />

        <VSidePanelInfoItem
          class="mb-4"
          caption="Дата выполнения"
          :value="formatDate(item?.recalculated_at)"
        />

        <VSidePanelInfoItem
          class="mb-4"
          caption="Затронуто товаров"
          :value="item?.products_affected_count"
        />

        <VSidePanelInfoItem
          class="mb-4"
          caption="Время выполнения"
          :value="item?.execution_time_ms !== null ? `${item.execution_time_ms} мс` : null"
        />

        <div
          v-if="item?.parameters && Object.keys(item.parameters).length"
          class="params-block"
        >
          <p class="params-block__title">
            Параметры
          </p>
          <div class="params-block__body">
            <div
              v-for="(val, key) in displayParams"
              :key="key"
              class="params-block__row"
            >
              <span class="params-block__key">{{ key }}:</span>
              <span class="params-block__val">{{ formatParamValue(val) }}</span>
            </div>
          </div>
        </div>
      </div>
    </template>
  </VSidePanel>
</template>

<script lang="ts" setup>
import { format, parseISO } from 'date-fns';
import { RECALCULATION_TYPE_LABELS, TRIGGER_TYPE_LABELS } from '@/modules/recalculations/types';

const props = withDefaults(defineProps<{
  item?: any | null;
  // eslint-disable-next-line func-call-spacing
  fetchItems?:() => Promise<void>;
}>(), {
  item: null,
  fetchItems: undefined,
});

// eslint-disable-next-line func-call-spacing, no-spaced-func
defineEmits<{
  (evt: 'close'): void;
}>();

const typeLabel = computed(() =>
  props.item?.recalculation_type
    ? RECALCULATION_TYPE_LABELS[props.item.recalculation_type] ?? `Тип ${props.item.recalculation_type}`
    : '—');

const triggerLabel = computed(() =>
  props.item?.trigger_type
    ? TRIGGER_TYPE_LABELS[props.item.trigger_type] ?? props.item.trigger_type
    : '—');

const displayParams = computed(() => {
  const params = props.item?.parameters ?? {};
  const ignore = ['recalculation_id', 'product_selection'];
  return Object.fromEntries(
    Object.entries(params).filter(([k]) => !ignore.includes(k)),
  );
});

const formatDate = (dateStr: string | null | undefined): string => {
  if (!dateStr) return '—';
  try {
    return format(parseISO(dateStr), 'dd.MM.yyyy HH:mm:ss');
  } catch {
    return dateStr;
  }
};

const formatParamValue = (val: any): string => {
  if (val === null || val === undefined) return '—';
  if (typeof val === 'object') return JSON.stringify(val);
  return String(val);
};
</script>

<style lang="scss" scoped>
.params-block {
  margin-top: 16px;

  &__title {
    @apply text-sm-medium;
    color: theme('colors.additional.300');
    margin-bottom: 8px;
  }

  &__body {
    display: flex;
    flex-direction: column;
    gap: 6px;
    padding: 10px 12px;
    background: theme('colors.main.50');
    border-radius: 6px;
  }

  &__row {
    display: flex;
    gap: 8px;
    align-items: baseline;
  }

  &__key {
    @apply text-xs-medium;
    color: theme('colors.additional.300');
    flex-shrink: 0;
  }

  &__val {
    @apply text-sm-regular;
    color: theme('colors.black');
    word-break: break-word;
  }
}
</style>

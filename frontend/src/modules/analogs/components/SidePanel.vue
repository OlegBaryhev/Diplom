<template>
  <VSidePanel
    class="item-side-panel"
    title="Аналог"
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
      <div
        class="content"
      >
        <VSidePanelInfoItem
          class="mb-4"
          caption="Наименование"
          :value="item?.name"
          data-test="analog-name"
        />

        <VSidePanelInfoItem
          class="mb-4"
          caption="Цена"
          :value="formatMoney(item?.price)"
          data-test="analog-price"
        />

        <VSidePanelInfoItem
          class="mb-4"
          caption="Категория"
          :value="item?.category?.name"
          data-test="analog-category"
        />

        <VSidePanelInfoItem
          class="mb-4"
          caption="Бренд"
          :value="item?.brand?.name"
          data-test="analog-brand"
        />

        <VSidePanelInfoItem
          class="mb-4"
          caption="Описание"
          :value="item?.description"
          data-test="analog-description"
        />
      </div>
    </template>
  </VSidePanel>
</template>

<script lang="ts" setup>
import type { Analog } from '@/modules/analogs/types';
import { formatMoney } from '@/common/utils/format';

withDefaults(defineProps<{
  item?: Analog | null;
  // eslint-disable-next-line func-call-spacing
  fetchItems:() => Promise<void>;
}>(), {
  item: null,
});

// eslint-disable-next-line func-call-spacing, no-spaced-func
defineEmits<{
  (evt: 'close'): void;
}>();
</script>

<template>
  <VSidePanel
    class="item-side-panel"
    title="Пересчет цен"
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
      </div>
    </template>
  </VSidePanel>
</template>

<script lang="ts" setup>
withDefaults(defineProps<{
  item?: any | null;
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

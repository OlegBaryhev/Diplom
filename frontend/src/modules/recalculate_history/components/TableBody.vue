<template>
  <VTableCell data-test="brand-name">
    {{ item?.name }}
  </VTableCell>

  <VTableCell data-test="brand-description">
    {{ item?.description }}
  </VTableCell>
</template>

<script lang="ts" setup>
// eslint-disable-next-line @typescript-eslint/no-unused-vars
const props = defineProps<{ item: any }>();
</script>

<template>
  <VTableCell data-test="brand-name">
    {{ item?.name }}
  </VTableCell>

  <VTableCell data-test="brand-description">
    {{ item?.description }}
  </VTableCell>

</template>

<script lang="ts" setup>
import type { Brand } from '../types';

/**
 * @oaram id
 * @oaram name
 * @oaram description
 */

// eslint-disable-next-line @typescript-eslint/no-unused-vars
const props = defineProps<{ item: Brand }>();
</script>

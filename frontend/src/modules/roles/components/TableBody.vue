<template>
  <VTableCell
    class="none-system-cell"
    data-test="role-name"
  >
    {{ item?.display_name || item?.name }}
  </VTableCell>

  <VTableCell
    class="none-system-cell"
    data-test="role-display-name"
  >
    {{ item?.name }}
  </VTableCell>
</template>

<script lang="ts" setup>
import type { Role } from '../types';

defineProps<{ item: Role }>();
</script>

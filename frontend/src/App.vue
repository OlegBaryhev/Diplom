<template>
  <RouterView />
</template>

<script lang="ts" setup>
import { useBodyScrollbar } from '@/stores/bodyScrollbar';

onMounted(() => {
  useBodyScrollbar().initBodyOverlayScrollbar();
});
</script>

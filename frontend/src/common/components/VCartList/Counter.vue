<template>
  <div
    class="counter inline-flex justify-center items-center text-white px-2 h-[24px] rounded-full text-sm-regular bg-main-400"
  >
    {{ value }}
  </div>
</template>

<script setup lang="ts">
withDefaults(defineProps<{
  value?: number;
}>(), {
  value: 0,
});
</script>

<template>
  <Transition
    name="fade"
  >
    <div
      v-if="error"
      class="error-message"
    >
      <VIcon
        name="error"
        class="w-4 h-4 mr-2 mt-0.5 flex-shrink-0"
      />
      {{ error }}
    </div>
  </Transition>
</template>

<script setup lang="ts">
import VIcon from './VIcon.vue';

defineProps<{
  error?: string;
}>();
</script>

<style lang="scss">
.error-message {
  @apply text-sm-regular text-negative;
  text-transform: initial;
  display: flex;
}
</style>

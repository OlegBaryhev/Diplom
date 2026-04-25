<template>
  <Component
    :is="tag"
    class="skeleton"
  >
    <slot />
  </Component>
</template>

<script lang="ts" setup>
withDefaults(defineProps<{
  tag?: string;
}>(), {
  tag: 'div',
});
</script>

<script lang="ts">
export default defineComponent({
  name: 'VSkeleton',
});
</script>

<style lang="scss" scoped>
.skeleton {
  cursor: wait;
}
</style>

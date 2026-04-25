<template>
  <div
    :class="{
      'w-6': hasNoWidthClass,
      'h-6': hasNoHeightClass,
    }"
  >
    <Component :is="comp" />
  </div>
</template>

<script lang="ts" setup>
import { useIconStore } from '@/stores/iconStore';
import type { ClassAttr, IconComponent } from '@/common/types';

const attrs = useAttrs();

const props = defineProps<{ name: string | undefined }>();

const iconStore = useIconStore();

const classes = computed(() => (attrs.class as ClassAttr)?.split(' ') ?? []);
const hasNoWidthClass = computed(() => !classes.value.some((className) => className.startsWith('w-')));
const hasNoHeightClass = computed(() => !classes.value.some((className) => className.startsWith('h-')));

const comp = computed(() => {
  const fileName = props.name; // we have to declare it explicitly, otherwise the computed won't be reactive
  return fileName && defineAsyncComponent<IconComponent>(() => iconStore.loadIcon(fileName));
});
</script>

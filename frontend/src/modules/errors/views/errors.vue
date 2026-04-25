<template>
  <h2
    v-if="typeof errorCode === 'number'"
    class="mt-14 mb-7 text-8xl font-bold text-main-400 leading-none tracking-[8%]"
  >
    {{ errorCode }}
  </h2>

  <div class="text-2xl-semibold mb-6">
    {{ ERRORS_CONTENT[errorCode].title }}
  </div>

  <div
    v-if="typeof errorCode === 'number'"
    class="text-base-regular text-additional max-w-sm text-center mb-16"
    v-html="ERRORS_CONTENT[errorCode].description"
  />

  <VBtn
    v-if="ERRORS_CONTENT[errorCode].btn"
    outlined
    tag="RouterLink"
    to="/"
  >
    {{ ERRORS_CONTENT[errorCode].btn }}
  </VBtn>
</template>

<script setup>
import { ERRORS_CONTENT } from '@/consts/errors.ts';

const { errorCode } = useRoute().meta;
</script>

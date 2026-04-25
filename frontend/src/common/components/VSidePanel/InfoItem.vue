<template>
  <div
    class="side-panel-info-item"
    :class="{
      'side-panel-info-item--is-head': isHead,
      'side-panel-info-item--strong': strong,
      'side-panel-info-item--line-clamped': lineClamp,
      'side-panel-info-item--space-beetweet': space,
    }"
  >
    <h5 class="side-panel-info-item__caption">
      {{ caption }}{{ isHead ? ':' : '' }}
    </h5>

    <div
      class="side-panel-info-item__value"
      :style="{ '-webkit-line-clamp': lineClamp ?? undefined }"
      :title="lineClamp ? formattedValue : undefined"
    >
      <slot>
        <RouterLink
          v-if="href"
          :to="href"
          :target="target"
          class="text-main-400 hover:text-main-350"
        >
          {{ formattedValue }}
        </RouterLink>

        <div v-else>
          {{ formattedValue }}
        </div>
      </slot>
    </div>
  </div>
</template>

<script lang="ts" setup>
const props = withDefaults(defineProps<{
  caption: string;
  value?: any;
  isHead?: boolean;
  strong?: boolean;
  lineClamp?: number;
  href?: string;
  target?: '_blank' | '_self';
  top?: boolean;
  left?: boolean;
  space?: boolean;
}>(), {
  isHead: false,
  strong: false,
  target: '_self',
  top: true,
  left: true,
  space: false,
});

const formattedValue = computed(() => props.value || props.value === 0 || props.value === '0' ? props.value : '-');
</script>

<style lang="scss" scoped>
.side-panel-info-item {
  $info-item: &;

  &__caption {
    font-size: 13px;
    color: theme('colors.additional.300');
  }

  &__value {
    @apply text-base-regular;

    color: theme('colors.black');
    word-break: break-word;
  }

  &--is-head {
    display: flex;

    #{$info-item}__caption {
      @apply text-sm-medium;

      margin-right: 4px;
    }

    #{$info-item}__value {
      @apply text-sm-regular;

      color: theme('colors.additional.300');
    }
  }

  &--space-beetweet {
    display: flex;
    width: 100%;
    justify-content: space-between;
  }

  &--strong {
    #{$info-item}__caption {
      @apply text-base-regular;

      color: theme('colors.additional.DEFAULT');
    }

    #{$info-item}__value {
      @apply font-medium;
    }
  }

  &--line-clamped &__value {
    display: -webkit-box;
    -webkit-box-orient: vertical;
    word-break: break-word;
    overflow: hidden;
  }
}
</style>

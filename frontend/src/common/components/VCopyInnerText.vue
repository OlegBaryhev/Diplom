<template>
  <div
    class="text-for-copy__wrapper"
    @click="copy"
  >
    <slot name="content" />
    <VTooltip
      class="blank-hint"
      content="Скопировано!"
      :show="isCopied"
      :left="left"
      :right="!left"
      :top="top"
      show-always
      style="pointer-events: none"
    >
      <VIcon
        class="text-for-copy__icon h-4 w-4"
        :class="{'recently-copied': isCopied}"
        name="copy"
      />
    </VTooltip>
  </div>
</template>

<script lang="ts" setup>
const props = withDefaults(defineProps<{
  text: string;
  left?: boolean;
  top?: boolean;
}>(), {
  left: false,
  top: true,
});

const isCopied = ref(false);

const copy = async () => {
  try {
    if (navigator.clipboard?.writeText) {
      await navigator.clipboard.writeText(props.text);
    } else {
      const textArea = document.createElement('textarea');
      textArea.value = props.text;
      textArea.style.position = 'fixed';
      textArea.style.opacity = '0';
      document.body.appendChild(textArea);
      textArea.focus();
      textArea.select();
      document.execCommand('copy');
      document.body.removeChild(textArea);
    }

    isCopied.value = true;
    setTimeout(() => {
      isCopied.value = false;
    }, 1000);
  } catch (err) {
    console.error('Ошибка копирования текста:', err);
  }
};
</script>

<style lang="scss" scoped>
.text-for-copy {
  &__wrapper {
    display: flex;
    align-items: flex-end;
    gap: 5px;
    cursor: pointer;
    width: fit-content;
    color: theme('colors.blue.500');
    &:hover .text-for-copy__icon {
      color: theme('colors.blue.600');
      background-color: theme('colors.blue.100');
    }
  }

  &__icon {
    transform: translateY(-4px);
    color: theme('colors.blue.500');
    border-radius: 4px;
    padding: 1px;
    &.recently-copied {
      color: theme('colors.blue.600');
    }
    &:focus {
      border: 1px solid theme('colors.blue.600');
    }
  }
}
</style>

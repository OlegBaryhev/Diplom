<template>
  <div
    class="profile-item w-full"
    @click="emit('openProfileModal')"
  >
    <div
      class="profile-item__image flex items-center justify-center"
      :class="{
        'profile-item__image--large': isLarge,
      }"
      @click="toggleIsOpen"
    >
      <VIcon
        v-if="!profileData?.avatar_url"
        class="profile-item__icon"
        name="plus"
      />
    </div>

    <div
      v-if="isOpen"
      class="profile__text w-full flex flex-col cursor-pointer"
    >
      <span class="profile-item__username min-h-[1em]">{{ `${profileData?.name}${profileData?.surname ? ' ' + profileData?.surname: ''}` || 'Пользователь' }}</span>
      <span class="profile-item__role text-main-300">{{ profileData?.role ? 'Администратор' : ( profileData?.role ?? 'Гость') }}</span>
    </div>
  </div>
</template>

<script lang="ts" setup>
const props = withDefaults(defineProps<{
  image?: string | Blob;
  profileData?: any;
  isOpen?: boolean;
  isLarge?: boolean;
}>(), {
  image: null,
  isOpen: false,
});

// eslint-disable-next-line func-call-spacing, no-spaced-func
const emit = defineEmits<{
  (evt: 'update:isOpen', newState: boolean): void,
  (evt: 'openProfile'): void,
  (evt: 'openProfileModal'): void,
}>();

const isOpen = useVModel<boolean>(props, 'isOpen', emit);

const toggleIsOpen = () => {
  isOpen.value = true;
  emit('openProfile');
};

</script>

<style lang="scss" scoped>
.profile-item {
  $root: &;
  --image-size: 60px;
  display: flex;
  gap: 12px;
  height: min-content;
  justify-content: start;
  align-items: center;
  height: 88px;
  width: 100%;
  transition: width 0.3s linear;
  margin-left: 14px;

  &__image {
    aspect-ratio: 1;
    background-color: theme('colors.main.100');
    color: theme('colors.main.DEFAULT');
    height: var(--image-size);
    width: var(--image-size);
    cursor: pointer;
    border-radius: max(calc(var(--image-size) / 2), 100%);
    transition: 0.2s ease-in-out background-color, color;

    &:hover {
      background: theme('colors.main.200');
      #{$root}__icon {
        transform: scale(1.1);
      }
    }
  }
  &__icon {
    transition: transform 0.2s linear;
  }
}
</style>

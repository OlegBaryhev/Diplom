<template>
  <div
    class="profile-item w-full"
    @click="emit('openProfileModal')"
  >
    <div
      class="profile-item__image flex items-center justify-center overflow-hidden"
      :class="{
        'profile-item__image--large': isLarge,
      }"
      @click="toggleIsOpen"
    >
      <img
        v-if="profileData?.avatar_url"
        :src="fullAvatarUrl"
        class="w-full h-full object-cover"
        alt=""
      />
      <VIcon
        v-else
        class="profile-item__icon"
        name="plus"
      />
    </div>

    <div
      v-if="isOpen"
      class="profile__text w-full flex flex-col cursor-pointer"
    >
      <span class="profile-item__username overflow-hidden whitespace-nowrap min-h-[1em]">{{ `${profileData?.name}${profileData?.surname ? ' ' + profileData?.surname: ''}` || 'Пользователь' }}</span>
      <span class="profile-item__role overflow-hidden whitespace-nowrap text-main-300">{{ roleDisplayName }}</span>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { REMOTE_SERVER_URL, ROLES_LOCALIZATION_NAMES } from '@/consts';

const props = withDefaults(defineProps<{
  image?: string | Blob;
  profileData?: any;
  isOpen?: boolean;
  isLarge?: boolean;
}>(), {
  image: null,
  isOpen: false,
});

const fullAvatarUrl = computed(() => {
  const url = props.profileData?.avatar_url;
  if (!url) return '';
  return url.startsWith('http') ? url : `${REMOTE_SERVER_URL}${url}`;
});

const roleDisplayName = computed(() => {
  const roleName = props.profileData?.role_name;
  if (!roleName) return 'Гость';
  return (ROLES_LOCALIZATION_NAMES as Record<string, string>)[roleName] ?? roleName;
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

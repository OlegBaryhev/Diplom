<template>
  <section class="profile flex flex-col gap-4 min-h-[100vh] w-full p-6">
    <article class="profile__main w-full h-[200px]">
      <div class="profile__background w-full"></div>
      <div class="profile__main-content h-[40%] px-3">
        <div
          class="profile__image
          rounded-[100%] absolute
          flex items-center justify-center "
        >
          <VIcon
            v-if="!profileData?.avatar_url"
            class="profile__icon"
            name="plus"
          />
        </div>
        <div class="profile__content h-full flex justify-between items-center">
          <div class="profile__info h-full flex items-center">
            <div class="flex flex-col">
              <span class="profile__username text-lg-medium"> {{ `${profileData?.name}${profileData?.surname ? ' ' + profileData?.surname : ''}` || 'Пользователь' }}</span>
              <span class="profile__role text-main-300"> {{ profileData?.role ? 'Администратор' : ( profileData?.role ?? 'Гость') }} </span>
            </div>
          </div>
          <div class="profile__actions h-full flex items-center">
            <div class="flex gap-2">
              <VBtn
                v-if="userHasPermission(Permissions.Edit)"
                text="Редактировать"
                outlined
                small
                class="profile__edit-btn"
                :disabled="saveChangesLoading"
                data-test="edit"
                @click="modalStore.open(EDIT_USER_MODAL_ID);"
              />

              <VBtn
                text="Выйти"
                small
                class="profile__exit"
                :disabled="saveChangesLoading"
                data-test="exit"
                @click="modalStore.open('logoutModal');"
              />
            </div>
          </div>
        </div>
      </div>
    </article>
  </section>

  <EditUserModel
    :modal-id="EDIT_USER_MODAL_ID"
    :user-data="profileData"
    @save-user="userStore?.getUser()"
  />

  <VConfirmationModal
    id="logoutModal"
    title="Вы действительно хотите выйти?"
    confirmation-text="Выйти"
    @confirm="exitFromUser()"
  />
</template>

<script lang="ts" setup>
import { userHasPermission } from '@/common/utils/permissions';
import { Permissions } from '@/common/types/permissions';
import { useUser } from '@/stores/user';
import EditUserModel from '@/modules/profile/components/EditUserModel.vue';
import { useModals } from '@/stores/modals';

const userStore = useUser();
const modalStore = useModals();

const EDIT_USER_MODAL_ID = 'edit-user-modal-id';

const profileData = computed(() => userStore?.user);

const exitFromUser = (): void => userStore.logout();
</script>

<style lang="scss">
@keyframes gradientShift {
  0% {
    background-position: 0 0;
  }
  100% {
    background-position: -200% 0;
  }
}

.profile {
  $root: &;
  --image-size: 120px;

  &__main {
    border-radius: 20px;
    overflow: hidden;
    border: 1px solid theme('colors.main.400');
    background: theme('colors.white');
  }

  &__background {
    height: 60%;
    min-height: 100px;
    background: linear-gradient(to right, theme('colors.main.400'), theme('colors.main.200'), theme('colors.main.400'));
    background-size: 200% 100%;
    animation: gradientShift 3s linear infinite;
  }

  &__image{
    aspect-ratio: 1;
    background-color: theme('colors.main.100');
    color: theme('colors.main.DEFAULT');
    height: var(--image-size);
    width: var(--image-size);
    margin-left: 20px;
    cursor: pointer;
    border: theme('colors.white') 10px solid;
    transform: translateY(-50%) scale(1);
    transition: 0.2s ease-in-out transform, 0.2s ease-in-out background;

    &:hover {
      background: theme('colors.main.200');
      transform: translateY(-50%) scale(1.1);
      #{$root}__icon {
        transform: scale(1.1);
      }
    }
  }

  &__info{
    margin-left: calc(40px + var(--image-size));
    height: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
  }
}
</style>

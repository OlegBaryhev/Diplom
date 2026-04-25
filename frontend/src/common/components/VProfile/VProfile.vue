<template>
  <div
    ref="profileRef"
    v-click-away="close"
    class="profile duration-300 ease-in-out"
  >
    <TransitionGroup
      name="fade"
    >
      <VLoader
        v-if="!user"
        class="profile__loader"
      />

      <template v-else>
        <div class="header mb-2">
          <div class="text-lg-semibold">
            {{ userFullName }}
          </div>

          <VIcon
            name="close"
            class="cursor-pointer"
            data-test="close-profile"
            @click.stop="close"
          />
        </div>

        <VTabs
          v-model="activeTab"
          class="tabs"
          :tabs="tabs"
          primary
        />

        <div class="line" />

        <VProfileInfo
          v-show="activeTab.id === 1"
          :user="user"
        />
      </template>
    </TransitionGroup>
  </div>
</template>

<script setup lang="ts">
const userFullName = computed(() => `${user.value?.surname} ${user.value?.name} ${user.value?.middle_name}`);

const emit = defineEmits(['close']);

const tabs = [
  {
    id: 1,
    text: 'Информация',
  },
];

const activeTab = ref(tabs[0]);
const profileRef = ref<HTMLElement | null>(null);

const close = () => {
  emit('close');
};
</script>

<script lang="ts">
export default defineComponent({
  name: 'VProfile',
});
</script>

<style lang="scss" scoped>

  .profile {
    width: 446px;
    height: 446px;
    max-height: 446px;
    box-shadow: 0px 0px 0px 1px rgba(0, 44, 94, 0.001), 0px 10px 20px -4px rgba(57, 80, 105, 0.15);
    border-radius: 12px;
    background-color: theme('colors.white');;
    padding-top: 24px;
    padding-left: 32px;
    padding-right: 4px;
    overflow: hidden;
    display: flex;
    flex-direction: column;

    .header {
      display: flex;
      width: 100%;
      justify-content: space-between;
      height: fit-content;
      padding-right: 28px;
    }

    .tabs {
      height: fit-content;
      position: relative;
    }

    .line {
      border-bottom: 1px solid theme('colors.additional.200');
      padding: 0 32px;
      margin: 0 -32px;
      margin-top: -1.5px;
      height: fit-content;
      box-shadow: 0px 0px 0px 1px rgba(0, 44, 94, 0.001), 0px 3px 20px -4px rgba(57, 80, 105, 0.15);
    }

    &__loader {
      position: absolute;
      left: 50%;
      top: 50%;
      transform: translate(-50%, -50%);
    }
  }

</style>

<template>
  <section class="profile flex flex-col gap-4 min-h-[100vh] w-full p-6">
    <article class="profile__main w-full h-[200px]">
      <div class="profile__background w-full" />
      <div class="profile__main-content h-[40%] px-3">
        <div
          class="profile__image rounded-[100%] absolute flex items-center justify-center cursor-pointer"
          @click="openAvatarEditor"
        >
          <img
            v-if="profileData?.avatar_url"
            :src="avatarUrl"
            class="w-full h-full rounded-full object-cover"
            alt=""
          />

          <VIcon
            v-else
            class="profile__icon"
            name="plus"
          />
        </div>

        <div class="profile__content h-full flex justify-between items-center">
          <div class="profile__info h-full flex items-center">
            <div class="flex flex-col">
              <span class="profile__username text-lg-medium">
                {{ `${profileData?.name}${profileData?.surname ? ' ' + profileData?.surname : ''}` || 'Пользователь' }}
              </span>
              <span class="profile__role text-main-300">
                {{ roleDisplayName }}
              </span>
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

    <article
      v-if="isSuperuser && stats"
      class="profile__stats"
    >
      <h2 class="profile__stats-title">
        Статистика перерасчетов
      </h2>

      <div class="stats-grid">
        <div class="stat-card">
          <span class="stat-card__value">{{ stats.total_executions }}</span>
          <span class="stat-card__label">Всего выполнено</span>
        </div>
        <div class="stat-card">
          <span class="stat-card__value">{{ stats.total_rules }}</span>
          <span class="stat-card__label">Правил всего</span>
        </div>
        <div class="stat-card stat-card--active">
          <span class="stat-card__value">{{ stats.active_rules }}</span>
          <span class="stat-card__label">Активных правил</span>
        </div>
        <div class="stat-card">
          <span class="stat-card__value">{{ stats.avg_products_affected }}</span>
          <span class="stat-card__label">Средн. товаров за раз</span>
        </div>
        <div class="stat-card">
          <span class="stat-card__value">{{ stats.avg_execution_time_ms }} мс</span>
          <span class="stat-card__label">Средн. время выполн.</span>
        </div>
      </div>

      <div class="charts-grid">
        <div class="chart-card">
          <VBarChart
            title="Выполнений по типу перерасчета"
            :items="byTypeChartData"
            bar-color="#3b82f6"
            :height="200"
          />
        </div>

        <div class="chart-card">
          <VBarChart
            title="Выполнений по инициатору"
            :items="byTriggerChartData"
            bar-color="#8b5cf6"
            :height="200"
          />
        </div>

        <div class="chart-card chart-card--wide">
          <VLineChart
            title="Динамика перерасчетов по дням"
            :items="byDayChartData"
            line-color="#10b981"
            :height="180"
          />
        </div>
      </div>
    </article>

    <div
      v-else-if="isSuperuser && statsLoading"
      class="profile__stats-loading"
    >
      <VLoader />
    </div>
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

    <AvatarEditorModal
      :modal-id="AVATAR_MODAL_ID"
      :current-avatar-url="profileData?.avatar_url"
      @saved="onAvatarSaved"
    />
  </section>
</template>

<script lang="ts" setup>
import { userHasPermission } from '@/common/utils/permissions';
import { Permissions } from '@/common/types/permissions';
import { useUser } from '@/stores/user';
import EditUserModel from '@/modules/profile/components/EditUserModel.vue';
import { useModals } from '@/stores/modals';
import AvatarEditorModal from '../components/AvatarEditorModal.vue';
import { getRecalculationStatisticsRequest } from '@/modules/recalculations/api';
import VBarChart from '@/common/components/charts/VBarChart.vue';
import VLineChart from '@/common/components/charts/VLineChart.vue';
import { REMOTE_SERVER_URL, ROLES_LOCALIZATION_NAMES } from '@/consts';

const userStore = useUser();
const modalStore = useModals();

const EDIT_USER_MODAL_ID = 'edit-user-modal-id';
const AVATAR_MODAL_ID = 'avatar-editor-modal';

const profileData = computed(() => userStore?.user);
const isSuperuser = computed(() => profileData.value?.role_name === 'superuser');
const roleDisplayName = computed(() => {
  const roleName = profileData.value?.role_name;
  if (!roleName) return 'Гость';
  return (ROLES_LOCALIZATION_NAMES as Record<string, string>)[roleName] ?? roleName;
});
const avatarUrl = computed(() => {
  const url = profileData.value?.avatar_url;
  if (!url) return '';
  return url.startsWith('http') ? url : `${REMOTE_SERVER_URL}${url}`;
});
const saveChangesLoading = ref(false);

const stats = ref<any>(null);
const statsLoading = ref(false);

const fetchStats = async () => {
  if (!isSuperuser.value) return;
  statsLoading.value = true;
  try {
    const { data } = await getRecalculationStatisticsRequest();
    stats.value = data;
  } catch (err) {
    console.error(err);
  } finally {
    statsLoading.value = false;
  }
};

const byTypeChartData = computed(() => (stats.value?.by_type ?? []).map((item: any) => ({
  label: item.label,
  value: item.count,
})));

const byTriggerChartData = computed(() => (stats.value?.by_trigger ?? []).map((item: any) => ({
  label: item.label,
  value: item.count,
})));

const byDayChartData = computed(() => (stats.value?.by_day ?? []).map((item: any) => ({
  label: item.date?.slice(5) ?? '',
  value: item.count,
})));

watch(isSuperuser, (val) => {
  if (val) fetchStats();
}, { immediate: true });

const exitFromUser = (): void => userStore.logout();

const openAvatarEditor = () => {
  modalStore.open(AVATAR_MODAL_ID);
};

const onAvatarSaved = async () => {
  await userStore.getUser();
};
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

  &__stats {
    background: theme('colors.white');
    border-radius: 16px;
    border: 1px solid theme('colors.main.100');
    padding: 24px;
    display: flex;
    flex-direction: column;
    gap: 20px;
  }

  &__stats-title {
    @apply text-xl-semibold;
    color: theme('colors.additional.DEFAULT');
  }

  &__stats-loading {
    display: flex;
    align-items: center;
    justify-content: center;
    min-height: 200px;
  }
}

.stats-grid {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.stat-card {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 16px 20px;
  background: theme('colors.main.50');
  border-radius: 12px;
  min-width: 130px;
  flex: 1;

  &--active {
    background: #dcfce7;
  }

  &__value {
    @apply text-xl-semibold;
    color: theme('colors.additional.DEFAULT');
  }

  &__label {
    @apply text-xs-regular;
    color: theme('colors.additional.300');
  }
}

.charts-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;

  @media (max-width: 900px) {
    grid-template-columns: 1fr;
  }
}

.chart-card {
  padding: 16px;
  background: theme('colors.main.50');
  border-radius: 12px;
  overflow: hidden;

  &--wide {
    grid-column: 1 / -1;
  }
}
</style>

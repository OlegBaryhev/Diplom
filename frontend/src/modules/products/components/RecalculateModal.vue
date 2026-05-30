<template>
  <VModalWrap
    :modal-id="modalId"
    title="Управление перерасчетами"
  >
    <template #modal-body>
      <div class="recalc-modal">
        <div class="recalc-modal__toolbar">
          <VInput
            v-model="searchQuery"
            class="recalc-modal__search"
            label="Поиск"
            sm
            secondary
          />

          <VMultiselect
            v-model="filterType"
            class="recalc-modal__filter"
            :options="typeFilterOptions"
            item-name="label"
            primary-key="value"
            label="Тип"
            sm
            clearable
          />

          <VMultiselect
            v-model="filterTrigger"
            class="recalc-modal__filter"
            :options="TRIGGER_TYPES"
            item-name="label"
            primary-key="value"
            label="Инициатор"
            sm
            clearable
          />

          <VBtn
            v-if="userHasPermission(Permissions.Write)"
            small
            @click="openCreate"
          >
            Создать
          </VBtn>
        </div>

        <div
          v-if="loading"
          class="recalc-modal__loading"
        >
          <VLoader />
        </div>

        <div
          v-else-if="!recalculations.length"
          class="recalc-modal__empty"
        >
          Перерасчеты не найдены. Нажмите «Создать» для добавления.
        </div>

        <div
          v-else
          class="recalc-modal__table-wrap"
        >
          <table class="recalc-table">
            <thead>
              <tr>
                <th>Наименование</th>
                <th>Тип</th>
                <th>Инициатор</th>
                <th>Приоритет</th>
                <th>Статус</th>
                <th>Обновлен</th>
                <th />
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="item in recalculations"
                :key="item.id"
                class="recalc-table__row"
                :class="{ 'recalc-table__row--active': detailedItem?.id === item.id }"
                @click="detailedItem = item"
              >
                <td class="recalc-table__cell recalc-table__cell--name">
                  {{ item.name }}
                </td>
                <td class="recalc-table__cell">
                  <span class="type-chip">{{ RECALCULATION_TYPE_LABELS[item.recalculation_type] ?? '—' }}</span>
                </td>
                <td class="recalc-table__cell">
                  {{ TRIGGER_TYPE_LABELS[item.trigger_type] ?? '—' }}
                </td>
                <td class="recalc-table__cell recalc-table__cell--center">
                  {{ item.priority }}
                </td>
                <td class="recalc-table__cell">
                  <span
                    class="status-chip"
                    :class="item.is_active ? 'status-chip--active' : 'status-chip--off'"
                  >
                    {{ item.is_active ? 'Активен' : 'Выкл' }}
                  </span>
                </td>
                <td class="recalc-table__cell">
                  {{ formatDate(item.updated_at) }}
                </td>
                <td
                  class="recalc-table__cell recalc-table__cell--actions"
                  @click.stop
                >
                  <button
                    v-if="userHasPermission(Permissions.Recalculate)"
                    class="recalc-table__action-btn"
                    title="Выполнить"
                    :disabled="executingId === item.id"
                    @click="executeItem(item)"
                  >
                    <VIcon
                      name="calculator"
                      class="w-4 h-4"
                    />
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <div
          v-if="total > recalculations.length"
          class="recalc-modal__load-more"
        >
          <VBtn
            outlined
            small
            :loading="loadingMore"
            @click="loadMore"
          >
            Загрузить ещё
          </VBtn>
        </div>
      </div>
    </template>

    <template #modal-footer>
      <VBtn
        text="Закрыть"
        outlined
        small
        @click="modalStore.close(modalId)"
      />
    </template>
  </VModalWrap>

  <SidePanel
    v-if="detailedItem || isCreating"
    :item="detailedItem"
    :fetch-items="fetchRecalculations"
    @close="onSidePanelClose"
    @delete="onDelete"
    @executed="onExecuted"
  />
</template>

<script lang="ts" setup>
import { debounce } from 'lodash';
import { format, parseISO } from 'date-fns';
import { useModals } from '@/stores/modals';
import { Permissions } from '@/common/types/permissions';
import { userHasPermission } from '@/common/utils/permissions';
import {
  searchRecalculationsRequest,
  executeRecalculationRequest,
} from '@/modules/recalculations/api';
import {
  RECALCULATION_TYPES,
  RECALCULATION_TYPE_LABELS,
  TRIGGER_TYPES,
  TRIGGER_TYPE_LABELS,
} from '@/modules/recalculations/types';
import type { Recalculation } from '@/modules/recalculations/types';
import SidePanel from '@/modules/recalculations/components/SidePanel.vue';
import { TABLE_ITEM_COUNT_TO_FETCH } from '@/consts';

const props = withDefaults(defineProps<{
  modalId?: string;
}>(), {
  modalId: 'recalculateModal',
});

const modalStore = useModals();

const searchQuery = ref('');
const filterType = ref<any>(null);
const filterTrigger = ref<any>(null);
const recalculations = ref<Recalculation[]>([]);
const total = ref(0);
const page = ref(1);
const loading = ref(false);
const loadingMore = ref(false);
const detailedItem = ref<Recalculation | null>(null);
const isCreating = ref(false);
const executingId = ref<number | null>(null);

const typeFilterOptions = [
  { value: null, label: 'Все типы' },
  ...RECALCULATION_TYPES,
];

const buildParams = (p = 1) => ({
  ...(searchQuery.value && { search: searchQuery.value }),
  ...(filterType.value?.value && { recalculation_type: filterType.value.value }),
  ...(filterTrigger.value?.value && { trigger_type: filterTrigger.value.value }),
  page: p,
  page_size: TABLE_ITEM_COUNT_TO_FETCH,
  sort_by: 'priority_desc',
});

const fetchRecalculations = debounce(async () => {
  loading.value = true;
  page.value = 1;
  try {
    const { data } = await searchRecalculationsRequest(buildParams(1));
    recalculations.value = data?.items ?? [];
    total.value = data?.total ?? 0;
  } catch (err) {
    console.error(err);
  } finally {
    loading.value = false;
  }
}, 300);

const loadMore = async () => {
  loadingMore.value = true;
  page.value += 1;
  try {
    const { data } = await searchRecalculationsRequest(buildParams(page.value));
    recalculations.value = [...recalculations.value, ...(data?.items ?? [])];
    total.value = data?.total ?? 0;
  } catch (err) {
    console.error(err);
    page.value -= 1;
  } finally {
    loadingMore.value = false;
  }
};

const openCreate = () => {
  detailedItem.value = null;
  isCreating.value = true;
};

const onSidePanelClose = () => {
  detailedItem.value = null;
  isCreating.value = false;
};

const onDelete = () => {
  detailedItem.value = null;
  isCreating.value = false;
  fetchRecalculations();
};

const onExecuted = () => {
  fetchRecalculations();
};

const executeItem = async (item: Recalculation) => {
  executingId.value = item.id;
  try {
    await executeRecalculationRequest(item.id);
    fetchRecalculations();
  } catch (err) {
    console.error(err);
  } finally {
    executingId.value = null;
  }
};

const formatDate = (dateStr: string | null | undefined): string => {
  if (!dateStr) return '—';
  try {
    return format(parseISO(dateStr), 'dd.MM.yyyy');
  } catch {
    return dateStr;
  }
};

watch(
  () => [searchQuery.value, filterType.value, filterTrigger.value],
  () => fetchRecalculations(),
  { deep: true },
);

const isOpen = computed(() => modalStore.activeModals.includes(props.modalId));

watch(isOpen, (val) => {
  if (val) fetchRecalculations();
});
</script>

<style lang="scss" scoped>
.recalc-modal {
  display: flex;
  flex-direction: column;
  gap: 12px;
  width: 100%;
  min-height: 400px;

  &__toolbar {
    display: flex;
    align-items: flex-end;
    gap: 10px;
    flex-wrap: wrap;
  }

  &__search {
    flex: 1;
    min-width: 180px;
  }

  &__filter {
    width: 180px;
    flex-shrink: 0;
  }

  &__loading {
    display: flex;
    align-items: center;
    justify-content: center;
    height: 200px;
  }

  &__empty {
    @apply text-sm-regular;
    color: theme('colors.additional.300');
    text-align: center;
    padding: 48px 0;
  }

  &__table-wrap {
    overflow-x: auto;
  }

  &__load-more {
    display: flex;
    justify-content: center;
  }
}

.recalc-table {
  width: 100%;
  border-collapse: collapse;

  th {
    @apply text-xs-medium;
    text-align: left;
    color: theme('colors.additional.300');
    padding: 6px 10px;
    border-bottom: 1px solid theme('colors.main.100');
    white-space: nowrap;
  }

  &__row {
    cursor: pointer;
    transition: background 0.1s;

    &:hover,
    &--active {
      background: theme('colors.main.50');
    }
  }

  &__cell {
    @apply text-sm-regular;
    color: theme('colors.black');
    padding: 8px 10px;
    border-bottom: 1px solid theme('colors.main.100');
    white-space: nowrap;

    &--name {
      font-weight: 500;
      max-width: 200px;
      overflow: hidden;
      text-overflow: ellipsis;
    }

    &--center {
      text-align: center;
    }

    &--actions {
      width: 48px;
    }
  }

  &__action-btn {
    padding: 4px;
    color: theme('colors.additional.300');
    background: none;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    transition: color 0.1s, background 0.1s;

    &:hover:not(:disabled) {
      color: theme('colors.main.400');
      background: theme('colors.main.100');
    }

    &:disabled {
      opacity: 0.5;
      cursor: not-allowed;
    }
  }
}

.type-chip {
  @apply text-xs-medium;
  display: inline-block;
  padding: 2px 7px;
  border-radius: 4px;
  background: theme('colors.main.50');
  color: theme('colors.main.400');
  white-space: nowrap;
}

.status-chip {
  @apply text-xs-medium;
  display: inline-block;
  padding: 2px 7px;
  border-radius: 4px;
  white-space: nowrap;

  &--active {
    background: #dcfce7;
    color: #16a34a;
  }

  &--off {
    background: #f3f4f6;
    color: theme('colors.additional.300');
  }
}
</style>

<template>
  <VSidePanel
    class="recalculation-side-panel"
    :title="panelTitle"
    :loading="loading"
    data-test="recalculation-side-panel"
    @close="$emit('close')"
  >
    <template #head>
      <VSidePanelInfoItem
        v-if="item && !formModel"
        caption="ID"
        :value="item.id"
        is-head
      />
    </template>

    <template #default>
      <div class="content">
        <template v-if="!formModel && item">
          <VSidePanelInfoItem
            class="mb-4"
            caption="Наименование"
            :value="item.name"
          />

          <VSidePanelInfoItem
            class="mb-4"
            caption="Описание"
            :value="item.description"
          />

          <VSidePanelInfoItem
            class="mb-4"
            caption="Тип перерасчета"
            :value="RECALCULATION_TYPE_LABELS[item.recalculation_type]"
          />

          <VSidePanelInfoItem
            class="mb-4"
            caption="Приоритет"
            :value="item.priority"
          />

          <VSidePanelInfoItem
            class="mb-4"
            caption="Статус"
            :value="item.is_active ? 'Активен' : 'Отключен'"
          />

          <VSidePanelInfoItem
            class="mb-4"
            caption="Инициатор"
            :value="TRIGGER_TYPE_LABELS[item.trigger_type]"
          />

          <VSidePanelInfoItem
            v-if="item.trigger_type === 'schedule' && item.trigger_config?.cron"
            class="mb-4"
            caption="Расписание (cron)"
            :value="item.trigger_config.cron"
          />

          <VSidePanelInfoItem
            v-if="item.trigger_type === 'event' && item.trigger_config?.event_type"
            class="mb-4"
            caption="Событие"
            :value="eventTypeLabel(item.trigger_config.event_type)"
          />

          <div class="params-section">
            <p class="params-section__title">
              Параметры перерасчета
            </p>
            <div class="params-section__body">
              <template v-if="item.recalculation_type === 1">
                <VSidePanelInfoItem
                  caption="Валюта"
                  :value="item.parameters.currency"
                />
                <VSidePanelInfoItem
                  caption="Старый курс"
                  :value="item.parameters.old_rate"
                />
                <VSidePanelInfoItem
                  caption="Новый курс"
                  :value="item.parameters.new_rate"
                />
              </template>
              <template v-else-if="item.recalculation_type === 2">
                <VSidePanelInfoItem
                  caption="Наценка, %"
                  :value="item.parameters.markup_percent"
                />
                <VSidePanelInfoItem
                  caption="Фиксированная надбавка"
                  :value="item.parameters.markup_fixed"
                />
                <VSidePanelInfoItem
                  caption="Область применения"
                  :value="scopeLabel(item.parameters.scope)"
                />
              </template>
              <template v-else-if="item.recalculation_type === 3">
                <p class="params-section__sub">
                  Пороги остатков
                </p>
                <div
                  v-for="(t, i) in (item.parameters.thresholds ?? [])"
                  :key="i"
                  class="params-section__threshold"
                >
                  <span>≤ {{ t.stock_quantity }} шт → скидка {{ t.extra_discount }}%</span>
                </div>
              </template>
              <template v-else-if="item.recalculation_type === 4">
                <VSidePanelInfoItem
                  caption="Стратегия"
                  :value="strategyLabel(item.parameters.strategy)"
                />
                <VSidePanelInfoItem
                  v-if="item.parameters.strategy === 'cheaper_by'"
                  caption="Дешевле на, %"
                  :value="item.parameters.lower_by_percent"
                />
                <VSidePanelInfoItem
                  v-if="item.parameters.strategy === 'average_plus'"
                  caption="Наценка на среднее, %"
                  :value="item.parameters.markup"
                />
              </template>
              <template v-else-if="item.recalculation_type === 5">
                <VSidePanelInfoItem
                  caption="Начало акции"
                  :value="formatDate(item.parameters.start_date)"
                />
                <VSidePanelInfoItem
                  caption="Конец акции"
                  :value="formatDate(item.parameters.end_date)"
                />
                <VSidePanelInfoItem
                  caption="Скидка акции, %"
                  :value="item.parameters.promo_discount"
                />
                <VSidePanelInfoItem
                  caption="Макс. скидка, %"
                  :value="item.parameters.max_discount"
                />
              </template>
              <template v-else-if="item.recalculation_type === 6">
                <p class="params-section__sub">
                  Уровни лояльности
                </p>
                <div
                  v-for="(lvl, i) in (item.parameters.levels ?? [])"
                  :key="i"
                  class="params-section__threshold"
                >
                  <span>От {{ lvl.min_orders }} заказов → скидка {{ lvl.discount_percent }}%</span>
                </div>
              </template>
              <template v-else-if="item.recalculation_type === 7">
                <VSidePanelInfoItem
                  caption="Шаг округления"
                  :value="item.parameters.step"
                />
                <VSidePanelInfoItem
                  caption="Метод"
                  :value="roundMethodLabel(item.parameters.method)"
                />
              </template>
              <template v-else-if="item.recalculation_type === 8">
                <VSidePanelInfoItem
                  caption="Макс. доп. скидка, %"
                  :value="item.parameters.max_extra"
                />
                <VSidePanelInfoItem
                  caption="Мин. рейтинг"
                  :value="item.parameters.min_rating"
                />
                <VSidePanelInfoItem
                  caption="Макс. рейтинг"
                  :value="item.parameters.max_rating"
                />
              </template>
            </div>
          </div>

          <div class="params-section mt-4">
            <p class="params-section__title">
              Выбор товаров
            </p>
            <VSidePanelInfoItem
              caption="Область"
              :value="selectionTypeLabel(item.product_selection?.selection_type)"
            />
            <template v-if="item.product_selection?.selection_type === 'individual'">
              <VSidePanelInfoItem
                caption="Режим"
                :value="item.product_selection.mode === 'include' ? 'Включить' : 'Исключить'"
              />
              <VSidePanelInfoItem
                caption="Кол-во товаров"
                :value="(item.product_selection.product_ids ?? []).length"
              />
            </template>
            <template v-else-if="item.product_selection?.selection_type === 'groups'">
              <VSidePanelInfoItem
                v-if="(item.product_selection.category_ids ?? []).length"
                caption="Категории (ID)"
                :value="(item.product_selection.category_ids ?? []).join(', ')"
              />
              <VSidePanelInfoItem
                v-if="(item.product_selection.brand_ids ?? []).length"
                caption="Бренды (ID)"
                :value="(item.product_selection.brand_ids ?? []).join(', ')"
              />
            </template>
          </div>

          <VSidePanelInfoItem
            class="mt-4"
            caption="Создан"
            :value="formatDate(item.created_at)"
          />
          <VSidePanelInfoItem
            class="mt-2"
            caption="Обновлен"
            :value="formatDate(item.updated_at)"
          />
        </template>

        <template v-else-if="formModel">
          <h3 class="form-section-title">
            Основные данные
          </h3>

          <VInput
            v-model="formModel.name"
            label="Наименование"
            secondary
            sm
            :error="v$.formModel.name.$errors?.[0]?.$message"
          />

          <div class="auto-textarea mt-7">
            <label class="auto-textarea__label">
              Описание
              <span class="auto-textarea__optional">(необязательно)</span>
            </label>
            <textarea
              ref="descriptionRef"
              v-model="formModel.description"
              class="auto-textarea__input"
              rows="3"
              maxlength="300"
              @input="growDescription"
            />
          </div>

          <VMultiselect
            v-model="formModel.recalculation_type"
            :options="RECALCULATION_TYPES"
            item-name="label"
            primary-key="value"
            label="Тип перерасчета"
            sm
            class="mt-7"
            :error="v$.formModel.recalculation_type.$errors?.[0]?.$message"
            @update:model-value="onTypeChange"
          />

          <VInput
            v-model="formModel.priority"
            label="Приоритет"
            mask="number"
            secondary
            sm
            class="mt-7"
          />

          <VCheckbox
            v-model="formModel.is_active"
            label="Активен"
            :value="true"
            class="mt-7"
          />

          <h3 class="form-section-title mt-7">
            Инициатор запуска
          </h3>

          <VMultiselect
            v-model="formModel.trigger_type"
            :options="TRIGGER_TYPES"
            item-name="label"
            primary-key="value"
            label="Тип инициатора"
            sm
          />

          <template v-if="triggerTypeValue === 'schedule'">
            <VInput
              v-model="formModel.trigger_config.cron"
              label="Cron-выражение (напр. 0 0 * * *)"
              secondary
              sm
              class="mt-7"
              optional
            />
          </template>

          <template v-if="triggerTypeValue === 'event'">
            <VMultiselect
              v-model="formModel.trigger_config.event_type"
              :options="EVENT_TYPES"
              item-name="label"
              primary-key="value"
              label="Тип события"
              sm
              class="mt-7"
              optional
            />
          </template>

          <template v-if="currentType !== null">
            <h3 class="form-section-title mt-7">
              Параметры перерасчета
            </h3>

            <template v-if="currentType === 1">
              <VInput
                v-model="formModel.parameters.currency"
                label="Валюта (напр. USD)"
                secondary
                sm
              />
              <VInput
                v-model="formModel.parameters.old_rate"
                label="Старый курс"
                mask="number"
                secondary
                sm
                class="mt-7"
              />
              <VInput
                v-model="formModel.parameters.new_rate"
                label="Новый курс"
                mask="number"
                secondary
                sm
                class="mt-7"
              />
            </template>

            <template v-else-if="currentType === 2">
              <VInput
                v-model="formModel.parameters.markup_percent"
                label="Наценка, %"
                mask="number"
                secondary
                sm
              />
              <VInput
                v-model="formModel.parameters.markup_fixed"
                label="Фиксированная надбавка, ₽"
                mask="number"
                secondary
                sm
                class="mt-7"
              />
              <div class="mt-7">
                <p class="field-label">
                  Область применения
                </p>
                <div class="flex gap-4 mt-2">
                  <VRadio
                    v-model="formModel.parameters.scope"
                    value="global"
                    name="scope"
                    label="Глобально"
                  />
                  <VRadio
                    v-model="formModel.parameters.scope"
                    value="category"
                    name="scope"
                    label="Категория"
                  />
                  <VRadio
                    v-model="formModel.parameters.scope"
                    value="brand"
                    name="scope"
                    label="Бренд"
                  />
                </div>
              </div>
            </template>

            <template v-else-if="currentType === 3">
              <div>
                <div class="flex items-center justify-between mb-2">
                  <p class="field-label">
                    Пороги остатков
                  </p>
                  <VBtn
                    text="Добавить порог"
                    outlined
                    small
                    @click="addThreshold"
                  />
                </div>
                <div
                  v-for="(t, i) in formModel.parameters.thresholds"
                  :key="i"
                  class="threshold-row"
                >
                  <VInput
                    v-model="t.stock_quantity"
                    label="Кол-во (≤)"
                    mask="number"
                    secondary
                    sm
                    class="flex-1"
                  />
                  <VInput
                    v-model="t.extra_discount"
                    label="Скидка, %"
                    mask="number"
                    secondary
                    sm
                    class="flex-1"
                  />
                  <button
                    type="button"
                    class="threshold-row__remove"
                    @click="removeThreshold(i)"
                  >
                    <VIcon
                      name="trash"
                      class="w-4 h-4"
                    />
                  </button>
                </div>
              </div>
            </template>

            <template v-else-if="currentType === 4">
              <div>
                <p class="field-label">
                  Стратегия
                </p>
                <div class="flex gap-4 mt-2">
                  <VRadio
                    v-model="formModel.parameters.strategy"
                    value="cheaper_by"
                    name="strategy"
                    label="Быть дешевле на X%"
                  />
                  <VRadio
                    v-model="formModel.parameters.strategy"
                    value="average_plus"
                    name="strategy"
                    label="Среднее + наценка"
                  />
                </div>
              </div>
              <VInput
                v-if="formModel.parameters.strategy === 'cheaper_by'"
                v-model="formModel.parameters.lower_by_percent"
                label="Дешевле на, %"
                mask="number"
                secondary
                sm
                class="mt-7"
              />
              <VInput
                v-if="formModel.parameters.strategy === 'average_plus'"
                v-model="formModel.parameters.markup"
                label="Наценка на среднее, %"
                mask="number"
                secondary
                sm
                class="mt-7"
              />
            </template>

            <template v-else-if="currentType === 5">
              <VInput
                v-model="formModel.parameters.start_date"
                label="Начало акции (YYYY-MM-DD)"
                secondary
                sm
                optional
              />
              <VInput
                v-model="formModel.parameters.end_date"
                label="Конец акции (YYYY-MM-DD)"
                secondary
                sm
                class="mt-7"
                optional
              />
              <VInput
                v-model="formModel.parameters.promo_discount"
                label="Скидка акции, %"
                mask="number"
                secondary
                sm
                class="mt-7"
              />
              <VInput
                v-model="formModel.parameters.max_discount"
                label="Макс. скидка, %"
                mask="number"
                secondary
                sm
                class="mt-7"
              />
            </template>

            <template v-else-if="currentType === 6">
              <div>
                <div class="flex items-center justify-between mb-2">
                  <p class="field-label">
                    Уровни лояльности
                  </p>
                  <VBtn
                    text="Добавить уровень"
                    outlined
                    small
                    @click="addLoyaltyLevel"
                  />
                </div>
                <div
                  v-for="(lvl, i) in formModel.parameters.levels"
                  :key="i"
                  class="threshold-row"
                >
                  <VInput
                    v-model="lvl.min_orders"
                    label="Мин. заказов"
                    mask="number"
                    secondary
                    sm
                    class="flex-1"
                  />
                  <VInput
                    v-model="lvl.discount_percent"
                    label="Скидка, %"
                    mask="number"
                    secondary
                    sm
                    class="flex-1"
                  />
                  <button
                    type="button"
                    class="threshold-row__remove"
                    @click="removeLoyaltyLevel(i)"
                  >
                    <VIcon
                      name="trash"
                      class="w-4 h-4"
                    />
                  </button>
                </div>
              </div>
            </template>

            <template v-else-if="currentType === 7">
              <VInput
                v-model="formModel.parameters.step"
                label="Шаг округления"
                mask="number"
                secondary
                sm
              />
              <div class="mt-7">
                <p class="field-label">
                  Метод округления
                </p>
                <div class="flex gap-4 mt-2">
                  <VRadio
                    v-model="formModel.parameters.method"
                    value="ceil"
                    name="method"
                    label="Вверх"
                  />
                  <VRadio
                    v-model="formModel.parameters.method"
                    value="floor"
                    name="method"
                    label="Вниз"
                  />
                  <VRadio
                    v-model="formModel.parameters.method"
                    value="round"
                    name="method"
                    label="До ближайшего"
                  />
                </div>
              </div>
            </template>

            <template v-else-if="currentType === 8">
              <VInput
                v-model="formModel.parameters.max_extra"
                label="Макс. доп. скидка, %"
                mask="number"
                secondary
                sm
              />
              <VInput
                v-model="formModel.parameters.min_rating"
                label="Мин. рейтинг"
                mask="number"
                secondary
                sm
                class="mt-7"
              />
              <VInput
                v-model="formModel.parameters.max_rating"
                label="Макс. рейтинг"
                mask="number"
                secondary
                sm
                class="mt-7"
              />
            </template>
          </template>

          <h3 class="form-section-title mt-7">
            Область применения товаров
          </h3>

          <ProductsSelector
            v-model="formModel.product_selection"
          />
        </template>
      </div>
    </template>

    <template
      v-if="!loading"
      #foot="{ onClose }"
    >
      <div class="flex justify-end gap-3 flex-wrap">
        <VBtn
          v-if="formModel || userHasPermission(Permissions.Delete)"
          :text="formModel ? 'Отменить' : 'Удалить'"
          outlined
          small
          :disabled="saveLoading || executeLoading"
          @click="cancelOrDelete(onClose)"
        />

        <VBtn
          v-if="item && !formModel && userHasPermission(Permissions.Recalculate)"
          text="Выполнить"
          small
          :loading="executeLoading"
          @click="executeNow"
        />

        <VBtn
          v-if="userHasPermission(Permissions.Edit) || userHasPermission(Permissions.Write)"
          :text="formModel ? 'Сохранить' : 'Редактировать'"
          small
          :loading="saveLoading"
          @click="formModel ? saveChanges().then(onClose) : startEditing()"
        />
      </div>
    </template>
  </VSidePanel>
</template>

<script lang="ts" setup>
import { required, helpers } from '@vuelidate/validators';
import { useVuelidate } from '@vuelidate/core';
import { format, parseISO } from 'date-fns';
import { ERRORS } from '@/common/validations';
import { Permissions } from '@/common/types/permissions';
import { userHasPermission } from '@/common/utils/permissions';
import {
  createRecalculationRequest,
  updateRecalculationRequest,
  executeRecalculationRequest,
} from '@/modules/recalculations/api';
import {
  RECALCULATION_TYPES,
  RECALCULATION_TYPE_LABELS,
  TRIGGER_TYPES,
  TRIGGER_TYPE_LABELS,
  EVENT_TYPES,
  DEFAULT_PRODUCT_SELECTION,
} from '@/modules/recalculations/types';
import type { Recalculation, RecalculationType } from '@/modules/recalculations/types';
import ProductsSelector from './ProductsSelector.vue';

// eslint-disable-next-line func-call-spacing, no-spaced-func
const props = withDefaults(defineProps<{
  item?: Recalculation | null;
  fetchItems:() => Promise<void>;
}>(), {
  item: null,
});

// eslint-disable-next-line func-call-spacing, no-spaced-func
const emit = defineEmits<{
  (evt: 'close'): void;
  (evt: 'delete', item: Recalculation): void;
  (evt: 'executed'): void;
}>();

const loading = ref(false);
const saveLoading = ref(false);
const executeLoading = ref(false);
const descriptionRef = ref<HTMLTextAreaElement | null>(null);

const growDescription = () => {
  const el = descriptionRef.value;
  if (!el) return;
  el.style.height = 'auto';
  el.style.height = `${el.scrollHeight}px`;
};

const itemSnapshot = ref<Recalculation | null>(props.item ?? null);

watch(
  () => props.item,
  (val) => {
    if (val) itemSnapshot.value = val;
  },
);

const hasBeenDeleted = ref(false);

const formModel = ref<{
  name: string;
  description: string;
  recalculation_type: any;
  priority: number | string;
  is_active: boolean;
  trigger_type: any;
  trigger_config: Record<string, any>;
  parameters: Record<string, any>;
  product_selection: any;
} | null>(null);

watch(
  () => formModel.value?.description,
  () => nextTick(growDescription),
);

const panelTitle = computed(() => {
  if (!props.item) return 'Создание';
  if (formModel.value) return 'Редактирование';
  return 'Перерасчет';
});

const currentType = computed((): RecalculationType | null => {
  if (!formModel.value) return null;
  const t = formModel.value.recalculation_type;
  return (typeof t === 'object' && t !== null ? t.value : t) as RecalculationType | null;
});

const triggerTypeValue = computed((): string => {
  if (!formModel.value) return '';
  const t = formModel.value.trigger_type;
  return typeof t === 'object' && t !== null ? t.value : (t ?? '');
});

const validationRules = computed(() => ({
  formModel: {
    name: { required: helpers.withMessage(ERRORS.required, required) },
    recalculation_type: { required: helpers.withMessage(ERRORS.required, required) },
  },
}));

const v$ = useVuelidate(validationRules, { formModel });

const defaultParamsByType = (type: number): Record<string, any> => {
  const defaults: Record<number, Record<string, any>> = {
    1: { currency: 'USD', old_rate: 0, new_rate: 0 },
    2: { markup_percent: 0, markup_fixed: 0, scope: 'global' },
    3: { thresholds: [{ stock_quantity: 5, extra_discount: 10 }] },
    4: { strategy: 'cheaper_by', lower_by_percent: 5, markup: 0 },
    5: {
      start_date: '',
      end_date: '',
      promo_discount: 10,
      max_discount: 50,
    },
    6: { levels: [{ min_orders: 5, discount_percent: 5 }] },
    7: { step: 10, method: 'ceil' },
    8: { max_extra: 20, min_rating: 0, max_rating: 5 },
  };
  return defaults[type] ?? {};
};

const onTypeChange = (val: any) => {
  if (!formModel.value) return;
  const typeNum = typeof val === 'object' && val !== null ? val.value : Number(val);
  formModel.value.parameters = defaultParamsByType(typeNum);
};

const startEditing = () => {
  const { item } = props;
  if (!item) return;
  formModel.value = {
    name: item.name,
    description: item.description ?? '',
    recalculation_type:
      RECALCULATION_TYPES.find((t) => t.value === item.recalculation_type)
      ?? item.recalculation_type,
    priority: item.priority,
    is_active: item.is_active,
    trigger_type:
      TRIGGER_TYPES.find((t) => t.value === item.trigger_type) ?? item.trigger_type,
    trigger_config: item.trigger_config ? { ...item.trigger_config } : {},
    parameters: item.parameters
      ? { ...item.parameters }
      : defaultParamsByType(item.recalculation_type),
    product_selection: item.product_selection
      ? { ...item.product_selection }
      : { ...DEFAULT_PRODUCT_SELECTION },
  };
};

if (!props.item) {
  formModel.value = {
    name: '',
    description: '',
    recalculation_type: null,
    priority: 0,
    is_active: true,
    trigger_type: TRIGGER_TYPES[0],
    trigger_config: {},
    parameters: {},
    product_selection: { ...DEFAULT_PRODUCT_SELECTION },
  };
}

const addThreshold = () => {
  if (!formModel.value) return;
  if (!Array.isArray(formModel.value.parameters.thresholds)) {
    formModel.value.parameters.thresholds = [];
  }
  formModel.value.parameters.thresholds.push({ stock_quantity: 0, extra_discount: 0 });
};

const removeThreshold = (index: number) => {
  if (!formModel.value) return;
  formModel.value.parameters.thresholds.splice(index, 1);
};

const addLoyaltyLevel = () => {
  if (!formModel.value) return;
  if (!Array.isArray(formModel.value.parameters.levels)) {
    formModel.value.parameters.levels = [];
  }
  formModel.value.parameters.levels.push({ min_orders: 0, discount_percent: 0 });
};

const removeLoyaltyLevel = (index: number) => {
  if (!formModel.value) return;
  formModel.value.parameters.levels.splice(index, 1);
};

const formatDate = (dateStr: string | null | undefined): string => {
  if (!dateStr) return '—';
  try {
    return format(parseISO(dateStr), 'dd.MM.yyyy HH:mm');
  } catch {
    return dateStr;
  }
};

const eventTypeLabel = (val: string): string =>
  EVENT_TYPES.find((e) => e.value === val)?.label ?? val;

const scopeLabel = (val: string): string => {
  const map: Record<string, string> = {
    global: 'Глобально',
    category: 'Категория',
    brand: 'Бренд',
  };
  return map[val] ?? val;
};

const strategyLabel = (val: string): string => {
  const map: Record<string, string> = {
    cheaper_by: 'Быть дешевле на X%',
    average_plus: 'Среднее + наценка',
  };
  return map[val] ?? val;
};

const roundMethodLabel = (val: string): string => {
  const map: Record<string, string> = {
    ceil: 'Вверх',
    floor: 'Вниз',
    round: 'До ближайшего',
  };
  return map[val] ?? val;
};

const selectionTypeLabel = (val: string): string => {
  const map: Record<string, string> = {
    all: 'Все товары',
    groups: 'По группам',
    individual: 'Точечно',
  };
  return map[val] ?? val ?? '—';
};

const saveChanges = async (): Promise<void> => {
  v$.value.$touch();
  try {
    if (v$.value.$invalid || !formModel.value) {
      throw new Error('Validation failed');
    }

    saveLoading.value = true;

    const typeVal = formModel.value.recalculation_type;
    const triggerVal = formModel.value.trigger_type;

    const recalculationType = typeof typeVal === 'object' && typeVal !== null
      ? typeVal.value
      : Number(typeVal);

    const triggerType = typeof triggerVal === 'object' && triggerVal !== null
      ? triggerVal.value
      : triggerVal;

    let triggerConfig: Record<string, any> | null = null;
    const rawConfig = formModel.value.trigger_config;
    if (rawConfig && Object.keys(rawConfig).length) {
      triggerConfig = {};
      if (rawConfig.cron) {
        triggerConfig.cron = rawConfig.cron;
      }
      const eventType = typeof rawConfig.event_type === 'object' && rawConfig.event_type !== null
        ? rawConfig.event_type.value
        : rawConfig.event_type;
      if (eventType) {
        triggerConfig.event_type = eventType;
      }
    }

    const payload = {
      name: formModel.value.name,
      description: formModel.value.description || null,
      recalculation_type: recalculationType,
      priority: Number(formModel.value.priority) || 0,
      is_active: formModel.value.is_active,
      trigger_type: triggerType,
      trigger_config: triggerConfig,
      parameters: formModel.value.parameters ?? {},
      product_selection:
        formModel.value.product_selection ?? { ...DEFAULT_PRODUCT_SELECTION },
    };

    if (props.item) {
      await updateRecalculationRequest(props.item.id, payload);
    } else {
      await createRecalculationRequest(payload as any);
    }

    await props.fetchItems();
    formModel.value = null;
  } catch (err: any) {
    if (err?.message !== 'Validation failed') {
      console.error(err);
    }
    throw err;
  } finally {
    saveLoading.value = false;
  }
};

const executeNow = async () => {
  if (!props.item) return;
  executeLoading.value = true;
  try {
    await executeRecalculationRequest(props.item.id);
    emit('executed');
  } catch (err) {
    console.error(err);
  } finally {
    executeLoading.value = false;
  }
};

const cancelOrDelete = (onClose: () => void) => {
  if (formModel.value) {
    if (props.item) {
      formModel.value = null;
    } else {
      onClose();
    }
    return;
  }
  hasBeenDeleted.value = true;
  onClose();
};

onBeforeUnmount(() => {
  if (hasBeenDeleted.value && itemSnapshot.value) {
    emit('delete', itemSnapshot.value);
  }
});
</script>

<style lang="scss" scoped>
.content {
  padding-bottom: 16px;
}

.form-section-title {
  @apply text-sm-medium;
  color: theme('colors.additional.300');
  margin-bottom: 8px;
}

.field-label {
  @apply text-sm-regular;
  color: theme('colors.additional.300');
}

.params-section {
  &__title {
    @apply text-sm-medium;
    color: theme('colors.additional.300');
    margin-bottom: 8px;
  }

  &__sub {
    @apply text-xs-medium;
    color: theme('colors.additional.300');
    margin-bottom: 4px;
  }

  &__body {
    display: flex;
    flex-direction: column;
    gap: 4px;
    padding: 10px 12px;
    background: theme('colors.main.50');
    border-radius: 6px;
  }

  &__threshold {
    @apply text-sm-regular;
    color: theme('colors.black');
    padding: 2px 0;
  }
}

.threshold-row {
  display: flex;
  align-items: flex-end;
  gap: 8px;
  margin-bottom: 8px;

  &__remove {
    flex-shrink: 0;
    padding: 6px;
    color: theme('colors.additional.300');
    background: none;
    border: none;
    cursor: pointer;
    transition: color 0.1s;
    margin-bottom: 4px;

    &:hover {
      color: #dc2626;
    }
  }
}

.auto-textarea {
  position: relative;

  &__label {
    @apply text-xs-regular;
    display: block;
    color: theme('colors.additional.300');
    margin-bottom: 2px;
  }

  &__optional {
    @apply text-xs-regular;
    color: theme('colors.additional.200');
    margin-left: 4px;
  }

  &__input {
    @apply text-base-regular;
    display: block;
    width: 100%;
    min-height: 48px;
    padding: 6px 0;
    border: none;
    border-bottom: 1px solid theme('colors.main.200');
    background: transparent;
    resize: none;
    overflow: hidden;
    color: theme('colors.black');
    font-family: inherit;
    transition: border-color 0.15s;

    &:focus {
      outline: none;
      border-bottom-color: theme('colors.main.400');
    }
  }
}
</style>

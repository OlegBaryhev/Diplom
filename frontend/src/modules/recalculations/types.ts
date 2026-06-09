export type RecalculationType = 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8;

export type TriggerType = 'manual' | 'schedule' | 'event';

export type SelectionType = 'all' | 'groups' | 'individual';

export interface ProductSelection {
  selection_type: SelectionType;
  mode: 'include' | 'exclude';
  product_ids: number[];
  category_ids: number[];
  brand_ids: number[];
}

export interface Recalculation {
  id: number;
  name: string;
  description?: string | null;
  recalculation_type: RecalculationType;
  priority: number;
  is_active: boolean;
  trigger_type: TriggerType;
  trigger_config?: Record<string, any> | null;
  parameters: Record<string, any>;
  product_selection: ProductSelection;
  created_at: string;
  updated_at: string;
}

export interface RecalculationCreate {
  name: string;
  description?: string | null;
  recalculation_type: RecalculationType;
  priority: number;
  is_active: boolean;
  trigger_type: TriggerType;
  trigger_config?: Record<string, any> | null;
  parameters: Record<string, any>;
  product_selection: ProductSelection;
}

export type RecalculationUpdate = Partial<RecalculationCreate>;

export interface RecalculationSearchRequest {
  search?: string;
  recalculation_type?: number | null;
  trigger_type?: string | null;
  is_active?: boolean | null;
  sort_by?: string;
  page?: number;
  page_size?: number;
}

export const RECALCULATION_TYPES: { value: RecalculationType; label: string }[] = [
  { value: 1, label: 'Валютный курс' },
  { value: 2, label: 'Себестоимость + наценка' },
  { value: 3, label: 'Скидка по остаткам' },
  { value: 4, label: 'Цена аналогов' },
  { value: 5, label: 'Промо-период' },
  { value: 6, label: 'Накопительная скидка' },
  { value: 7, label: 'Красивые цены' },
  { value: 8, label: 'Скидка по рейтингу' },
];

export const RECALCULATION_TYPE_LABELS: Record<number, string> = Object.fromEntries(
  RECALCULATION_TYPES.map((t) => [t.value, t.label]),
);

export const TRIGGER_TYPES: { value: TriggerType; label: string }[] = [
  { value: 'manual', label: 'Ручной' },
  { value: 'schedule', label: 'По расписанию' },
  { value: 'event', label: 'По событию' },
];

export const TRIGGER_TYPE_LABELS: Record<string, string> = Object.fromEntries(
  TRIGGER_TYPES.map((t) => [t.value, t.label]),
);

export const EVENT_TYPES: { value: string; label: string }[] = [
  { value: 'price_change', label: 'Изменение цены аналога' },
  { value: 'stock_change', label: 'Изменение остатков' },
  { value: 'rating_change', label: 'Изменение рейтинга' },
  { value: 'analog_added', label: 'Добавление аналога' },
  { value: 'exchange_rate_update', label: 'Обновление курса валют' },
];

export const DEFAULT_PRODUCT_SELECTION: ProductSelection = {
  selection_type: 'all',
  mode: 'include',
  product_ids: [],
  category_ids: [],
  brand_ids: [],
};

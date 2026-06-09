export type PriceRecalculationFilter = {
  search?: string;
  min_price?: number;
  max_price?: number;
  category_id?: number;
  brand_id?: number;
  sort_by?: string;
};

export type RelativeCurrentPriceRequest = PriceRecalculationFilter & {
  value: number;
  type: 'rubles' | 'percent';
  name: string;
  description?: string;
};

export type FixedValueRequest = PriceRecalculationFilter & {
  value: number;
  name: string;
  description?: string;
};

export type AverageRelativePriceRequest = PriceRecalculationFilter & {
  value: number;
  type: 'rubles' | 'percent';
  offset: boolean;
  name: string;
  description?: string;
};

export interface RecalculateHistoryItem {
  id: number;
  name: string;
  description?: string | null;
  recalculation_type?: number | null;
  trigger_type?: string | null;
  recalculated_by: string;
  recalculated_at: string;
  parameters: Record<string, any>;
  products_affected_count?: number | null;
  execution_time_ms?: number | null;
}

export interface RecalculateHistorySearchRequest {
  search?: string;
  min_date?: string;
  max_date?: string;
  recalculation_type?: number | null;
  trigger_type?: string | null;
  sort_by?: string;
  page?: number;
  page_size?: number;
}

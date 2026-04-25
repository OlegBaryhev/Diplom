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

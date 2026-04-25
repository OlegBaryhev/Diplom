export type optionsSortBy = '' | 'price_ask' | 'price_desc' | 'name_asc' | 'name_desc';

export interface productFilter {
  search: string,
  min_price?: number | null,
  max_price?: number | null,
  category_id: string,
  sort_by: optionsSortBy,
}

export interface Category {
  id: number;
  name: string;
}

export interface Product {
  id: number;
  name: string;
  description: string;
  price: number;
  category?: Category;
  brand?: string;
}

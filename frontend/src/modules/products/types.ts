export type optionsSortBy = '' | 'price_ask' | 'price_desc' | 'name_asc' | 'name_desc';

export interface productFilter {
  search: string;
  min_price?: number | null;
  max_price?: number | null;
  category_id: string;
  sort_by: optionsSortBy;
}

export interface Category {
  id: number;
  name: string;
}

export interface Brand {
  id: number;
  name: string;
}

export interface ProductImage {
  id: number;
  url: string;
  is_primary: boolean;
  order: number;
}

export interface Product {
  id: number;
  name: string;
  description: string;
  price: number;
  discount: number;
  category?: Category;
  brand?: Brand;
  images: ProductImage[];
}

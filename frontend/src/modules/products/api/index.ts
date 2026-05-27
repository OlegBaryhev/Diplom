import api from '@/api';

import { REMOTE_SERVER_URL } from '@/consts';

export const getCategoriesRequest = () => api.get(`${REMOTE_SERVER_URL}/category/`);
export const getBrandsRequest = () => api.get(`${REMOTE_SERVER_URL}/brand/`);

export const getProductsRequest = (data?: {
  search?: string;
  min_price?: number;
  max_price?: number;
  category_id?: number;
  brand_id?: number;
  sort_by?: string;
  page?: number;
  page_size?: number;
}) => api.post(`${REMOTE_SERVER_URL}/products/search`, data || {});

export const addProductRequest = (data: any) => api.post(`${REMOTE_SERVER_URL}/products`, data);
export const updateProductRequest = (id: string, data: any) => api.put(`${REMOTE_SERVER_URL}/products/${id}`, data);

export const exportProductsRequest = (data: any) => api.post(`${REMOTE_SERVER_URL}/products/export/xlsx`, data, { responseType: 'blob' });

export const deleteProductsRequest = (id: string) => api.delete(`${REMOTE_SERVER_URL}/products/${id}`);

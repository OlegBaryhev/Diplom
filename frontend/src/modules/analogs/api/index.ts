import api from '@/api';

import { REMOTE_SERVER_URL } from '@/consts';

export const getCategoriesRequest = () => api.get(`${REMOTE_SERVER_URL}/category/`);
export const getBrandsRequest = () => api.get(`${REMOTE_SERVER_URL}/brand/`);

export const getAnalogsRequest = (data?: {
  search?: string;
  min_price?: number;
  max_price?: number;
  category_id?: number;
  brand_id?: number;
  sort_by?: string;
}) => api.post(`${REMOTE_SERVER_URL}/analogs/search`, data || {});

export const exportAnalogsRequest = (data: any) => api.post(`${REMOTE_SERVER_URL}/analogs/export/xlsx`, data, { responseType: 'blob' });

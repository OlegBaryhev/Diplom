import api from '@/api';

import { REMOTE_SERVER_URL } from '@/consts';

export const getCategoriesRequest = (data: any) => api.post(`${REMOTE_SERVER_URL}/category/search`, data);

export const exportCategoriesRequest = (data: any) => api.post(`${REMOTE_SERVER_URL}/category/export/xlsx`, data, { responseType: 'blob' });

export const deleteCategoriesRequest = (id: string) => api.delete(`${REMOTE_SERVER_URL}/category/${id}`);

export const addCategoriesRequest = (data: any) => api.post(`${REMOTE_SERVER_URL}/category`, data);
export const updateCategoriesRequest = (id: string, data: any) => api.put(`${REMOTE_SERVER_URL}/category/${id}`, data);

import api from '@/api';

import { REMOTE_SERVER_URL } from '@/consts';

export const getBrandsRequest = (data: any) => api.post(`${REMOTE_SERVER_URL}/brand/search`, data);

export const exportBrandsRequest = (data: any) => api.post(`${REMOTE_SERVER_URL}/brand/export/xlsx`, data, { responseType: 'blob' });

export const deleteBrandsRequest = (id: string) => api.delete(`${REMOTE_SERVER_URL}/brand/${id}`);

export const addBrandsRequest = (data: any) => api.post(`${REMOTE_SERVER_URL}/brand`, data);
export const updateBrandsRequest = (id: string, data: any) => api.put(`${REMOTE_SERVER_URL}/brand/${id}`, data);

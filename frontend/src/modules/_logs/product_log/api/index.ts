import { getLogsRequest, deleteLogRequest } from '@/modules/_logs/api';

export const getProductLogsRequest = (filters: Record<string, any> = {}) =>
  getLogsRequest('product', filters);

export const deleteProductLogRequest = (id: number) =>
  deleteLogRequest('product', id);

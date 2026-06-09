import { getLogsRequest, deleteLogRequest } from '@/modules/_logs/api';

export const getBrandLogsRequest = (filters: Record<string, any> = {}) =>
  getLogsRequest('brand', filters);

export const deleteBrandLogRequest = (id: number) =>
  deleteLogRequest('brand', id);

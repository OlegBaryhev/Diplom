import { getLogsRequest, deleteLogRequest } from '@/modules/_logs/api';

export const getOrderLogsRequest = (filters: Record<string, any> = {}) =>
  getLogsRequest('order', filters);

export const deleteOrderLogRequest = (id: number) =>
  deleteLogRequest('order', id);

import { getLogsRequest, deleteLogRequest } from '@/modules/_logs/api';

export const getCategoryLogsRequest = (filters: Record<string, any> = {}) =>
  getLogsRequest('category', filters);

export const deleteCategoryLogRequest = (id: number) =>
  deleteLogRequest('category', id);

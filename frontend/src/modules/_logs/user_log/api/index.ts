import { getLogsRequest, deleteLogRequest } from '@/modules/_logs/api';

export const getUserLogsRequest = (filters: Record<string, any> = {}) =>
  getLogsRequest('user', filters);

export const deleteUserLogRequest = (id: number) =>
  deleteLogRequest('user', id);

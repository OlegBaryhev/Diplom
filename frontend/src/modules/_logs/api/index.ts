import api from '@/api';
import { REMOTE_SERVER_URL } from '@/consts';

export const getLogsRequest = (tableName: string, filters: Record<string, any> = {}) =>
  api.post(`${REMOTE_SERVER_URL}/logs/${tableName}/search`, filters);

export const deleteLogRequest = (tableName: string, logId: number) =>
  api.delete(`${REMOTE_SERVER_URL}/logs/${tableName}/${logId}`);

export const getLogSettingsRequest = () =>
  api.get(`${REMOTE_SERVER_URL}/logs/settings`);

export const updateLogSettingsRequest = (tableName: string, data: Record<string, any>) =>
  api.put(`${REMOTE_SERVER_URL}/logs/settings/${tableName}`, data);

import api from '@/api';
import { REMOTE_SERVER_URL } from '@/consts';
import type {
  RecalculationCreate,
  RecalculationUpdate,
  RecalculationSearchRequest,
} from '@/modules/recalculations/types';

export const searchRecalculationsRequest = (data: RecalculationSearchRequest) =>
  api.post(`${REMOTE_SERVER_URL}/recalculations/search`, data);

export const createRecalculationRequest = (data: RecalculationCreate) =>
  api.post(`${REMOTE_SERVER_URL}/recalculations/`, data);

export const updateRecalculationRequest = (id: number, data: RecalculationUpdate) =>
  api.put(`${REMOTE_SERVER_URL}/recalculations/${id}`, data);

export const deleteRecalculationRequest = (id: number) =>
  api.delete(`${REMOTE_SERVER_URL}/recalculations/${id}`);

export const executeRecalculationRequest = (id: number) =>
  api.post(`${REMOTE_SERVER_URL}/recalculations/${id}/execute`, {});

export const getRecalculationStatisticsRequest = () =>
  api.get(`${REMOTE_SERVER_URL}/recalculations/statistics`);

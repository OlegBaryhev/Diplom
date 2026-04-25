import api from '@/api';
import { REMOTE_SERVER_URL } from '@/consts';
import {
  RelativeCurrentPriceRequest,
  FixedValueRequest,
  AverageRelativePriceRequest,
  PriceRecalculationFilter,
} from '@/modules/recalculate_history/types';

export const recalculateRelativeCurrentPrice = (data: RelativeCurrentPriceRequest) =>
  api.post(`${REMOTE_SERVER_URL}/recalculate/relative_current_price`, data);

export const recalculateFixedValue = (data: FixedValueRequest) =>
  api.post(`${REMOTE_SERVER_URL}/recalculate/fixed_value`, data);

export const recalculateAverageRelativePrice = (data: AverageRelativePriceRequest) =>
  api.post(`${REMOTE_SERVER_URL}/recalculate/average_relative_price`, data);

export const getRecalculateHistorysRequest = (data: PriceRecalculationFilter) =>
  api.post(`${REMOTE_SERVER_URL}/recalculate_history/search`, data);

export const exportRecalculateHistorysRequest = (data: PriceRecalculationFilter) =>
  api.post(`${REMOTE_SERVER_URL}/recalculate_history/export/xlsx`, data, { responseType: 'blob' });

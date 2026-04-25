import api from '@/api';

import { REMOTE_SERVER_URL } from '@/consts';
import { OrderRead } from '@/modules/orders/types';

export const createOrderByCartRequest = () =>
  api.post<OrderRead>(`${REMOTE_SERVER_URL}/order/create-by-cart`);

export const createOrderRequest = (data: { items: { product_id: number; quantity: number }[] }) =>
  api.post<OrderRead>(`${REMOTE_SERVER_URL}/order`, data);

export const getOrdersRequest = () =>
  api.get<OrderRead[]>(`${REMOTE_SERVER_URL}/order/`);

export const searchOrdersRequest = (data?: {
  search?: string;
  sort_by?: string;
}) => api.post(`${REMOTE_SERVER_URL}/order/search`, data);

export const exportOrdersRequest = (data: any) =>
  api.post(`${REMOTE_SERVER_URL}/order/export/xlsx`, data, { responseType: 'blob' });

export const updateOrderRequest = (id: number, data: any) =>
  api.patch<OrderRead>(`${REMOTE_SERVER_URL}/order/status/${id}`, data);

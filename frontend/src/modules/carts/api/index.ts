import api from '@/api';

import { REMOTE_SERVER_URL } from '@/consts';
import { CartItemCreate, CartItem, CartSearchItem } from '@/modules/carts/types';

/** ------------------------------------------------------------------------------------------- */

export const getCartRequest = () =>
  api.get<CartItem>(`${REMOTE_SERVER_URL}/cart/`);

export const getCartSearchRequest = (data: any) =>
  api.post<CartSearchItem[]>(`${REMOTE_SERVER_URL}/cart/search`, data);

export const addToCartRequest = (data: CartItemCreate) =>
  api.post<CartItem>(`${REMOTE_SERVER_URL}/cart/`, data);

export const removeFromCartRequest = (itemId: number | string) =>
  api.delete<void>(`${REMOTE_SERVER_URL}/cart/from_cart/${itemId}`);

export const setProductQuantity = (
  data: {
    product_id: number;
    quantity: number;
  },
) => api.put<CartItem>(`${REMOTE_SERVER_URL}/cart/me`, data);

export const clearCartRequest = () => api.delete(`${REMOTE_SERVER_URL}/cart/me`);
// export const changeQuantityInCartRequest = () =>
//   api.put<CartItem>(`${REMOTE_SERVER_URL}/cart/`);
/** ------------------------------------------------------------------------------------------- */

import api from '@/api';
import { REMOTE_SERVER_URL } from '@/consts';
import type { registerParams } from '@/common/types';

/**
 * @param email - Эл. Почта
 * @param name - Имя
 * @param password - Пароль
 * @returns { data: access_token },
 */

export const registerRequest = (data: registerParams) => api.post(`${REMOTE_SERVER_URL}/auth/register`, data);
export const loginRequest = (data: registerParams) => api.post(`${REMOTE_SERVER_URL}/auth/token`, data);

export const fetchMyself = () => api.get(`${REMOTE_SERVER_URL}/auth/me`);

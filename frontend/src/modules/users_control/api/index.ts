import api from '@/api';
import { REMOTE_SERVER_URL } from '@/consts';

export const getUsersRequest = (data?: any) => api.post(`${REMOTE_SERVER_URL}/user/search`, data || {});

export const getUserRequest = (userId: number | string) => api.get(`${REMOTE_SERVER_URL}/user/get-user/${userId}/`);

export const getUsersSimple = () => api.get(`${REMOTE_SERVER_URL}/user/list-simplified/`);

export const createUserRequest = (formData: FormData) => api.post(`${REMOTE_SERVER_URL}/user/create`, formData);

export const updateUserRequest = (userId: number | string, formData: FormData) =>
  api.put(`${REMOTE_SERVER_URL}/user/update-user/${userId}`, formData);

export const activateUserRequest = (userId: number | string, activate: boolean) =>
  api.patch(`${REMOTE_SERVER_URL}/user/activate/${userId}`, null, { params: { activate } });

export const deleteUserRequest = (userId: number | string) => api.delete(`${REMOTE_SERVER_URL}/user/delete/${userId}`);

export const exportUsersRequest = (data: any) =>
  api.post(`${REMOTE_SERVER_URL}/user/export/xlsx`, data, { responseType: 'blob' });

export const getRolesRequest = () =>
  api.get(`${REMOTE_SERVER_URL}/roles/`);

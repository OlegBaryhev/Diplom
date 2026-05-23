import api from '@/api';
import { REMOTE_SERVER_URL } from '@/consts';

export const getRolesRequest = (data?: any) =>
  api.post(`${REMOTE_SERVER_URL}/roles/search`, data || {});

export const createRoleRequest = (data: any) =>
  api.post(`${REMOTE_SERVER_URL}/roles/`, data);

export const updateRoleRequest = (roleId: number, data: any) =>
  api.put(`${REMOTE_SERVER_URL}/roles/${roleId}`, data);

export const deleteRoleRequest = (roleId: number) =>
  api.delete(`${REMOTE_SERVER_URL}/roles/${roleId}`);

export const getRoleRequest = (roleId: number) =>
  api.get(`${REMOTE_SERVER_URL}/roles/${roleId}`);

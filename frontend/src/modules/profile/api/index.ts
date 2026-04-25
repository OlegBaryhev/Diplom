import api from '@/api';

import { REMOTE_SERVER_URL } from '@/consts';

export const editUserRequest = (data: {
  name: string,
  surname: string,
  email: string,
}) => api.put(`${REMOTE_SERVER_URL}/auth/edit`, data);

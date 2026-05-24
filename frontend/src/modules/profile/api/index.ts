import api from '@/api';

import { REMOTE_SERVER_URL } from '@/consts';

export const editUserRequest = (data: {
  name: string,
  surname: string,
  email: string,
}) => api.put(`${REMOTE_SERVER_URL}/auth/edit`, data);

export const uploadAvatar = (formData: FormData) => api.post(
  `${REMOTE_SERVER_URL}/auth/upload-avatar`,
  formData,
  {
    headers: { 'Content-Type': 'multipart/form-data' },
  },
).then((res) => res.data);

import axios from 'axios';
import type { AxiosResponse, AxiosRequestConfig, AxiosInstance } from 'axios';
import router from '../router';

const READ_HANG_TIMEOUT = 10000;
const READ_HANG_TIMEOUT_ERROR_MESSAGE = 'READ_HANG_TIMEOUT_ERROR';

const { isAxiosError, isCancel, CancelToken } = axios;

interface CustomAxiosInstance extends AxiosInstance {
  postWithFile: (url: string, data: FormData, config?: AxiosRequestConfig<FormData>) => ReturnType<AxiosInstance['post']>,
  importFile: (url: string, data: FormData, config?: AxiosRequestConfig<FormData>) => ReturnType<AxiosInstance['post']>,
}

const api = axios.create() as CustomAxiosInstance;

api.interceptors.request.use((config) => {
  const handlerOnDownloadProgress = config.onDownloadProgress;

  const source = CancelToken.source();
  config.cancelToken = source.token;

  let lastProgressTimeout: number;

  config.onDownloadProgress = (evt) => {
    if (handlerOnDownloadProgress) {
      handlerOnDownloadProgress(evt);
    }

    clearTimeout(lastProgressTimeout);
    lastProgressTimeout = window.setTimeout(() => {
      source.cancel(READ_HANG_TIMEOUT_ERROR_MESSAGE);
    }, READ_HANG_TIMEOUT);
  };

  return config;
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');

  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }

  return config;
});

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response && error.response.status === 401) {
      localStorage.removeItem('token');
      await router.replace({ name: 'enter' });
    }

    return Promise.resolve(error);
  },
);

api.postWithFile = async (url, data, config) => {
  const file = (data as FormData).get('file') as File;
  data.delete('file');
  const result = await api.post(url, data, config);
  if (file && result.data) {
    await fetch(result.data, {
      method: 'PUT',
      headers: {
        'Content-Type': file.type,
      },
      body: file,
    });
  }

  return result;
};

api.importFile = async (url, data, config) => {
  const file = (data as FormData).get('file') as File;
  data.delete('file');
  const result = await api.get(url, config);
  if (file && result.data?.pre_signed_url) {
    await fetch(result.data?.pre_signed_url, {
      method: 'PUT',
      headers: {
        'Content-Type': file.type,
      },
      body: file,
    });
  }

  return result;
};

export {
  api,
  isAxiosError as isAPIError,
  isCancel as isCancelError,
  AxiosResponse as APIResponse,
};

export default api;

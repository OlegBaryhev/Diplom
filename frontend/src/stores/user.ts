import { defineStore } from 'pinia';
import { loginRequest, fetchMyself } from '@/api/auth';
import type { UserItem } from '@/modules/users_control/types';
import type { registerParams } from '@/common/types';
import { useStoreRouter } from '@/stores/storeRouter';

export const useUser = defineStore('user', () => {
  const user = ref<UserItem | null>(null);
  const token = ref(localStorage.getItem('token') || null);
  const storeRouter = useStoreRouter();
  const { replace } = storeRouter.router;
  const loading = ref<boolean>();

  const getUser = async (): Promise<UserItem | null> => {
    const { data: myselfData } = await fetchMyself();
    user.value = myselfData;
    return Promise.resolve(user.value);
  };

  const login = async (registerData: registerParams, setToken: boolean = true, withReplace: boolean = true): Promise<UserItem | null> => {
    loading.value = true;

    try {
      const req = await loginRequest(registerData);
      if (req?.response?.data?.detail === 'Incorrect email or password') {
        throw new Error(req?.response?.data?.detail);
      }
      if (setToken && req?.data?.access_token) {
        localStorage.setItem('token', req?.data?.access_token);
        token.value = req?.data?.access_token;
        await getUser();
        withReplace && await replace({ name: 'home' });
      }
    } catch (e) {
      console.error(e);
      throw e;
    } finally {
      loading.value = false;
    }

    return Promise.resolve(user.value);
  };

  const resetUser = () => {
    user.value = null;
    token.value = null;
    localStorage.removeItem('token');
  };

  const logout = async (): Promise<void> => {
    resetUser();

    await replace({ name: 'register' });
  };

  return {
    user,
    login,
    token,
    getUser,
    logout,
    resetUser,
    loading,
  };
});

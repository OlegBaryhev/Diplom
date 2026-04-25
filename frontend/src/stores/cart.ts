import { defineStore } from 'pinia';
import {
  getCartRequest,
  removeFromCartRequest,
  addToCartRequest,
} from '@/modules/carts/api';

export const useCart = defineStore('cart', () => {
  const cart = ref<any[]>([]);
  const loading = ref<boolean>(false);
  const isUserReloading = ref<boolean>(false);
  const addingLoading = ref<boolean>(false);

  const reloadCart = async (isUserReload: boolean = false): Promise<void> => {
    (isUserReload ? isUserReloading : loading).value = true;

    try {
      const { data } = await getCartRequest();
      cart.value = data;
    } finally {
      isUserReloading.value = false;
      loading.value = false;
    }
  };

  const addToCart = async (item: any, count: number = 1): Promise<void> => {
    addingLoading.value = true;
    try {
      await addToCartRequest({
        product_id: item?.id,
        quantity: count,
      });
    } finally {
      addingLoading.value = false;
    }
  };

  const removeFromCart = async (itemId: string | number): Promise<void> => {
    await removeFromCartRequest(itemId);
  };

  return {
    cart,
    reloadCart,
    addToCart,
    removeFromCart,
    isUserReloading,
    loading,
  };
});

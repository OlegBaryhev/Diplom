<template>
  <div
    ref="cartRef"
    v-click-away="close"
    class="cart duration-300 ease-in-out"
  >
    <div class="header px-8 py-6">
      <div class="text-lg-semibold flex gap-2 items-center select-none">
        <span
          class="relative w-5 h-5 flex items-center justify-center"
          role="button"
          tabindex="1"
          @click="cartStore.reloadCart(true)"
        >
          <VIcon
            name="refresh"
            class="w-5 h-5 absolute text-main-400"
            :class="{'spinning': cartStore.isUserReloading}"
          />
        </span>
        Корзина
        <Counter
          v-if="itemsToDisplay.length > 0"
          class="ml-2 mr-1"
          :value="itemsToDisplay.length"
        />
      </div>
      <VIcon
        name="close"
        class="cursor-pointer"
        data-test="close-cart"
        @click.stop="close"
      />
    </div>

    <div class="line" />

    <VLoader v-if="useCart.loading" />

    <template v-else-if="itemsToDisplay?.length">
      <div
        v-scroll
        class="h-full"
      >
        <DynamicScroller
          ref="scroller"
          class="h-full cart-scroller"
          key-field="id"
          :prerender="2"
          :min-item-size="60"
          :items="itemsToDisplay"
          :buffer="10"
        >
          <template #default="{ item, index, active }">
            <DynamicScrollerItem
              :item="item"
              :active="!!active"
              :data-index="index"
              :size-dependencies="[ item.popupText ]"
            >
              <CartItem
                :item="item"
                @set-value="updateItemInCart"
                @delete="deleteItemFromCart"
              />
            </DynamicScrollerItem>
          </template>
        </DynamicScroller>
      </div>

      <div class="cart__footer w-full py-4 gap-2 px-4 flex items-center justify-end">
        <VBtn
          text="Очистить"
          outlined
          small
          :loading="clearCartLoading"
          :disabled="cartStore.loading"
          data-test="clear-btn"
          @click="clearCart()"
        />

        <VBtn
          text="Заказать"
          small
          :disabled="clearCartLoading || cartStore.loading"
          data-test="order-btn"
          @click="confirmCart()"
        />
      </div>
    </template>
    <div
      v-else
      class="p-8"
    >
      <div class="px-8 bg-main-50 h-[310px] flex flex-col justify-center items-center rounded-2xl">
        <span class="inline-block mt-4 text-additional-300 text-base-medium">
          У вас пока нет товаров в корзине!
        </span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { OverlayScrollbars } from 'overlayscrollbars';
import CartItem from '@/common/components/VCartList/CartItem.vue';

import {
  setProductQuantity,
  removeFromCartRequest,
  clearCartRequest,
} from '@/modules/carts/api';

import Counter from './Counter.vue';
import { useCart } from '@/stores/cart';

const cartStore = useCart();
const emit = defineEmits(['close', 'confirm-cart']);
const cartRef = ref<HTMLElement | null>(null);
const scroller = ref<any | null>(null);

const itemsToDisplay = computed(() => cartStore.cart ?? []);
const close = () => emit('close');

cartStore.reloadCart();
const vScroll = {
  mounted: (el: HTMLElement) => {
    OverlayScrollbars({
      target: el,
      elements: {
        viewport: scroller.value.$el,
      },
    }, {
      overflow: {
        x: 'visible',
      },
      scrollbars: {
        visibility: 'auto',
      },
    });
  },
};

const updateItemLoading = ref<boolean>(false);
const clearCartLoading = ref<boolean>(false);
const updateItemInCart = async (event: any): Promise<void> => {
  updateItemLoading.value = true;
  try {
    await setProductQuantity({
      product_id: Number(event.item?.product_id),
      quantity: Number(event.value),
    });
  } finally {
    updateItemLoading.value = false;
  }
};

const deleteItemFromCart = async (event: any): Promise<void> => {
  updateItemLoading.value = true;
  try {
    await removeFromCartRequest(event.id);
    cartStore.reloadCart();
  } finally {
    updateItemLoading.value = false;
  }
};

const confirmCart = () => emit('confirm-cart');

const clearCart = async (): Promise<void> => {
  clearCartLoading.value = true;
  try {
    await clearCartRequest();
    cartStore.reloadCart();
  } finally {
    clearCartLoading.value = false;
  }
};
</script>

<script lang="ts">
export default defineComponent({
  name: 'VCartList',
});
</script>

<style lang="scss" scoped>
@use '@/assets/mixins';
@keyframes rotating {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}
.spinning {
  animation: rotating 1s linear infinite;
}

.cart {
  width: 446px;
  height: 446px;
  max-height: 446px;
  box-shadow: 0px 0px 0px 1px rgba(0, 44, 94, 0.001), 0px 10px 20px -4px rgba(57, 80, 105, 0.15);
  border-radius: 12px;
  background-color: theme('colors.white');;
  overflow: hidden;
  display: flex;
  flex-direction: column;

  .header {
    display: flex;
    width: 100%;
    justify-content: space-between;
    height: fit-content;
    padding-right: 28px;
  }

  .line {
    border-bottom: 1px solid theme('colors.additional.200');
    padding: 0 32px;
    margin: 0 -32px;
    margin-top: -1.5px;
    height: fit-content;
    box-shadow: 0px 0px 0px 1px rgba(0, 44, 94, 0.001), 0px 3px 20px -4px rgba(57, 80, 105, 0.15);
  }
}
:deep() .cart-scroller{
  -ms-overflow-style: none;
  scrollbar-width: none;
  &::-webkit-scrollbar {
    display: none;
  }
}
</style>

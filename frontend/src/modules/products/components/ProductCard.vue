<template>
  <div class="product-card">
    <div class="product-card__image">
      <img
        v-if="primaryImage && !imgError"
        :src="fullUrl(primaryImage.url)"
        :alt="product.name"
        class="product-card__img"
        @error="imgError = true"
      >
      <div
        v-else
        class="product-card__img-fallback"
      >
        <VIcon
          name="photo"
          class="product-card__img-icon"
        />
      </div>
    </div>

    <div class="product-card__body">
      <div class="product-card__header">
        <h3 class="product-card__name">
          {{ product.name }}
        </h3>

        <div class="product-card__pricing">
          <template v-if="product.discount > 0">
            <span class="product-card__price-original">
              {{ formatMoney(product.price) }}
            </span>
            <span class="product-card__price-discounted">
              {{ formatMoney(discountedPrice) }}
            </span>
          </template>
          <span
            v-else
            class="product-card__price"
          >
            {{ formatMoney(product.price) }}
          </span>
        </div>
      </div>

      <p class="product-card__description">
        {{ product.description || '—' }}
      </p>
    </div>

    <div class="product-card__actions">
      <VBtn
        v-if="canEdit"
        outlined
        small
        @click="$emit('edit', product)"
      >
        Редактировать
      </VBtn>

      <VBtn
        small
        @click="$emit('buy', product)"
      >
        Купить
      </VBtn>
    </div>
  </div>
</template>

<script lang="ts" setup>
import type { Product } from '../types';
import { formatMoney, calcDiscountedPrice } from '@/common/utils/format';
import { Permissions } from '@/common/types/permissions';
import { userHasPermission } from '@/common/utils/permissions';
import { REMOTE_SERVER_URL } from '@/consts';

const props = defineProps<{ product: Product }>();

defineEmits<{(e: 'edit', product: Product): void;
  (e: 'buy', product: Product): void;
}>();

const imgError = ref(false);

const canEdit = computed(() => userHasPermission(Permissions.Edit) || userHasPermission(Permissions.Write));

const primaryImage = computed(() => props.product.images?.find((img) => img.is_primary) ?? props.product.images?.[0] ?? null);

const discountedPrice = computed(() => calcDiscountedPrice(props.product.price, props.product.discount));

const fullUrl = (url: string) => (url.startsWith('http') ? url : `${REMOTE_SERVER_URL}${url}`);

watch(() => props.product.images, () => { imgError.value = false; });
</script>

<style lang="scss" scoped>
.product-card {
  display: flex;
  flex-direction: column;
  border-radius: 12px;
  border: 1px solid theme('colors.main.200');
  overflow: hidden;
  background: white;
  transition: box-shadow 0.2s;

  &:hover {
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  }

  &__image {
    aspect-ratio: 1 / 1;
    overflow: hidden;
    background: theme('colors.main.50');
    display: flex;
    align-items: center;
    justify-content: center;
  }

  &__img {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }

  &__img-fallback {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 100%;
    height: 100%;
  }

  &__img-icon {
    width: 48px;
    height: 48px;
    color: theme('colors.additional.200');
  }

  &__body {
    flex: 1;
    padding: 12px 14px 8px;
    display: flex;
    flex-direction: column;
    gap: 8px;
  }

  &__header {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    gap: 8px;
  }

  &__name {
    @apply text-sm-medium;
    flex: 1;
    overflow: hidden;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    color: theme('colors.black');
  }

  &__pricing {
    display: flex;
    flex-direction: column;
    align-items: flex-end;
    flex-shrink: 0;
    gap: 2px;
  }

  &__price {
    @apply text-sm-medium;
    color: theme('colors.black');
    white-space: nowrap;
  }

  &__price-original {
    @apply text-xs-regular;
    color: theme('colors.additional.300');
    text-decoration: line-through;
    text-decoration-color: #dc2626;
    white-space: nowrap;
  }

  &__price-discounted {
    @apply text-sm-medium;
    background: #FFF3C4;
    color: #7A5F00;
    border-radius: 6px;
    padding: 2px 7px;
    white-space: nowrap;
  }

  &__description {
    @apply text-xs-regular;
    color: theme('colors.additional.300');
    overflow: hidden;
    display: -webkit-box;
    -webkit-line-clamp: 3;
    -webkit-box-orient: vertical;
    flex: 1;
  }

  &__actions {
    display: flex;
    gap: 8px;
    padding: 8px 14px 14px;
    border-top: 1px solid theme('colors.main.100');
    justify-content: flex-end;
  }
}
</style>

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

      <div
        v-if="product.discount > 0"
        class="product-card__discount-badge"
      >
        -{{ product.discount }}%
      </div>
    </div>

    <div class="product-card__body">
      <p
        v-if="product.category?.name"
        class="product-card__category"
      >
        {{ product.category.name }}
      </p>

      <h3 class="product-card__name">
        {{ product.name }}
      </h3>

      <div class="product-card__pricing">
        <template v-if="product.discount > 0">
          <span class="product-card__price-discounted">
            {{ formatMoney(discountedPrice) }}
          </span>
          <span class="product-card__price-original">
            {{ formatMoney(product.price) }}
          </span>
        </template>
        <span
          v-else
          class="product-card__price"
        >
          {{ formatMoney(product.price) }}
        </span>
      </div>

      <p class="product-card__description">
        {{ product.description || '—' }}
      </p>
    </div>

    <div class="product-card__actions">
      <button
        v-if="canEdit"
        class="product-card__edit-btn"
        title="Редактировать"
        @click="$emit('edit', product)"
      >
        <VIcon
          name="edit"
          class="product-card__edit-icon"
        />
      </button>

      <button
        class="product-card__buy-btn"
        @click="$emit('buy', product)"
      >
        Купить
      </button>
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
  height: 100%;
  border-radius: 16px;
  overflow: hidden;
  background: white;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.06), 0 4px 12px rgba(0, 0, 0, 0.05);
  transition: box-shadow 0.2s, transform 0.2s;

  &:hover {
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1), 0 8px 24px rgba(0, 0, 0, 0.07);
    transform: translateY(-2px);
  }

  &__image {
    aspect-ratio: 4 / 3;
    overflow: hidden;
    background: theme('colors.main.50');
    display: flex;
    align-items: center;
    justify-content: center;
    position: relative;
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
    width: 40px;
    height: 40px;
    color: theme('colors.additional.200');
  }

  &__discount-badge {
    position: absolute;
    top: 10px;
    left: 10px;
    background: #dc2626;
    color: white;
    font-size: 11px;
    font-weight: 700;
    border-radius: 6px;
    padding: 2px 7px;
    letter-spacing: 0.3px;
  }

  &__body {
    flex: 1;
    padding: 14px 16px 10px;
    display: flex;
    flex-direction: column;
    gap: 4px;
  }

  &__category {
    @apply text-xs-regular;
    color: theme('colors.main.DEFAULT');
    text-transform: uppercase;
    letter-spacing: 0.5px;
    font-weight: 600;
    font-size: 10px;
  }

  &__name {
    color: theme('colors.black');
    overflow: hidden;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    margin-top: 2px;
  }

  &__pricing {
    display: flex;
    align-items: baseline;
    gap: 8px;
    margin-top: 6px;
    flex-wrap: wrap;
  }

  &__price {
    @apply text-lg-semibold;
    color: theme('colors.black');
    white-space: nowrap;
  }

  &__price-discounted {
    @apply text-lg-semibold;
    color: theme('colors.black');
    white-space: nowrap;
  }

  &__price-original {
    @apply text-sm-regular;
    color: theme('colors.additional.300');
    text-decoration: line-through;
    text-decoration-color: #dc2626;
    white-space: nowrap;
  }

  &__description {
    @apply text-xs-regular;
    color: theme('colors.additional.300');
    overflow: hidden;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    flex: 1;
    margin-top: 4px;
  }

  &__actions {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 12px 16px 16px;
  }

  &__edit-btn {
    width: 36px;
    height: 36px;
    border-radius: 10px;
    border: 1.5px solid theme('colors.main.200');
    background: white;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    flex-shrink: 0;
    transition: border-color 0.15s, background 0.15s;

    &:hover {
      border-color: theme('colors.main.400');
      background: theme('colors.main.50');
    }
  }

  &__edit-icon {
    width: 16px;
    height: 16px;
    color: theme('colors.main.400');
  }

  &__buy-btn {
    flex: 1;
    height: 36px;
    border-radius: 10px;
    border: none;
    background: theme('colors.main.DEFAULT');
    color: white;
    font-size: 13px;
    font-weight: 600;
    cursor: pointer;
    transition: background 0.15s, transform 0.1s;

    &:hover {
      background: theme('colors.main.400');
    }

    &:active {
      transform: scale(0.98);
    }
  }
}
</style>

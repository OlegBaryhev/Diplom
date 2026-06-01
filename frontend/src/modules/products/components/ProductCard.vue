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

      <h3 class="product-card__name text-base-medium">
        {{ product.name }}
      </h3>

      <div class="product-card__pricing">
        <template v-if="product.discount > 0">
          <span class="product-card__price product-card__price--discounted text-lg-semibold">
            {{ formatMoney(discountedPrice) }}
          </span>
          <span class="product-card__price product-card__price--original text-sm-regular">
            {{ formatMoney(product.price) }}
          </span>
        </template>
        <span
          v-else
          class="product-card__price text-lg-semibold"
        >
          {{ formatMoney(product.price) }}
        </span>
      </div>

      <p class="product-card__description text-sm-regular">
        {{ product.description || '—' }}
      </p>
    </div>

    <div class="product-card__actions">
      <VBtn
        v-if="canEdit"
        ghost
        small
        icon="edit"
        title="Редактировать"
        class="product-card__edit-btn"
        @click="$emit('edit', product)"
      />

      <VBtn
        small
        class="product-card__buy-btn"
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

// eslint-disable-next-line func-call-spacing, no-spaced-func
defineEmits<{
  (e: 'edit', product: Product): void;
  (e: 'buy', product: Product): void;
}>();

const imgError = ref(false);

const canEdit = computed(() =>
  userHasPermission(Permissions.Edit) || userHasPermission(Permissions.Write),
);

const primaryImage = computed(() =>
  props.product.images?.find((img) => img.is_primary) ?? props.product.images?.[0] ?? null,
);

const discountedPrice = computed(() =>
  calcDiscountedPrice(props.product.price, props.product.discount),
);

const fullUrl = (url: string) => (url.startsWith('http') ? url : `${REMOTE_SERVER_URL}${url}`);

watch(() => props.product.images, () => { imgError.value = false; });
</script>

<style lang="scss" scoped>
.product-card {
  display: flex;
  flex-direction: column;
  height: 100%;
  border-radius: 12px;
  overflow: hidden;
  background: theme('colors.white');
  border: 1px solid theme('colors.main.100');
  transition: box-shadow 0.2s;

  &:hover {
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
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
    width: 36px;
    height: 36px;
    color: theme('colors.additional.200');
  }

  &__discount-badge {
    position: absolute;
    top: 8px;
    left: 8px;
    background: #dc2626;
    color: white;
    font-size: 11px;
    font-weight: 700;
    border-radius: 6px;
    padding: 2px 6px;
  }

  &__body {
    flex: 1;
    padding: 12px 14px 8px;
    display: flex;
    flex-direction: column;
    gap: 4px;
  }

  &__category {
    @apply text-xs-medium;
    color: theme('colors.main.400');
    text-transform: uppercase;
    letter-spacing: 0.4px;
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
    margin-top: 4px;
    flex-wrap: wrap;
  }

  &__price {
    color: theme('colors.black');
    white-space: nowrap;

    &--discounted {
      color: theme('colors.black');
    }

    &--original {
      color: theme('colors.additional.300');
      text-decoration: line-through;
      text-decoration-color: #dc2626;
    }
  }

  &__description {
    color: theme('colors.additional.300');
    overflow: hidden;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    flex: 1;
    margin-top: 2px;
  }

  &__actions {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 10px 14px 14px;
  }

  &__edit-btn {
    flex-shrink: 0;
  }

  &__buy-btn {
    flex: 1;
  }
}
</style>

<template>
  <VSidePanel
    class="item-side-panel"
    :title="title"
    :loading="fetchFormOptionsLoading"
    data-test="item-side-panel"
    @close="$emit('close')"
  >
    <template #title>
      <div class="flex gap-3 items-center mb-5">
        <div
          v-if="item"
          class="side-panel-thumb"
        >
          <img
            v-if="primaryImage && !thumbError"
            :src="primaryImage.url"
            :alt="item.name"
            class="side-panel-thumb__img"
            @error="thumbError = true"
          >
          <VIcon
            v-else
            name="photo"
            class="side-panel-thumb__icon"
          />
        </div>

        <VIcon
          v-if="item"
          name="cart"
          data-test="add-to-cart-button"
          class="h-[20px] w-[20px] text-main-300"
          tabindex="1"
          role="button"
          @click="cartStore.addToCart(item)"
        />

        <h3
          v-if="title"
          class="side-panel__title text-2xl-semibold"
        >
          {{ title }}
        </h3>
      </div>
    </template>

    <template
      v-if="!formModel"
      #head
    >
      <VSidePanelInfoItem
        caption="ID"
        :value="item?.id"
        is-head
      />
    </template>

    <template #default>
      <div class="content">
        <template v-if="!formModel">
          <div
            v-if="item"
            class="images-section mb-5"
          >
            <p class="images-section__label">
              Изображения
            </p>
            <VCarousel
              :images="item.images ?? []"
              class="images-section__carousel"
            />
          </div>

          <VSidePanelInfoItem
            class="mb-4"
            caption="Наименование"
            :value="item?.name"
            data-test="product-name"
          />

          <VSidePanelInfoItem
            class="mb-4"
            caption="Цена"
            :value="priceDisplay"
            data-test="product-price"
          />

          <VSidePanelInfoItem
            v-if="item?.discount"
            class="mb-4"
            caption="Скидка"
            :value="`${item.discount}%`"
            data-test="product-discount"
          />

          <VSidePanelInfoItem
            class="mb-4"
            caption="Категория"
            :value="item?.category?.name"
            data-test="product-category"
          />

          <VSidePanelInfoItem
            class="mb-4"
            caption="Бренд"
            :value="item?.brand?.name"
            data-test="product-brand"
          />

          <VSidePanelInfoItem
            class="mb-4"
            caption="Описание"
            :value="item?.description"
            data-test="product-description"
          />
        </template>

        <template v-else>
          <div class="images-section">
            <div class="images-section__header">
              <p class="images-section__label">
                Изображения ({{ totalImageCount }}/10)
              </p>
              <VBtn
                v-if="totalImageCount < 10"
                small
                outlined
                @click="fileInputRef?.click()"
              >
                Добавить
              </VBtn>
            </div>

            <input
              ref="fileInputRef"
              type="file"
              accept="image/jpeg,image/png,image/webp,image/gif"
              multiple
              class="hidden"
              @change="handleFileSelect"
            >

            <div
              v-if="displayImages.length"
              class="images-grid"
            >
              <div
                v-for="img in displayImages"
                :key="img.id"
                class="image-item"
                :class="{
                  'image-item--primary': img.is_primary,
                  'image-item--pending': img.isPending,
                }"
              >
                <img
                  :src="img.url"
                  :alt="props.item?.name"
                  class="image-item__img"
                  @error="(e) => (e.target as HTMLImageElement).style.display = 'none'"
                >
                <div class="image-item__actions">
                  <button
                    v-if="!img.is_primary && (!img.isPending || currentImages.length === 0)"
                    class="image-item__btn"
                    title="Сделать основным"
                    @click="img.isPending ? setPendingPrimary(img.pendingIndex) : setPrimary(img.id)"
                  >
                    <VIcon
                      name="check"
                      class="image-item__btn-icon"
                    />
                  </button>
                  <button
                    class="image-item__btn image-item__btn--danger"
                    title="Удалить"
                    @click="img.isPending ? removePendingImage(img.pendingIndex) : removeImage(img.id)"
                  >
                    <VIcon
                      name="trash"
                      class="image-item__btn-icon"
                    />
                  </button>
                </div>
                <span
                  v-if="img.is_primary"
                  class="image-item__primary-badge"
                >
                  Основное
                </span>
                <span
                  v-if="img.isPending"
                  class="image-item__pending-badge"
                >
                  Новое
                </span>
              </div>
            </div>

            <p
              v-else
              class="images-section__empty"
            >
              Нет изображений
            </p>
          </div>

          <VInput
            v-model="formModel.name"
            class="mt-5"
            label="Наименование"
            secondary
            sm
            :error="v$.formModel.name.$errors?.[0]?.$message || dateApiError"
            @update:model-value="dateApiError = ''"
          />

          <VInput
            v-model="formModel.price"
            class="mt-7"
            label="Цена"
            secondary
            sm
            mask="number"
            :max-length="10"
            :error="unref(v$.formModel.price.$errors[0]?.$message)"
            data-test="price"
          />

          <VInput
            v-model="formModel.discount"
            class="mt-7"
            label="Скидка, %"
            secondary
            sm
            mask="number"
            :max-length="3"
            placeholder="0"
            optional
            :error="discountError"
            data-test="discount"
            @update:model-value="discountError = ''"
          />

          <VMultiselect
            v-model="formModel.category"
            :options="formOptions?.categories"
            item-name="name"
            class="mt-7"
            primary-key="id"
            sm
            label="Категория"
            :error="v$.formModel.category.$errors?.[0]?.$message"
            data-test="select-category"
          />

          <VMultiselect
            v-model="formModel.brand"
            :options="formOptions?.brands"
            item-name="name"
            class="mt-7"
            primary-key="id"
            sm
            label="Бренд"
            :error="v$.formModel.category.$errors?.[0]?.$message"
            data-test="select-brand"
          />

          <VInput
            v-model="formModel.description"
            input-classes="resize-none"
            tag="textarea"
            class="mt-7"
            label="Описание"
            optional
            secondary
            sm
            :max-length="180"
            :error="v$.formModel.description.$errors?.[0]?.$message"
            data-test="description"
          />
        </template>
      </div>
    </template>

    <template
      v-if="!(formModel && fetchFormOptionsLoading)"
      #foot="{ onClose }"
    >
      <div class="flex justify-end space-x-4">
        <VBtn
          v-if="formModel || userHasPermission(Permissions.Delete)"
          :text="formModel ? 'Отменить' : 'Удалить'"
          outlined
          small
          :disabled="saveChangesLoading"
          :data-test="formModel ? 'cancel-editing' : 'delete-item'"
          @click="cancelOrDelete(onClose)"
        />

        <VBtn
          v-if="userHasPermission(Permissions.Edit)"
          :text="formModel ? 'Сохранить' : 'Редактировать'"
          small
          :loading="saveChangesLoading"
          :data-test="formModel ? 'save-changes' : 'start-editing'"
          @click="formModel ? saveOrChange().then(onClose) : startEditing()"
        />
      </div>
    </template>
  </VSidePanel>
</template>

<script lang="ts" setup>
import { onBeforeUnmount, unref } from 'vue';
import { required, helpers } from '@vuelidate/validators';
import { useVuelidate } from '@vuelidate/core';
import { ERRORS } from '@/common/validations';
import type { Product, ProductImage } from '@/modules/products/types';
import { formatMoney, calcDiscountedPrice } from '@/common/utils/format';
import {
  addProductRequest,
  updateProductRequest,
  getCategoriesRequest,
  getBrandsRequest,
  uploadProductImageRequest,
  deleteProductImageRequest,
  setPrimaryImageRequest,
} from '../api';
import { isAPIError } from '@/api';
import { Permissions } from '@/common/types/permissions';
import { userHasPermission } from '@/common/utils/permissions';
import { useCart } from '@/stores/cart';
import { REMOTE_SERVER_URL } from '@/consts';
import VCarousel from '@/common/components/VCarousel.vue';

const cartStore = useCart();

const props = withDefaults(defineProps<{
  item?: Product | null;
  fetchItems:() => Promise<void>;
}>(), {
  item: null,
});

const emits = defineEmits<{(evt: 'close'): void;
  (evt: 'delete', item: Product): void;
}>();

const fullUrl = (url: string) => (url.startsWith('http') ? url : `${REMOTE_SERVER_URL}${url}`);

const currentImages = ref<ProductImage[]>([...(props.item?.images ?? [])]);

interface PendingImage {
  file: File;
  previewUrl: string;
  is_primary: boolean;
}
const pendingImages = ref<PendingImage[]>([]);

const totalImageCount = computed(() => currentImages.value.length + pendingImages.value.length);

const displayImages = computed(() => [
  ...currentImages.value.map((img) => ({
    id: img.id,
    url: fullUrl(img.url),
    is_primary: img.is_primary,
    isPending: false,
    pendingIndex: -1,
  })),
  ...pendingImages.value.map((p, i) => ({
    id: -(i + 1),
    url: p.previewUrl,
    is_primary: p.is_primary,
    isPending: true,
    pendingIndex: i,
  })),
]);

const primaryImage = computed(() => {
  const serverPrimary = currentImages.value.find((img) => img.is_primary) ?? currentImages.value[0] ?? null;
  if (serverPrimary) return { url: fullUrl(serverPrimary.url) };
  const pendingPrimary = pendingImages.value.find((p) => p.is_primary) ?? pendingImages.value[0] ?? null;
  if (pendingPrimary) return { url: pendingPrimary.previewUrl };
  return null;
});

const dateApiError = ref('');
const discountError = ref('');
const thumbError = ref(false);
const hasBeenDeleted = ref<boolean>(false);
const fileInputRef = ref<HTMLInputElement | null>(null);

const formOptions = ref<{ categories: any[]; brands: any[] } | null>(null);

const formModel = ref<{
  name: string;
  description: string;
  price: number | string;
  discount: number | string;
  category: null | any;
  brand: null | any;
} | null>(null);

watch(() => props.item, () => { thumbError.value = false; });
watch(() => props.item?.images, (imgs) => {
  currentImages.value = [...(imgs ?? [])];
}, { deep: true });

onBeforeUnmount(() => {
  pendingImages.value.forEach((p) => URL.revokeObjectURL(p.previewUrl));
  if (hasBeenDeleted.value && props.item) {
    emits('delete', props.item);
  }
});

const title = computed(() => {
  if (!props.item) return 'Добавление';
  return formModel.value ? 'Редактирование' : 'Товар';
});

const priceDisplay = computed(() => {
  if (!props.item) return '';
  if (props.item.discount > 0) {
    const discounted = calcDiscountedPrice(props.item.price, props.item.discount);
    return `${formatMoney(props.item.price)} → ${formatMoney(discounted)}`;
  }
  return formatMoney(props.item.price);
});

const validationRules = computed(() => ({
  formModel: {
    name: { required: helpers.withMessage(ERRORS.required, required) },
    description: { required: helpers.withMessage(ERRORS.required, required) },
    price: { required: helpers.withMessage(ERRORS.required, required) },
    category: { required: helpers.withMessage(ERRORS.required, required) },
  },
}));

const v$ = useVuelidate(validationRules, { formModel });

const fetchFormOptionsLoading = ref(false);

const fetchFormOptions = async (): Promise<void> => {
  fetchFormOptionsLoading.value = true;
  try {
    const { data: categories } = await getCategoriesRequest();
    const { data: brands } = await getBrandsRequest();
    formOptions.value = { categories, brands };
  } catch (err) {
    console.error('Неудачная загрузка опций');
    throw err;
  } finally {
    fetchFormOptionsLoading.value = false;
  }
};

(userHasPermission(Permissions.Edit) || userHasPermission(Permissions.Write)) && fetchFormOptions();

const startEditing = () => {
  formModel.value = {
    name: props.item?.name ?? '',
    description: props.item?.description ?? '',
    price: props.item?.price ?? '',
    discount: props.item?.discount ?? 0,
    category: props.item?.category ?? null,
    brand: props.item?.brand ?? null,
  };
};

if (props.item === null) {
  startEditing();
}

const saveChangesLoading = ref(false);

const handleFileSelect = (e: Event) => {
  const { files } = (e.target as HTMLInputElement);
  if (!files?.length) return;

  const remaining = 10 - totalImageCount.value;
  const toAdd = Array.from(files).slice(0, remaining);

  // eslint-disable-next-line no-restricted-syntax
  for (const file of toAdd) {
    const isPrimary = currentImages.value.length === 0 && pendingImages.value.length === 0;
    pendingImages.value.push({
      file,
      previewUrl: URL.createObjectURL(file),
      is_primary: isPrimary,
    });
  }

  if (fileInputRef.value) fileInputRef.value.value = '';
};

const removePendingImage = (index: number) => {
  const [removed] = pendingImages.value.splice(index, 1);
  URL.revokeObjectURL(removed.previewUrl);
  if (removed.is_primary && currentImages.value.length === 0 && pendingImages.value.length > 0) {
    pendingImages.value[0].is_primary = true;
  }
};

const setPendingPrimary = (index: number) => {
  pendingImages.value.forEach((p, i) => {
    p.is_primary = i === index;
  });
};

const removeImage = async (imageId: number) => {
  if (!props.item) return;
  try {
    await deleteProductImageRequest(props.item.id, imageId);
    currentImages.value = currentImages.value.filter((img) => img.id !== imageId);
    if (currentImages.value.length && !currentImages.value.some((img) => img.is_primary)) {
      currentImages.value[0].is_primary = true;
    }
    if (currentImages.value.length === 0 && pendingImages.value.length > 0) {
      pendingImages.value.forEach((p, i) => { p.is_primary = i === 0; });
    }
  } catch (err) {
    console.error('Ошибка удаления изображения', err);
  }
};

const setPrimary = async (imageId: number) => {
  if (!props.item) return;
  try {
    const { data } = await setPrimaryImageRequest(props.item.id, imageId);
    currentImages.value = data.images ?? [];
    pendingImages.value.forEach((p) => { p.is_primary = false; });
  } catch (err) {
    console.error('Ошибка установки основного изображения', err);
  }
};

const cancelOrDelete = (onClose: () => void) => {
  if (formModel.value && props.item) {
    formModel.value = null;
    pendingImages.value.forEach((p) => URL.revokeObjectURL(p.previewUrl));
    pendingImages.value = [];
    return;
  }
  hasBeenDeleted.value = true;
  onClose();
};

const validateDiscount = (val: number | string): boolean => {
  const n = Number(val);
  if (Number.isNaN(n) || n < 0 || n > 100) {
    discountError.value = 'Скидка от 0 до 100';
    return false;
  }
  discountError.value = '';
  return true;
};

const saveOrChange = async (): Promise<void> => {
  v$.value.$touch();
  try {
    if (!(formOptions.value && formModel.value) || v$.value.$invalid) {
      throw new Error('validation err');
    }
    if (!validateDiscount(formModel.value.discount)) {
      throw new Error('discount err');
    }
    saveChangesLoading.value = true;

    const requestData = {
      name: formModel.value.name ?? '',
      description: formModel.value.description ?? '',
      price: formModel.value.price ?? 0,
      discount: Number(formModel.value.discount) || 0,
      category_id: formModel.value.category?.id ?? null,
      brand_id: formModel.value.brand?.id ?? null,
    };

    let productId: number;
    if (props.item) {
      await updateProductRequest(props.item.id, requestData);
      productId = props.item.id;
    } else {
      const { data: newProduct } = await addProductRequest(requestData);
      productId = newProduct.id;
    }

    // eslint-disable-next-line no-restricted-syntax
    for (const pending of pendingImages.value) {
      const fd = new FormData();
      fd.append('file', pending.file);
      fd.append('is_primary', String(pending.is_primary && currentImages.value.length === 0));
      // eslint-disable-next-line no-await-in-loop
      await uploadProductImageRequest(productId, fd);
    }

    pendingImages.value.forEach((p) => URL.revokeObjectURL(p.previewUrl));
    pendingImages.value = [];

    await props.fetchItems();
  } catch (err: any) {
    console.error(err.message);
    if (!isAPIError(err)) throw err;
    if (err.response?.status === 409) {
      dateApiError.value = 'Такой продукт уже существует';
    }
    throw err;
  } finally {
    saveChangesLoading.value = false;
  }
};
</script>

<style lang="scss" scoped>
.images-section {
  &__label {
    @apply text-sm-medium;
    color: theme('colors.additional.300');
    margin-bottom: 8px;
  }

  &__header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 8px;
  }

  &__carousel {
    width: 100%;
    height: 200px;
    border-radius: 8px;
    overflow: hidden;
  }

  &__empty {
    @apply text-sm-regular;
    color: theme('colors.additional.200');
    text-align: center;
    padding: 16px 0;
  }
}

.images-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 8px;
}

.image-item {
  position: relative;
  aspect-ratio: 1 / 1;
  border-radius: 8px;
  overflow: hidden;
  border: 2px solid transparent;
  background: theme('colors.main.50');

  &--primary {
    border-color: theme('colors.main.400');
  }

  &--pending {
    border-color: theme('colors.additional.200');
    border-style: dashed;
  }

  &--primary#{&}--pending {
    border-color: theme('colors.main.400');
    border-style: dashed;
  }

  &__img {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }

  &__actions {
    position: absolute;
    inset: 0;
    background: rgba(0, 0, 0, 0);
    display: flex;
    align-items: flex-start;
    justify-content: flex-end;
    gap: 4px;
    padding: 4px;
    transition: background 0.15s;
    opacity: 0;

    .image-item:hover & {
      background: rgba(0, 0, 0, 0.35);
      opacity: 1;
    }
  }

  &__btn {
    width: 24px;
    height: 24px;
    border-radius: 4px;
    background: rgba(255, 255, 255, 0.9);
    border: none;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: background 0.1s;

    &:hover {
      background: white;
    }

    &--danger:hover {
      background: #fee2e2;
    }

    &-icon {
      width: 12px;
      height: 12px;
      color: theme('colors.main.400');

      .image-item__btn--danger & {
        color: #dc2626;
      }
    }
  }

  &__primary-badge {
    position: absolute;
    bottom: 4px;
    left: 4px;
    background: theme('colors.main.400');
    color: white;
    font-size: 9px;
    font-weight: 600;
    border-radius: 4px;
    padding: 1px 5px;
  }

  &__pending-badge {
    position: absolute;
    top: 4px;
    left: 4px;
    background: theme('colors.additional.300');
    color: white;
    font-size: 9px;
    font-weight: 600;
    border-radius: 4px;
    padding: 1px 5px;
  }
}

.side-panel-thumb {
  width: 44px;
  height: 44px;
  border-radius: 8px;
  overflow: hidden;
  background: theme('colors.main.50');
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px solid theme('colors.main.100');

  &__img {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }

  &__icon {
    width: 20px;
    height: 20px;
    color: theme('colors.additional.200');
  }
}
</style>

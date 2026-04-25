<template>
  <VSidePanel
    class="item-side-panel"
    :title="title"
    :loading="fetchFormOptionsLoading"
    data-test="item-side-panel"
    @close="$emit('close')"
  >
    <template #title>
      <div class="flex gap-7 items-center mb-5">
        <VIcon
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
      <div
        class="content"
      >
        <template v-if="!formModel">
          <VSidePanelInfoItem
            class="mb-4"
            caption="Наименование"
            :value="item?.name"
            data-test="product-name"
          />

          <VSidePanelInfoItem
            class="mb-4"
            caption="Цена"
            :value="formatMoney(item?.price)"
            data-test="product-price"
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
          <VInput
            v-model="formModel.name"
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
            sn
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
import { onBeforeUnmount } from 'vue';
import { required, helpers } from '@vuelidate/validators';

import { useVuelidate } from '@vuelidate/core';
import {
  ERRORS,
} from '@/common/validations';
import type { Product } from '@/modules/products/types';
import { formatMoney } from '@/common/utils/format';

import {
  addProductRequest,
  updateProductRequest,
  getCategoriesRequest,
  getBrandsRequest,
} from '../api';

import { isAPIError } from '@/api';
import { Permissions } from '@/common/types/permissions';
import { userHasPermission } from '@/common/utils/permissions';
import { useCart } from '@/stores/cart';

const cartStore = useCart();

const props = withDefaults(defineProps<{
  item?: Product | null;
  // eslint-disable-next-line func-call-spacing
  fetchItems:() => Promise<void>;
}>(), {
  item: null,
});

// eslint-disable-next-line func-call-spacing, no-spaced-func
const emits = defineEmits<{
  (evt: 'close'): void;
  (evt: 'delete', item: Product): void;
}>();

const dateApiError = ref('');
const hasBeenDeleted = ref<boolean>(false);

const formOptions = ref<{
  categories: any[];
} | null>(null);

const formModel = ref<{
  name: string,
  description: string,
  price: number | string,
  category: null | any[],
} | null>(null);

onBeforeUnmount(() => {
  if (hasBeenDeleted.value && props.item) {
    emits('delete', props.item);
  }
});

const title = computed(() => {
  if (!props.item) {
    return 'Добавление';
  }

  return formModel.value ? 'Редактирование' : 'Товар';
});

const validationRules = computed(() => ({
  formModel: {
    name: {
      required: helpers.withMessage(ERRORS.required, required),
    },
    description: {
      required: helpers.withMessage(ERRORS.required, required),
    },
    price: {
      required: helpers.withMessage(ERRORS.required, required),
    },
    category: {
      required: helpers.withMessage(ERRORS.required, required),
    },
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
    name: props.item ? props.item?.name ?? '' : '',
    description: props.item ? props.item?.description ?? '' : '',
    price: props.item ? props.item?.price ?? '' : '',
    category: props.item ? props.item?.category ?? '' : '',
    brand: props.item ? props.item?.brand ?? '' : '',
  };
};

if (props.item === null) {
  startEditing();
}

const saveChangesLoading = ref(false);
const cancelOrDelete = (onClose: () => void) => {
  if (formModel.value && props.item) {
    formModel.value = null;
    return;
  }

  hasBeenDeleted.value = true;
  onClose();
};

const saveOrChange = async (): Promise<void> => {
  v$.value.$touch();
  try {
    if (!(formOptions.value && formModel.value) || v$.value.$invalid) {
      throw new Error('validation err');
    }
    saveChangesLoading.value = true;
    const requestData = {
      name: formModel.value?.name ?? '',
      description: formModel.value?.description ?? '',
      price: formModel.value?.price ?? 0,
      category_id: formModel.value?.category?.id ?? null,
      brand_id: formModel.value?.brand?.id ?? null,
    };
    if (props.item) {
      await updateProductRequest(props.item.id, requestData);
    } else {
      await addProductRequest(requestData);
    }
    await props.fetchItems();
  } catch (err) {
    console.error(err.message);
    if (!isAPIError(err)) {
      throw err;
    }
    if (err.response?.status === 409) {
      dateApiError.value = 'Такой продукт уже существует';
    }
    throw err;
  } finally {
    saveChangesLoading.value = false;
  }
};
</script>

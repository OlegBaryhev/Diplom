<template>
  <VSidePanel
    class="item-side-panel"
    :title="title"
    :loading="fetchFormOptionsLoading"
    data-test="item-side-panel"
    @close="$emit('close')"
  >
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
        <VSidePanelInfoItem
          class="mb-4"
          caption="Код получения"
          data-test="order-pickup_code"
        >
          <VCopyInnerText
            :text="item?.pickup_code "
          >
            <template #content>
              {{ item?.pickup_code }}
            </template>
          </VCopyInnerText>
        </VSidePanelInfoItem>

        <VSidePanelInfoItem
          class="mb-4"
          caption="Имя получателя"
          :value="item?.user?.name"
          data-test="order-user-name"
        />

        <VSidePanelInfoItem
          class="mb-4"
          caption="Фамилия получателя"
          :value="item?.user?.surname"
          data-test="order-user-surname"
        />

        <VSidePanelInfoItem
          class="mb-4"
          caption="Email получателя"
          :value="item?.user?.email"
          data-test="order-user-email"
        />

        <VSidePanelInfoItem
          class="mb-4"
          caption="Количество позиций"
          :value="item?.total_product_varieties"
          data-test="order-user-email"
        />

        <VSidePanelInfoItem
          class="mb-4"
          caption="Количество товаров"
          :value="item?.total_product_quantity"
          data-test="order-user-email"
        />

        <VSidePanelInfoItem
          class="mb-4"
          caption="Дата создания"
          :value="formatDate(item?.created_at, 'dd.MM.yy HH:mm')"
          data-test="order-created_at"
        />

        <template v-if="!formModel">
          <VSidePanelInfoItem
            class="mb-4"
            caption="Статус"
            data-test="category-description"
          >
            <VStatus
              :value="item?.status"
              class="mt-1"
            >
              {{ ORDER_STATUS?.[item?.status] }}
            </VStatus>
          </VSidePanelInfoItem>
        </template>

        <template v-else>
          <VMultiselect
            v-model="formModel.status"
            :options="STATUSES"
            item-name="name"
            primary-key="value"
            sm
            label="Статус"
            :loading="filterLoading"
            data-test="order-select-status"
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
import type { Category } from '@/modules/categories/types';

import {
  updateOrderRequest,
} from '../api';

import { formatDate } from '@/common/utils/format';
import { isAPIError } from '@/api';
import { Permissions } from '@/common/types/permissions';
import { userHasPermission } from '@/common/utils/permissions';
import { STATUSES, ORDER_STATUS } from '@/modules/orders/const';

const props = withDefaults(defineProps<{
  item?: Category | null;
  // eslint-disable-next-line func-call-spacing
  fetchItems:() => Promise<void>;
}>(), {
  item: null,
});

// eslint-disable-next-line func-call-spacing, no-spaced-func
const emits = defineEmits<{
  (evt: 'close'): void;
  (evt: 'delete', item: Category): void;
}>();

const dateApiError = ref('');
const hasBeenDeleted = ref<boolean>(false);

const formModel = ref<{ status?: any } | null>(null);

onBeforeUnmount(() => {
  if (hasBeenDeleted.value && props.item) emits('delete', props.item);
});

const title = computed(() => !props.item ? 'Добавление' : (formModel.value ? 'Редактирование' : 'Заказ'));

const startEditing = () => {
  formModel.value = {
    status: STATUSES.find(({ value }) => value === props.item?.status) ?? STATUSES[0],
  };
};

if (props.item === null) startEditing();
const saveChangesLoading = ref(false);

const cancelOrDelete = (onClose: () => void) => {
  if (formModel.value && props.item) {
    formModel.value = null;
    return;
  }
  onClose();
};

const saveOrChange = async (): Promise<void> => {
  try {
    if (!formModel.value) throw new Error('validation err');
    saveChangesLoading.value = true;

    const requestData = {
      status: formModel.value?.status?.value ?? '',
    };

    await updateOrderRequest(props.item.id, requestData);

    await props.fetchItems();
  } catch (err) {
    console.error(err.message);
    if (!isAPIError(err)) {
      throw err;
    }
    if (err.response?.status === 409) {
      dateApiError.value = 'Такая категория уже существует';
    }
    throw err;
  } finally {
    saveChangesLoading.value = false;
  }
};
</script>

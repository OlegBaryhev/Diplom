<template>
  <VSidePanel
    class="item-side-panel"
    :title="title"
    data-test="item-side-panel"
    @close="$emit('close')"
  >
    <template #default>
      <div
        class="content"
      >
        <template v-if="!formModel">
          <VSidePanelInfoItem
            class="mt-4"
            caption="Таблица"
            :value="item?.table_name"
            data-test="settings-table-name"
          />

          <VSidePanelInfoItem
            class="mt-4"
            caption="Хранение (минуты)"
            :value="String(item?.time_retention_minutes ?? '')"
            data-test="settings-time-retention"
          />

          <VSidePanelInfoItem
            class="mt-4"
            caption="Лимит записей"
            :value="String(item?.count_retention_limit ?? '')"
            data-test="settings-count-retention"
          />
        </template>

        <template v-else>
          <VInput
            v-model="formModel.time_retention_minutes"
            label="Хранение (минуты)"
            secondary
            sm
            mask="number"
            :max-length="10"
            data-test="time-retention"
          />

          <VInput
            v-model="formModel.count_retention_limit"
            class="mt-7"
            label="Лимит записей"
            secondary
            sm
            mask="number"
            :max-length="10"
            data-test="count-retention"
          />
        </template>
      </div>
    </template>

    <template #foot>
      <div class="flex justify-end space-x-4">
        <VBtn
          v-if="formModel"
          text="Отменить"
          outlined
          small
          :disabled="saveChangesLoading"
          data-test="cancel-editing"
          @click="formModel = null"
        />

        <VBtn
          v-if="userHasPermission(Permissions.Edit)"
          :text="formModel ? 'Сохранить' : 'Редактировать'"
          small
          :loading="saveChangesLoading"
          :data-test="formModel ? 'save-changes' : 'start-editing'"
          @click="formModel ? saveChanges() : startEditing()"
        />
      </div>
    </template>
  </VSidePanel>
</template>

<script lang="ts" setup>
import { Permissions } from '@/common/types/permissions';
import { userHasPermission } from '@/common/utils/permissions';
import type { ILogSettings } from '@/modules/_logs/types';
import { updateLogSettingsRequest } from '../api';

const props = withDefaults(defineProps<{
  item?: ILogSettings | null;
  fetchItems:() => Promise<void>;
}>(), {
  item: null,
});

// eslint-disable-next-line func-call-spacing, no-spaced-func
const emits = defineEmits<{
  (evt: 'close'): void;
}>();

const title = computed(() => (formModel.value ? 'Редактирование' : 'Настройки'));

const formModel = ref<{
  time_retention_minutes: number | string;
  count_retention_limit: number | string;
} | null>(null);

const saveChangesLoading = ref(false);

const startEditing = () => {
  formModel.value = {
    time_retention_minutes: props.item?.time_retention_minutes ?? 0,
    count_retention_limit: props.item?.count_retention_limit ?? 0,
  };
};

const saveChanges = async () => {
  saveChangesLoading.value = true;

  try {
    await updateLogSettingsRequest(props.item!.table_name, {
      time_retention_minutes: Number(formModel.value?.time_retention_minutes),
      count_retention_limit: Number(formModel.value?.count_retention_limit),
    });
    await props.fetchItems();
    formModel.value = null;
  } catch (error) {
    console.error(error);
    throw error;
  } finally {
    saveChangesLoading.value = false;
  }
};
</script>

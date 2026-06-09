<template>
  <VSidePanel
    class="item-side-panel"
    :title="TITLE"
    data-test="item-side-panel"
    @close="$emit('close')"
  >
    <template #head>
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
          class="mt-4"
          caption="Операция"
          :value="item?.operation"
          data-test="log-operation"
        />

        <VSidePanelInfoItem
          v-if="item"
          class="mt-4"
          caption="Изменено"
          :value="formatDate(item.changed_at, 'dd.MM.yy HH:mm')"
          data-test="log-changed_at"
        />

        <VSidePanelInfoItem
          class="mt-4"
          caption="Данные"
          :value="JSON.stringify(item?.row_data)"
          data-test="log-row"
        />
      </div>
    </template>

    <template
      #foot="{ onClose }"
    >
      <div class="flex justify-end space-x-4">
        <VBtn
          v-if="userHasPermission(Permissions.Delete)"
          text="Удалить"
          outlined
          small
          data-test="delete-item"
          @click="handleDelete(onClose)"
        />
      </div>
    </template>
  </VSidePanel>
</template>

<script lang="ts" setup>
import { Permissions } from '@/common/types/permissions';
import { userHasPermission } from '@/common/utils/permissions';
import { formatDate } from '@/common/utils/format';
import type { ILogData } from '@/modules/_logs/types';

const props = withDefaults(defineProps<{
  item?: ILogData | null;
}>(), {
  item: null,
});

// eslint-disable-next-line func-call-spacing, no-spaced-func
const emits = defineEmits<{
  (evt: 'close'): void;
  (evt: 'delete', item: ILogData): void;
}>();

const TITLE = 'Лог пользователей';

const handleDelete = (onClose: () => void) => {
  if (props.item) {
    emits('delete', props.item);
  }
  onClose();
};
</script>

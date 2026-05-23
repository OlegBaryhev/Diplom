<template>
  <VSidePanel
    class="item-side-panel"
    :title="TITLE"
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
          :value="JSON.stringify(item?.row)"
          data-test="brand-row"
        />
      </div>
    </template>

    <!-- <template
      #foot="{ onClose }"
    >
      <div class="flex justify-end space-x-4">
        <VBtn
          v-if="userHasPermission(Permissions.Delete)"
          text="Удалить"
          outlined
          small
          :disabled="saveChangesLoading"
          data-test="delete-item"
          @click="console.log('Удалить')"
        />
      </div>
    </template> -->
  </VSidePanel>
</template>

<script lang="ts" setup>
import { Permissions } from '@/common/types/permissions';
import { userHasPermission } from '@/common/utils/permissions';
import { formatDate } from '@/common/utils/format';
import type { ILogData } from '@/modules/_logs/types.ts';

const props = withDefaults(defineProps<{
  item?: ILogData | null;
}>(), {
  item: null,
});

// eslint-disable-next-line func-call-spacing, no-spaced-func
const emits = defineEmits<{
  (evt: 'close'): void;
}>();

const TITLE = 'Логи таблицы Брендов';
</script>

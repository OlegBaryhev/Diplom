<template>
  <VTooltip
    :content="tooltipContent"
    hover-tooltip
    right
  >
    <VBtn
      outlined
      icon="file-xls"
      :disabled="localLoading || disabled"
      :loading="localLoading"
      data-test="export-file"
      @click="exportFile"
    />
  </VTooltip>
</template>

<script lang="ts" setup>
import { downloadFileByBlob } from '@/common/utils/download-file';

const props = withDefaults(defineProps<{
  exportFileName?: string;
  exportFunction?:() => void;
  disabled?: boolean;
  loading?: boolean;
  tooltipContent?: string;
  items?: any[];
}>(), {
  exportFileName: 'default',
  tooltipContent: 'Подготовить для экспорта',
});

const ALLOWED_FILE_TYPES_TO_UPLOAD = '.xlsx';
const isExportBtnLoading = ref<boolean>(false);
const localLoading = computed<boolean>(() => isExportBtnLoading.value || props.loading);

const defaultExport = () => {
  downloadFileByBlob(props.items, `${props.exportFileName}${ALLOWED_FILE_TYPES_TO_UPLOAD}`);
};

const exportFile = async (): Promise<void> => {
  if (!props.exportFunction) {
    defaultExport();
    return;
  }

  isExportBtnLoading.value = true;
  try {
    await props.exportFunction();
  } finally {
    isExportBtnLoading.value = false;
  }
};
</script>

<template>
  <VModalWrap
    :modal-id="id"
    :title="title"
    @closed="$emit('closed')"
  >
    <template #modal-body>
      <slot name="body">
        <div v-html="text"></div>
      </slot>
    </template>

    <template #modal-footer>
      <div
        class="flex w-full space-x-4"
        :class="{'justify-end': !secondConfirmationText}"
      >
        <template v-if="loading">
          <div class="h-10 flex items-center space-x-4">
            <VLoader small />

            <p class="text-base-medium text-main-400">
              Загрузка...
            </p>
          </div>
        </template>
        <template v-else>
          <VBtn
            :text="refusalText"
            :class="{'mr-auto': secondConfirmationText}"
            outlined
            small
            data-test="close"
            @click="modalStore.close(id)"
          />

          <VBtn
            v-if="secondConfirmationText"
            :text="secondConfirmationText"
            small
            outlined
            data-test="continueWithoutSave"
            :loading="loading"
            @click="secondConfirm"
          />

          <VBtn
            :text="confirmationText"
            small
            data-test="confirm"
            :loading="loading || outerLoading"
            :disabled="confirmDisabled"
            @click="confirm"
          />
        </template>
      </div>
    </template>
  </VModalWrap>
</template>

<script lang="ts" setup>
import { useModals } from '@/stores/modals';

const modalStore = useModals();
//
// eslint-disable-next-line no-spaced-func
const props = withDefaults(defineProps<{
  id: string;
  title: string;
  text?: string;
  refusalText?: string;
  confirmationText?: string;
  secondConfirmationText?: string;
  // eslint-disable-next-line func-call-spacing
  asyncConfirmationFunc?: (...args: any[]) => Promise<any>;
  secondAsyncConfirmationFunc?: (...args: any[]) => Promise<any>;
  confirmDisabled?: boolean;
  outerLoading?: any;
}>(), {
  text: '',
  refusalText: 'Отменить',
  confirmationText: 'Подтвердить',
  confirmDisabled: false,
});

// eslint-disable-next-line func-call-spacing, no-spaced-func
const emit = defineEmits<{
  (evt: 'closed'): void;
  (evt: 'confirm'): void;
  (evt: 'second-confirm'): void
}>();

const loading = ref(false);

const confirm = async (): Promise<void> => {
  if (props.asyncConfirmationFunc) {
    loading.value = true;

    try {
      await props.asyncConfirmationFunc();

      modalStore.close(props.id);
    } finally {
      emit('confirm');
      loading.value = false;
    }
  } else {
    emit('confirm');

    if (typeof props.outerLoading === 'boolean') {
      watch(() => props.outerLoading, (isLoading) => {
        if (!isLoading) {
          modalStore.close(props.id);
        }
      });
      return;
    }
    modalStore.close(props.id);
  }
};

const secondConfirm = async (): Promise<void> => {
  if (props.secondAsyncConfirmationFunc) {
    loading.value = true;

    try {
      await props.secondAsyncConfirmationFunc();

      modalStore.close(props.id);
    } finally {
      emit('second-confirm');
      loading.value = false;
    }
  } else {
    emit('second-confirm');
    modalStore.close(props.id);
  }
};
</script>

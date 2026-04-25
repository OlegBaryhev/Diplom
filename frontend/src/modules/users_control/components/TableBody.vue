<template>
  <VTableCell
    class="none-system-cell"
    data-test="user-name"
  >
    {{ item?.name }}
  </VTableCell>

  <VTableCell
    class="none-system-cell"
    data-test="user-surname"
  >
    {{ item?.surname }}
  </VTableCell>

  <VTableCell
    class="none-system-cell"
    data-test="user-email"
  >
    {{ item?.email }}
  </VTableCell>

  <VTableCell
    class="none-system-cell"
    data-test="user-role"
  >
    {{ ROLES_LOCALIZATION_NAMES[item?.role] ?? 'Гость' }}
  </VTableCell>

  <VTableCell
    class="none-system-cell"
    data-test="user-status"
  >
    <VStatus
      class="mt-1"
      :value="item.is_active ? 'active' : 'not_activated'"
    >
      {{ item?.is_active ? 'Активный' : 'Не активный' }}
    </VStatus>
  </VTableCell>
</template>
<script lang="ts" setup>
import type { UserItem } from '../types';
import { ROLES_LOCALIZATION_NAMES } from '@/consts';
/**
 * @oaram id
 * @oaram name
 * @oaram description
 */

// eslint-disable-next-line @typescript-eslint/no-unused-vars
const props = defineProps<{ item: UserItem }>();
</script>

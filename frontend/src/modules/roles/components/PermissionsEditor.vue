<template>
  <div class="permissions-editor">
    <div
      v-for="(sectionPerms, sectionName) in localPermissions"
      :key="sectionName"
      class="permission-section mb-6"
    >
      <div class="flex items-center gap-2 justify-between mb-2">
        <VInput
          :model-value="sectionName"
          label="Раздел"
          class="w-full"
          @update:model-value="(val) => updateSectionName(sectionName, val)"
        />

        <VBtn
          class="min-w-max whitespace-nowrap"
          small
          outlined
          @click="removeSection(sectionName)"
        >
          <span class="px-6">Удалить раздел</span>
        </VBtn>
      </div>

      <div class="subsection-list pl-4">
        <div
          v-for="(actions, subName) in sectionPerms"
          :key="subName"
          class="subsection-item mb-4 p-3 rounded-2xl border border-gray-200 bg-gray-50"
        >
          <div class="flex items-center justify-between mb-2">
            <VInput
              :model-value="subName"
              label="Подраздел"
              class="w-48"
              @update:model-value="(val) => updateSubsectionName(sectionName, subName, val)"
            />
            <VBtn
              small
              outlined
              @click="removeSubsection(sectionName, subName)"
            >
              Удалить подраздел
            </VBtn>
          </div>
          <div class="permission-actions flex flex-wrap gap-3">
            <VCheckbox
              v-for="action in availableActions"
              :key="action"
              :model-value="hasAction(sectionName, subName, action)"
              :label="actionLabels[action]"
              @update:model-value="
                toggleAction(sectionName, subName, action, $event)
              "
            />
          </div>
        </div>
        <VBtn
          small
          secondary
          @click="addSubsection(sectionName)"
        >
          Добавить подраздел
        </VBtn>
      </div>
    </div>
    <VBtn @click="addSection">Добавить раздел</VBtn>
  </div>
</template>

<script lang="ts" setup>
const props = defineProps<{
  modelValue: Record<string, Record<string, string[]>>;
}>();

const emit = defineEmits(['update:modelValue']);

const localPermissions = ref(JSON.parse(JSON.stringify(props.modelValue || {})));

const availableActions = [
  'read',
  'write',
  'edit',
  'delete',
  'status',
  'change-role',
  'recalculate',
  'download',
  'buy',
];

const actionLabels: Record<string, string> = {
  read: 'Чтение',
  write: 'Запись',
  edit: 'Редактирование',
  delete: 'Удаление',
  status: 'Статус',
  'change-role': 'Смена роли',
  recalculate: 'Пересчёт',
  download: 'Скачивание',
  buy: 'Покупка',
};

watch(
  localPermissions,
  (newVal) => {
    emit('update:modelValue', newVal);
  },
  { deep: true },
);

const hasAction = (section: string, subsection: string, action: string) =>
  localPermissions.value[section]?.[subsection]?.includes(action) || false;

const toggleAction = (
  section: string,
  subsection: string,
  action: string,
  value: boolean,
) => {
  if (!localPermissions.value[section]) localPermissions.value[section] = {};
  if (!localPermissions.value[section][subsection]) {
    localPermissions.value[section][subsection] = [];
  }

  if (value) {
    if (!localPermissions.value[section][subsection].includes(action)) {
      localPermissions.value[section][subsection].push(action);
    }
  } else {
    localPermissions.value[section][subsection] = localPermissions.value[
      section
    ][subsection].filter((a) => a !== action);
  }
};

const addSection = () => {
  const newSection = `new_section_${Date.now()}`;
  localPermissions.value[newSection] = { default: [] };
};

const removeSection = (section: string) => {
  delete localPermissions.value[section];
};

const addSubsection = (section: string) => {
  const newSub = `new_sub_${Date.now()}`;
  if (!localPermissions.value[section]) localPermissions.value[section] = {};
  localPermissions.value[section][newSub] = [];
};

const removeSubsection = (section: string, subsection: string) => {
  delete localPermissions.value[section][subsection];
  if (Object.keys(localPermissions.value[section]).length === 0) removeSection(section);
};

const updateSectionName = (oldName: string, newName: string) => {
  if (oldName === newName) return;
  const data = localPermissions.value[oldName];
  delete localPermissions.value[oldName];
  localPermissions.value[newName] = data;
};

const updateSubsectionName = (
  section: string,
  oldSub: string,
  newSub: string,
) => {
  if (oldSub === newSub) return;
  const data = localPermissions.value[section][oldSub];
  delete localPermissions.value[section][oldSub];
  localPermissions.value[section][newSub] = data;
};
</script>

import { ref } from 'vue';

// Module-level singleton — shared across all VExpandedPhoto instances
export const activePreviewId = ref<string | null>(null);

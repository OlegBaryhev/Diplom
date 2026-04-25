export const useIconStore = defineStore('icon', () => {
  const iconCache = shallowRef<Record<string, Promise<any>>>({});

  const loadIcon = async (fileName: string): Promise<any> => {
    if (!iconCache.value[fileName]) {
      try {
        const module = await import(`../assets/svg/mono/${fileName}.svg?component`);
        iconCache.value[fileName] = module.default;
      } catch (e) {
        console.error(`Не удалось загрузить иконку ${fileName}:`, e);
        delete iconCache.value[fileName];
      }
    }
    return iconCache.value[fileName];
  };

  return { loadIcon };
});

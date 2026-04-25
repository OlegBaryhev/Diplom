/* eslint-disable no-restricted-globals */

interface WorkerMessage {
  type: 'updateEdit' | 'updateAdd' | 'updateDelete';
  data: any;
}

const cloneDeep = (obj:any) => JSON.parse(JSON.stringify(obj));

const isEqual = (a:any, b:any) => JSON.stringify(a) === JSON.stringify(b);

const sortBy = (arr:any, key:string | number) => arr.slice().sort((a:any, b:any) => (a[key] > b[key] ? 1 : -1));

const processEdit = (data: any) => {
  const { items, edit, primaryKey } = data;
  let newItems = cloneDeep(items);

  if (edit.excludeAccepted && edit.template) {
    newItems = newItems
      .map((el:Record<string, any>) => (!edit.exclude.includes(el?.[primaryKey]) ? { ...el, ...edit.template, isTemporary: true } : el));
    edit.include = edit.include.filter((item:any) => edit.exclude.includes(item?.[primaryKey]));
  }

  edit.include.forEach((el:Record<string, any>) => {
    if (primaryKey in el) {
      const index = newItems.findIndex((item:Record<string, any>) => item[primaryKey] === el?.[primaryKey]);

      newItems[index] = {
        ...newItems[index],
        ...el,
        isTemporary: true,
      };
    }
  });

  return { values: newItems };
};

const processAdd = (data:any) => {
  const { items, add, primaryKey } = data;
  return { values: [...new Map([...add.reverse().map((el:Record<string, any>) => ({ ...el, isTemporary: true })), ...items].map((item) => [item[primaryKey], item])).values()] };
};

const processDelete = (data: any) => {
  const {
    items,
    delete: del,
    primaryKey,
    oldDelete,
    add,
  } = data;

  const filteredAdd = add.filter((item: any) => !del.include.includes(item[primaryKey]));

  const updatedInclude = del.include.filter((key: any) => !add.some((item: any) => item[primaryKey] === key));

  const filteredItems = items.filter((el: Record<string, any>) => {
    if (el?.isAddedItem && del.include.some((key: any) => key === el?.[primaryKey])) {
      return false;
    }
    return !del.include.includes(el?.[primaryKey]);
  });

  if (del.excludeAccepted) {
    const filteredItemsExcl = filteredItems.filter((el: Record<string, any>) => !el?.isAddedItem && (del.exclude.includes(el?.[primaryKey]) && !del.include.includes(el?.[primaryKey])));
    return { values: filteredItemsExcl, add: filteredAdd, deleteInclude: updatedInclude };
  }

  if (!isEqual(sortBy(del.include, primaryKey), sortBy(oldDelete.include, primaryKey)) || del.include.length <= 0) {
    return { values: filteredItems, add: filteredAdd, deleteInclude: updatedInclude };
  }

  return { values: filteredItems, add: filteredAdd, deleteInclude: updatedInclude };
};

self.onmessage = (event: MessageEvent<WorkerMessage>) => {
  const { type, data } = event.data;

  self.postMessage(
    {
      ...{
        updateEdit: processEdit,
        updateAdd: processAdd,
        updateDelete: processDelete,
      }[type](data),
      type,
    },
  );
};

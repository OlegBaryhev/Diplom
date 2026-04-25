export interface ColumnHeader {
  name?: string;
  key: string;
  enable?: boolean;
  sortingDirection?: 'increase' | 'decrease';
  order?: number;
}

export interface ItemChecking<T = any> {
  mode: 'include' | 'exclude';
  ids: T[];
}

export interface ProcessCheckedItems {
  func?: (...args: any[]) => Promise<any>;
  uncheckAllButtonText?: string;
  actionButtonText?: string;
  modalTitle?: string;
  modalText?: string;
  isActionButtonDisabled?: boolean;
}

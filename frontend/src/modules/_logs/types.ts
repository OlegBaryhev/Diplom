export interface ILogData {
  operation: string;
  changed_at: string;
  row: Record<string, any> | string;
}

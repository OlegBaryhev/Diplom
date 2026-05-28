export interface ILogData {
  id: number;
  operation: string;
  changed_at: string;
  row_data: Record<string, any>;
}

export interface ILogSettings {
  table_name: string;
  time_retention_minutes: number;
  count_retention_limit: number;
}

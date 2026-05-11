export interface PermissionAction {
  [subsection: string]: string[] | { allSubsections?: string[] };
}

export interface Role {
  id: number;
  name: string;
  permissions: Record<string, Record<string, string[]>>;
}

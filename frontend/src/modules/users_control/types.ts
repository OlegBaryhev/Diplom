interface roleType {
  name: string;
  value: string;
  text: string;
}

export interface UserBase {
  id: string;
  name?: string;
  email?: string;
  role: roleType;
}

export interface UserItem extends UserBase {
  updated_at?: string;
  created_by?: string;

  created_at?: string;
  updated_by?: string;
  permissions?: Record<string, { allSubsections?: string[]; [key: string]: any }>;
}

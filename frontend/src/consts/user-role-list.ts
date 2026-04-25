import { Permissions } from '@/common/types/permissions';

type UserRole = {
  value: string;
  text: string;
  accessRoutesWithPermissions?: {
    [key: string]: {
      [key: string]: Permissions[];
    }
  };
};

const ALL_PERMISSIONS: Permissions[] = [
  Permissions.Read,
  Permissions.Edit,
  Permissions.Write,
  Permissions.Delete,
  Permissions.Status,
  Permissions.ChangeRole,
  Permissions.Recalculate,
  Permissions.Buy,
  Permissions.Download,
];

export const USER_ROLE_LIST: UserRole[] = [
  {
    value: 'superuser',
    text: 'Администратор',
    accessRoutesWithPermissions: {
      home: { allSubsections: [Permissions.Read] },
      products: { allSubsections: ALL_PERMISSIONS },
      orders: { allSubsections: ALL_PERMISSIONS },
      carts: { allSubsections: ALL_PERMISSIONS },
      profile: { allSubsections: ALL_PERMISSIONS },
      analogs: { allSubsections: ALL_PERMISSIONS },
      recalculate_history: { allSubsections: ALL_PERMISSIONS },
      users_control: { allSubsections: ALL_PERMISSIONS },
      more: { allSubsections: [Permissions.Read] },
      categories: { allSubsections: ALL_PERMISSIONS },
      brands: { allSubsections: ALL_PERMISSIONS },
    },
  },

  {
    value: 'guest',
    text: 'Гость',
    accessRoutesWithPermissions: {
      home: { allSubsections: [Permissions.Read] },
      products: {
        allSubsections: [
          Permissions.Read,
          Permissions.Buy,
        ],
      },
      profile: {
        allSubsections: ALL_PERMISSIONS,
      },
      more: {
        allSubsections: [
          Permissions.Read,
        ],
      },
      categories: {
        allSubsections: [
          Permissions.Read,
        ],
      },
      brands: {
        allSubsections: [
          Permissions.Read,
        ],
      },
    },
  },

  {
    value: 'moderator',
    text: 'Модератор',
    accessRoutesWithPermissions: {
      home: { allSubsections: [Permissions.Read] },
      products: {
        allSubsections: [
          Permissions.Read,
          Permissions.Edit,
          Permissions.Write,
          Permissions.Delete,
          Permissions.Buy,
        ],
      },
      profile: {
        allSubsections: ALL_PERMISSIONS,
      },
      more: {
        allSubsections: [
          Permissions.Read,
        ],
      },
      categories: {
        allSubsections: [
          Permissions.Read,
          Permissions.Edit,
          Permissions.Write,
          Permissions.Delete,
        ],
      },
      brands: {
        allSubsections: [
          Permissions.Read,
          Permissions.Edit,
          Permissions.Write,
          Permissions.Delete,
        ],
      },
      orders: {
        allSubsections: [
          Permissions.Read,
          Permissions.Edit,
          Permissions.Delete,
        ],
      },
    },
  },
];

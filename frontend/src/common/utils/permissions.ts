import type { RouteRecordRaw } from 'vue-router';
import type { RouteMenu } from '@/common/types/menu';
import { USER_ROLE_LIST } from '@/consts/user-role-list';
import { useUser } from '@/stores/user';
import type { Permissions } from '../types/permissions';

export const userHasRouteAccess = (routeAccess: RouteMenu | RouteRecordRaw): boolean => {
  const userStore = useUser();

  const routeName = routeAccess.routeName || routeAccess.name;
  const { path } = routeAccess;

  const [section, subSection] = (path?.split('/')?.slice(1, 3) || routeName?.split('/')?.slice(0, 2) || []);

  const rolePermissions = USER_ROLE_LIST?.find(
    ({ value }) => value === userStore.user?.role,
  )?.accessRoutesWithPermissions;

  return !!(
    rolePermissions?.[routeName]
    || rolePermissions?.[section]?.[subSection]
    || rolePermissions?.[section]?.allSubsections
  );
};

export const userHasPermission = (action: Permissions): boolean => {
  const userStore = useUser();
  const [section, subSection] = (window.location.pathname?.split('/')?.slice(1, 3) || []);

  if (!section && !subSection) return false;

  const rolePermissions = USER_ROLE_LIST?.find(
    ({ value }) => value === userStore.user?.role,
  )?.accessRoutesWithPermissions;

  const curentSectionRolePermissions = rolePermissions?.[section];

  return !!curentSectionRolePermissions?.[subSection]?.includes(action)
    || !!curentSectionRolePermissions?.allSubsections?.includes(action);
};

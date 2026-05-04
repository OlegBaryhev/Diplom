import type { RouteRecordRaw } from 'vue-router';
import type { RouteMenu } from '@/common/types/menu';
import { useUser } from '@/stores/user';
import type { Permissions } from '../types/permissions';

const defaultPermissions = {
  home: { allSubsections: ['read'] },
  products: { allSubsections: ['read', 'buy'] },
};

export const userHasRouteAccess = (routeAccess: RouteMenu | RouteRecordRaw): boolean => {
  const userStore = useUser();
  const userPerms = userStore.user?.permissions || defaultPermissions;

  const routeName = routeAccess.routeName || routeAccess.name;
  const { path } = routeAccess;
  const [section, subSection] = (path?.split('/')?.slice(1, 3) || routeName?.split('/')?.slice(0, 2) || []);

  const sectionPerms = userPerms[section];
  if (!sectionPerms) return false;
  if (sectionPerms.allSubsections) return true;
  if (subSection && sectionPerms[subSection]) return true;
  return false;
};

export const userHasPermission = (action: Permissions): boolean => {
  const userStore = useUser();
  const userPerms = userStore.user?.permissions || defaultPermissions;
  const [section, subSection] = (window.location.pathname?.split('/')?.slice(1, 3) || []);

  if (!section && !subSection) return false;
  const sectionPerms = userPerms[section];
  if (!sectionPerms) return false;

  if (sectionPerms.allSubsections?.includes(action)) return true;
  if (subSection && sectionPerms[subSection]?.includes(action)) return true;
  return false;
};

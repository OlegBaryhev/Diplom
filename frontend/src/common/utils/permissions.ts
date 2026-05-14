import { unref } from 'vue';
import type { RouteRecordRaw } from 'vue-router';
import type { RouteMenu } from '@/common/types/menu';
import { useUser } from '@/stores/user';
import type { Permissions } from '../types/permissions';

export const userHasRouteAccess = (routeAccess: RouteMenu | RouteRecordRaw, parentRouteName?: string): boolean => {
  const userStore = useUser();
  const user = unref(userStore.user);
  if (!user) return false;

  const { permissions } = user;
  if (!permissions) return false;

  const { routeName, name, path } = routeAccess;
  const effectiveRouteName = routeName || name;

  if (effectiveRouteName && permissions[effectiveRouteName]?.all_subsections) return true;
  if (parentRouteName && permissions[parentRouteName]?.[effectiveRouteName as string]) return true;

  const routePath = path?.split('/').filter(Boolean) || [];
  let section = '';
  let subSection = '';

  if (routePath.length >= 2) {
    [section, subSection] = routePath;
  } else if (effectiveRouteName && typeof effectiveRouteName === 'string' && effectiveRouteName.includes('/')) {
    const parts = effectiveRouteName.split('/');
    [section, subSection] = parts;
  } else {
    const [, first, second] = path?.split('/') || [];
    section = first;
    subSection = second;
  }

  if (!section) return false;
  const sectionPerms = permissions[section];
  if (!sectionPerms) return false;
  if (sectionPerms.all_subsections) return true;
  if (subSection && sectionPerms[subSection]) return true;
  return false;
};

export const userHasPermission = (action: Permissions): boolean => {
  const userStore = useUser();
  const user = unref(userStore.user);
  if (!user) return false;

  const { permissions } = user;
  if (!permissions) return false;

  const { pathname } = window.location;
  const [, section, subSection] = pathname.split('/');
  if (!section) return false;

  const sectionPerms = permissions[section];
  if (!sectionPerms) return false;

  if (sectionPerms.all_subsections?.includes(action)) return true;
  if (subSection && sectionPerms[subSection]?.includes(action)) return true;
  return false;
};

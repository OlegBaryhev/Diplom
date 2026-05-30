import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router';
import { useUser } from '@/stores/user';
import { DEFAULT_TITLE } from '@/consts';
import ErrorPage from '@/modules/errors/views/errors.vue';
import { userHasRouteAccess } from '@/common/utils/permissions';
import { LOGS_PAGES } from '@/modules/_logs/routes';

const routes = [
  {
    name: 'MainLayout',
    component: () => import('../layouts/Main.vue'),
    redirect: 'home',
    children: [
      ...LOGS_PAGES,
      {
        path: '/home',
        name: 'home',
        component: () => import('../modules/home/view/index.vue'),
        meta: {
          title: 'Главная - Система ценообразования "Doge Devices"',
          breadcrumb: [{
            to: '',
            text: 'Главная',
          }],
        },
      },
      {
        path: '/products',
        name: 'products',
        component: () => import('../modules/products/view/index.vue'),
        meta: {
          title: 'Продукты - Система ценообразования "Doge Devices"',
          breadcrumb: [{
            to: '',
            text: 'Главная',
          }],
        },
      },
      {
        path: '/roles',
        name: 'roles',
        component: () => import('../modules/roles/view/index.vue'),
        meta: {
          title: 'Роли - Система ценообразования "Doge Devices"',
          requiresAuth: true,
          requiresSuperuser: true,
          breadcrumb: [{
            to: '',
            text: 'Главная',
          }],
        },
      },
      {
        path: '/analogs',
        name: 'analogs',
        component: () => import('../modules/analogs/view/index.vue'),
        meta: {
          title: 'Аналоги - Система ценообразования "Doge Devices"',
          breadcrumb: [{
            to: '',
            text: 'Главная',
          }],
        },
      },
      {
        path: '/categories',
        name: 'categories',
        component: () => import('../modules/categories/view/index.vue'),
        meta: {
          title: 'Категории - Система ценообразования "Doge Devices"',
          breadcrumb: [{
            to: '',
            text: 'Главная',
          }],
        },
      },
      {
        path: '/brands',
        name: 'brands',
        component: () => import('../modules/brands/view/index.vue'),
        meta: {
          title: 'Бренды - Система ценообразования "Doge Devices"',
          breadcrumb: [{
            to: '',
            text: 'Главная',
          }],
        },
      },
      {
        path: '/orders',
        name: 'orders',
        component: () => import('../modules/orders/view/index.vue'),
        meta: {
          title: 'Заказы - Система ценообразования "Doge Devices"',
          breadcrumb: [{
            to: '',
            text: 'Главная',
          }],
        },
      },
      {
        path: '/carts',
        name: 'carts',
        component: () => import('../modules/carts/view/index.vue'),
        meta: {
          title: '"Все корзины" - Система ценообразования "Doge Devices"',
          breadcrumb: [{
            to: '',
            text: 'Главная',
          }],
        },
      },
      {
        path: '/profile',
        name: 'profile',
        component: () => import('../modules/profile/view/index.vue'),
        meta: {
          title: '"Профиль" - Система ценообразования "Doge Devices"',
          breadcrumb: [{
            to: '',
            text: 'Главная',
          }],
          requiresAuth: true,
        },
      },
      {
        path: '/users_control',
        name: 'users_control',
        component: import('../modules/users_control/view/index.vue'),
        meta: {
          requiresAuth: true,
          breadcrumb: [{
            to: '',
            text: 'Главная',
          }],
        },
      },
      {
        path: '/recalculate_history',
        name: 'recalculate_history',
        component: import('../modules/recalculate_history/view/index.vue'),
        meta: {
          requiresAuth: true,
          breadcrumb: [{
            to: '',
            text: 'Главная',
          }],
        },
      },
      {
        path: '/recalculations',
        name: 'recalculations',
        component: () => import('../modules/recalculations/view/index.vue'),
        meta: {
          title: 'Перерасчеты - Система ценообразования "Doge Devices"',
          requiresAuth: true,
          breadcrumb: [{
            to: '',
            text: 'Главная',
          }],
        },
      },
    ],
  },

  {
    path: '/',
    redirect: '/home',
  },

  {
    name: 'AuthLayout',
    component: () => import('../layouts/Auth.vue'),
    path: '',

    children: [
      {
        path: '/register',
        name: 'register',
        component: () => import('../modules/signup/view/index.vue'),
        meta: {
          title: 'Регистрация - Система ценообразования "Doge Devices"',
        },
      },
      {
        path: '/login',
        name: 'login',
        component: () => import('../modules/signin/view/index.vue'),
        meta: {
          title: 'Вход - Система ценообразования "Doge Devices"',
        },
      },
    ],
  },

  {
    name: 'EmptyLayoutName',
    component: () => import('../layouts/Empty.vue'),
    path: '',
    children: [
      {
        path: '/500',
        name: '500',
        component: ErrorPage,
        meta: {
          errorCode: 500,
        },
      },
      {
        path: '/403',
        name: '403',
        component: ErrorPage,
        meta: {
          errorCode: 403,
        },
      },
      {
        path: '/404',
        name: '404',
        component: ErrorPage,
        meta: {
          errorCode: 404,
        },
      },
      {
        path: '/:pathMatch(.*)*',
        name: '404',
        component: ErrorPage,
        meta: {
          errorCode: 404,
        },
      },
    ],
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

router.beforeEach(async (to, from, next): Promise<void> => {
  document.title = to.meta?.title && typeof to.meta?.title === 'string' ? to.meta?.title : DEFAULT_TITLE;

  if (to.query.token && typeof to.query.token === 'string') {
    localStorage.setItem('token', to.query.token);
    if (to.name === 'login' || to.name === 'register') {
      return next({ name: 'home' });
    }
    return next({ name: to.name });
  }

  const userStore = useUser();
  const { token } = userStore;

  if (!token && to.name !== 'login' && to.name !== 'register') {
    return next({ name: 'login' });
  }

  if (token && !userStore.user) {
    await userStore.getUser();
  }

  const currentUser = unref(userStore.user);

  if (token && (to.name === 'login' || to.name === 'register')) {
    return next({ name: 'home' });
  }

  if (currentUser && !userHasRouteAccess({ name: to.name as string, path: to.path } as RouteRecordRaw) && to.name !== '404') {
    console.warn('Access denied to', to.name, 'for user', currentUser.email);
    return next({ name: '404' });
  }

  next();
});

export default router;

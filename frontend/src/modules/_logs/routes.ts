export const LOGS_PAGES = [
  {
    path: '/brand_log',
    name: 'brand_log',
    component: () => import('./brand_log/view/index.vue'),
    meta: {
      title: 'Логи - Система ценообразования "Doge Devices"',
      breadcrumb: [{
        to: '',
        text: 'Главная',
      },
      {
        to: 'logs',
        text: 'Логи',
      }],
    },
  },
  {
    path: '/category_log',
    name: 'category_log',
    component: () => import('./category_log/view/index.vue'),
    meta: {
      title: 'Логи - Система ценообразования "Doge Devices"',
      breadcrumb: [{
        to: '',
        text: 'Главная',
      },
      {
        to: 'logs',
        text: 'Логи',
      }],
    },
  },
  {
    path: '/order_log',
    name: 'order_log',
    component: () => import('./order_log/view/index.vue'),
    meta: {
      title: 'Логи - Система ценообразования "Doge Devices"',
      breadcrumb: [{
        to: '',
        text: 'Главная',
      },
      {
        to: 'logs',
        text: 'Логи',
      }],
    },
  },
  {
    path: '/product_log',
    name: 'product_log',
    component: () => import('./product_log/view/index.vue'),
    meta: {
      title: 'Логи - Система ценообразования "Doge Devices"',
      breadcrumb: [{
        to: '',
        text: 'Главная',
      },
      {
        to: 'logs',
        text: 'Логи',
      }],
    },
  },
  {
    path: '/user_log',
    name: 'user_log',
    component: () => import('./user_log/view/index.vue'),
    meta: {
      title: 'Логи - Система ценообразования "Doge Devices"',
      breadcrumb: [{
        to: '',
        text: 'Главная',
      },
      {
        to: 'logs',
        text: 'Логи',
      }],
    },
  },
];

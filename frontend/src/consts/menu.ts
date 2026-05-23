import type { RouteMenu } from '@/common/typesnu';

export const VERTICAL_MENU: RouteMenu[] = [
  {
    id: 0,
    name: 'Главная',
    svg_name: 'main-page',
    routeName: 'home',
  },
  {
    id: 1,
    name: 'Продукты',
    svg_name: 'all-prices',
    routeName: 'products',
  },
  {
    id: 2,
    name: 'Все корзины',
    svg_name: 'reference-books',
    routeName: 'carts',
  },
  {
    id: 3,
    name: 'Заказы',
    svg_name: 'shelf-prices',
    routeName: 'orders',
  },
  {
    id: 4,
    name: 'Прочие таблицы',
    svg_name: 'db',
    routeName: 'more',
    submenu: [
      {
        id: 5,
        name: 'Категории',
        routeName: 'categories',
      },
      {
        id: 6,
        name: 'Бренды',
        routeName: 'brands',
      },
    ],
  },
  {
    id: 7,
    name: 'Аналоги',
    svg_name: 'rules-setup',
    routeName: 'analogs',
  },
  {
    id: 8,
    name: 'История перерасчетов',
    svg_name: 'clock-thick',
    routeName: 'recalculate_history',
  },
  {
    id: 9,
    name: 'Пользователи',
    svg_name: 'users',
    routeName: 'users_control',
  },
  {
    id: 10,
    name: 'Роли',
    svg_name: 'users',
    routeName: 'roles',
  },
].filter(Boolean) as RouteMenu[];

export const VERTICAL_MENU_BOTTOM: RouteMenu[] = [
  {
    id: 0,
    name: 'Корзина',
    svg_name: 'cart',
    disabled: {
      sidePanel: false,
      mainPage: true,
    },
  },
];

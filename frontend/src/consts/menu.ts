import type { RouteMenu } from '@/common/typesnu';

export const LOGS_PAGES_MENU: RouteMenu[] = [
  {
    id: 11,
    name: 'Логи',
    svg_name: 'archive',
    routeName: 'logs',
    submenu: [
      {
        id: 12,
        name: 'Настройки логгирования',
        routeName: 'logs',
      },
      {
        id: 13,
        name: 'Логи таблицы "Бренды"',
        routeName: 'brand_log',
      },
      {
        id: 14,
        name: 'Логи таблицы "Продукты"',
        routeName: 'product_log',
      },
      {
        id: 15,
        name: 'Логи таблицы "Категории"',
        routeName: 'category_log',
      },
      {
        id: 16,
        name: 'Логи таблицы "Заказы"',
        routeName: 'order_log',
      },
      {
        id: 17,
        name: 'Логи таблицы "Пользователи"',
        routeName: 'user_log',
      },
    ],
  },
];

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
    name: 'Перерасчеты',
    svg_name: 'price-calculating',
    routeName: 'recalculations',
    submenu: [
      {
        id: 18,
        name: 'Управление правилами',
        routeName: 'recalculations',
      },
      {
        id: 19,
        name: 'История перерасчетов',
        routeName: 'recalculate_history',
      },
    ],
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
    svg_name: 'edit',
    routeName: 'roles',
  },
].filter(Boolean) as RouteMenu[];

export const UNITED_VERTICAL_MENU = [...VERTICAL_MENU, ...LOGS_PAGES_MENU];

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

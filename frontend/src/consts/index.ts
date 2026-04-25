/** @description Важные настройки */
export const RENDER_DATE_FORMAT = 'dd.MM.yyyy';

export const REMOTE_SERVER_URL = 'http://localhost:8000';

export const DEFAULT_TITLE = 'Система ценообразования "Doge Devices"';
export const AUTHOR = 'Барышев Олег';

/** @description Пагинация */
export const TABLE_ITEM_COUNT_TO_FETCH = 100;

/**
 * @description Значения для инпута с типом number
 */
export const MAX_INTAGER_VALUE = 9_999_999_999_999;
export const MAX_FLOAT_VALUE = 99_999_999_999.99;

/**
 * --------------------------------------------------
 * @description Дни недели на случай, еслм они поналаьяися
 * @todo Удалить, если я не буду делать "Журнал действий"
 * --------------------------------------------------
 */

export const OPTION_COUNT_TO_SHOW_MASTER_CHECKBOX = 4;
export const OPTION_COUNT_TO_SEARCH = 6;

export const DAYS_OF_WEEK = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье'] as const;
export const SHORT_DAYS_OF_WEEK = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс'] as const;

export const DayOfWeekMatcherToServer = {
  Понедельник: 'monday',
  Пн: 'monday',
  Вторник: 'tuesday',
  Вт: 'tuesday',
  Среда: 'wednesday',
  Ср: 'wednesday',
  Четверг: 'thursday',
  Чт: 'thursday',
  Пятница: 'friday',
  Пт: 'friday',
  Суббота: 'saturday',
  Сб: 'saturday',
  Воскресенье: 'sunday',
  Вс: 'sunday',
} as const;

export const DayOfWeekMatcherToClient = {
  monday: 'Понедельник',
  tuesday: 'Вторник',
  wednesday: 'Среда',
  thursday: 'Четверг',
  friday: 'Пятница',
  saturday: 'Суббота',
  sunday: 'Воскресенье',
} as const;

export const DayOfWeekMatcherToShortClient = {
  monday: 'Пн',
  tuesday: 'Вт',
  wednesday: 'Ср',
  thursday: 'Чт',
  friday: 'Пт',
  saturday: 'Сб',
  sunday: 'Вс',
} as const;

/** ------------------------------------------------------------ */

export const ROLES_LOCALIZATION_NAMES = {
  superuser: 'Администратор',
  moderator: 'Модератор',
  guest: 'Гость',
};

export const ROLES_LOCALIZATION_NAMES_LIST = (user_role: any) => ([
  ...(user_role === 'superuser' ? [{ value: 'superuser', name: 'Администратор' }] : []),
  { value: 'moderator', name: 'Модератор' },
  { value: 'guest', name: 'Гость' },
]);

export const USER_STATUS_LIST = [
  { value: 1, name: 'Активный' },
  { value: 0, name: 'Не активный' },
];

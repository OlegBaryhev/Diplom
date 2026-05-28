import {
  format,
  parseISO,
  fromUnixTime,
  parse,
  formatISO,
  getUnixTime,
  hoursToSeconds,
  minutesToSeconds,
  secondsToHours,
  secondsToMinutes,
} from 'date-fns';

import { utcToZonedTime, zonedTimeToUtc } from 'date-fns-tz';

import { ru } from 'date-fns/locale';
import { isNil } from 'lodash';

export const formatMoney = (kopecks?: number | null, withoutCurrency?: boolean): string => {
  if (isNil(kopecks)) {
    return '';
  }

  const rubles = kopecks / 100;

  return rubles.toLocaleString('ru-RU', {
    minimumFractionDigits: Number.isInteger(rubles) ? 0 : 2,
    ...(withoutCurrency ? {} : { style: 'currency', currency: 'RUB' }),
  });
};

const numberFormatter = new Intl.NumberFormat('ru-RU');

export const formatNumber = (number?: number | null): string => isNil(number) ? '' : numberFormatter.format(number);

export const toNormalNumber = (formattedNumber: string): number => Number(formattedNumber.replace(/\s/g, '').replace(',', '.'));

export const formatDate = (date: Date | string | number, formatStr = 'PP'): string => {
  if (!date) {
    return '';
  }

  let dateObject;

  switch (typeof date) {
    case 'string': dateObject = zonedTimeToUtc(new Date(date), 'Europe/Moscow'); break;
    case 'number': dateObject = fromUnixTime(date); break;
    default: dateObject = date;
  }

  return format(utcToZonedTime(dateObject, 'Europe/Moscow'), formatStr, {
    locale: ru,
  });
};

export const formatDateToMoscowTimeZone = (dateValue: Date | string | number, formatStr = 'PP'): string => {
  if (!dateValue) {
    return '';
  }

  let date;

  if (typeof dateValue === 'string') {
    date = parseISO(dateValue);
  } else if (typeof dateValue === 'number') {
    date = new Date(dateValue);
  } else if (dateValue instanceof Date) {
    date = dateValue;
  } else {
    throw new Error('Неверный формат даты. Ожидается строка ISO, число миллисекунд или объект Date');
  }

  const dateWithTimezone = utcToZonedTime(date, 'Europe/Moscow');

  return format(dateWithTimezone, formatStr);
};

export const fromDatepickerFormatToDate = (date: string): Date => parse(date, 'dd.MM.yyyy', new Date());

export const fromDatepickerFormatToISO = (
  date: string,
  options: Parameters<typeof formatISO>[1] = { representation: 'date' },
): string => formatISO(fromDatepickerFormatToDate(date), options);

export const fromDatepickerFormatToUnixTime = (date: string): number => getUnixTime(fromDatepickerFormatToDate(date));

export const fromDatepickerFormatToUnixTimePeriod = ([beginDateRaw, endDateRaw]: [string?, string?]): [number?, number?] => {
  const beginDateUnixTime = beginDateRaw ? fromDatepickerFormatToUnixTime(beginDateRaw) : undefined;
  const endDate = endDateRaw ? fromDatepickerFormatToDate(endDateRaw) : undefined;

  if (endDate) {
    endDate.setHours(23, 59, 59, 999);
  }

  const endDateUnixTime = endDate && getUnixTime(endDate);

  return [beginDateUnixTime, endDateUnixTime];
};

export const toDatepickerFormat = (date: Date | string | number): string => formatDate(date, 'dd.MM.yyyy');

export const getFormattedUpdateDate = (
  updatedBy?: string | null,
  createdBy?: string | null,
  updated?: string | number | null,
  created?: string | number | null,
): string => {
  const unionOfUpdatedBy = updatedBy || createdBy;
  const unionOfUpdated = updated || created;

  return `${unionOfUpdatedBy ? `${unionOfUpdatedBy} ` : ''}${
    unionOfUpdated ? formatDate(unionOfUpdated, 'dd.MM.yyyy HH:mm') : ''}`;
};

export const fromTimeToSeconds = (time: string): number => {
  const [hours, minutes] = time.split(':').map(Number);
  return hoursToSeconds(hours) + minutesToSeconds(minutes);
};

export const fromSecondsToTime = (seconds: number): string => {
  const hours = secondsToHours(seconds);
  const minutes = secondsToMinutes(seconds - hoursToSeconds(hours));

  return `${String(hours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}`;
};

export const getDayTime = (seconds: number): string => {
  let hours = secondsToHours(seconds);
  const minutes = secondsToMinutes(seconds - hoursToSeconds(hours));

  if (hours < 0) hours += 24;
  if (hours >= 24) hours -= 24;

  return `${String(hours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}`;
};

export const getDayUnixTime = (time: string): number => {
  // eslint-disable-next-line prefer-const
  let [hours, minutes] = time.split(':').map(Number);

  if (hours < 0) hours += 24;
  if (hours >= 24) hours -= 24;
  return hoursToSeconds(hours) + minutesToSeconds(minutes);
};

export const getInitialsFormat = (surname: string | null | undefined, name: string | null | undefined) => `${surname || ''} ${name && name[0] ? `${name[0].toUpperCase()}.` : ''}`;

export const calcDiscountedPrice = (priceKopecks: number, discountPercent: number): number =>
  Math.round(priceKopecks * (1 - discountPercent / 100));

export const formatBool = (value:boolean, options?: { trueValue?: string; falseValue?: string }): string => {
  const defaultOptions = {
    trueValue: 'Да',
    falseValue: 'Нет',
  };
  const $options = { ...defaultOptions, ...options };

  return value ? $options.trueValue : $options.falseValue;
};

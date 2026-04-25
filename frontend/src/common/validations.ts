import type { ValidationRule, ValidatorResponse } from '@vuelidate/core';
import { helpers } from '@vuelidate/validators';
import { dateIsValid } from '@/common/utils/date';

export type SimpleValidatorFn<T = any> = (value: T) => boolean | ValidatorResponse | Promise<boolean | ValidatorResponse>;

export const requiredDate: SimpleValidatorFn = (value: string[] | string): boolean => helpers.req(value) && /\d/.test(value.toString());

export const oneDate: SimpleValidatorFn = (value: string): boolean => !requiredDate(value) || dateIsValid(value);

export const twoDates: SimpleValidatorFn = (value: string[]): boolean => !requiredDate(value) || dateIsValid(value[0]) && dateIsValid(value[1]);

export const validTimeShort = (value: string): boolean => /^(?:[01]?\d|2[0-3])(?::[0-5]\d){1,2}$/gm.test(value);
export const validTimeRange = (value: string): boolean => {
  const regex = /^([01]\d|2[0-3]):([0-5]\d) - ([01]\d|2[0-3]):([0-5]\d)$/;
  const match = value.match(regex);
  if (!match) return false;
  const [startHour, startMinute, endHour, endMinute] = match.slice(1).map(Number);
  const startMinutes = startHour * 60 + startMinute;
  const endMinutes = endHour * 60 + endMinute;
  return startMinutes < endMinutes;
};
export const validTime = (value: string): boolean => /^(?:[01]?\d|2[0-3])\s(?::\s[0-5]\d){1,2}$/gm.test(value);

export const anyRadioSelected: ValidationRule = (value: any): boolean => value !== null;

export const validSigma = (value: string): boolean => /]/.test(value);

export const validEmail: SimpleValidatorFn = (value: string): boolean | ValidatorResponse => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value);

export const checkLength = (value:string, lenght: number) => value?.length >= lenght;

export const ERRORS = {
  oneDate: 'Укажите дату',
  twoDates: 'Укажите обе даты',
  nonuniqueSubsection: 'Наименование подраздела уже существует',
  dateValid: 'Дата не существует',
  email: 'Введите email',
  required: 'Обязательное поле',
  integer: 'Число должно быть целым',
  time: 'Время должно быть формата 00:00',
  timeRange: 'Время начала должно быть не раньше времени окончания',
  userAlreadyExist: 'Пользователь с такой учетной записью уже существует',
  checkLength: (length: number) => `Длина значения должна быть больше или равно ${length}`,
  between: (from: number, to: number) => `Введите число от ${from} до ${to}`,
  dateStartNotCorrect: 'Дата начала должна быть меньше даты окончания',
  dateEndNotCorrect: 'Дата окончания должна быть больше даты начала',
  nonuniqueLocality: 'Такой населенный пункт уже существует',
};

import { isValid, parse } from 'date-fns';

export const dateIsValid = (dateToCheck: string) => !!dateToCheck && dateToCheck?.split('.').join('').length === 8;

export const addDays = (date: Date, days:number = 1) => {
  date && date.setDate(date.getDate() + days);
  return date;
};

export const newDate = (date: string) => {
  if (!dateIsValid(date)) {
    return '';
  }

  const dateParse = parse(date, 'dd.MM.yyyy', new Date());

  return isValid(dateParse) ? dateParse : '';
};

import { describe, it, expect } from 'vitest';
import { numWord } from './numWord';

describe('numWord', () => {
  const words: [string, string, string] = ['товар', 'товара', 'товаров'];

  it('возвращает единственную форму для числа 1', () => {
    expect(numWord(1, words)).toBe('товар');
  });

  it('возвращает форму для чисел 2–4 при значении 3', () => {
    expect(numWord(3, words)).toBe('товара');
  });

  it('возвращает undefined при передаче нуля', () => {
    expect(numWord(0, words)).toBeUndefined();
  });

  it('возвращает форму множественного числа для числа 11 (исключение «тин»)', () => {
    expect(numWord(11, words)).toBe('товаров');
  });
});

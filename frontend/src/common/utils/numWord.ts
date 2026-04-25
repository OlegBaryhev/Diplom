export const numWord = (value: number, words: string[]): string | void => {
  if (!value) return;

  const localValue = Math.abs(value) % 100;
  const num = value % 10;

  if (localValue > 10 && localValue < 20) return words[2];
  if (num > 1 && num < 5) return words[1];
  if (num === 1) return words[0];

  return words[2];
};

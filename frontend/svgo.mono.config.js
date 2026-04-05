export default {
  plugins: [
    'preset-default',
    {
      name: 'convertColors',
      params: {
        currentColor: true,
      },
    },
    'removeDimensions',
    {
      name: 'removeAttrs',
      params: {
        attrs: 'style',
      },
    },
  ],
};

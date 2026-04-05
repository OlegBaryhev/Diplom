module.exports = {
  root: true,

  env: {
    node: true,
  },

  extends: [
    './.eslintrc-auto-import.json',
    'airbnb-base',
    'plugin:vue/vue3-recommended',
    'plugin:vue/base',
  ],

  parserOptions: {
    ecmaVersion: 'latest',
  },

  rules: {
    /* see https://eslint.org/docs/rules/ */
    'no-constant-condition': ['error', { checkLoops: false }],
    'no-param-reassign': ['error', { props: false }],
    'no-console': ['warn', { allow: ['warn', 'error'] }],
    'no-unused-vars': 'warn',
    'global-require': 'off',
    'consistent-return': 'off',
    camelcase: 'off',
    'linebreak-style': 'off',
    'no-confusing-arrow': 'off',
    'no-plusplus': 'off',
    'no-underscore-dangle': 'off',
    'implicit-arrow-linebreak': 'off',
    'no-shadow': 'off',
    'func-names': 'off',
    'max-len': 'off',
    'no-mixed-operators': 'off',
    'no-unused-expressions': 'off',
    'no-nested-ternary': 'off',

    /* see https://github.com/import-js/eslint-plugin-import#rules */
    'import/prefer-default-export': 'off',
    'import/no-extraneous-dependencies': 'off',
    'import/no-unresolved': 'off',
    'import/extensions': 'off',

    /* see https://eslint.vuejs.org/rules/ */
    'vue/max-attributes-per-line': ['error', {
      singleline: 1,
      multiline: 1,
    }],
    'vue/component-name-in-template-casing': ['error', 'PascalCase', {
      registeredComponentsOnly: false,
    }],
    'vue/eqeqeq': 'error',
    'vue/require-name-property': 'error',
    'vue/require-default-prop': 'off',
    'vue/valid-v-slot': 'off',
    'vue/no-v-html': 'off',
    'vue/multi-word-component-names': 'off',
    'vue/v-on-event-hyphenation': 'off',
    'vue/no-reserved-component-names': 'off',
    'vue/html-self-closing': 'off',
  },

  overrides: [
    {
      files: ['*.ts', '*.tsx', '*.vue'],
      extends: ['@vue/typescript/recommended'],
      rules: {
        /* see https://www.npmjs.com/package/@typescript-eslint/eslint-plugin */
        '@typescript-eslint/no-explicit-any': 'off',
        '@typescript-eslint/no-inferrable-types': 'off',
        '@typescript-eslint/no-non-null-assertion': 'off',
      },
    },

    {
      files: ['cypress/e2e/**.{cy,spec}.{js,ts,jsx,tsx}'],
      extends: ['plugin:cypress/recommended'],
    },
  ],
};

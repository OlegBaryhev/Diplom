/// <reference types="vitest" />
import { fileURLToPath, URL } from 'node:url';
import { defineConfig, loadEnv } from 'vite';
import type { ConfigEnv } from 'vite';
import vue from '@vitejs/plugin-vue';
import vueJsx from '@vitejs/plugin-vue-jsx';
import eslint from 'vite-plugin-eslint';
import svgLoader from 'vite-svg-loader';
import inspect from 'vite-plugin-inspect';
import AutoImport from 'unplugin-auto-import/vite';
import components from 'unplugin-vue-components/vite';

export default ({ mode }: ConfigEnv) => {
  process.env = Object.assign(process.env, loadEnv(mode, process.cwd(), ''));

  return defineConfig({
    define: {
      __VUE_PROD_HYDRATION_MISMATCH_DETAILS__: false,
    },
    plugins: [
      vue({
        script: {
          defineModel: true,
          propsDestructure: true,
        },
      }),
      vueJsx(),
      eslint(),
      svgLoader({
        svgo: false,
      }),
      inspect(),
      AutoImport({
        imports: [
          'vue',
          'vue-router',
          'pinia',
          '@vueuse/core',
          { '@vueuse/router': ['useRouteHash', 'useRouteParams', 'useRouteQuery'] },
        ],
        vueTemplate: true,
        eslintrc: { enabled: true },
      }),
      components({
        dirs: ['./src/common/components'],
        directoryAsNamespace: true,
        globalNamespaces: ['modals', 'tables'],
      }),
    ],

    resolve: {
      alias: {
        '@': fileURLToPath(new URL('./src', import.meta.url)),
      },
    },

    test: {
      environment: 'jsdom',
      coverage: {
        enabled: true,
      },
    },
  });
};

import 'pinia';

declare module '*.webp';
declare module '*.png';
declare module '*.jpg';
declare module '*.jpeg';

declare module '*.vue' {
  const component: ReturnType<typeof defineComponent>;
  export default component;
}

declare module '*.scss' {
  const css: {
    [key: string]: string,
  };
  export default css;
}

declare module '*.sass' {
  const css: {
    [key: string]: string,
  };
  export default css;
}

declare module 'pinia' {
  import type Router from 'vue-router';

  export interface PiniaCustomProperties {
    router: Router;
  }
}

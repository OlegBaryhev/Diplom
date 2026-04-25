import type { FunctionalComponent, SVGAttributes } from 'vue';

export interface registerParams {
  email: string;
  name: string;
  password: string;
}

export type ClassAttr = string | undefined;
export type IconComponent = FunctionalComponent<SVGAttributes>;

export type SidePanelMode = 'adding' | 'editing' | 'reading' | 'copy';

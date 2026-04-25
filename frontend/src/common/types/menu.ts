export type RouteMenu = {
  id: number;
  name: string;
  svg_name?: string;
  routeName?: string;
  data_test?: string | null;
  disabled?: boolean | { sidePanel: boolean; mainPage: boolean };
  submenu?: RouteMenu[];
};

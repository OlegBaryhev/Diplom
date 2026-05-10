<template>
  <div class="pl-4">
    <div
      class="menu mt-4"
      :class="{
        'menu--flex': filteredMenu?.list?.length <= 3
      }"
    >
      <div
        v-for="menuItem of filteredMenu.list"
        :key="menuItem.id"
        class="menu__wrapper"
        :style="{
          ...(filteredMenu?.list?.length > 3 && {'grid-row': menuItem?.submenu ? `span ${menuItem.submenu.length + 1}` : null}),
        }"
      >
        <RouterLink
          v-if="!menuItem.submenu && menuItem.routeName !== 'main'"
          :to="{ name: menuItem.routeName }"
          class="menu__link"
          :class="{
            'menu__link--disabled': menuItem.disabled
          }"
        >
          <div
            tabindex="0"
            role="button"
          >
            {{ menuItem.name }}
          </div>
        </RouterLink>

        <template v-else>
          <div
            v-if="menuItem.routeName !== 'main'"
            class="menu__link--title"
            :class="{
              'menu__link--disabled': menuItem.submenu?.every(item => item.disabled)
            }"
          >
            {{ menuItem.name }}
          </div>

          <RouterLink
            v-for="submenuItem of menuItem.submenu"
            :key="submenuItem.id"
            :to="{ name: submenuItem.routeName }"
            class="menu__link menu__link--submenu"
            :class="{'menu__link--disabled': submenuItem.disabled}"
          >
            <div
              tabindex="0"
              role="button"
            >
              <div
                class="menu__link__text"
              >
                <VIcon
                  name="arrow-right"
                  class="w-3 h-3"
                />
                <span>{{ submenuItem.name }}</span>
              </div>
            </div>
          </RouterLink>
        </template>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { userHasRouteAccess } from '@/common/utils/permissions';
import { VERTICAL_MENU } from '@/consts/menu';

const MAX_ROWS_COUNT = 7;

const filteredMenu = computed(() => VERTICAL_MENU.reduce((acc, val) => {
  if (val.routeName !== 'main' && userHasRouteAccess(val)) {
    acc.list.push(val);
    acc.total += (val?.submenu?.length ?? 0) + 1;
  }

  return acc;
}, {
  list: [] as typeof VERTICAL_MENU,
  total: 0,
}));

const calculatedColumnsCount = computed(() => Math.max(Math.ceil(filteredMenu.value.total / MAX_ROWS_COUNT), 3));
</script>

<style lang="scss" scoped>
.menu {
  $root: &;
  --columns-count: v-bind(calculatedColumnsCount);

  $items-width: 252px;
  display: grid;
  gap: 10px;
  grid-template-columns: repeat(auto-fill, minmax($items-width, 1fr));
  color: theme('colors.white');

  min-width: $items-width;
  max-width: min(calc(var(--columns-count) * ($items-width + 10px)), calc(100vw - 88px));

  &--flex {
    display: flex;
    flex-direction: column;
  }

  &__wrapper {
    margin: 8px;
  }

  &__link {
    display: flex;
    padding: 8px 0;
    font-size: 26px;
    width: $items-width;
    color: theme('colors.white');
    transform-origin: left;
    transition: transform 0.2s ease-in-out, filter 0.2s ease-in-out;

    &--title {
      font-size: 26px;
      padding: 8px 0;
      width: $items-width;
      color: theme('colors.white');
    }

    &:not(&--disabled) {
      &:hover, &:focus {
        transform: scale(105%);
      }

      &:active {
        transform: scale(95%);
        filter: brightness(90%);
      }
    }

    &__text {
      display: flex;
      align-items: center;
      gap: 8px;
    }

    &--submenu {
      padding-left: 16px;
      margin: 14px;
    }

    &--disabled {
      color: theme('colors.additional.200');
      pointer-events: none;
    }
  }
}
</style>

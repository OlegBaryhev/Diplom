<template>
  <div
    ref="blackout"
    v-scroll-lock="blackoutIsActive"
    class="side-bar__blackout fixed top-0 bg-black w-screen h-screen z-[80] transition-opacity ease-in-out duration-300"
    :class="{
      'active': blackoutIsActive
    }"
    data-test="toggleMenu"
    @click="setMenuState(false)"
  />

  <aside
    ref="verticalMenu"
    class="select-none side-bar fixed top-0 left-0 flex flex-col overflow-x-hidden bg-white z-[80] h-screen w-22 min-w-22 border-r border-main-200"
    :class="{
      'open': menuState,
    }"
  >
    <VTooltip
      :show="tooltip.value"
      content="Развернутое меню"
      trail
    >
      <div
        class="h-22 min-h-22 cursor-pointer w-full py-5 px-4"
        data-test="toggleMenu"
        @click.prevent="toggleMenu()"
      >
        <div
          class="side-bar__item focus-element"
          tabindex="0"
          role="button"
          @keydown.enter.stop="toggleMenu()"
        >
          <div class="side-bar__item-icon">
            <VIcon
              v-if="!menuState"
              name="expand"
            />
            <VIcon
              v-else
              name="collapse"
            />
          </div>
          <span class="side-bar__item-name">Свернуть</span>
        </div>
      </div>
    </VTooltip>

    <div
      ref="sideBar"
      class="overflow-x-hidden side-bar__content"
    >
      <template
        v-for="menuItem of filteredVerticalMenu"
        :key="menuItem.id"
      >
        <template v-if="userHasRouteAccess(menuItem)">
          <VTooltip
            v-if="!menuItem.submenu"
            :show="tooltip.value"
            :content="menuItem.name"
            class="relative w-full"
            trail
            data-test="closeMenu"
            @click.stop="!menuItem.disabled && setMenuState(false)"
          >
            <RouterLink
              :to="{ name: menuItem.routeName } "
              tabindex="-1"
              class="side-bar__item-wrap group"
              :class="{
                'side-bar__item--active': routerIncludesUrl(menuItem)
                  && menuItem.routeName && menuItem.routeName?.length > 1
                  || route.name === menuItem.routeName,
                'side-bar__item--disabled': menuItem.disabled || !menuItem.routeName
              }"
              @click.stop="linkClicked()"
            >
              <div
                class="side-bar__item focus-element"
                tabindex="0"
                role="button"
                @keydown.enter.stop="router.push({ name: menuItem.routeName }); linkClicked()"
              >
                <div class="side-bar__item-icon">
                  <VIcon :name="menuItem.svg_name" />
                </div>

                <span class="side-bar__item-name flex justify-between items-center">
                  <span>{{ menuItem.name }}</span>
                </span>
              </div>
            </RouterLink>
          </VTooltip>

          <div
            v-else
            ref="accordionEl"
            class="side-bar__item-accordion"
            :class="{'accordion-active': routerIncludesUrl(menuItem)}"
            data-test="toggleAccordion"
            @click.stop="!disabledSubmenu(menuItem) && (toggleAccordion($event), setMenuState(true))"
          >
            <VTooltip
              :show="tooltip.value"
              :content="menuItem.name"
              trail
              class="side-bar__item-wrap w-full group"
              :class="{'side-bar__item--active': routerIncludesUrl(menuItem) }"
              data-test="openMenu"
            >
              <div
                class="side-bar__item flex py-5 focus-element cursor-pointer"
                :class="{'side-bar__item--disabled': disabledSubmenu(menuItem) }"
                tabindex="getAccordionState(menuItem.id) ? 0 : -1"
                role="button"
                @click.stop="toggleAccordion($event); setMenuState(true)"
              >
                <div class="side-bar__item-icon">
                  <VIcon :name="menuItem.svg_name" />
                </div>

                <span class="side-bar__item-name flex justify-between items-center">
                  <span>{{ menuItem.name }}</span>
                  <VIcon
                    name="down"
                    class="side-bar__item-arrow transition"
                  />
                </span>
              </div>
            </VTooltip>

            <ul
              class="side-bar__submenu"
              @click.stop
            >
              <li
                v-for="submenuItem of menuItem.submenu"
                :key="submenuItem.id"
              >
                <RouterLink
                  :to="{ name: submenuItem.routeName }"
                  :tabindex="routerIncludesUrl(submenuItem) ? 0 : -1"
                  class="w-full side-bar__submenu-item-wrap group"
                  data-test="closeMenu"
                  :class="{
                    'side-bar__item--disabled': submenuItem.disabled || !submenuItem.routeName
                  }"
                  @click.stop="!submenuItem.disabled && linkClicked()"
                >
                  <div
                    class="side-bar__submenu-item side-bar__item-name focus-element"
                    tabindex="-1"
                    role="button"
                    :class="{'side-bar__submenu-item--active': routerIncludesUrl(submenuItem) }"
                    @keydown.enter="router.push({ name: submenuItem.routeName }); toggleAccordion($event); linkClicked();"
                  >
                    {{ submenuItem.name }}
                  </div>
                </RouterLink>
              </li>
            </ul>
          </div>
        </template>
      </template>
    </div>
    <div
      class="side-bar__bottom mt-auto flex flex-col"
      :class="{
        'show-shadow': isEndPosition,
      }"
    >
      <VTooltip
        v-for="menuItem of VERTICAL_MENU_BOTTOM"
        :key="menuItem.id"
        :show="tooltip.value"
        :content="menuItem.name"
        bottom
        left
        trail
        mouse-move
        class="w-full"
        data-test="closeMenu"
        @click.stop="setMenuState(false)"
      >
        <button
          tabindex="-1"
          type="button"
          :data-test="menuItem.data_test"
          class="side-bar__item-wrap group"
          :class="{
            'side-bar__item--active': menuItem.id === activeVerticalMenuBottomId,
            'side-bar__item--disabled': typeof menuItem.disabled === 'object' && menuItem.disabled?.sidePanel
          }"
          @click="openModal(menuItem.id)"
        >
          <div
            class="side-bar__item focus-element"
            tabindex="0"
            role="button"
            @keydown.enter.stop="router.push({ name: menuItem.routeName }); setMenuState(false)"
          >
            <div class="side-bar__item-icon">
              <VIcon :name="menuItem.svg_name" />
            </div>
            <span class="side-bar__item-name">
              {{ menuItem.name }}
            </span>
          </div>
        </button>
      </VTooltip>

      <VProfileItem
        v-if="user && !isEmpty(user)"
        :is-open="menuState"
        :profile-data="user"
        @open-profile-modal="router.push({ name: 'profile' })"
      />
    </div>
  </aside>

  <TransitionGroup>
    <VCartList
      v-if="activeVerticalMenuBottomId === VERTICAL_MENU_BOTTOM[0].id && user && !isEmpty(user)"
      @close="closeModal()"
      @confirm-cart="modalStore.open('add-order-modal')"
    />
  </TransitionGroup>

  <VConfirmationModal
    id="add-order-modal"
    title="Вы уверены, что хотите оплатить данный заказ?"
    :text="`
      После этого действия не будет оплаты, так что закупайтесь по максимуму!!!\n
      ЗЕМЛЯ — КРЕСТЬЯНАМ! ФАБРИКИ — РАБОЧИМ! Далой капитализм!
    `"
    confirmation-text="Подтвердить"
    :async-confirmation-func="confirmCart"
  />
</template>

<script setup lang="ts">
import { isEmpty } from 'lodash';
import { OverlayScrollbars } from 'overlayscrollbars';
import { VERTICAL_MENU, VERTICAL_MENU_BOTTOM } from '@/consts/menu';
import { useModals } from '@/stores/modals';
import { useScrollCount } from '@/stores/scrollCount';
import type { RouteMenu } from '@/common/types/menu';
import { userHasRouteAccess } from '@/common/utils/permissions';
import { createOrderByCartRequest } from '@/modules/orders/api';
import { useUser } from '@/stores/user';
import { useCart } from '@/stores/cart';

const router = useRouter();
const route = useRoute();
const cartStore = useCart();

const tooltip = reactive({ value: true });

const verticalMenu = ref();
const blackout = ref();
const accordionEl = ref();
const sideBar = ref();

const userStore = useUser();
const modalStore = useModals();

const user = computed(() => userStore.user);

const storeScrollCount = useScrollCount();

const menuState = ref<boolean>(false);
const activeVerticalMenuBottomId = ref(-1);

const blackoutIsActive = computed(() => activeVerticalMenuBottomId.value !== -1 || menuState.value);

const filteredVerticalMenu = computed(() => VERTICAL_MENU);

const confirmCart = async (): Promise<void> => {
  await createOrderByCartRequest();
  await cartStore.reloadCart();
};

const isEndPosition = ref<boolean>(true);

const setEndPositionFlag = (target:any) => {
  const { scrollHeight, clientHeight, scrollTop } = target;
  isEndPosition.value = scrollHeight !== clientHeight && Math.ceil(scrollTop + clientHeight) !== scrollHeight;
};

const observer = ref<null | ResizeObserver>(new ResizeObserver(([e]:any) => setEndPositionFlag(e.target)));
onMounted(() => {
  OverlayScrollbars(sideBar.value, {
    overflow: {
      x: 'hidden',
    },
    scrollbars: {
      visibility: 'auto',
    },
  }, {
    scroll(e) {
      setEndPositionFlag(e.elements().content);
    },
  });
  observer.value?.observe(sideBar.value.children[1]);
});

const closeAccordion = (): void => {
  if (!accordionEl.value) {
    return;
  }

  accordionEl.value.forEach((el: HTMLElement) => {
    if (!el.classList.contains('accordion-active')) {
      el.classList.remove('open');
    }
  });
};

const openModal = (id: number):void => {
  activeVerticalMenuBottomId.value = activeVerticalMenuBottomId.value !== id ? id : -1;
};

const closeModal = () => { openModal(-1); };

const toggleAccordion = (event: Event) => {
  const accordion = (event.target as HTMLElement).closest('.side-bar__item-accordion');
  const submenuItems = accordion!.querySelectorAll('.side-bar__submenu-item');

  accordion!.classList.toggle('open');

  if (!menuState.value) {
    accordion!.classList.add('open');
  }

  if (accordion!.classList.contains('open')) {
    submenuItems.forEach((item: any) => {
      item.tabIndex = 0;
    });
    return;
  }

  submenuItems.forEach((item: any) => {
    item.tabIndex = -1;
  });
};

const disabledSubmenu = (menuItem:any) => menuItem.submenu?.every(({ disabled }: boolean) => disabled);

const setTooltipValue = (flag:boolean | null):void => {
  setTimeout(() => { tooltip.value = (flag ?? !tooltip.value); }, 300);
};

watch(
  () => blackoutIsActive.value,
  (val, old) => val !== old && (val ? storeScrollCount.increase() : storeScrollCount.decrease()),
);

const setMenuState = (state:boolean = true):void => {
  menuState.value = state;
  setTooltipValue(!state);
  !state && closeAccordion();
};

const linkClicked = () => {
  closeModal();
  nextTick(() => { setMenuState(false); });
};

const toggleMenu = (): void => setMenuState(!menuState.value);

const routerIncludesUrl = (menuItem: RouteMenu):boolean => !!(menuItem.routeName && route.name === menuItem.routeName
  || menuItem.submenu && menuItem.submenu.some(({ routeName }: any) => route.name === routeName));

onBeforeUnmount(() => blackoutIsActive.value && storeScrollCount.decrease());
</script>

<style lang="scss" scoped>
.side-bar {
  $root: &;
  width: 88px;
  min-width: 88px;
  z-index: 81;
  transition: width 0.3s ease-in-out, min-width 0.3s ease-in-out;

  &__blackout {
    @apply inset-0 bg-black/40;

    position: fixed;
    top: 0;
  }

  &__blackout:not(.active) {
    @apply opacity-0 invisible;
  }

  &__blackout.active {
    @apply opacity-40;
  }

  &__item-wrap {
    white-space: nowrap;
    display: flex;
    align-items: center;
    height: 64px;
    padding: 8px 16px;
    width: 100%;
    background-color: theme('colors.white');
  }

  &__item {
    @apply text-base-regular text-additional group-hover:text-main-400 bg-white group-hover:bg-main-50 ease-in-out duration-300;
    display: flex;
    align-items: center;
    width: 100%;
    height: 100%;
    border-radius: 8px;
    padding: 0 16px;
    cursor: pointer;

    &-name {
      @apply invisible flex w-full ml-8;
    }

    &--active {
      color: theme('colors.main.400');

      #{$root}__item-name, #{$root}__item-icon  {
        color: theme('colors.main.400');
      }

      &:before {
        content: '';
        position: absolute;
        width: 4px;
        height: 100%;
        background: theme('colors.main.400');
        border-radius: 2px;
        left: 0;
      }
    }

    &--disabled {
      pointer-events: none;

      #{$root}__item-name {
        color: theme('colors.additional.200');
      }

      #{$root}__item-icon {
        color: theme('colors.additional.200');
      }
    }
  }

  &__submenu-item {
    @apply inline-block w-full py-3 text-additional hover:text-main-400 hover:bg-main-50;
    padding-left: 40px;
    border-radius: 8px;
    background-color: theme('colors.white');
    &-wrap {
      white-space: nowrap;
      display: block;
      height: 48px;
      padding: 0 16px;
    }
  }

  &__item-accordion:not(.open) {
    .side-bar__submenu {
      max-height: 0;
      overflow: hidden;
      transition: all 0.5s;
    }
  }

  &__item-accordion.open {
    .side-bar__item-arrow {
      @apply rotate-180;
    }

    .side-bar__submenu {
      max-height: 1000px;
      transition: all 2s;
    }
  }

  &__bottom {
    position: relative;
    &::before{
     content: '';
     display: flex;
     position: absolute;
     pointer-events: none;
     height: 15px;
     width: 100%;
     background: linear-gradient(0deg ,#9CACBE26 3px, transparent 100%);
     top: 0;
     left: 0;
     transition: 0.1s ease-out transform;
     transform-origin: bottom;
     transform: translateY(-100%) scaleY(0);
   }

   &.show-shadow::before{
    transform: translateY(-100%) scaleY(100%);
   }
  }
}

.side-bar.open {
  @apply w-80 min-w-80 ease-in-out duration-300;

  &__item {
    @apply flex justify-start;
  }

  .side-bar__item-name {
    @apply visible;
  }
}

.side-bar__submenu-item--active {
  color: theme('colors.main.400');
}

.side-bar:not(.open) {
  .side-bar__submenu {
    max-height: 0;
    overflow: hidden;
    transition: all 0.3s;
  }
}

.cart {
  position: fixed;
  left: 90px;
  bottom: 24px;
  z-index: 80;
  transition: all .3s ease-in-out;
}

.v-enter-active,
.v-leave-active {
  transition: opacity 0.5s ease;
}

.v-enter-from,
.v-leave-to {
  opacity: 0;
}

</style>

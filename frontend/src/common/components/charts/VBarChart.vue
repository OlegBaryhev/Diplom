<template>
  <div class="bar-chart">
    <p
      v-if="title"
      class="bar-chart__title"
    >
      {{ title }}
    </p>

    <div
      v-if="!items.length"
      class="bar-chart__empty"
    >
      Нет данных
    </div>

    <div
      v-else
      class="bar-chart__wrap"
    >
      <svg
        :width="svgWidth"
        :height="svgHeight"
        class="bar-chart__svg"
      >
        <g :transform="`translate(${margin.left},${margin.top})`">
          <line
            v-for="tick in yTicks"
            :key="tick"
            :x1="0"
            :y1="yScale(tick)"
            :x2="innerWidth"
            :y2="yScale(tick)"
            stroke="#e5e7eb"
            stroke-width="1"
          />

          <text
            v-for="tick in yTicks"
            :key="`label-${tick}`"
            :x="-6"
            :y="yScale(tick)"
            text-anchor="end"
            dominant-baseline="middle"
            class="bar-chart__tick-label"
          >
            {{ tick }}
          </text>

          <rect
            v-for="(item, i) in items"
            :key="i"
            :x="barX(i)"
            :y="yScale(item.value)"
            :width="barWidth"
            :height="innerHeight - yScale(item.value)"
            :fill="barColor"
            rx="3"
            class="bar-chart__bar"
          >
            <title>{{ item.label }}: {{ item.value }}</title>
          </rect>

          <text
            v-for="(item, i) in items"
            :key="`xlab-${i}`"
            :x="barX(i) + barWidth / 2"
            :y="innerHeight + 14"
            text-anchor="middle"
            class="bar-chart__tick-label"
          >
            {{ truncate(item.label, 12) }}
          </text>

          <text
            v-for="(item, i) in items"
            :key="`val-${i}`"
            :x="barX(i) + barWidth / 2"
            :y="yScale(item.value) - 4"
            text-anchor="middle"
            class="bar-chart__value-label"
          >
            {{ item.value }}
          </text>
        </g>
      </svg>
    </div>
  </div>
</template>

<script lang="ts" setup>
const props = withDefaults(defineProps<{
  items: { label: string; value: number }[];
  title?: string;
  barColor?: string;
  height?: number;
}>(), {
  title: '',
  barColor: '#3b82f6',
  height: 220,
});

const margin = { top: 20, right: 16, bottom: 40, left: 40 };
const svgWidth = computed(() => Math.max(320, props.items.length * 60 + margin.left + margin.right));
const svgHeight = computed(() => props.height + margin.top + margin.bottom);
const innerWidth = computed(() => svgWidth.value - margin.left - margin.right);
const innerHeight = computed(() => props.height);

const maxVal = computed(() => Math.max(...props.items.map((i) => i.value), 1));

const barWidth = computed(() => Math.max(8, (innerWidth.value / (props.items.length || 1)) * 0.6));
const barGap = computed(() => innerWidth.value / (props.items.length || 1));

const barX = (i: number) => i * barGap.value + (barGap.value - barWidth.value) / 2;

const yScale = (val: number) => innerHeight.value - (val / maxVal.value) * innerHeight.value;

const yTicks = computed(() => {
  const count = 4;
  const step = Math.ceil(maxVal.value / count);
  const ticks: number[] = [];
  for (let i = 0; i <= count; i++) {
    const v = i * step;
    if (v <= maxVal.value + step) ticks.push(v);
  }
  return ticks;
});

const truncate = (str: string, max: number) =>
  str.length > max ? `${str.slice(0, max)}…` : str;
</script>

<style lang="scss" scoped>
.bar-chart {
  &__title {
    @apply text-sm-medium;
    color: theme('colors.additional.DEFAULT');
    margin-bottom: 10px;
  }

  &__empty {
    @apply text-sm-regular;
    color: theme('colors.additional.300');
    text-align: center;
    padding: 32px 0;
  }

  &__wrap {
    overflow-x: auto;
  }

  &__svg {
    display: block;
  }

  &__tick-label {
    font-size: 11px;
    fill: #6b7280;
  }

  &__value-label {
    font-size: 10px;
    fill: #374151;
    font-weight: 500;
  }

  &__bar {
    transition: opacity 0.15s;
    cursor: default;

    &:hover {
      opacity: 0.8;
    }
  }
}
</style>

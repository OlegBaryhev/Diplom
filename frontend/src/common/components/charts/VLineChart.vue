<template>
  <div class="line-chart">
    <p
      v-if="title"
      class="line-chart__title"
    >
      {{ title }}
    </p>

    <div
      v-if="!items.length"
      class="line-chart__empty"
    >
      Нет данных
    </div>

    <div
      v-else
      class="line-chart__wrap"
    >
      <svg
        :width="svgWidth"
        :height="svgHeight"
        class="line-chart__svg"
      >
        <defs>
          <linearGradient
            :id="`grad-${uid}`"
            x1="0"
            y1="0"
            x2="0"
            y2="1"
          >
            <stop
              offset="0%"
              :stop-color="lineColor"
              stop-opacity="0.25"
            />
            <stop
              offset="100%"
              :stop-color="lineColor"
              stop-opacity="0"
            />
          </linearGradient>
        </defs>

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
            :key="`yt-${tick}`"
            :x="-6"
            :y="yScale(tick)"
            text-anchor="end"
            dominant-baseline="middle"
            class="line-chart__tick-label"
          >
            {{ tick }}
          </text>

          <path
            v-if="areaPath"
            :d="areaPath"
            :fill="`url(#grad-${uid})`"
          />

          <polyline
            v-if="linePath"
            :points="linePath"
            :stroke="lineColor"
            stroke-width="2"
            fill="none"
            stroke-linejoin="round"
            stroke-linecap="round"
          />

          <circle
            v-for="(item, i) in items"
            :key="i"
            :cx="xScale(i)"
            :cy="yScale(item.value)"
            r="3.5"
            :fill="lineColor"
            class="line-chart__dot"
          >
            <title>{{ item.label }}: {{ item.value }}</title>
          </circle>

          <text
            v-for="(item, i) in visibleXLabels"
            :key="`xl-${i}`"
            :x="xScale(item.index)"
            :y="innerHeight + 16"
            text-anchor="middle"
            class="line-chart__tick-label"
          >
            {{ item.label }}
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
  lineColor?: string;
  height?: number;
}>(), {
  title: '',
  lineColor: '#3b82f6',
  height: 180,
});

const uid = Math.random().toString(36).slice(2, 8);

const margin = { top: 20, right: 20, bottom: 36, left: 40 };
const svgWidth = computed(() => Math.max(360, props.items.length * 28 + margin.left + margin.right));
const svgHeight = computed(() => props.height + margin.top + margin.bottom);
const innerWidth = computed(() => svgWidth.value - margin.left - margin.right);
const innerHeight = computed(() => props.height);

const maxVal = computed(() => Math.max(...props.items.map((i) => i.value), 1));

const xScale = (i: number) =>
  props.items.length > 1 ? (i / (props.items.length - 1)) * innerWidth.value : innerWidth.value / 2;

const yScale = (val: number) => innerHeight.value - (val / maxVal.value) * innerHeight.value;

const linePath = computed(() =>
  props.items.map((item, i) => `${xScale(i)},${yScale(item.value)}`).join(' '),
);

const areaPath = computed(() => {
  if (!props.items.length) return '';
  const pts = props.items.map((item, i) => `${xScale(i)},${yScale(item.value)}`).join(' L ');
  const last = `${xScale(props.items.length - 1)},${innerHeight.value}`;
  const first = `${xScale(0)},${innerHeight.value}`;
  return `M ${pts} L ${last} L ${first} Z`;
});

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

const visibleXLabels = computed(() => {
  const step = Math.max(1, Math.floor(props.items.length / 6));
  return props.items
    .map((item, i) => ({ ...item, index: i }))
    .filter((_, i) => i % step === 0 || i === props.items.length - 1);
});
</script>

<style lang="scss" scoped>
.line-chart {
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

  &__dot {
    cursor: default;
    transition: r 0.1s;

    &:hover {
      r: 5;
    }
  }
}
</style>

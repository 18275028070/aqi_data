<template>
  <div class="com-container">
    <div class="com-chart" ref="stock_ref"></div>
  </div>
</template>

<script>
import { mapState } from "vuex";
export default {
  // eslint-disable-next-line vue/multi-word-component-names
  name: "Stock",
  data() {
    return {
      chartInstance: null,
      allData: null,
      currentIndex: 0, // 当前显示的数据
      timeId: null, // 定时器的标识
      titleFontSize: null, // 字体大小配置
    };
  },

  created() {
    this.getData();
  },

  mounted() {
    this.initChart();
    this.getData()
    window.addEventListener("resize", this.screenAdapter);
    this.screenAdapter();
  },

  destroyed() {
    // 组件销毁移除掉事件
    window.removeEventListener("resize", this.screenAdapter);
    clearInterval(this.timeId);
  },

  methods: {
    initChart() {
      // 初始化echarts对象
      this.chartInstance = this.$echarts.init(this.$refs.stock_ref, this.theme);
      const initOption = {
        title: {
          text: "▍当前城市温度",
          left: 20,
          top: 20,
        },

        series: [
          {
            axisLine: {
              show: true,
              lineStyle: {
                color: [
                  [
                    1,
                    new this.$echarts.graphic.LinearGradient(0, 0, 1, 0, [
                      {
                        offset: 0.1,
                        color: "#4ed6b3",
                      },
                      {
                        offset: 0.5,
                        color: "#b2df6b",
                      },
                    ]),
                  ],
                ],
                width: 23,
              },
            },
            name: "温度",
            type: "gauge",
            radius: "70%",
            max: 50,
            startAngle: 180, //开始角度 左侧角度
            endAngle: 0, //结束角度 右侧
            splitNumber: 6,
            axisTick: {
              show: false,
            },
            axisLabel: {
              show: false,
            },
            pointer: {
              length: "45%",
              width: 3,
            },
            itemStyle: {
              color: "#2adff1",
            },
            detail: {
              formatter: "{value}°C",
              offsetCenter: [0, 50],
              fontSize: 30,
              lineHeight: 24,
              color: "#ffe599",
            },
            title: {
              offsetCenter: [0, "10%"],
              textStyle: {
                color: "#99ffff",
              },
            },
          },
        ],
      };

      this.chartInstance.setOption(initOption);
    },

    async getData() {
      // 异步获取数据
      const {data:ret} = await this.$http.get('/cd_tems')
      this.allData = ret.data;
      this.updataChart();
    },

    updataChart() {
      const legendData = this.allData[0].daytime;
      const seriesData = this.allData[0].text;
      const dataOption = {
        series: [
          {
            data: [
              {
                value: parseFloat(legendData),
                name: seriesData,
              },
            ],
          },
        ],
      };
      this.chartInstance.setOption(dataOption);
    },

    screenAdapter() {
      // 屏幕适配
      this.titleFontSize = (this.$refs.stock_ref.offsetWidth / 100) * 3.6;
      const adapterOpton = {
        title: {
          textStyle: {
            fontSize: this.titleFontSize,
          },
        },
      };
      this.chartInstance.setOption(adapterOpton);
      this.chartInstance.resize();
    },
  },

  computed: {
    ...mapState(["theme"]),
  },

  watch: {
    theme() {
      this.chartInstance.dispose();
      this.initChart();
      this.updataChart();
      this.screenAdapter();
    },
  },
};
</script>

<style lang="less" scoped></style>

<template>
  <div class="com-container">
    <div class="com-chart" ref="hot_ref"></div>
    <span class="iconfont arr-left" @click="toLeft" :style="comStyle"
      >&#xe6ef;</span
    >
    <span class="iconfont arr-right" @click="toRight" :style="comStyle"
      >&#xe6ed;</span
    >
    <span class="cat-name" :style="comStyle">{{ catName }}</span>
  </div>
</template>

<script>
import { mapState } from "vuex";
// import { getThemeValue } from "../utils/theme_utils";
export default {
  name: "sixData",
  data() {
    return {
      chartInstance: null,
      allData: null,
      currentIndex: 0, // 当前所展示出来的一级分类数据
      titleFontSize: null,
      city_data:[] // 最终呈现的数据
    };
  },

  computed: {
    catName() {
      if (!this.allData) {
        return "";
      } else {
        return this.allData[this.currentIndex].city;
      }
    },
    comStyle() {
      return {
        fontSize: this.titleFontSize + "px",
        // color:getThemeValue(this.theme).titleColor
      };
    },
    ...mapState(["theme"]),
  },

  watch: {
    theme() {
      this.chartInstance.dispose(); // 销毁当前图表
      this.initChart(); // 以最新的主题名称初始化图表对象
      this.screenAdapter();
      this.updataChart();
    },
  },

  created() {
    this.getData();
  },

  mounted() {
    this.initChart();
    window.addEventListener("resize", this.screenAdapter);
    this.screenAdapter();
  },

  destroyed() {
    window.removeEventListener("resize", this.screenAdapter);
  },

  methods: {
    initChart() {
      // 初始化图表(chartInstance)对象
      this.chartInstance = this.$echarts.init(this.$refs.hot_ref, this.theme);
      const initOption = {
        title: {
          text: "▍城市空气质量6项指标",
          left: 20,
          top: 10,
        },
        legend: {
          top: "8%",
          icon: "circle",
        },
        tooltip: {
          show: true,
        },
        series: [
          {
            type: "pie",
            roseType: "radius",
            emphasis: {
              // 高亮
              label: {
                show: true,
              },
            },
            labelLine: {
              length: this.titleFontSize / 2,
            },
          },
        ],
      };
      this.chartInstance.setOption(initOption);
    },

    async getData() {
      // 获取服务器的数据
      const {data:{data}} = await this.$http.get('/seven')
      data.map(item=>{
        this.city_data.push({
          city:item.city,
          data:[
            {
              name:"AQI",
              value:item.aqi
            },
            {
              name:"CO",
              value:item.co
            },
            {
              name:"NO2",
              value:item.no2
            },
            {
              name:"O3",
              value:item.o3
            },
            {
              name:"PM2.5",
              value:item["pm2.5"]
            },
            {
              name:"PM10",
              value:item.pm10
            },
            {
              name:"SO2",
              value:item.so2
            },
          ]
        })
      })
      this.allData = data;
      this.updataChart();
    },

    updataChart() {
      // 处理图表的数据
      const legendData = this.city_data[this.currentIndex].data.forEach(
        (item) => {
          // console.log(item)
          return item.name;
        }
      );

      

      const data_list = [];
      this.city_data[this.currentIndex].data.forEach(
        (item) => {
          data_list.push({ value: parseFloat(item.value), name: item.name });
        }
      );
      const dataOption = {
        series: [
          {
            data: data_list,
          },
        ],
        legend: {
          data: legendData,
        },
      };
      this.chartInstance.setOption(dataOption);
    },

    screenAdapter() {
      // 屏幕适配相关
      this.titleFontSize = (this.$refs.hot_ref.offsetWidth / 100) * 3.6;
      const adapterOption = {
        title: {
          textStyle: {
            fontSize: this.titleFontSize,
          },
        },
        legend: {
          itemWidth: this.titleFontSize / 2, // 图例宽度
          itemHeight: this.titleFontSize / 2,
          itemGap: this.titleFontSize / 2,
          textStyle: {
            fontSize: this.titleFontSize / 2,
          },
        },
        series: [
          {
            center: ["50%", "55%"],
          },
        ],
      };
      this.chartInstance.setOption(adapterOption);
      this.chartInstance.resize();
    },

    toLeft() {
      // 向左切换一级图表
      this.currentIndex--;
      if (this.currentIndex < 0) {
        this.currentIndex = this.city_data.length - 1;
      }
      this.updataChart();
    },

    toRight() {
      // 向右切换一级图表

      this.currentIndex++;
      if (this.currentIndex > this.city_data.length - 1) {
        this.currentIndex = 0;
      }
      this.updataChart();
    },
  },
};
</script>

<style lang="less" scoped>
.com-container {
  .iconfont {
    color: rgb(34, 55, 124);
    background-color: rgb(194, 176, 176);
    cursor: pointer;
  }
  .arr-left {
    position: absolute;
    left: 10%;
    top: 50%;
    transform: translateY(-50%);
  }
  .arr-right {
    position: absolute;
    right: 10%;
    top: 50%;
    transform: translateY(-50%);
  }
  .cat-name {
    position: absolute;
    color: #fff;
    left: 80%;
    bottom: 20px;
    text-align: center;
    border-radius: 5px;
    background-color: rgba(23, 58, 90, 1);
  }
}
</style>

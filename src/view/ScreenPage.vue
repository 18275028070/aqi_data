<template>
  <div class="screen-container" :style="containerStyle">
    <header class="screen-header">
      <div>
        <img :src="headerSrc" alt />
      </div>
      <span class="logo">
        <img :src="logoSrc" alt />
      </span>
      <span class="title">基于Vue+Echarts的全国空气质量数据可视化</span>
      <div class="title-right">
        <img :src="themeSrc" class="qiehuan" @click="handleChangeTheme" />
        <span class="datetime">{{ gettime }}</span>
      </div>
    </header>
    <div class="screen-body">
      <section class="screen-left">
        <div id="left-top" :class="screenShow('trend')">
          <!-- 销量趋势图表 -->
          <CdTem ref="trend"></CdTem>
          <div class="resize">
            <span
              @click="changeSize('trend')"
              :class="iconChange('trend')"
            ></span>
          </div>
        </div>

        <div id="left-bottom" :class="screenShow('temhot')">
          <!-- 商家销售金额图表 -->
          <TemHot ref="temhot"></TemHot>
          <div class="resize">
            <span
              @click="changeSize('temhot')"
              :class="iconChange('temhot')"
            ></span>
          </div>
        </div>
      </section>
      <section class="screen-middle">
        <div id="middle-top" :class="screenShow('map')">
          <!-- 商家分布图表 -->
          <Map ref="map"></Map>
          <div class="resize">
            <span @click="changeSize('map')" :class="iconChange('map')"></span>
          </div>
        </div>

        <div id="middle-bottom" :class="screenShow('rank')">
          <!-- 地区销量排行图表 -->
          <TemCool ref="rank"></TemCool>
          <div class="resize">
            <span
              @click="changeSize('rank')"
              :class="iconChange('rank')"
            ></span>
          </div>
        </div>
      </section>
      <section class="screen-right">
        <div id="right-top" :class="screenShow('six')">
          <!-- 热销商品占比图表 -->
          <Six ref="six"></Six>
          <div class="resize">
            <span @click="changeSize('six')" :class="iconChange('six')"></span>
          </div>
        </div>

        <div id="right-bottom" :class="screenShow('stock')">
          <!-- 库存销量分析图表 -->
          <Stock ref="stock"></Stock>
          <div class="resize">
            <span
              @click="changeSize('stock')"
              :class="iconChange('stock')"
            ></span>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>

<script>
import Six from "../components/Sixdata";
import Map from "../components/Map";
import TemCool from "../components/TemCool";
import TemHot from "../components/TemHot";
import Stock from "../components/Stock";
import CdTem from "../components/CdTem";
import { mapState } from "vuex";
import { getThemeValue } from "../utils/theme_utils";
import { nextTick } from "vue";
import moment from "moment";
export default {
  name: "ScreenPage",
  data() {
    return {
      fullScreenStatus: {
        trend: false,
        temhot: false,
        map: false,
        TemCool: false,
        six: false,
        stock: false,
      },
      gettime: "",
    };
  },

  mounted() {
    setInterval(()=>{
      this.Date();
    }, 1000)
  },

  components: {
    Six,
    Map,
    TemCool,
    TemHot,
    Stock,
    CdTem,
  },

  methods: {
    screenShow(value) {
      // 大屏切换
      return this.fullScreenStatus[value] ? "fullscreen" : "";
    },
    iconChange(value) {
      // 缩放图标切换
      return [
        "iconfont",
        this.fullScreenStatus[value] ? "icon-compress-alt" : "icon-expand-alt",
      ];
    },
    changeSize(chartName) {
      // 1.改变fullScreenStatus的数据
      // 2.需要调用每一个图表组件的screenAdapter的方法
      this.fullScreenStatus[chartName] = !this.fullScreenStatus[chartName];
      this.$nextTick(() => {
        this.$refs[chartName].screenAdapter();
      });
    },
    handleChangeTheme() {
      // 修改Vuex中的数据
      this.$store.commit("changeTheme");
    },

    // 定义时间
    Date() {
      let date = Date.now()
      this.gettime = moment(date).format("YYYY-MM-DD HH:mm:ss");
    },
  },

  computed: {
    logoSrc() {
      return "/static/img/" + getThemeValue(this.theme).logoSrc;
    },

    headerSrc() {
      return "/static/img/" + getThemeValue(this.theme).headerBorderSrc;
    },

    themeSrc() {
      return "/static/img/" + getThemeValue(this.theme).themeSrc;
    },

    containerStyle() {
      return {
        backgroundColor: getThemeValue(this.theme).backgroundColor,
        color: getThemeValue(this.theme).titleColor,
      };
    },

    ...mapState(["theme"]),
  },
};
</script>

<style lang="less" scoped>
//  全屏样式的定义
.fullscreen {
  position: fixed !important;
  top: 0 !important;
  left: 0 !important;
  width: 100% !important;
  height: 100% !important;
  margin: 0 !important;
  z-index: 9999;
}

.screen-container {
  width: 100%;
  height: 100%;
  padding: 0 20px;
  background-color: #161522;
  color: #fff;
  box-sizing: border-box;
}
.screen-header {
  width: 100%;
  height: 64px;
  font-size: 20px;
  position: relative;
  > div {
    img {
      width: 100%;
    }
  }
  .title {
    position: absolute;
    left: 50%;
    top: 50%;
    font-size: 20px;
    transform: translate(-50%, -50%);
  }
  .title-right {
    display: flex;
    align-items: center;
    position: absolute;
    right: 0px;
    top: 50%;
    transform: translateY(-80%);
  }
  .qiehuan {
    width: 28px;
    height: 21px;
    cursor: pointer;
  }
  .datetime {
    font-size: 15px;
    margin-left: 10px;
  }
  .logo {
    position: absolute;
    left: 0px;
    top: 50%;
    transform: translateY(-80%);
    img {
      width: 184px;
      height: 51px;
    }
    a {
      text-decoration: none;
    }
  }
}
.screen-body {
  width: 100%;
  height: 100%;
  display: flex;
  margin-top: 10px;
  .screen-left {
    height: 100%;
    width: 27.6%;
    #left-top {
      height: 53%;
      position: relative;
    }
    #left-bottom {
      height: 31%;
      margin-top: 25px;
      position: relative;
    }
  }
  .screen-middle {
    height: 100%;
    width: 41.5%;
    margin-left: 1.6%;
    margin-right: 1.6%;
    #middle-top {
      width: 100%;
      height: 56%;
      position: relative;
    }
    #middle-bottom {
      margin-top: 25px;
      width: 100%;
      height: 28%;
      position: relative;
    }
  }
  .screen-right {
    height: 100%;
    width: 27.6%;
    #right-top {
      height: 46%;
      position: relative;
    }
    #right-bottom {
      height: 38%;
      margin-top: 25px;
      position: relative;
    }
  }
}
.resize {
  position: absolute;
  right: 20px;
  top: 20px;
  cursor: pointer;
}
</style>

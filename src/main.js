import Vue from 'vue'
import App from './App.vue'
import router from './router'
import store from './store'
import axios from 'axios'

import './assets/css/global.css'
import './assets/font/iconfont.css'

axios.defaults.baseURL = 'http://127.0.0.1:5500/aqi'

Vue.prototype.$http = axios

Vue.prototype.$echarts = window.echarts

Vue.config.productionTip = false

new Vue({
  router,
  store,
  render: h => h(App),
}).$mount('#app')


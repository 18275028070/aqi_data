// 路由组件的配置
import Vue from 'vue'
import VueRouter from 'vue-router'
import TemHotPage from '../view/TemHotPage'
import CdTemPage from '../view/CdTemPage'
import MapPage from '../view/MapPage'
import TemCoolPage from '../view/TemCoolPage'
import SixPage from '../view/SixPage'
import StockPage from '../view/StockPage'
import ScreenPage from '../view/ScreenPage'
Vue.use(VueRouter)

export default new VueRouter({
    routes:[
        {
            path:'/',
            redirect:'/screen'
        },
        {
            path:'/screen',
            component:ScreenPage
        },
        {
            path:'/temhotpage',
            component:TemHotPage
        },
        {
            path:'/cdtempage',
            component:CdTemPage
        },
        {
            path:'/mappage',
            component:MapPage
        },
        {
            path:'/temcoolpage',
            component:TemCoolPage
        },
        {
            path:'/sixdata',
            component:SixPage
        },
        {
            path:'/stockpage',
            component:StockPage
        },
    ]
})
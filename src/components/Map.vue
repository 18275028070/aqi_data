<template>
    <div class="com-container" @dblclick="revertMap">
        <div class="com-chart" ref="map_ref"></div>
    </div>
</template>

<script>
    import {mapState} from 'vuex'
    import axios from 'axios'
    import {getProvinceMapInfo} from '../utils/map_utils'
    export default {
        name:'MapCom',
        data(){
            return {
                chartInstance:null, //定义ECharts实例化对象
                allData:null, // 接收要呈现的数据 
                titleFontSize:0, // 图例字体大小
                mapData:{}, // 所获取的省份的地图矢量数据
                aqiData:[], // 整理数据库结构，最后呈现的数据
            }
        },

        computed:{
            ...mapState(['theme'])
        },

        watch:{
            theme(){
                this.chartInstance.dispose()
                this.initCharts()
                this.screenAdapter()
                this.updataChart()
            }
        },
        
        created(){
            this.getData()
        },

        mounted() {
            this.initCharts()
            this.getData()
            window.addEventListener('resize', this.screenAdapter)
            this.screenAdapter()
        },

         destroyed() {
            window.removeEventListener('resize', this.screenAdapter)
        },

        methods: {
            async initCharts(){
                this.chartInstance = this.$echarts.init(this.$refs.map_ref, this.theme)
                // 中国地图数据：http://localhost:8999/static/map/china.json,路径没有配置到Koa2里面，所以不能直接用$http
                const res = await axios.get('http://localhost:8999/static/map/china.json')
                this.$echarts.registerMap('china', res.data)
                const initOption = {
                    title:{
                        text:'▍全国AQI数据展示',
                        left:20,
                        top:20
                    },
                    geo:{
                        type:'map',
                        map:"china",
                        zoom:1,
                        // roam:true,
                        top:'5%',
                        bottom:'5%',
                        itemStyle:{
                            areaColor:"#3399ff",
                            borderColor:'#333'
                        },
                        label:{
                            show:true,
                            fontSize:14,
                            backgroundColor:'#E0FFFF',
                            borderRadius:5,
                        },
                    },
                    legend:{
                        left:'5%',
                        bottom:'5%',
                        orient:'vertical' // 垂直显示
                    }
                }
                this.chartInstance.setOption(initOption)

                // 获取点击的省份
                this.chartInstance.on('click', async arg=>{
                    const provinceInfo = getProvinceMapInfo(arg.name)
                    console.log(provinceInfo)

                    // 获取省份的矢量数据
                    // 判断当期所点击的省份的地图矢量数据是否存在mapData中
                    if(!this.mapData[provinceInfo.key]){  // 当没有访问过时才发起ajax请求
                        const ret = await axios.get('http://localhost:8999' + provinceInfo.path)
                        console.log(ret)
                        this.mapData[provinceInfo.key] = ret.data // 将省份的数据进行缓存
                        this.$echarts.registerMap(provinceInfo.key, ret.data) // 注册得到省份的拼音和矢量数据
                    }
                   
                    const changeOption = {
                        geo:{
                            map:provinceInfo.key,
                            label:{
                                show:true
                            }
                        }
                    }
                    this.chartInstance.setOption(changeOption) // 将图表信息配置到实例中
                })
            },

            // 获取服务器数据
            async getData(){
                const {data: ret} = await this.$http.get('/map_aqis')
                this.allData = ret.data
                // 将数据压入数组
                this.aqiData = this.allData.map(item=>{
                    return{
                            name:item.degree,
                            data:[
                                {
                                    name:item.city_name,
                                    value:[
                                        item.ing,
                                        item.lat,
                                        item.aqi
                                    ]
                                }
                            ]
                        }
                })
                this.updataChart()
            },

            // 更新图表
            updataChart(){
                // 图例的数据
                // const legendArr = this.allData.map(item=>{
                //     return item.name
                // })
                
                // 分别创建5个容器    
                const bestLv = { // 优级
                    name:null,
                    textStyle : {
                        color:null
                    }
                }  
                const goodLv = { // 良好
                    name:null,
                    textStyle : {
                        color:null
                    }
                }  
                const mildLv = { // 轻度
                    name:null,
                    textStyle : {
                        color:null
                    }
                }  
                const mezzoLv = { // 中度
                    name:null,
                    textStyle : {
                        color:null
                    }
                }  
                const severityLv = { // 严重
                    name:null,
                    textStyle : {
                        color:null
                    }
                }  

                
                // 创建每个指标的容器
                const legendColor = []

                this.aqiData.forEach(item => {
                    if (item.name === "优级") {
                        bestLv.name = item.name
                        bestLv.textStyle.color = '#99ffff'
                    } else if (item.name === "良好") {
                        goodLv.name = item.name
                        goodLv.textStyle.color = '#ccff99'
                    } else if (item.name === "轻度污染") {
                        mildLv.name = item.name
                        mildLv.textStyle.color = '#ffff66'
                    } else if (item.name === "中度污染") {
                        mezzoLv.name = item.name
                        mezzoLv.textStyle.color =  '#ffcc33'
                    } else if (item.name === "重度污染" || item.name === "重污染") {
                        severityLv.name = item.name
                        severityLv.textStyle.color = '#ff3300'
                    }
                    // 返回的是一个对象类型
                })
                legendColor.push(bestLv, goodLv, mildLv, mezzoLv, severityLv)
                const seriesArr = this.aqiData.map(item => {
                   // 代表一个类别下的所有散点数据  
                   // 如果想要在地图中显示散点的数据，需要在散点的图表增加一个配置，coordinateSystem  
                   return {
                       type:'effectScatter',
                       rippleEffect:{ // 配置涟漪效果
                            scale:5,
                            brushType:'stroke' // 涟漪类型，空心
                        },
                    //    name:item.name,
                       data:item.data,
                       coordinateSystem:'geo'
                   }
                })

                // 样式配置
                const dataOption = {
                    series:seriesArr,
                    visualMap: { // 结合visualMap配合使用
                        type:"piecewise",
                        pieces: [
                            { min: 0, max: 50, label:legendColor[0].name,color: '#66ff00' },
                            { min: 51, max: 100, label:legendColor[1].name,color: '#ffff99' },
                            { min: 101, max: 150, label:legendColor[2].name,color: '#ffcc33' },
                            { min: 151, max: 200, label:legendColor[3].name,color: '#ff9933' },
                            { min: 201, max: 300, label:legendColor[4].name || "重度污染",color: '#ff6633' },
                            // { min: 301, max: 1000, label:legendColor[5].name,color: '#ff3333' },
                        ],  
                        textStyle: {
                            color: "#FFF",
                            fontSize:16
                        }
                    }
                }
                this.chartInstance.setOption(dataOption)
            },

            // 屏幕适配
            screenAdapter(){
                this.titleFontSize = this.$refs.map_ref.offsetWidth / 100 * 3.6
                const adapterOption = {
                    title:{
                        textStyle:{
                            fontSize:this.titleFontSize
                        }
                    },
                    legend:{
                        itemWidth:this.titleFontSize/2,
                        itemHeight:this.titleFontSize/2,
                        itemGap:this.titleFontSize / 2, // 设置图例间隔
                        textStyle:{
                            fontSize:this.titleFontSize / 2
                        }
                    }
                }
                this.chartInstance.setOption(adapterOption)
                this.chartInstance.resize()
            },

            // 回到中国地图
            revertMap(){
                const revertOption = {
                    geo:{
                        map:'china'
                    }
                }
                this.chartInstance.setOption(revertOption)
            }
        },
    }
</script>

<style lang="less" scoped>

</style>
<template>
    <div class="com-container">
        <div class="title" :style="comStyle">
            <span>{{"▍ "+showTitle}}</span>
            <span class="iconfont title-icon" :style="comStyle" @click="showChoice = !showChoice"></span>
        </div>
        <div class="com-chart" ref="trend_ref"></div>
    </div>
</template>

<script>
    import {mapState} from 'vuex' 
    // import {getThemeValue} from '../utils/theme_utils'
    export default {
        name:'CdTem',
        data(){
            return {
                chartInstance: null, // 定义ECharts实例化对象
                allData:null, // 从服务器中获取的所有数据
                showChoice:false, // 是否显示可选项
                choiceType:'city', // 显示数据类型不同条目
                titleFontSize:0,  // 指明标题的字体大小
                cd_tem:{
                    city:{
                        title:"成都温度趋势",
                        data:[
                            {
                                name:"白天",
                                data:null
                            },
                            {
                                name:"夜晚",
                                data:null
                            }
                        ]
                    },
                    common:{
                        day:null
                    },
                    type:[{ "key": "city", "text": "成都" }]
                } // 最后数据的容器
            }
        },

        created(){
            // 在组件创建完成之后， 进行回调函数的注册
            this.getData()
        },

        mounted() {
            this.initChart()
            window.addEventListener('resize', this.screenAdapter)
            this.screenAdapter()
        },

        destroyed(){
            // 在组件销毁的时候 进行回调函数的取消
            window.removeEventListener('resize', this.screenAdapter)
        },

        computed:{
            showTitle(){ // 控制显示标题
                if(!this.allData){
                    return ''
                } else {
                    return this.allData[0].title
                }
            },
            comStyle(){ // 设置给标题的样式
                return{
                    fontSize:this.titleFontSize + 'px',
                }
            },
            marginStyle(){
                return{
                    marginLeft:this.titleFontSize + 'px'
                }
            },
            ...mapState(['theme'])
        },

        methods: {
            // 初始化Echarts实例对象
            initChart(){
               this.chartInstance = this.$echarts.init(this.$refs.trend_ref, this.theme)
               const initOption = {
                   grid:{
                       left:'5%',
                       top:'30%',
                       containLabel:true,
                   },
                   xAxis:{ // 坐标轴类型
                       type:'category',
                       boundaryGap:false // 取消间隙
                   },
                   yAxis:{
                       type:'value'
                   },
                   tooltip:{
                       trigger:'axis'
                   },
                   legend:{
                       left:20,
                       top:'15%',
                       icon:'circle'
                   },
               }
               // 将配置项配置给echarts实例对象
               this.chartInstance.setOption(initOption) 
            }, 

            // 获取服务器数据;ret 就是服务端发送给客户端的图表的数据    
            async getData(){
                const {data: ret} = await this.$http.get('/cd_tems')
                this.allData = ret.data
                // 白天数据
                const daytime = []
                // 夜晚数据
                const night = []
                // 日期
                const day = []
                this.allData.map(item=>{
                    daytime.push(item.daytime)
                    night.push(item.night)
                    day.push(item.day)
                    return false
                })

                this.cd_tem.city.data[0].data = daytime
                this.cd_tem.city.data[1].data = night
                this.cd_tem.common.day = day

                this.updataChart()
            },

            // 数据改变时更新图表
            updataChart(){
                // 半透明的颜色值
                const colorArr1 = [
                    'rgba(11,148,44,0.5)',
                    'rgba(44,110,255,0.5)',
                    'rgba(22,242,217,0.5)',
                    'rgba(254,33,30,0.5)',
                    'rgba(250,105,0,0.5)'
                ]
                // 半透明的颜色值
                const colorArr2 = [
                    'rgba(11,168,44,0)',
                    'rgba(44,110,255,0)',
                    'rgba(22,242,217,0)',
                    'rgba(254,33,30,0)',
                    'rgba(250,105,0,0)'
                ]

                // 处理数据
                const timeArr = this.cd_tem.common.day // 类目轴数据
                const valueArr = this.cd_tem.city.data // y轴数据

                const seriesArr = valueArr.map((item, index) => {
                    return {
                        name:item.name,
                        type:'line',
                        data:item.data,
                        stack:this.choiceType, // 堆叠效果
                        areaStyle:{ // 填充效果
                            color: new this.$echarts.graphic.LinearGradient(0, 0, 0, 1, [
                                {
                                    // 0%的颜色值
                                    offset:0,
                                    color:colorArr1[index]
                                }, 
                                {
                                    // 100%的颜色值
                                    offset:1,
                                    color:colorArr2[index]
                                }
                            ])
                        }
                    }
                })

                // 图例的数据
                const legendArr = valueArr.map(item => {
                    return item.name
                })

                const dataOption = {
                    xAxis:{ // 类目轴数据
                        data:timeArr
                    },
                    series:seriesArr,
                    legend:{ // 图例效果
                        data:legendArr
                    }
                }
                this.chartInstance.setOption(dataOption)
            },

            // 进行屏幕适配--图表自适应
            screenAdapter(){
                this.titleFontSize = this.$refs.trend_ref.offsetWidth/100 * 3.6
                const adapterOption = {
                    legend:{ // 设置图例的大小
                        itemWidth:this.titleFontSize,
                        itemHeight:this.titleFontSize,
                        itemGap:this.titleFontSize,
                        textStyle:{
                            fontSize:this.titleFontSize / 2
                        } 
                    }
                }
                this.chartInstance.setOption(adapterOption)
                this.chartInstance.resize()
            },

            // 点击切换显示不同类型条目
            handleSelect(currentType){
                this.choiceType = currentType
                this.updataChart()
                this.showChoice = false
            }
        },

        watch:{
            theme(){
                this.chartInstance.dispose()    
                this.initChart()
                this.updataChart()
                this.screenAdapter()
            }
        },
    }
</script>

<style lang="less" scoped>
    .title{
        position:absolute;
        left:25px;
        top: 20px;
        z-index: 2;
        overflow: hidden;
        color: rgb(180, 198, 216);
        background-color: rgb(27, 74, 102);
        border-radius: 20px;
        cursor: pointer;
        .title-icon{
            margin-left: 10px;
            cursor: pointer;
        }
    }
</style>
<template>
  <!-- 商家销量统计的横向状图 -->
  <div class="com-container">
      <div class="com-chart" ref="seller_ref"></div>
  </div>
</template>

<script>
    import {mapState} from 'vuex'
    export default {
        name:'TemHot',
        data(){
            return {
                chartsInstance: null,
                allData:null, // 服务器返回的数据
                currentPage:1, // 当前显示的页数
                totalPage:0, // 一共有多少页
                timerId:null // 定时器标识
            }
        }, 

        created(){
            this.getData()
        },

        mounted() { // 页面挂载完毕执行相关操作
            this.initCharts()
            this.getData()
            window.addEventListener('resize', this.screenAdapter)
            // 在界面加载完成时，主动进行屏幕的适配
            this.screenAdapter() 
        },

        destroyed(){ // 组件销毁时取消定时器
            clearInterval(this.timerId)
            // 注销监听事件，防止出现内存泄露的问题，组件销毁后注销
            window.removeEventListener('resize', this.screenAdapter)
        },

        methods: {
            // 初始化echartsInstance对象
            initCharts () {
                this.chartsInstance = this.$echarts.init(this.$refs.seller_ref, this.theme)
                // 对图表初始化配置的控制
                const initOption = {
                    title:{
                        text:'▍全国高温城市排行',
                        left:10,
                        top:10
                    },

                    grid:{ // 修改整个网格的布局
                        top:'15%',
                        left:'8%',
                        containLabel:true // 百分比距离包含坐标轴文字
                    },

                    xAxis:{
                        type:'value',
                        name:"单位:°C"
                    },

                    yAxis:{
                        type:'category',
                        name:"城市"
                    },

                    tooltip:{
                        trigger:'axis',
                        axisPointer:{ // 鼠标触发类型
                            type:'line',
                            z:0,// 改变层级
                            lineStyle:{ // 线条配置
                                color:"#333",
                            }
                        }
                    },

                    series:[
                        {
                            type:'bar',
                            label:{
                                show:true,
                                position:'right',
                                textStyle:{
                                    color:'fff'
                                }
                            },
                            itemStyle:{
                                /* 
                                    graphic.LinearGradient(a, b, c, d, arr)
                                        a,b,c,d值可取0，1

                                        a:1 arr中的颜色从右到左渐变
                                        c:1 arr中的颜色从左到右渐变
                                        b:1 arr中的颜色从下到上渐变
                                        d:1 arr中的颜色从上到下渐变

                                        arr:[ // 从起点到终点
                                            {
                                                offset:位置,
                                                color:'颜色'
                                            }
                                            .....
                                        ]
                                */
                                color: new this.$echarts.graphic.LinearGradient(0,0,1,0, [ // 从左到右渐变
                                    {
                                        // 0%状态之下的颜色值
                                        offset:0,
                                        color:'#5052EE'
                                    },
                                    {
                                        // 100%状态下的颜色值
                                        offset:1,
                                        color:'#AB6EE5'
                                    }
                                ])
                            }
                        }
                    ]
                }
                this.chartsInstance.setOption(initOption) // 第一次配置setOption
                // 对图表对象进行鼠标事件的监听
                this.chartsInstance.on('mouseover', ()=>{ // 鼠标移入时移除定时器
                    clearInterval(this.timerId)
                })
                this.chartsInstance.on('mouseout',()=>{ // 移出时执行定时器
                    this.startInsterval()
                })
            },
            // 获取服务器的数据
            async getData () {
                // http://127.0.0.1:5000/api/seller, 基准路径为 http://127.0.0.1:5000/api 添加seller即可
                const {data: ret} = await this.$http.get('/tem_hots')
                console.log(ret.data)
                this.allData = ret.data
                // 对数据进行排序
                this.allData.sort((a, b)=>{
                    return parseFloat(a.average) - parseFloat(b.average) // 从小到大排序
                })
                // 每5个元素显示一页
                this.totalPage = this.allData.length % 5 === 0 ? this.allData.length / 5 : this.allData.length / 5 + 1
                this.updataChart()
                this.startInsterval()
            },

            // 更新图表
            updataChart () {
                const start = (this.currentPage - 1) * 5 // 索引值从0开始
                const end = this.currentPage * 5 // 5
                const showData = this.allData.slice(start, end) // 截取数据段
                const sellerName = showData.map((item)=>{
                    return item.city_name
                })
                const sellerValue = showData.map((item)=>{
                    return parseFloat(item.average)
                })

                const option = {
                    yAxis:{
                        data:sellerName
                    },
                    series:[
                        {
                            data:sellerValue,
                        }
                    ]
                }

                // 第二次配置setOption
                this.chartsInstance.setOption(option)
            },

            startInsterval(){
                if(this.timerId){ // 如果存在定时器则清除上一次定时器
                    clearInterval(this.timerId)
                }
                this.timerId = setInterval(() => {
                    this.currentPage++
                    if(this.currentPage > this.totalPage){
                        this.currentPage = 1
                    }
                    this.updataChart() // 跟随最新的数据进行配置
                }, 3000);
            },

            // 浏览器大小发生改变时，会调用的方法，来完成屏幕的适配
            screenAdapter(){
                const titleFontSize = this.$refs.seller_ref.offsetWidth / 100 * 3.6 // 字体大小与屏幕宽度的比例关系 

                // 和分辨率大小相关的配置项
                const adapterOption = {
                    title:{
                        text:'▍全国高温城市排行',
                        textStyle:{
                            fontSize:titleFontSize,
                            // color:'#fff',
                        },
                    },

                    tooltip:{
                        axisPointer:{ // 鼠标触发类型
                            lineStyle:{ // 线条配置
                                width:titleFontSize,
                            }
                        }
                    },

                    series:[
                        {
                            barWidth:titleFontSize,
                            itemStyle:{
                                barBorderRadius:[titleFontSize/2, titleFontSize/2, titleFontSize/2, titleFontSize/2]
                            }
                        }
                    ]
                }
                this.chartsInstance.setOption(adapterOption)
                // 手动的调用图表对象的resize才能产生
                this.chartsInstance.resize()
            }
        },

        computed:{
            ...mapState(['theme'])
        },

        watch:{
            theme(){
                this.chartsInstance.dispose()
                this.initCharts()
                this.updataChart()
                this.screenAdapter()
            }
        }, 
    }
</script>

<style lang="less" scoped>

</style>
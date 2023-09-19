<template>
    <div class="com-container">
        <div class="com-chart" ref="rank_ref"></div>
    </div>
</template>

<script>
    import {mapState} from 'vuex'
    export default {
        name:'TemCool',
        data() {
            return {
                chartInstance:null,
                allData:null,
                startValue:0, // 区域缩放起点值
                endValue:9, // 区域缩放终点值
                timeId:null, // 定时器标识
                titleFonsize:null,
            }
        },

        created(){
            this.getData
        },

        mounted() {
            this.initChart()
            this.getData()
            window.addEventListener('resize', this.screenAdapter)
            this.screenAdapter()
        },

        destroyed() {
            window.removeEventListener('resize', this.screenAdapter)
            clearInterval(this.timeId)
        },

        methods: {
            initChart(){
                // 'rdf_dark'
                this.chartInstance = this.$echarts.init(this.$refs.rank_ref,this.theme)
                const initOption = {
                    title:{
                        text:'▍低温城市详情',
                        left:20,
                        top:20
                    },
                    grid:{
                        top:'20%',
                        left:'10%',
                        containLabel:true
                    },
                    tooltip:{
                        show:true 
                    },
                    xAxis:{
                        type:'category'
                    },
                    yAxis:{
                        type:"value"
                    },
                    series:[
                        {
                            type:'bar'
                        }
                    ]
                }
                this.chartInstance.setOption(initOption)
                this.chartInstance.on('mouseover', ()=>{ // 鼠标移入时清除定时器
                    clearInterval(this.timeId)
                })
                this.chartInstance.on('mouseout', ()=>{ // 鼠标移出时启动定时器
                    this.startInterval()
                })

            },

            async getData(){ // 异步获取数据
                const {data:ret} = await this.$http.get('/tem_cols')
                this.allData = ret.data
                this.allData.sort((a, b)=>{
                    return b.average - a.average
                })
                // console.log(ret)
                this.updataChart()
                this.startInterval()
            },

            updataChart(){
                // 所有省份的数组
                const provinceArr = this.allData.map(item => {
                    return item.city_name
                })

                // 所有省份对应的温度
                const valueArr = this.allData.map(item=>{
                    return parseFloat(item.average)
                })
                
                const dataOption = {
                    xAxis:{
                        data:provinceArr
                    },
                    dataZoom:{
                        show:false,
                        startValue:this.startValue,
                        endValue:this.endValue
                    },
                    series:[
                        {
                            data:valueArr,
                            itemStyle:{
                                color: new this.$echarts.graphic.LinearGradient(0,0,1,0,[
                                    {
                                        offset:0,
                                        color:'#5052EE'
                                    },
                                    {
                                        offset:1,
                                        color:'#AB6EE5'
                                    }
                                ]),
                                
                            }
                        }
                    ]
                }
                this.chartInstance.setOption(dataOption)
            },

            screenAdapter(){
                this.titleFonsize = this.$refs.rank_ref.offsetWidth / 100 *3.6
                const adapterOption = {
                    title:{
                        textStyle:{
                            fontSize:this.titleFonsize
                        }
                    },
                    series:[
                        {
                            barWidth:this.titleFonsize,
                            itemStyle:{
                                barBorderRadius:[this.titleFonsize / 2, this.titleFonsize / 2, this.titleFonsize / 2, this.titleFonsize / 2]
                            },
                            label:{
                                show:true,
                                color:'#fff'
                            }
                        }
                    ]
                }
                this.chartInstance.setOption(adapterOption)
                this.chartInstance.resize()
            },
            
            startInterval(){
                // 判断之前的定时器是否存在，先取消掉之前的定时器
                if(this.timeId){
                    clearInterval(this.timeId)
                }
                this.timeId = setInterval(()=>{
                    this.startValue++
                    this.endValue++
                    if(this.endValue>this.allData.length-1){
                        this.startValue = 0
                        this.endValue = 9
                    }
                    this.updataChart()
                }, 2000)
            }
        },
        
        computed:{
            ...mapState(['theme'])
        },

        watch:{
            theme(){
                this.chartInstance.dispose()
                this.initChart()
                this.screenAdapter()
                this.updataChart()
            }
        },
    }
</script>

<style lang='less' scoped>

</style>
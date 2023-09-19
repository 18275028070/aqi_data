export default class SocketService {
    /* 
        单例设计模式
    */
    static instance = null
    static get Instance(){ // 对外开放
        if(!this.instance){
            this.instance = new SocketService()
        }
        return this.instance
    }

    // 和服务端连接的socket对象
    ws = null

    // 存储回调函数
    callBackMapping = {}

    // 标识是否已经连接成功(默认为否)
    connected = false

    // 记录尝试的次数
    sendRetryCount = 0

    // 重新连接尝试的次数
    connectRetryCount = 0

    // 定义连接服务器的方法
    connect(){
        // 连接服务器
        if(!window.WebSocket){
            return console.log('您的浏览器不支持WebSocket')
        }
        this.ws = new WebSocket('ws://127.0.0.1:8880')

        // 连接成功的事件
        this.ws.onopen = () => {
            console.log("连接服务端成功了")
            this.connected = true
            this.connectRetryCount = 0 // 重置重连次数
        }
        // 1.连接失败的事件
        // 2.当连接成功之后，服务器关闭的情况
        this.ws.onclose = () => {
            console.log("连接服务端失败")
            this.connected = false
            this.connectRetryCount++
            setTimeout(()=>{
                this.connect()
            },500 * this.connectRetryCount) // 失败次数越多，重连的时间越长
        }
        // 得到服务端发送过来的数据
        this.ws.onmessage = msg => {
            console.log("从服务端获取到了数据")
            // console.log(msg.data) // 原始数据
            const recvData = JSON.parse(msg.data)
            const socketType = recvData.socketType
            if(this.callBackMapping[socketType]){
                const action = recvData.action
                if(action === 'getData'){
                    const realData = JSON.parse(recvData.data)
                    this.callBackMapping[socketType].call(this, realData)
                } else if (action === 'fullScreen'){

                } else if (action === 'themechange') {

                }
            }
        }
    }

    // 回调函数的注册(存储)
    registerCallBack(socketType, callBack){
        this.callBackMapping[socketType] = callBack
    }
    
    // 取消某一个回调函数
    unregisterCallBack(socketType){
        this.callBackMapping[socketType] = null
    }
    
    // 发送数据的方法
    send(data){
        // 判断此刻有没有连接成功   
        if(this.connected){
            this.ws.send(JSON.stringify(data))
        } else {
            this.sendRetryCount++ 
            setTimeout(()=>{
                this.send(data)
            },500)
        }   
        
    }
}


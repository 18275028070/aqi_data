// 创建WebSocket服务端对象
const WebSocket = require('ws')
const path = require('path')
const fileUtils = require('../utils/file_utils')
const wss = new WebSocket.Server({
    port: 8880
})

module.exports.listen = () => {
    // 对客户端的连接事件进行监听
    // client:代表的是客户端的连接socket对象
    wss.on('connection', client => {
        console.log("客户端连接成功")
        // 对客户端的连接对象进行message事件的监听
        // msg: 由客户端发给服务端的数据
        client.on('message', async msg => { // 后端接收到的数据
            // console.log('客户端发送数据给服务端了: ' + msg)
            let payload = JSON.parse(msg)
            const action = payload.action

            if(action === 'getData'){
                let filePath = '../data/' + payload.chartName + '.json' // 进行对应文件路径的拼接
                filePath = path.join(__dirname, filePath)
                const ret = await fileUtils.getFileJsonDate(filePath) // promise对象返回过来的状态对应的数据字段
                // 需要在服务端获取到数据的基础之上，增加一个data字段
                // data所对应的值，就是某个json文件的内容
                payload.data = ret
                client.send(JSON.stringify(payload)) // 向前端发送数据
            } else {
                // 原封不动的将接收到的数据转发给每一个处于连接状态的客户端
                // wss.clients  所有客户端的连接
                wss.clients.forEach(client => {
                    client.send(msg)
                })
            }

            // client.send('hello socket from backend') // 后端向前端发送数据
        })
    })
}


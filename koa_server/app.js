// 服务器入口文件
const Koa = require("koa2")
const app = new Koa()

// 绑定第一层中间件,耗时中间件
const resDurationMiddleware = require("./middleware/koa_response_duration")
app.use(resDurationMiddleware)

// 绑定第二层中间件,响应头中间件
const resHeaderMiddleware = require("./middleware/koa_response_header")
app.use(resHeaderMiddleware)

// 绑定第三层中间件,业务逻辑中间件    
const resDataMiddleware = require("./middleware/koa_response_data")
app.use(resDataMiddleware)

app.listen(5000, ()=>{
    console.log("开启服务器:http://127.0.0.1:5000/api/seller")
})



const webSocketService = require('./serves/web_socket_service')
// 开启服务端的监听，监听客户端的连接
// 当某一个客户端连接成功之后，就会对这个客户端进行message事件的监听
webSocketService.listen()
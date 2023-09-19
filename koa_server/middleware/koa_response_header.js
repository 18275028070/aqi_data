// 设置响应头的中间件

/* 
    允许跨域
        1.实际是通过Ajax访问服务器
        2.同源策略
            同协议\同域名\同端口
            当前页面的地址和Ajax获取数据的地址
        3.设置响应头
            app.use(async (ctx, next)=>{
                ctx.set("Access-Control-Allow-Origin","*")
                ctx.set("Access-Control-Allow-Methods","OPTIONS,GET,PUT,POST,DELETE")
                await next()
            })
*/

module.exports = async (ctx, next) => {
    const contentType = 'application/json; charset=utf-8'
    ctx.set('Content-Type',contentType)
    ctx.set("Access-Control-Allow-Origin","*")
    ctx.set("Access-Control-Allow-Methods","OPTIONS,GET,PUT,POST,DELETE")
    ctx.response.body = '{"success":true}'
    await next()
}
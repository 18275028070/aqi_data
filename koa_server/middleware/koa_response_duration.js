// 计算服务器消耗时长的中间件
/* 
    总耗时中间件
        1.第一层中间件
        2.计算执行时间
            一进入时开始时间
            其他所有中间件执行完后记录执行时间
            两者相减
        3.设置响应头 X-Response-Time
*/
module.exports = async (ctx, next)=>{
    const start = Date.now()
    const end = Date.now()
    // 设置响应头,X-Response-Time
    const duration = end - start
    // ctx.set 设置响应头
    ctx.set('X-Response-Time', duration + 'ms')
    await next()
}
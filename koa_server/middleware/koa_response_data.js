// 处理业务逻辑的中间件，读取某个json文件的数据
const path = require('path')
const fileUtils = require('../utils/file_utils')
module.exports = async (ctx, next) => {
    // 获取url,修改至指定路径:../data/seller.json
    const url = ctx.request.url // /api/seller 
    // 将/api替换掉
    let filePath = url.replace('/api', '') // seller
    // 将请求的网址加上.json则为对应的文件
    filePath = '../data' + filePath + '.json' // ../data/seller.json
    // 将当前路径和请求路径进行拼接
    filePath = path.join(__dirname, filePath) // 把路径给替换掉  
    
    try {
        // 得到一个Promise对象，语法糖 await得到成功之后的Promise
        const ret = await fileUtils.getFileJsonDate(filePath)

        // 将获取到的内容添加到
        ctx.response.body = ret
    } catch (error) {
        const errorMsg = {
            message:'读取文件内容失败, 文件资源不存在',
            status:404
        }
        ctx.response.body = JSON.stringify(errorMsg)
    }   

    console.log(filePath)
    await next()
}
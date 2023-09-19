// 读取文件的工具方法
const fs = require('fs')
module.exports.getFileJsonDate = (filePath) => {
    // 根据文件路径读取文件的内容
    return new Promise((resolve, reject) => {
        fs.readFile(filePath, 'utf-8', (error, data) => {
            if (error) {
                // 读取文件失败
                reject(error)
            } else {
                // 读取文件成功
                resolve(data)
            }
        })
    })
}   
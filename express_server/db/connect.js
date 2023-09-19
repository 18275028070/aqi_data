const mongoose = require("mongoose");

mongoose.connect("mongodb://127.0.0.1:27017/aqis").then(
  () => {
    console.log("连接成功")
  },
  (e) => {
    console.log("连接失败，请重试...");
    throw e;
  }
)

let aqiSchema = new mongoose.Schema({})

let aqiModel = document =>{
    return mongoose.model(document, aqiSchema);
}

module.exports = aqiModel
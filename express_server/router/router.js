const express = require("express");
const router = express.Router();
const aqiModel = require("../db/connect");

router.get("/", async (req, res, next) => {
  // 得到aqi数据
  let data = await aqiModel("aqi_datas").find();
  res.json({
    code: 200,
    msg: "请求成功",
    data: data,
  });
  next();
});

router.get("/cd_tems", async (req, res, next) => {
  // 得到成都温度数据
  let data = await aqiModel("cd_tems").find();
  res.json({
    code: 200,
    msg: "请求成功",
    data: data,
  });
  next();
});

router.get("/tem_cols", async (req, res, next) => {
  // 得到全国低温数据
  let data = await aqiModel("tem_cols").find();
  res.json({
    code: 200,
    msg: "请求成功",
    data: data,
  });
  next();
});

router.get("/tem_hots", async (req, res, next) => {
  // 得到全国高温数据
  let data = await aqiModel("tem_hots").find();
  res.json({
    code: 200,
    msg: "请求成功",
    data: data,
  });
  next();
});

router.get("/map_aqis", async (req, res, next) => {
  // 得到全国aqi地图数据
  let data = await aqiModel("aqi_datas").find()
  res.json({
    code:200,
    msg:"请求成功",
    data:data
  })
  next()
})

router.get("/seven", async (req, res, next)=>{
  // 得到全国aqi地图数据
  let data = await aqiModel("aqi_sevens").find()
  res.json({
    code:200,
    msg:"请求成功",
    data:data
  })
  next()
})

module.exports = router;

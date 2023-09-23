const router = require("./router/router")
const express = require("express")
const cors = require("cors")
const app = express()

app.use(cors())
app.use(express.json())
app.use(express.urlencoded({extended:false}))

app.use("/aqi", router)

app.listen("5500", "0.0.0.0", ()=>{
    console.log("http://localhost:5500服务开启成功,监听端口中...")
})

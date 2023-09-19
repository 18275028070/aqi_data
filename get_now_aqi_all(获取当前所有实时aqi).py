import csv
import json
import requests
from bs4 import BeautifulSoup
import sched
import time
import pandas as pd
import os
import pymongo as pg

"""
    设计思路一：
        获取全部城市数据以后，将数据保存于csv文件以后，进行追加每个城市的数据

    设计思路二： 
        获取每个城市数据，单独的文件
        
    空气质量划分
        指标：AQI (O3, CO, SO2, pm2.2, pm10, NO2)

        1、一级： 空气污染指数 ≤50优级
        2、二级： 空气污染指数 ≤100良好
        3、三级： 空气污染指数 ≤150轻度污染
        4、四级： 空气污染指数 ≤200中度污染
        5、五级： 空气污染指数 ≤300重度污染
        6、六级：空气污染指数＞300严重污染
"""

"""
    目标网站：http://www.tianqihoubao.com/aqi/ ----> 获取城市单页面
    获取单城市页面实时数据
"""
header = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 "
                  "Safari/537.36 Edg/110.0.1587.57",
    "referer": "http://www.tianqihoubao.com/"
}

# 用于存放城市名称
city_names = list()

# 将对应的数据放入容器中
city_now_datas = []
city_now_data_db = []

# 定义城市名对应下标
index = 0


class Get_one_url:
    def __init__(self, _name, _url):
        self.url = _url
        self.name = _name

    ############################################################
    # 函数功能：获取各个城市的名字及对应的url
    # 传入参数：无
    # 输出参数：citys_name，字典类型，城市名称为键，对应的url为值
    ############################################################
    def get_city(self):
        response = requests.get(url=self.url, headers=header).text
        soup = BeautifulSoup(response, 'html.parser')  # 用靓汤解析网页源码获取class为citychk的标签
        tables = soup.find_all(class_="citychk")
        citys_name = dict()
        for table in tables:
            citys_url = table.select("a")  # 挑选出其中的a标签并抽取其中的文本以及href
            for city in citys_url:
                city_name = city.text.strip()  # 城市名称，使用strip去除尾部的空格
                city_name = city_name.encode('iso-8859-1').decode('gbk')  # 对中文乱码重新编码
                city_urls = city.attrs.get("href").strip()  # 城市的url
                city_names.append(city_name)  # 保存的当前获取数据的城市名
                if city_name == "全国空气质量排名":  # 忽略网页中禹城市无关的文本
                    continue
                # 百色需要特殊处理——html源码中的地址爬取后为http://www.tianqihoubao.com/aqi/baise\r\n.html
                # 由于噪声字符不是位于字符串的头和尾，因此需要额外加个特判
                if city_name == "百色":
                    citys_name[city_name] = "http://www.tianqihoubao.com/aqi/baise.html"
                    continue
                # if city_name == "石家庄":
                #     break
                citys_name[city_name] = "http://www.tianqihoubao.com" + city_urls  # 添加字典，格式为：城市名称——对应url
        return citys_name

    ############################################################
    # 函数功能：根据提取的城市链接获取对应城市相关数据
    # 传入参数：city_url：每个城市的URL
    # 输出参数：city_now_data：每个城市的相关数据
    ############################################################
    def get_now_data(self, city_url):
        response = requests.get(url=city_url, headers=header).text
        # 获取表格标签
        html = BeautifulSoup(response, "html.parser")
        table = html.find("table", class_="b")

        global index
        try:
            t_b = table.findAll("tr")[1]
            # 获取城市
            # 得到具体的aqi数据
            t_aqi = t_b.findAll("td")[1].text.strip()
            print(t_aqi)
            # 获取PM10
            t_p_2_10 = t_b.findAll("td")[3].text.strip()
            # 获取PM2.5
            t_p_2_5 = t_b.findAll("td")[4].text.strip()
            # 获取CO
            t_co = t_b.findAll("td")[5].text.strip()
            # NO2
            t_no2 = t_b.findAll("td")[6].text.strip()
            # 获取SO2
            t_so2 = t_b.findAll("td")[7].text.strip()
            # O3
            t_O3 = t_b.findAll("td")[8].text.strip()

            # for i in range(len(city_names)):

            city_now_data = {"city": city_names[index],
                             "AQI": t_aqi,
                             "PM2.5": t_p_2_5,
                             "PM10": t_p_2_10,
                             "CO": t_co,
                             "NO2": t_no2,
                             "SO2": t_so2,
                             "O3": t_O3
                             }

            # 保存为JSON格式
            city_now_data2 = {"city": city_names[index],
                              "data": [
                                  {
                                      "name": "AQI",
                                      "value": t_aqi
                                  },
                                  {
                                      "name": "PM2.5",
                                      "value": t_p_2_5
                                  },
                                  {
                                      "name": "PM10",
                                      "value": t_p_2_10
                                  },
                                  {
                                      "name": "CO",
                                      "value": t_co
                                  },
                                  {
                                      "name": "NO2",
                                      "value": t_no2
                                  },
                                  {
                                      "name": "SO2",
                                      "value": t_so2
                                  },
                                  {
                                      "name": "O3",
                                      "value": t_O3
                                  }
                              ]
                              }
            city_now_data_db.append(city_now_data2)
            city_now_datas.append(city_now_data)
            time.sleep(1)
        except:
            print("cannot found")
        index += 1
        return city_now_datas

    ############################################################
    # 函数功能：保存模块
    # 传入参数：data：最终爬取的数据
    # 输出参数：.json文件
    ############################################################
    def save_json(self, data):

        """
            将json数据保存到前端文件夹或当前AQI文件夹作为分析处理
        """
        # 当前文件夹
        path = 'AQI/'
        # 前端项目文件夹
        path_2 = 'D:/毕业设计/vue_project_study/koa_server/data/'
        # with open(path2 + "city_now(包括6项指标)_1.json", 'w', encoding='utf-8') as f:
        #     f.write(json.dumps(data, indent=4, ensure_ascii=False))
        #     print("文件写入成功")
        # print("前端项目文件夹已接收文件")

        """
            将爬取的数据保存到实时数据分析文件夹里面
        """
        if os.path.exists("./实时数据分析/实时数据.csv"):
            os.remove("./实时数据分析/实时数据.csv")
        with open("./实时数据分析/实时数据.csv", "w", newline="", encoding="gb2312") as to_csv:
            column = ['city', 'AQI', 'PM2.5', 'PM10', 'CO', 'NO2', 'SO2', 'O3']  # 定义列名
            writer = csv.DictWriter(to_csv, fieldnames=column)
            writer.writeheader()  # 写入列名
            for d in data:
                writer.writerow(d)  # 写入数据

    def save_mongo(self, data):
        """
            保存至mongoDB数据库
        """
        try:
            client = pg.MongoClient("mongodb://127.0.0.1:27017/")
            # 链接数据库
            db = client["aqis"]
            # 查询字段
            coll = db["aqi_sevens"]
            # 查询文档
            for i in data:
                city = i["city"]
                AQI = i["data"][0]["value"]
                PM2_5 = i["data"][1]["value"]
                PM10 = i["data"][2]["value"]
                CO = i["data"][3]["value"]
                NO2 = i["data"][4]["value"]
                SO2 = i["data"][5]["value"]
                O3 = i["data"][6]["value"]
                coll.insert_one(
                    {
                        "city": city,
                        "aqi": AQI,
                        "pm2.5": PM2_5,
                        "pm10": PM10,
                        "co": CO,
                        "no2": NO2,
                        "so2": SO2,
                        "o3": O3
                    }
                )
            print("保存数据库成功")
            client.close()
        except EOFError as e:
            print(e)

    ############################################################
    # 函数功能：主函数
    # 传入参数：无
    # 输出参数：
    ############################################################
    def main(self):
        if not os.path.exists("./AQI"):  # 创建文件夹
            os.mkdir(r'./AQI')
        #  定义数据容器
        # city_aqi_data_all = list()
        _city_names = self.get_city()  # 得到城市URL数据
        for city in _city_names:
            print("开始爬取%s数据:" % city)
            try:
                city_url = _city_names[city]  # 获取每个城市的url
                city_aqi_data = self.get_now_data(city_url)  # 获取每个城市url中的对应数据
                print(city_aqi_data[-1]["city"])
                # 如果获取的城市url中name==对应的值的时候，则进行保存
                if city_aqi_data[-1]["city"] == "喀什":
                    # city_aqi_data_all.append(city_aqi_data)
                    self.save_json(city_aqi_data)
                    print("数据保存成功!!")
            except:
                print("list index out of range,没有获取到数据"),
                return ""

        print("数据爬取完成")

        self.save_mongo(city_now_data_db)
        print("数据库保存成功")

    # def crawl(self, sc):
    #     # 爬取逻辑
    #     self.crawl()
    #
    #     # 重新安排定时器,继续循环
    #     sc.enter(60 * 60 * 24, 1, crawl, (sc,))
    #
    # schedule.enter(0, 1, crawl, (schedule,))
    # schedule.run()


if __name__ == "__main__":
    # 创建对象
    url = "http://www.tianqihoubao.com/aqi/"
    name = None
    get_one_url = Get_one_url(name, url)
    # 访问城市列表数据
    get_one_url.main()

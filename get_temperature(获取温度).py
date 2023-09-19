import json
import requests
from bs4 import BeautifulSoup
import pandas as pd
import pymongo as pg
"""
    url_最高：https://tianqi.2345.com/temperature-rank.htm
    url_最低：https://tianqi.2345.com/temperature-rank-rev.htm
"""

header = {
    # "Host": "tianqi.2345.com",
    # "Referer": "http://tianqi.2345.com/",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 "
                  "Safari/537.36",
}


class Temperature:
    def __init__(self, url, _header):
        self.url = url
        self.header = _header

    # 访问页面
    def request_url(self):
        try:
            rsp = requests.get(self.url, headers=self.header)
            rsp.encoding = "utf-8"
            html = BeautifulSoup(rsp.text, "html.parser")
            print("访问成功")
            return html
        except IOError as i:
            print("请求失败", i)
            return ""

    # 因为最高气温和最低气温网页结构，所以将共同代码提取出来
    def request_data_same(self):
        j_table = self.request_url().find("div", class_="j-tbody")
        j_trs = j_table.find_all("div", class_="j-tr")
        # print(j_trs)
        # 创建数据容器
        data_list = []
        for j_tr in j_trs:
            # 获取城市
            j_tr_city = j_tr.find("div", class_="j-td j-td-l").a.text
            # print(j_tr_city)
            # 获取今日气温
            j_tr_today = j_tr.find_all("div", class_="j-td")[2].text.strip()  # 去掉两端空格
            # print(j_tr_today)
            # 获取平均气温
            j_tr_avg = j_tr.find_all("div", class_="j-td")[3].text.strip()
            # print(j_tr_avg)
            # 保存到容器
            temperature_data = {"city": j_tr_city, "today": j_tr_today, "average": j_tr_avg}
            data_list.append(temperature_data)
        print(data_list)

        return data_list

    # 获取最高气温
    def get_hot(self):
        print("获取数据成功!")
        return self.request_data_same()

    # 获取最低气温
    def get_cool(self):
        print("获取数据成功!")
        return self.request_data_same()

    # 保存数据,name为保存的高温和低温，info为键盘输入
    def save_data(self, info):
        path = "./temperature/"
        path2 = "D:/毕业设计/vue_project_study/koa_server/data/"  # 前端文件路径
        # 连接数据库
        client = pg.MongoClient("mongodb://127.0.0.1:27017/")
        db = client["aqis"]
        # 判断，如果输入info为hot，那么保存为高温数据文件
        if info == 1:
            hot = self.get_hot()
            name = "_hot"  # 定义一个接收参数
            with open(path2 + f"temperature{name}.json", "w+", encoding="utf-8") as f:
                f.write(json.dumps(hot, indent=4, ensure_ascii=False))
                print("高温城市数据文件写入成功")
            try:
                # # 链接数据库
                # db = client["aqis"]
                # 查询字段
                coll = db["tem_hots"]
                # 添加字段
                for i in hot:
                    city_name = i["city"]  # 城市
                    today = i["today"]  # 今天温度
                    average = i["average"]  # 经度

                    coll.insert_one(
                        {
                            "city_name": city_name,
                            "today": today,
                            "average": average
                        }
                    )
                print("添加成功")
            except EOFError as e:
                print(e)
        elif info == 2:
            cool = self.get_cool()
            name = "_cool"  # 定义一个接收参数
            with open(path2 + f"temperature{name}.json", "w+", encoding="utf-8") as f:
                f.write(json.dumps(cool, indent=4, ensure_ascii=False))
                print("低温城市数据文件写入成功")
            try:
                # 查询字段
                coll = db["tem_cols"]
                # 添加字段
                for i in cool:
                    city_name = i["city"]  # 城市
                    today = i["today"]  # 今天温度
                    average = i["average"]  # 经度

                    coll.insert_one(
                        {
                            "city_name": city_name,
                            "today": today,
                            "average": average
                        }
                    )
                print("添加成功")
            except EOFError as e:
                print(e)

        else:
            print("请输入正确的字段")
        # 关闭连接
        client.close()

    # 主函数
    def main(self):
        info = int(input("请输入你要保存的数据字段（hot(高温城市) || cool(低温城市)）: "))
        self.save_data(info)


# 访问最高气温页面
url_hot = "https://tianqi.2345.com/temperature-rank.htm"
# 创建高温对象
temperature_hot = Temperature(url_hot, header)
# temperature_hot.get_hot()
temperature_hot.main()

# 访问最低气温页面
url_cool = "https://tianqi.2345.com/temperature-rank-rev.htm"
# 创建低温对象
temperature_cool = Temperature(url_cool, header)
# temperature_cool.get_cool()
temperature_cool.main()
"""
    .代表一个空格
    "···xyz···".strip()            # returns "xyz"  删除字符两端空格
    "···xyz···".lstrip()           # returns "xyz···"  删除左侧空格
    "···xyz···".rstrip()           # returns "···xyz"  删除右侧空格
    "··x·y·z··".replace(' ', '')   # returns "xyz"    替换空格，用法为replace(old,new)比如替换空格
"""

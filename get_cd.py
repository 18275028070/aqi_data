"""
    当地城市实时天气变化：
        http://t.weather.sojson.com/api/weather/city/101270101
"""
import requests
from bs4 import BeautifulSoup
import csv
import json
import numpy as np
import pymongo as pg
from datetime import date

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 "
                  "Safari/537.36",
}


def getHTMLtext(url):
    """请求获得网页内容"""
    try:
        r = requests.get(url, timeout=30, headers=headers)
        r.encoding = "utf-8"
        print("成功访问")
        return r.text
    except:
        print("访问错误")
        return " "


def get_content(html):
    """处理得到有用信息保存数据文件"""
    final = []  # 初始化一个列表保存数据
    bs = BeautifulSoup(html, "html.parser")  # 创建BeautifulSoup对象
    day = bs.find("div", id="7d").find_all("li")
    i = 0
    for li in day:
        if 7 > i > 0:
            temp = []  # 临时存放每天的数据
            date = li.find('h1').string  # 得到日期
            date = date[0:date.index('日')]  # 取出日期号
            temp.append(date)
            inf = li.find_all('p')  # 找出li下面的p标签,提取第一个p标签的值，即天气
            temp.append(inf[0].string)

            tem_low = inf[1].find('i').string  # 找到最低气温

            if inf[1].find('span') is None:  # 天气预报可能没有最高气温
                tem_high = None
            else:
                tem_high = inf[1].find('span').string  # 找到最高气温
            temp.append(tem_low[:-1])
            if tem_high[-1] == '℃':
                temp.append(tem_high[:-1])
            else:
                temp.append(tem_high)
            final.append(temp)
        i = i + 1
    return final


def get_content2(html, data_7_list):
    """处理得到有用信息保存数据文件"""
    final = []  # 初始化一个列表保存数据
    bs = BeautifulSoup(html, "html.parser")  # 创建BeautifulSoup对象
    body = bs.body
    data = body.find('div', {'id': '15d'})  # 找到div标签且id = 15d
    ul = data.find('ul')  # 找到所有的ul标签
    li = ul.find_all('li')  # 找到左右的li标签
    i = 0  # 控制获取的天数
    for day in li:  # 遍历找到的每一个li
        if i < 8:
            temp = []  # 临时存放每天的数据
            date = day.find('span', {'class': 'time'}).string  # 得到日期
            date = date[date.index('（') + 1:-2]  # 取出日期号
            temp.append(date)
            weather = day.find('span', {'class': 'wea'}).string  # 找到天气
            temp.append(weather)
            tem = day.find('span', {'class': 'tem'}).text  # 找到温度
            temp.append(tem[tem.index('/') + 1:-1])  # 找到最低气温
            temp.append(tem[:tem.index('/') - 1])  # 找到最高气温
            final.append(temp)
    list_data = data_7_list + final
    # print(list_data)
    return list_data


today = date.today()
y = today.strftime("%Y")
s = today.strftime("%m")


def write_to_csv(data):
    """
        保存为json文件
        {
            "city": {
                "title": "成都温度趋势",
                "data": [{
                    "name": "白天",
                    "data": ["10","11","18","21","19","23","15"]
                }, {
                    "name": "夜晚",
                    "data": ["6","9","10","12","9","13","9"]
                }]
            },
            "common": {
                "day": ["2023/3/3", "2023/3/4", "2023/3/5", "2023/3/6", "2023/3/7", "2023/3/8", "2023/3/9"]
            },
            "type": [{
                "key": "city",
                "text": "成都"
            }]
        }
    """
    data_list = []
    np_data = np.array(data)
    print(np_data)
    # 日期
    date = np_data[:, 0]
    # 白天温度
    daytime = np_data[:, 3]
    # 夜晚温度
    nightTime = np_data[:, 2]

    m = s  # 月份替换
    day_list = []  # 日期的列表
    day_data_list = []  # 白天数据
    night_data_list = []  # 夜晚数据
    n = 0  # 用于日期计数
    for i in list(date):
        if int(i) < 31:
            day_list.append(f"{y}/{m}/{i}")
            day_data_list.append(daytime[n])
            night_data_list.append(nightTime[n])
            n += 1
        elif int(i) == 31:

            day_list.append(f"{y}/{m}/{i}")
            day_data_list.append(daytime[n])
            night_data_list.append(nightTime[n])
            m = f'0{int(m) + 1}'

        try:
            client = pg.MongoClient("mongodb://127.0.0.1:27017/")
            # 链接数据库
            db = client["aqis"]
            # 查询字段
            coll = db["cd_tems"]
            coll.insert_one(
                {
                    "day": f"{y}/{m}/{i}",
                    "daylight": "白天",
                    "daytime": daytime[n],
                    "daynight": "夜晚",
                    "night": nightTime[n],
                    "title": "成都温度趋势",
                    "key": "city",
                    "text": "成都"
                }
            )

        except EOFError as e:
            print(e)

    dic = {
        "city": {
            "title": "成都温度趋势",
            "data": [{
                "name": "白天",
                "data": day_data_list
            }, {
                "name": "夜晚",
                "data": night_data_list
            }]
        },
        "common": {
            "day": day_list
        },
        "type": [{
            "key": "city",
            "text": "成都"
        }]
    }

    print(dic)

    with open("D:/毕业设计/vue_project_study/koa_server/data/成都未来几日温度变化.json", "w", encoding="utf-8") as f:
        f.write(json.dumps(dic, ensure_ascii=False))


def main():
    """主函数"""
    print("Weather test")
    # 珠海
    url1 = 'http://www.weather.com.cn/weather/101270101.shtml'  # 7天天气中国天气网
    url2 = 'http://www.weather.com.cn/weather15d/101270101.shtml'  # 8-15天天气中国天气网

    # 获取1~7天的数据
    data7 = getHTMLtext(url1)
    data7_list = get_content(data7)

    # 获取8~15天的数据
    data14 = getHTMLtext(url2)
    data_7_14_data = get_content2(data14, data7_list)

    # 保存数据
    write_to_csv(data_7_14_data)


if __name__ == '__main__':
    main()

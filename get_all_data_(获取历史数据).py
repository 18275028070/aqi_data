# -*- coding = utf-8 -*-
import requests
from lxml import etree
from bs4 import BeautifulSoup
import csv
import os

# UA伪装所使用的User-Agent
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                  '(KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36'
}


############################################################
# 函数功能：获取各个城市的名字及对应的url
# 传入参数：无
# 输出参数：citys_name，字典类型，城市名称为键，对应的url为值
############################################################
def get_city():
    url = r'http://www.tianqihoubao.com/aqi/'

    response = requests.get(url=url, headers=headers).text
    soup = BeautifulSoup(response, 'lxml')  # 用靓汤解析网页源码获取class为citychk的标签
    tables = soup.find_all(class_="citychk")

    citys_name = dict()
    for table in tables:
        citys_url = table.select("a")  # 挑选出其中的a标签并抽取其中的文本以及href
        for city in citys_url:
            city_name = city.text.strip()  # 城市名称，使用strip去除尾部的空格
            city_name = city_name.encode('iso-8859-1').decode('gbk')  # 对中文乱码重新编码
            city_urls = city.attrs.get("href").strip()  # 城市的url

            if city_name == "全国空气质量排名":  # 忽略网页中禹城市无关的文本
                continue
            # 百色需要特殊处理——html源码中的地址爬取后为http://www.tianqihoubao.com/aqi/baise\r\n.html
            # 由于噪声字符不是位于字符串的头和尾，因此需要额外加个特判
            if city_name == "百色":
                citys_name[city_name] = "http://www.tianqihoubao.com/aqi/baise.html"
                continue

            citys_name[city_name] = "http://www.tianqihoubao.com" + city_urls  # 添加字典，格式为：城市名称——对应url

    return citys_name


############################################################
# 函数功能：根据城市的url获取历史大气数据页面的url
# 传入参数：city_url,字符串类型，表示城市的url地址
# 输出参数：months，列表类型，表示该城市一年各月份数据的url
############################################################
def get_month(city_url):
    months = list()

    response = requests.get(url=city_url, headers=headers).text
    tree = etree.HTML(response)  # 使用etree解析网页源码，下面为xpath
    month_list = tree.xpath('//div[@class="box p"]//li[2]/a/@href | //div[@class="box p"]//li[3]/a/@href'
                            '| //div[@class="box p"]//li[4]/a/@href | //div[@class="box p"]//li[5]/a/@href'
                            '| //div[@class="box p"]//li[6]/a/@href | //div[@class="box p"]//li[7]/a/@href'
                            '| //div[@class="box p"]//li[8]/a/@href | //div[@class="box p"]//li[9]/a/@href'
                            '| //div[@class="box p"]//li[10]/a/@href | //div[@class="box p"]//li[11]/a/@href'
                            '| //div[@class="box p"]//li[12]/a/@href | //div[@class="box p"]//li[13]/a/@href')

    for month in month_list:
        month = r'http://www.tianqihoubao.com' + month  # 某城市每个月的url
        months.append(month)

    return months


############################################################
# 获取历史数据
# 输入参数：month_url, 字符串类型，对应月份的url地址
# 输出参数：data_list, 列表，元素也为列表，12个月份的数据
############################################################
def get_record(month_url):
    response = requests.get(url=month_url, headers=headers).text
    tree = etree.HTML(response)
    tr_list = tree.xpath('//div[@class="api_month_list"]/table//tr')

    data_list = list()
    for tr in tr_list[1:]:  # 定位到行，除去表头
        td_list = tr.xpath('./td/text()')
        data = list()
        for td in td_list:  # 定位到具体列
            data.append(td.strip())  # 使用strip函数出去原来数据头和尾的\r\n以及空格
        data_list.append(data)

    return data_list


############################################################
# main函数
############################################################
def main():
    if not os.path.exists(r"./AQI"):  # 创建文件夹
        os.mkdir(r"./AQI")

    citys_name = get_city()  # 获取城市名称及url
    for city in citys_name:  # city为字符串，表示城市名称
        print("开始爬取%s的历史大气数据" % city)
        city_url = citys_name[city]  # 获取每个城市的url
        months = get_month(city_url)  # 获取该城市对应的12个月的url

        index = 0
        for month_url in months:
            index = index + 1
            data_list = get_record(month_url)  # 获取每个月的数据

            with open('./AQI/' + city + '.csv', 'a', newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                if index == 1:  # 写入表头，只写入一次
                    writer.writerow(
                        ["日期", '质量等级', 'AQI指数', '当天AQI排名', 'PM2.5', 'PM10', 'SO2', 'NO2', 'CO', 'O3'])
                writer.writerows(data_list)  # 写入数据

            print("第%d个月已经爬取完成" % index)
        print()


if __name__ == '__main__':
    main()

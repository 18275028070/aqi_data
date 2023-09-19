"""
    数据整合：
        将city.csv文件和爬取的数据csv文件进行整合
"""
import pandas as pd
import csv
import matplotlib.pyplot as plt
import seaborn as sns
import pyecharts.charts
from datetime import datetime
from pyecharts import options as opts
from pyecharts.charts import Geo
from pyecharts.globals import ThemeType, ChartType
import pymongo as pg
import json


# 读取city文件
def read_city():
    df = pd.read_csv("./实时数据.csv", encoding="gb2312")
    df_pd = pd.DataFrame(df)
    df_sorted = df_pd.sort_values(by='city', key=lambda x: x.str.encode('gbk'))
    print(df_sorted)
    return df_sorted


# 读取空气数据
def read_aqi():
    df2 = pd.read_csv("./data/city.csv", encoding="gb2312")
    df_pd = pd.DataFrame(df2)
    df_sorted = df_pd.sort_values(by='city', key=lambda x: x.str.encode('gbk'))
    print(df_sorted.head())
    return df_sorted


# 数据清洗
def data_clean():
    city = read_city()
    aqi = read_aqi()
    merge_df = pd.merge(city, aqi, on="city", how="inner")  # 通过两个数据表共同的字段“city”进行合并
    print(merge_df)
    # 1、查看是否存在缺失值
    print(merge_df.notnull().count())

    # 2.查看是否存在重复值，因为通过数据合并过，所以不存在重复数据
    # 3.处理没有代表性或者没有意义的数据，在表字段中，AQI作为主要体现数据，所以，AQI为0的数据应当去除
    data = merge_df.drop(merge_df[merge_df["AQI"] == 0].index)
    print(data)
    return data


# 数据分析
def analysis():
    data = data_clean()

    # 1.添加时间字段
    now = datetime.now()
    timestamp = now.strftime("%Y-%m-%d")
    print(timestamp)
    df = data.assign(timestamp=timestamp)
    print(df)

    # 2.创建空气质量等级列
    bin_edges = [0, 50, 100, 150, 200, 300, 1210]  # 根据AQI的划分等级设置标签
    bin_names = ['优级', '良好', '轻度污染', '中度污染', '重度污染', '重污染']
    df['空气质量'] = pd.cut(df['AQI'], bin_edges, labels=bin_names)
    print(df.head())

    # 3.列出每个城市所属的省份；
    city_province = {'即墨': '山东省', '阿坝州': '四川省', '安康': '陕西省', '阿克苏地区': '新疆维吾尔自治区',
                     '阿里地区': '西藏区', '阿拉善盟': '内蒙古自治区', '安庆': '安徽省', '安顺': '贵州省',
                     '鞍山': '辽宁省',
                     '克孜勒苏州': '新疆维吾尔自治区', '安阳': '河南省', '蚌埠': '安徽省', '白城': '吉林省',
                     '北海': '广西壮族自治区', '宝鸡': '陕西省', '毕节': '贵州省', '白山': '吉林省',
                     '百色': '广西壮族自治区',
                     '保山': '云南省', '包头': '内蒙古自治区', '本溪': '辽宁省', '巴彦淖尔': '内蒙古自治区',
                     '白银': '甘肃省', '巴中': '四川省', '滨州': '山东省', '亳州': '安徽省', '昌都': '西藏区',
                     '常德': '湖南省', '赤峰': '内蒙古自治区', '昌吉州': '新疆维吾尔自治区',
                     '五家渠': '新疆维吾尔自治区',
                     '楚雄州': '云南省', '朝阳': '辽宁省', '长治': '山西省', '潮州': '广东省', '郴州': '湖南省',
                     '池州': '安徽省', '崇左': '广西壮族自治区', '滁州': '安徽省', '丹东': '辽宁省', '德宏州': '云南省',
                     '大理州': '云南省', '大庆': '黑龙江', '大同': '山西省', '定西': '甘肃省', '大兴安岭地区': '黑龙江',
                     '德阳': '四川省', '东营': '山东省', '黔南州': '贵州省', '达州': '四川省', '德州': '山东省',
                     '鄂尔多斯': '内蒙古自治区', '恩施州': '湖北省', '鄂州': '湖北省', '防城港': '广西壮族自治区',
                     '抚顺': '辽宁省', '阜新': '辽宁省', '阜阳': '安徽省', '抚州': '江西省', '广安': '四川省',
                     '贵港': '广西壮族自治区', '桂林': '广西壮族自治区', '果洛州': '青海省', '甘南州': '甘肃省',
                     '广元': '四川省', '甘孜州': '四川省', '赣州': '江西省', '海北州': '青海省', '鹤壁': '河南省',
                     '淮北': '安徽省', '河池': '广西壮族自治区', '海东地区': '青海省', '鹤岗': '黑龙江',
                     '黄冈': '湖北省',
                     '黑河': '黑龙江', '红河州': '云南省', '怀化': '湖南省', '呼伦贝尔': '内蒙古自治区',
                     '葫芦岛': '辽宁省',
                     '哈密地区': '新疆维吾尔自治区', '淮南': '安徽省', '黄山': '安徽省', '黄石': '湖北省',
                     '和田地区': '新疆维吾尔自治区', '海西州': '青海省', '河源': '广东省', '衡阳': '湖南省',
                     '汉中': '陕西省', '菏泽': '山东省', '贺州': '广西壮族自治区', '吉安': '江西省', '金昌': '甘肃省',
                     '晋城': '山西省', '景德镇': '江西省', '西双版纳州': '云南省', '九江': '江西省', '吉林': '吉林省',
                     '荆门': '湖北省', '佳木斯': '黑龙江', '济宁': '山东省', '酒泉': '甘肃省', '湘西州': '湖南省',
                     '鸡西': '黑龙江', '揭阳': '广东省', '嘉峪关': '甘肃省', '焦作': '河南省', '锦州': '辽宁省',
                     '晋中': '山西省', '荆州': '湖北省', '开封': '河南省', '黔东南州': '贵州省',
                     '克拉玛依': '新疆维吾尔自治区', '喀什地区': '新疆维吾尔自治区', '六安': '安徽省',
                     '来宾': '广西壮族自治区', '聊城': '山东省', '临沧': '云南省', '娄底': '湖南省', '临汾': '山西省',
                     '漯河': '河南省', '丽江': '云南省', '吕梁': '山西省', '陇南': '甘肃省', '六盘水': '贵州省',
                     '乐山': '四川省', '凉山州': '四川省', '莱芜': '山东省', '辽阳': '辽宁省', '辽源': '吉林省',
                     '临沂': '山东省', '龙岩': '福建省', '洛阳': '河南省', '林芝': '西藏区', '柳州': '广西壮族自治区'
        , '泸州': '四川省', '马鞍山': '安徽省', '牡丹江': '黑龙江', '茂名': '广东省', '眉山': '四川省',
                     '绵阳': '四川省', '梅州': '广东省', '南充': '四川省', '宁德': '福建省', '内江': '四川省',
                     '怒江州': '云南省', '南平': '福建省', '那曲地区': '西藏区', '南阳': '河南省', '平顶山': '河南省',
                     '盘锦': '辽宁省', '平凉': '甘肃省', '莆田': '福建省', '萍乡': '江西省', '濮阳': '河南省', '攀枝花':
                         '四川省', '曲靖': '云南省', '齐齐哈尔': '黑龙江', '七台河': '黑龙江', '黔西南州': '贵州省',
                     '清远':
                         '广东省', '庆阳': '甘肃省', '钦州': '广西壮族自治区', '泉州': '福建省', '日喀则': '西藏区',
                     '日照':
                         '山东省', '韶关': '广东省', '绥化': '黑龙江', '石河子': '新疆维吾尔自治区', '商洛': '陕西省',
                     '三明':
                         '福建省', '三门峡': '河南省', '山南': '西藏区', '遂宁': '四川省', '四平': '吉林省',
                     '商丘': '河南省',
                     '上饶': '江西省', '汕头': '广东省', '汕尾': '广东省', '三亚': '海南省', '邵阳': '湖南省', '十堰':
                         '湖北省', '松原': '吉林省', '双鸭山': '黑龙江', '朔州': '山西省', '宿州': '安徽省',
                     '随州': '湖北省',
                     '泰安': '山东省', '塔城地区': '新疆维吾尔自治区', '铜川': '陕西省', '通化': '吉林省',
                     '铁岭': '辽宁省',
                     '通辽': '内蒙古自治区', '铜陵': '安徽省', '吐鲁番地区': '新疆维吾尔自治区', '铜仁地区': '贵州省',
                     '天水': '甘肃省', '潍坊': '山东省', '威海': '山东省', '乌海': '内蒙古自治区', '芜湖': '安徽省',
                     '乌兰察布': '内蒙古自治区', '渭南': '陕西省', '文山州': '云南省', '武威': '甘肃省', '梧州':
                         '广西壮族自治区', '兴安盟': '内蒙古自治区', '许昌': '河南省', '宣城': '安徽省',
                     '孝感': '湖北省',
                     '迪庆州': '云南省', '锡林郭勒盟': '内蒙古自治区', '咸宁': '湖北省', '湘潭': '湖南省', '新乡':
                         '河南省', '咸阳': '陕西省', '新余': '江西省', '信阳': '河南省', '忻州': '山西省',
                     '雅安': '四川省',
                     '延安': '陕西省', '延边州': '吉林省', '宜宾': '四川省', '宜昌': '湖北省', '宜春': '江西省', '运城':
                         '山西省', '伊春': '黑龙江', '云浮': '广东省', '阳江': '广东省', '营口': '辽宁省',
                     '榆林': '陕西省',
                     '玉林': '广西壮族自治区', '阳泉': '山西省', '玉树州': '青海省', '烟台': '山东省', '鹰潭': '江西省',
                     '玉溪': '云南省', '益阳': '湖南省', '岳阳': '湖南省', '永州': '湖南省', '淄博': '山东省', '自贡':
                         '四川省', '湛江': '广东省', '张家界': '湖南省', '周口': '河南省', '驻马店': '河南省',
                     '昭通': '云南省',
                     '张掖': '甘肃省', '资阳': '四川省', '遵义': '贵州省', '枣庄': '山东省', '漳州': '福建省', '株洲':
                         '湖南省', '深圳': '广东省', '福州': '福建省', '舟山': '浙江省', '青岛': '山东省',
                     '无锡': '江苏省',
                     '湖州': '浙江省', '成都': '四川省', '石家庄': '河北省', '苏州': '新疆维吾尔自治区',
                     '连云港': '江苏省',
                     '徐州': '江苏省', '廊坊': '河北省', '常州': '江苏省', '宿迁': '江苏省', '衡水': '河北省', '兰州':
                         '甘肃省', '邢台': '河北省', '沧州': '河北省', '哈尔滨': '黑龙江', '济南': '山东省',
                     '昆明': '云南省',
                     '扬州': '江苏省', '杭州': '浙江省', '海口': '海南省', '南京': '江苏省', '广州': '广东省', '长沙':
                         '湖南省', '厦门': '福建省', '秦皇岛': '河北省', '张家口': '河北省', '宁波': '浙江省', '南宁':
                         '广西壮族自治区', '盐城': '江苏省', '邯郸': '河北省', '贵阳': '贵州省', '衢州': '浙江省',
                     '承德':
                         '河北省', '南通': '江苏省', '沈阳': '辽宁省', '呼和浩特': '内蒙古自治区', '中山': '广东省',
                     '武汉':
                         '湖北省', '合肥': '安徽省', '长春': '吉林省', '嘉兴': '浙江省', '大连': '辽宁省',
                     '台州': '浙江省',
                     '拉萨': '西藏区', '肇庆': '广东省', '西安': '陕西省', '保定': '河北省', '江门': '广东省', '西宁':
                         '青海省', '乌鲁木齐': '新疆维吾尔自治区', '绍兴': '浙江省', '淮安': '江苏省', '温州': '浙江省',
                     '郑州':
                         '河南省', '惠州': '广东省', '泰州': '新疆维吾尔自治区', '珠海': '广东省', '南昌': '江西省',
                     '唐山':
                         '河北省', '金华': '浙江省', '佛山': '广东省', '东莞': '广东省', '丽水': '浙江省',
                     '太原': '山西省',
                     '镇江': '江苏省', '阿勒泰地区': '新疆维吾尔自治区', '北京': '北京', '博州': '新疆维吾尔自治区',
                     '常熟': '江苏省', '富阳': '浙江省', '固原': '宁夏回族自治区', '海门': '江苏省', '海南州': '青海省',
                     '黄南州': '青海省', ' 即墨': '山东省', '胶南': '山东省', '句容': '江苏省', '金坛': '江苏省',
                     '江阴':
                         '江苏省', '胶州': '山东省', '库尔勒': '新疆维吾尔自治区', '昆山': '江苏省', '临安': '浙江省',
                     '莱西': '山东省', '临夏州': '甘肃省', '溧阳': '江苏省', '莱州': '山东省', '平度': '山东省', '普洱':
                         '云南省', '蓬莱': '山东省', '荣成': '山东省', '乳山': '山东省', '寿光': '山东省', '石嘴山':
                         '宁夏回族自治区', '太仓': '江苏省', '文登': '山东省', '瓦房店': '辽宁省', '吴江': '江苏省',
                     '吴忠':
                         '宁夏回族自治区', '襄阳': '湖北省', '伊犁哈萨克州': '新疆维吾尔自治区', '义乌': '浙江省',
                     '宜兴':
                         '江苏省', '诸暨': '浙江省', '张家港': '江苏省', '章丘': '山东省', '中卫': '宁夏回族自治区',
                     '招远':
                         '山东省', '天津': '天津市', '重庆': '重庆市', '银川': '甘肃省', '上海': '上海市'}
    df['省份'] = df['city'].map(city_province)
    # 去除省份为NAN的数据
    df = df.dropna()
    print(df.head())

    # 4.创建省份空气质量排名列(以AQI平均值为基础）
    a = df.groupby('省份').mean()["AQI"].sort_values().index
    b = []
    for _ in range(1, a.shape[0] + 1):
        b.append(_)
    pro_rank_dic = dict(zip(a, b))
    print(pro_rank_dic)
    # 匹配省名，增加排名列
    df['所属省份空气质量排名'] = df['省份'].map(pro_rank_dic)
    print(df.head())

    # 5.创建城市空气质量排名列（以AQI为基础）。
    c = df.groupby('city').mean()["AQI"].sort_values().index
    d = []
    for _ in range(1, c.shape[0] + 1):
        d.append(_)
    city_rank_dic = dict(zip(c, d))
    print(city_rank_dic)
    # 匹配城市名，增加排名列
    df['城市空气质量全国排名'] = df['city'].map(city_rank_dic)
    print(df.head())
    print(df.info())  # 全部清洗完后，再查看一次数据整体情况

    # 6.查看数据的相关各项指标
    print(df.loc[:, ['AQI', 'PM2.5', 'PM10', 'CO', 'NO2', 'SO2', 'O3']].describe())
    print(df.shape)

    # 7.得到AQI数据的相关性
    plt.figure(figsize=(25, 5))
    sns.heatmap(df.corr(), vmax=1, square=False, annot=True, linewidth=1)
    plt.rcParams['font.family'] = ['sans-serif']
    plt.rcParams['font.sans-serif'] = ['SimHei']
    plt.rcParams['axes.unicode_minus'] = False
    plt.yticks(rotation=0)
    plt.show()

    # 8.全国哪些城市污染较严重，那些省份污染较严重？（AQI作为判断依据）
    name_list = list(df["city"].drop_duplicates())
    value_list = list(df["AQI"])
    level_aqi = list(df["空气质量"])

    # 对应的城市数据
    data = [z for z in zip(name_list, value_list)]
    # 市级单位的经纬度坐标
    print(df)
    # df.to_csv("./excel文件夹/实时数据分析.csv", index=False, encoding="gb2312")
    lat = list(df["lat"].drop_duplicates())
    lng = list(df["lng"].drop_duplicates())

    """
        将清洗过的数据保存，保存数据至当前路径或者前端路径
    """

    lng_lat_value = [list(z) for z in zip(lng, lat, value_list)]  # 经纬度和数值结合
    print(lng_lat_value)
    lat_ing_value = list()
    for val in range(len(name_list)):
        lat_ing_dic = {"name": level_aqi[val],
                       "data": [
                           {
                               'name': name_list[val],
                               'value': lng_lat_value[val]
                           }
                       ]
                       }
        lat_ing_value.append(lat_ing_dic)
    print(lat_ing_value)
    # with open('./data/mapAqi.json', 'w', encoding='utf-8') as f2:
    #     # ensure_ascii=False才能输入中文，否则是Unicode字符
    #     # indent=2 JSON数据的缩进，美观
    #     json.dump(lat_ing_value, f2, ensure_ascii=False, indent=2)

    """
        将数据整合
    """
    lng_lat = [list(z) for z in zip(lng, lat)]  # 经纬度结合
    print(lng_lat)
    lat_ing_city = {}  # 存放经纬度数据
    for name_list, lng_lat in zip(name_list, lng_lat):
        lat_ing_city[name_list] = lng_lat
    print(lat_ing_city)

    """
        全国地图数据展示
             空气质量划分
                指标：AQI (O3, CO, SO2, pm2.2, pm10, NO2)
        
                1、一级： 空气污染指数 ≤50优级 #99ffff
                2、二级： 空气污染指数 ≤100良好 #ffff99
                3、三级： 空气污染指数 ≤150轻度污染 #ffcc33
                4、四级： 空气污染指数 ≤200中度污染 #ff9933
                5、五级： 空气污染指数 ≤300重度污染 #ff6633
                6、六级：空气污染指数＞300严重污染 #ff3333
    """
    # 定义范围样式
    visual_range = [0, 500]
    visual_text_color = "#33ffff"
    visual_range_color = ["#99ffff", "#ffff99", "#ffcc33", "#ff9933", "#ff6633", "#ff3333"]
    geo = Geo(init_opts=opts.InitOpts(width="1200px", height="600px", theme=ThemeType.DARK))
    for name, coordinate in lat_ing_city.items():
        geo.add_coordinate(name, *coordinate)
    geo.add_schema(maptype="china")
    geo.add(
        "全国空气质量数据展示",
        data,
        type_=ChartType.EFFECT_SCATTER,
        symbol_size=10,
        color="red",
        label_opts=opts.LabelOpts(is_show=False),
        tooltip_opts=opts.TooltipOpts(formatter="{b} : {c}")
    )
    geo.set_series_opts(label_opts=opts.LabelOpts(is_show=False))
    geo.set_global_opts(
        visualmap_opts=opts.VisualMapOpts(
            min_=visual_range[0],
            max_=visual_range[1],
            range_text=["High", "Low"],
            textstyle_opts=opts.TextStyleOpts(color=visual_text_color),
            is_piecewise=True,
            pieces=[
                {"min": 301, "label": ">300", "color": visual_range_color[5]},
                {"min": 201, "max": 300, "label": "201-300", "color": visual_range_color[4]},
                {"min": 151, "max": 200, "label": "151-200", "color": visual_range_color[3]},
                {"min": 101, "max": 150, "label": "101-105", "color": visual_range_color[2]},
                {"min": 51, "max": 100, "label": "51-100", "color": visual_range_color[1]},
                {"min": 0, "max": 50, "label": "0-50", "color": visual_range_color[0]},
            ],
        ),
        title_opts=opts.TitleOpts(
            title="全国空气质量数据可视化",
            pos_top="70px",
            pos_left="50px",
            title_textstyle_opts=opts.TextStyleOpts(
                font_size=20,
                color="#fff"
            )
        ),
        legend_opts=opts.LegendOpts(
            is_show=True,
            pos_top="5%",
            pos_left="50%",
            textstyle_opts=opts.TextStyleOpts(
                font_size=14,
                color="#FFF"
            )
        )
    )
    geo.render("全国空气质量数据可视化.html")

    # 9.查看当前城市中空气质量最差的10个城市
    pd.DataFrame(df.groupby('city')['AQI'].mean().sort_values().tail(10)).plot.barh(figsize=(20, 10))
    plt.xlim(125, 500)
    plt.style.use('bmh')
    plt.title('全国空气质量最差城市')
    plt.xlabel('AQI')
    plt.ylabel('城市名')
    plt.legend('AQI')
    plt.grid(linestyle=':', color='w')
    plt.show()

    # 10.全国空气十佳城市
    pd.DataFrame(df.groupby('city')["AQI"].mean().sort_values(ascending=False).tail(10)).plot.barh(figsize=(20, 10))
    plt.style.use("bmh")
    plt.title('全国空气质量十佳城市')
    plt.xlabel('AQI')
    plt.ylabel('城市名')
    plt.xlim(0, 50)
    plt.legend('AQI')
    plt.grid(linestyle=':', color='w')
    plt.show()

    # 11.全国空气质量最差省份
    pd.DataFrame(df.groupby('省份')["AQI"].mean().sort_values().tail(10)).plot.barh(figsize=(20, 10))
    plt.style.use('dark_background')
    plt.title('全国空气质量最差省份')
    plt.xlabel('AQI')
    plt.ylabel('省份')
    plt.xlim(80, 150)
    plt.legend('AQI')
    plt.grid(linestyle=':', color='w')
    plt.show()

    """污染比较严重的省份的主要污染物是什么"""
    df_top10_polluted = []
    df_top10_polluted = pd.DataFrame(df_top10_polluted)
    for _ in range(0, 10):
        '''
            提取空气质量最严重的省份信息
        '''
        temp = df[df['省份'] == df.groupby('省份')["AQI"].mean().sort_values().tail(10).index[_]]
        df_top10_polluted = pd.concat([df_top10_polluted, temp])
        # 这里只关注轻度污染以上时的污染物情况
    df_over_polluted = df_top10_polluted[df_top10_polluted['AQI'] >= 100][
        ['AQI', 'PM2.5', 'PM10', 'SO2', 'NO2', 'CO', 'O3']]
    sns.regplot(x='PM2.5', y='AQI', data=df_over_polluted)
    plt.show()
    sns.regplot(x='PM10', y='AQI', data=df_over_polluted)
    plt.show()
    sns.regplot(x='SO2', y='AQI', data=df_over_polluted)
    plt.show()
    sns.regplot(x='NO2', y='AQI', data=df_over_polluted)
    plt.show()
    sns.regplot(x='CO', y='AQI', data=df_over_polluted)
    plt.show()
    sns.regplot(x='O3', y='AQI', data=df_over_polluted)
    plt.show()

    sns.heatmap(df_over_polluted.corr(), vmax=1, square=False, annot=True, linewidth=1)
    plt.figure(figsize=(15, 5))
    plt.yticks(rotation=0)
    plt.show()

    return lat_ing_value


# 保存至MongoDB数据库以及前端项目文件夹
def save_data():
    data = analysis()
    path = "D:/毕业设计/vue_project_study/koa_server/data"
    with open(path+'./mapAqi.json', 'w', encoding='utf-8') as f2:
        # ensure_ascii=False才能输入中文，否则是Unicode字符
        # indent=2 JSON数据的缩进，美观
        json.dump(data, f2, ensure_ascii=False, indent=2)

    # mongodb数据库
    try:
        client = pg.MongoClient("mongodb://127.0.0.1:27017/")
        # 链接数据库
        db = client["aqis"]
        # 查询字段
        coll = db["aqi_datas"]
        # 添加字段
        for i in data:
            degree = i["name"]  # 污染程度
            city_name = i["data"][0]["name"]  # 城市名称
            ing = i["data"][0]["value"][0]  # 经度
            lat = i["data"][0]["value"][1]  # 维度
            aqi = i["data"][0]["value"][2]  # aqi
            # print()
            coll.insert_one(
                {
                    "degree": degree,
                    "city_name": city_name,
                    "ing": ing,
                    "lat": lat,
                    "aqi": aqi
                }
            )
        print("添加成功")
    except EOFError as e:
        print(e)
        return


# 主函数
def main():
    read_city()
    analysis()
    save_data()


if __name__ == "__main__":
    main()

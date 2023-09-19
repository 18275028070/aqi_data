import numpy as np
import pandas as pd
import json
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from sklearn.preprocessing import KBinsDiscretizer
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.feature_selection import RFECV

sns.set(style="darkgrid")
plt.rcParams["font.family"] = "SimHei"
plt.rcParams["axes.unicode_minus"] = False

data = pd.read_csv("data/2015空气质量数据集.csv")
print(data.shape)
print(data.head())

"""
    缺失值处理
        对于缺失值，我们可以使用如下方式处理：
        
        删除缺失值：适合缺失值数量相对很少时。
        填充缺失值：
            数值变量
            均值填充：适合非偏态分布的数据。
            中值填充：适合偏态分布的数据。
            类别变量
            众数填充
            空值单独作为一个类别
"""

# 查看缺失值数量：
print(data.isnull().sum(axis=0))

# 查看含缺失值列数据的偏度和分布：
print(data.Precipitation.skew())
sns.histplot(data.Precipitation, stat="density", kde=True)
plt.title("分布密度图")
# plt.show()

# 对缺失值进行中位数填充：
data.Precipitation.fillna(data.Precipitation.median(), inplace=True)
data.isnull().sum()

# 查看数据集的统计信息：
print(data.describe().round(2))

# 查看数据集的偏度：
print(data.skew(numeric_only=True))

# 我们可视化这两列的分布情况：
fig, ax = plt.subplots(1, 2)
fig.set_size_inches(15, 5)
sns.histplot(data.GDP, stat="density", kde=True, ax=ax[0])
sns.histplot(data.PopulationDensity, stat="density", kde=True, ax=ax[1])
# plt.show()

# 我们可以通过箱线图查看除了经纬度以外所有数值列的异常值情况：
fig, ax = plt.subplots(2, 5)
# wspace左右距离，hspace上下距离
plt.subplots_adjust(wspace=0.05, hspace=0.5)
fig.set_size_inches(15, 3)
for i, c in enumerate(data.select_dtypes("number").columns):
    row, col = i // 5, i % 5
    sns.boxplot(data=data, x=c, ax=ax[row, col])


# plt.show()


# 根据正态分布的特性，在均值3倍标准差范围内的数据，包含约99.7%的数据。我们可以将3倍标准差范围以外的数据全部视为异常值。
# 例如查看GDP的异常值：
def query_3std_outlier(data, column, gt_zero=True):
    mean, std = data[column].mean(), data[column].std()
    lower, upper = mean - 3 * std, mean + 3 * std
    lower = 0 if gt_zero and lower < 0 else lower
    print(f"均值：{mean:.2f}，标准差：{std:.2f}，3倍标准差范围：({round(lower, 2)}, {upper:.2f})")
    return data.query(f"{column} < @lower | {column} > @upper")[column]


# 查看人口密度的异常值：
query_3std_outlier(data, "PopulationDensity")


def func(s):
    mean, std = s.mean(), s.std()
    lower, upper = mean - 3 * std, mean + 3 * std
    a, b = (s < lower).sum(), (s > upper).sum()
    return pd.Series((a, b, a + b), index=("极小异常值", "极大异常值", "总和"))


print(data.select_dtypes(include='number').agg(func).T)


# 箱线图判断异常值的标准是，四分位距IQR=Q3-Q1，上下边界：Q3+1.5IQR，Q1-1.5IQR。基于此编写方法
def query_box_outlier(data, column, gt_zero=True):
    q1, q3 = np.quantile(data[column], [0.25, 0.75])
    IQR = q3 - q1
    lower, upper = q1 - 1.5 * IQR, q3 + 1.5 * IQR
    lower = 0 if gt_zero and lower < 0 else lower
    print(
        f"Q1：{q1:.2f}，Q3：{q3:.2f}，IQR：{IQR:.2f}，正常数据范围：({round(lower, 2)}, {upper:.2f})")
    print("异常值：", data.query(
        f"{column} < @lower | {column} > @upper")[column].tolist())


# 例如查看GDP的箱线图异常值：
print(query_box_outlier(data, "GDP"))


# 下面按照箱线图的标准计算一下各列的异常值的数量：
def func(s):
    q1, q3 = np.quantile(s, [0.25, 0.75])
    IQR = q3 - q1
    lower, upper = q1 - 1.5 * IQR, q3 + 1.5 * IQR
    a, b = (s < lower).sum(), (s > upper).sum()
    return pd.Series((a, b, a + b), index=("极小异常值", "极大异常值", "总和"))


print(data.select_dtypes(include='number').agg(func).T)

"""
    异常值处理的方式
        异常值处理常见的处理方式有：删除异常数据、视为缺失值、对数转换、使用边界值替换、分箱离散化。
        本节不实际进行处理，简单演示下各种操作方法，后续再模型预测时，再测试各种方法处理异常值后的预测效果。
"""

# 对数转换
# 由于右偏分布在取对数后，往往呈现正态分布，所以我们可以对右偏分布进行取对数转换。
# 例如，GDP变量呈现严重的右偏分布，看下对数转换前后的数据分布情况：
fig, ax = plt.subplots(1, 2)
fig.set_size_inches(15, 5)
sns.histplot(data.GDP, stat="density", kde=True, ax=ax[0])
sns.histplot(np.log(data.GDP), stat="density", kde=True, ax=ax[1])

# 边界值替换
# 有基于正态分布3倍标准差和箱线图两种方式判断异常值，下面我们基于箱线图的标准进行边界值替换。
# 查看处理前的数据：
print(data.select_dtypes("number").agg(["max", "min"]))
# 对所有列用边界值替换处理后再查看：
data_c = data.copy()
for c, s in data.select_dtypes("number").iteritems():
    q1, q3 = np.quantile(s, [0.25, 0.75])
    IQR = q3 - q1
    lower, upper = q1 - 1.5 * IQR, q3 + 1.5 * IQR
    data_c[c] = s.clip(lower, upper)
data_c.select_dtypes("number").agg(["max", "min"]).round(2)
# 再次查看箱线图：
fig, ax = plt.subplots(2, 5)
# wspace左右距离，hspace上下距离
plt.subplots_adjust(wspace=0.05, hspace=0.5)
fig.set_size_inches(15, 3)
for i, c in enumerate(data.select_dtypes("number").columns):
    row, col = i // 5, i % 5
    sns.boxplot(data=data_c, x=c, ax=ax[row, col])

# 重复值处理
# 发现重复值。
print(data.duplicated().sum())
# 查看哪些记录出现了重复值。
print(data[data.duplicated(keep=False)])
# 重复值需要进行去重仅保留一条：
data.drop_duplicates(inplace=True)
print(data.duplicated().sum())  # 去重后检查

"""
    数据保存
"""
data_list = list()
City = list(data["City"])  # 城市名
Precipitation = list(data["Precipitation"])  # 降雨量
Temperature = list(data["Temperature"])  # 温度
Incineration = list(data["Incineration(10,000ton)"])  # 垃圾焚烧量
for i in range(len(City)):
    d = {
        "city": City[i],
        "Precipitation": Precipitation[i],
        "Temperature": Temperature[i],
        "Incineration": Incineration[i]
    }
    data_list.append(d)
# print(data_list)
# path_2 = 'D:/毕业设计/vue_project_study/koa_server/data/'
# with open(path_2 + "其他相关数据.json", 'w', encoding='utf-8') as f:
#     f.write(json.dumps(data_list, indent=4, ensure_ascii=False))
#     print("文件写入成功")

"""
    数据分析
        哪些城市的空气质量较好/较差？
        空气质量最好的5个城市
"""
t = data.nsmallest(5, "AQI")
print(t)
plt.xticks(rotation=10)
sns.barplot(x="City", y="AQI", data=t)
# plt.show()

# 空气质量最差的5个城市
t = data.nlargest(5, "AQI")
print(t)
plt.xticks(rotation=10)
sns.barplot(x="City", y="AQI", data=t)
# plt.show()

# 查看AQI的最大值：
data.AQI.max()
level = pd.cut(data.AQI, [0, 50, 100, 150, 200, 300],
               labels=['优', '良', '轻度', '中度', '重度'])
print(level.value_counts(sort=False))
sns.countplot(x=level)
# plt.show()

data["level"] = level
sns.scatterplot(x="Longitude", y="Latitude", hue="level",
                palette="RdYlGn_r", data=data)
plt.title("空气质量等级分布图", size=16)
# plt.show()

"""
    临海城市的空气质量是否优于内陆城市？
    数量统计
    首先看下临海城市与内陆城市的数量：
"""
print(data.Coastal.value_counts())
sns.countplot(x="Coastal", data=data)
# plt.show()

"""
    分布统计
    Coastal的值为是表示沿海城市，否表示内陆城市。
    箱线图可以清楚看到均值、Q1分位点、Q3分位点以及临界值：
"""
sns.boxplot(x="Coastal", y="AQI", data=data)
# plt.show()

# 超过临界值，在1.5倍IQR之外的是异常值。
# 看分布密度，可以使用直方图：
sns.histplot(data, x="AQI", hue="Coastal", stat="density", kde=True)
# plt.show()

# 小提琴图内部的箱线图替换为分簇散点图，可以更清晰观察数据分布情况：
sns.violinplot(x="Coastal", y="AQI", data=data, inner=None)
sns.swarmplot(x="Coastal", y="AQI", color="r", data=data)
# plt.show()

"""
    根据中心极限定理，样本的均值有95%的概率会在1.96倍标准差以内，95%置信度的置信区间就是该范围。
    基于此，我们可以假设样本符合正态分布计算均值和置信区间：
"""
for x, aqi in data.AQI.groupby(data.Coastal):
    x = "沿海" if x == "是" else "内陆"
    mean, std = aqi.mean(), aqi.std()
    se = std / np.sqrt(aqi.shape[0])
    min_ = mean - 1.96 * se
    max_ = mean + 1.96 * se
    print(f"{x}95%置信度的置信区间为({min_:.2f},{max_:.2f})，均值为{mean:.2f}")

# scipy提供了计算正态分布置信区间的方法：
for x, aqi in data.AQI.groupby(data.Coastal):
    x = "沿海" if x == "是" else "内陆"
    mean = aqi.mean()
    min_, max_ = stats.norm.interval(0.95, mean, stats.sem(aqi))
    print(f"{x}95%置信度的置信区间为({min_:.2f},{max_:.2f})，均值为{mean:.2f}")

# 不过实际上样本数量较少，相对正态分布而言样本更符合t分布，基于t分布计算置信区间：
for x, aqi in data.AQI.groupby(data.Coastal):
    x = "沿海" if x == "是" else "内陆"
    mean = aqi.mean()
    min_, max_ = stats.t.interval(0.95, df=len(
        aqi) - 1, loc=mean, scale=stats.sem(aqi))
    print(f"{x}95%置信度的置信区间为({min_:.2f},{max_:.2f})，均值为{mean:.2f}")

# 当然我们可以直接绘制柱形图展示均值和置信区间，无需自己计算：柱形图上方的竖线表示置信区间。
sns.barplot(x="Coastal", y="AQI", data=data)
# plt.show()


"""
    差异检验：两样本t检验
        下面我们进行两样本t检验，检验沿海与内陆城市的AQI均值差异是否显著。
"""
coastal = data.query("Coastal=='是'").AQI
inland = data.query("Coastal=='否'").AQI
# 进行两样本t检验前，需要先知道两样本的方差是否一致。所以首先进行方差齐性检验：
print(stats.levene(coastal, inland))

# 方差齐性检验的原假设为方差相等（齐性），显然p-value超过显著性水平0.05，说明两样本的方差是相等的。
# 下面进行两样本t检验：
# equal_var=True表示两样本方差一致
r = stats.ttest_ind(coastal, inland, equal_var=True)
print(r)

# 两样本t检验的原假设为均值相等，P值小于显著性水平，所以拒绝原假设，接受备择假设，即内陆AQI和沿海城市AQI的均值不相等。
# 由于统计量由左样本减右样本得到，统计量小于0说明 临海的均值小于内陆。
# 下面我们假设临海空气质量的均值小于内陆空气质量的均值，则这是一个右边假设检验，可以通过以下方法根据前面两样本t检验得到的统计量得到P值
p = stats.t.sf(r.statistic, df=len(coastal) + len(inland) - 2)
print(p)  # 说明有99.7%的信心可以认为沿海的空气质量整体好于内陆空气质量（均值小于内陆）。

"""
    多图矩阵
        首先查看空气质量、人口密度和绿化率之间的矩阵图：
"""
g = sns.PairGrid(data[["AQI", "PopulationDensity", "GreenCoverageRate"]])
g.map_upper(sns.scatterplot)
g.map_lower(sns.kdeplot)
g.map_diag(sns.histplot, kde=True)

# 也可以直接绘制散点图矩阵：#参数 kind="reg"给散点图绘制一条回归线
sns.pairplot(data[["AQI", "PopulationDensity", "GreenCoverageRate"]])
# plt.show()  # 从散点图矩阵中可以看到，三个变量两两之间并没有明显的线性关系，可以说几乎不相关。

# 计算空气质量与降雨量的相关系数：
x = data.AQI
y = data.Precipitation
# 计算AQI与Precipitation的协方差。
a = (x - x.mean()) * (y - y.mean())
cov = np.sum(a) / (len(a) - 1)
print("协方差：", cov)
# 计算AQI与Precipitation的相关系数。
corr = cov / np.sqrt(x.var() * y.var())
print("相关系数：", corr)
print(data.corr())

# 使用热力图呈现相关系数更佳：
"""
    从上述相关性热力图中，我们可以看到，AQI与人口密度和绿化覆盖率几乎不相关。
    AQI与纬度（0.55）和降雨量（-0.4）的相关性最高。说明：
        纬度越低，空气质量越好。
        降雨量越多，空气质量越好。
"""
plt.figure(figsize=(15, 10))
ax = sns.heatmap(data.corr(), cmap="RdYlGn", annot=True, fmt=".2f")
plt.xticks(rotation=10)
# plt.show()

# 传言说，全国所有城市的空气质量指数均值为71左右，请问，这个消息可靠吗？
# 下面作出原假设：全部城市的AQI均值为71，进行假设检验：
print("样本均值 ：", data.AQI.mean())  # 可以看到，P值大于显著性水平0.05，故我们没有充足的证据拒绝原假设，于是接受原假设全部城市的AQI均值为71。
print(stats.ttest_1samp(data.AQI, 71))  # 因此，我们可以认为全国所有城市的平均空气质量，95%的可能在(70.63, 80.04)范围内。
print(stats.t.interval(0.95, df=len(data) - 1, loc=data.AQI.mean(), scale=stats.sem(data.AQI)))
"""
    对空气质量进行预测
        问题：已知某市的降雨量、温度、经纬度等指标，如何预测其空气质量？
        
    数据转换
        为了进行模型计算，我们首先需要将一些文本型变量转换为离散数值变量。
"""
data.Coastal = data.Coastal.map({"是": 1, "否": 0})
print(data.Coastal.value_counts())

"""
    基础模型
        首先建立一个基本的线性回归模型，后续操作在此基础上改进：
"""

# 特征数据后续要进行异常数据替换，所以保留列信息
X = data.drop(["City", "AQI", "level"], axis=1)
y = data.AQI.values
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.3, random_state=0)

lr = LinearRegression()
lr.fit(X_train, y_train)
print(lr.score(X_train, y_train))
print(lr.score(X_test, y_test))

y_hat = lr.predict(X_test)
plt.figure(figsize=(15, 5))
plt.plot(y_test, "-r", label="真实值", marker="o")
plt.plot(y_hat, "-g", label="预测值", marker="D")
plt.legend(loc="upper left")
plt.title("线性回归预测结果", fontsize=20)
# plt.show()

# 临界值替换异常值
# 数据中存在异常值，可能影响模型的效果，我使用前面在异常值处理一节中使用的方法对异常值进行临界值替换。
# 首先我们使用训练集的临界值替换异常值：
for c in X_train.columns.drop("Coastal"):
    s = X_train[c]
    q1, q3 = np.quantile(s, [0.25, 0.75])
    IQR = q3 - q1
    lower, upper = q1 - 1.5 * IQR, q3 + 1.5 * IQR
    s.clip(lower, upper, inplace=True)
    X_test[c].clip(lower, upper, inplace=True)
lr.fit(X_train, y_train)
print(lr.score(X_train, y_train))
print(lr.score(X_test, y_test))

# 下面开始进行递归特征消除，并进行交叉验证：
# estimator： 要操作的模型。
# step： 每次删除的变量数。
# cv： 使用的交叉验证折数。
# n_jobs： 并发的数量。
# scoring: 评估的方式。
rfecv = RFECV(estimator=lr, step=1, cv=5, n_jobs=-1, scoring="r2")
rfecv.fit(X_train, y_train)

print("剩余的特征数量:", rfecv.n_features_)
# 返回经过特征选择后，使用缩减特征训练后的模型。
print(rfecv.estimator_)
# 返回每个特征的等级，数值越小，特征越重要。
print(rfecv.ranking_)
print("被选择的特征布尔数组：", rfecv.support_)
mean_test_score = rfecv.cv_results_["mean_test_score"]
print("交叉验证的评分:", mean_test_score)

# 绘图表示，在特征选择的过程中，使用交叉验证获取R平方的值：
plt.plot(range(1, len(mean_test_score) + 1), mean_test_score, marker="o")
plt.xlabel("特征数量")
plt.ylabel("交叉验证$R^2$值")
# plt.show()  # 从图中可以看到，9个特征时模型可以达到最佳的效果。那么我们可以删除该特征。

# 先看看被删除的特征列：
del_cols = X_train.columns[~rfecv.support_].values
print("剔除的变量：", del_cols)

# 然后看看删除该特征后，模型的评分：
X_train_eli = X_train.drop(columns=del_cols)
X_test_eli = X_test.drop(columns=del_cols)
print(rfecv.estimator_.score(X_train_eli.values, y_train))
print(rfecv.estimator_.score(X_test_eli.values, y_test))

"""
    分箱离散化
    由于有些变量对目标的影响并不是连续的，而是阶梯式的，所以我们可以考虑使用KBinsDiscretizer对有这种特征的数据作分箱离散化。
    
    KBinsDiscretizer是K个分箱的离散器，用于将数值（通常是连续变量）变量进行区间离散化操作。
    
    KBinsDiscretizer的参数如下：
    
        n_bins：分箱（区间）的个数。
        encode：离散化编码方式。分为：onehot，onehot-dense与ordinal。
        onehot：使用独热编码，返回稀疏矩阵。
        onehot-dense：使用独热编码，返回稠密矩阵。
        ordinal：使用序数编码（0,1,2……）。
        strategy：分箱的方式。分为：uniform，quantile，kmeans。
        uniform：每个区间的长度范围大致相同。
        quantile：每个区间包含的元素个数大致相同。
        kmeans：使用一维kmeans方式进行分箱。
    下面我对经度，纬度，温度 和 降雨量 进行分箱离散化，读者们可以自己凭感觉测试其他的参数。
"""

k = KBinsDiscretizer(n_bins=[4, 6, 5, 14],
                     encode="onehot-dense", strategy="uniform")
# 经纬度，温度，降雨量
discretize = ["Longitude", "Latitude", "Temperature", "Precipitation"]
# 将目标特征进行分箱李四化
X_train_dis = k.fit_transform(X_train_eli[discretize])
print(X_train_dis.shape[1])
# 将剔除离散化特征的其他特征与离散化后的特征进行重新组合
X_train_dis = np.c_[X_train_eli.drop(columns=discretize).values, X_train_dis]
# 对测试集进行同样的离散化操作。
X_test_dis = k.transform(X_test_eli[discretize])
X_test_dis = np.c_[X_test_eli.drop(discretize, axis=1).values, X_test_dis]
print(X_test_dis)

# 上面的代码将经度、维度、温度和降雨量分别拆分成4、6、5、14个区间，使用独热编码意味着每个区间都会成为单独的一列，所以总共有29列。
# 然后我们对转换后的数据进行训练：
lr.fit(X_train_dis, y_train)
print(lr.score(X_train_dis, y_train))
print(lr.score(X_test_dis, y_test))

"""
    残差图分析
        残差就是模型的预测值与真实值之间的差异，可以绘制残差图对模型进行评估，横坐标为预测值，纵坐标为真实值。
        
        对于一个模型，误差应该的随机性的，而不是有规律的。残差也随机分布于中心线附近，如果残差图中残差是有规律的，则说明模型遗漏了某些能够影响残差的解释信息。
        
        异方差性，是指残差具有明显的方差不一致性。
绘制残差图：
"""
fig, ax = plt.subplots(1, 2)
fig.set_size_inches(15, 5)
data = [X_train, X_train_dis]
title = ["原始数据", "处理后数据"]
for d, a, t in zip(data, ax, title):
    model = LinearRegression()
    model.fit(d, y_train)
    y_hat_train = model.predict(d)
    residual = y_hat_train - y_train
    a.set_xlabel("预测值")
    a.set_ylabel(" 残差")
    a.axhline(y=0, color="red")
    a.set_title(t)
    sns.scatterplot(x=y_hat_train, y=residual, ax=a)

model = LinearRegression()
y_train_log = np.log(y_train)
y_test_log = np.log(y_test)
model.fit(X_train, y_train_log)

y_hat_train = model.predict(X_train)
residual = y_hat_train - y_train_log
plt.xlabel("预测值")
plt.ylabel(" 残差")
plt.axhline(y=0, color="red")
sns.scatterplot(x=y_hat_train, y=residual)
# plt.show()

# 检查离群点：对于多元线性回归，其回归线已经成为超平面，无法通过可视化来观测。
# 但我们可以通过残差图，通过预测值与实际值之间的关系，来检测离群点。我们认为偏离2倍标准差的点为离群点：
y_hat_train = lr.predict(X_train_dis)
residual = y_hat_train - y_train

r = (residual - residual.mean()) / residual.std()

plt.xlabel("预测值")
plt.ylabel(" 残差")
plt.axhline(y=0, color="red")
sns.scatterplot(x=y_hat_train[np.abs(r) <= 2],
                y=residual[np.abs(r) <= 2], color="b", label="正常值")
sns.scatterplot(x=y_hat_train[np.abs(r) > 2], y=residual[np.abs(r) > 2], color="orange", label="异常值")
# plt.show()

# 剔除异常值后，训练模型并查看效果：
X_train_dis_filter = X_train_dis[np.abs(r) <= 2]
y_train_filter = y_train[np.abs(r) <= 2]
lr.fit(X_train_dis_filter, y_train_filter)
print(lr.score(X_train_dis_filter, y_train_filter))
print(lr.score(X_test_dis, y_test))

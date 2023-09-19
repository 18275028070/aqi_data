import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
from datetime import datetime, timedelta
from sklearn import model_selection
import statsmodels.api as sm

# # 读入数据
df = pd.read_csv('./data/成都AQI历史数据.csv')
print(df.loc[:, "time"])

# 设置绘图风格
plt.style.use('ggplot')
# 处理中文乱码
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei']
# 坐标轴负号的处理
plt.rcParams['axes.unicode_minus'] = False

# 绘制散点图，用seaborn，默认拟合为一元
sns.lmplot(x='pm2_5', y='aqi', data=df, ci=None)
# 设置横纵坐标的刻度范围
plt.xlim()  # x轴的刻度范围被设为a到b
plt.ylim()  # y轴的刻度范围被设为a'到b'
plt.show()

"""
    一元拟合函数的斜率b： 1.0029373676730937
    一元拟合函数的截距a： 36.804673530070005

    Intercept    36.804674
    pm2_5         1.002937
    dtype: float64

    模型的偏回归系数分别为：
     Intercept    -3.734110
     pm2_5         0.987764
     pm10          0.032608
     so2          -0.215898
     co           11.438076
     no2           0.021664
     o3            0.320077
"""

# 计算回归系数
# 样本量
n = df.shape[0]
# 计算自变量、因变量、自变量平方、自变量与因变量乘积的和
sum_x = df.pm2_5.sum()  # 自变量x的和
sum_y = df.aqi.sum()  # 因变量y的和
sum_x2 = df.pm2_5.pow(2).sum()  # 自变量平方的和
xy = df.pm2_5 * df.aqi  # 自变量与因变量乘积
sum_xy = xy.sum()  # 自变量与因变量乘积的和
# 计算回归系数a,b
b = (sum_xy - (sum_x * sum_y) / n) / (sum_x2 - sum_x ** 2 / n)
a = df.aqi.mean() - b * df.pm2_5.mean()
print('一元拟合函数的斜率b：', b)
print('一元拟合函数的截距a：', a)

# 利用收入数据集，构建回归模型
fit = sm.formula.ols('aqi ~ pm2_5', data=df).fit()
# 返回模型的参数值
print(fit.params)

"""
    aqi,pm2_5,pm10,so2,co,no2,o3
"""

# 将数据集拆分为训练集和测试集
train, test = model_selection.train_test_split(df, test_size=0.2, random_state=1234)
# 根据train数据集建模
model = sm.formula.ols('aqi ~ pm2_5 + pm10 + so2 + co + no2 + o3 ', data=train).fit()
print('模型的偏回归系数分别为：\n', model.params)
# 删除test数据集中的Profit变量，用剩下的自变量进行预测
test_X = test.drop(labels='aqi', axis=1)
pred = model.predict(exog=test_X)
print('对比预测值和实际值的差异：\n', pd.DataFrame({'Prediction': pred, 'Real': test.aqi}))

"""
    Profit（预测值） =   -3.734110 + 0.99pm2_5 +0.033pm10 - 0.216so2 + 11.43co + 0.32o3 - 0.022no2
"""


np_data = np.array(df)
print(np_data)
dates = np.array([datetime.strptime(d, "%Y/%m/%d") for d in np_data[:, 0]])
print(dates[-1])

# 获取历史数据的特征和标签
X = np_data[:, 1:-1].astype(float)
print(X)
y = X[:, 0]  # 预测第一列，即AQI
# 创建线性回归模型
model = LinearRegression()

# 拟合模型
model.fit(X, y)
# 预测未来5天的空气质量指标
n_days = 1
last_date = dates[-1]
future_dates = np.array([last_date + timedelta(days=i+1) for i in range(n_days)])
future_X = np.array([X[-1] for i in range(n_days)])
print(future_X)
future_y = model.predict(future_X)

# 将未来日期、特征和预测结果合并成一个数组
future_data = np.concatenate([
    np.array([d.strftime("%Y/%m/%d") for d in future_dates]).reshape(-1, 1),
    future_X,
    future_y.reshape(-1, 1)
], axis=1)
#
print("预测未来{}天的空气质量指标为：\n{}".format(n_days, future_data))

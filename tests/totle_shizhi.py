import akshare as ak
import datetime
import io
import warnings
import pandas as pd
import requests

def stock_szse_summary(date: str = "20240830") -> pd.DataFrame:
    """
    深证证券交易所-总貌-证券类别统计 (已修复数值格式兼容Bug)
    https://www.szse.cn/market/overview/index.html
    :param date: 最近结束交易日，格式如 "20240830"
    :type date: str
    :return: 证券类别统计
    :rtype: pandas.DataFrame
    """
    url = "http://www.szse.cn/api/report/ShowReport"
    params = {
        "SHOWTYPE": "xlsx",
        "CATALOGID": "1803_sczm",
        "TABKEY": "tab1",
        "txtQueryDate": "-".join([date[:4], date[4:6], date[6:]]),
        "random": "0.39339437497296137",
    }
    
    # 发送请求获取 Excel 字节流
    r = requests.get(url, params=params)
    
    # 读取 Excel，忽略 openpyxl 的样式警告
    with warnings.catch_warnings(record=True):
        warnings.simplefilter("always")
        temp_df = pd.read_excel(io.BytesIO(r.content), engine="openpyxl")
    
    # 修复点 1：防止“证券类别”由于缺失值转成了 float（例如 NaN），先强转 str 再去空格
    temp_df["证券类别"] = temp_df["证券类别"].astype(str).str.strip()
    
    # 修复点 2：增加 isinstance 判断。如果是文本则去掉千分位逗号；如果是纯数字或 NaN 则直接跳过
    temp_df.iloc[:, 2:] = temp_df.iloc[:, 2:].map(lambda x: x.replace(",", "") if isinstance(x, str) else x)
    
    # 重新映射标准列名
    temp_df.columns = ["证券类别", "数量", "成交金额", "总市值", "流通市值"]
    
    # 强制将各数据列转换为数值类型，遇到无法转换的脏数据（或 nan 字符串）会自动处理为 NaN
    temp_df["数量"] = pd.to_numeric(temp_df["数量"], errors="coerce")
    temp_df["成交金额"] = pd.to_numeric(temp_df["成交金额"], errors="coerce")
    temp_df["总市值"] = pd.to_numeric(temp_df["总市值"], errors="coerce")
    temp_df["流通市值"] = pd.to_numeric(temp_df["流通市值"], errors="coerce")
    
    return temp_df


def get_a_market_cap_summary():
    """
    通过汇总交易所官方的市场总貌获取总市值
    :return: 总市值（单位：万亿元）
    """
    now = datetime.datetime.now()
    yesterday = now - datetime.timedelta(days=1)
    yesterday_str = yesterday.strftime("%Y%m%d")
    total_cap = 0.0
    
    try:
        # 1. 上海证券交易所股票数据总貌
        sse_df = ak.stock_sse_summary()
        # 找到“总市值”行（注意：sse_df 的单位通常是“亿元”）
        # 实际使用时建议 print(sse_df) 确认最新的 DataFrame 结构
        sse_cap = float(sse_df[sse_df['项目'] == '总市值']['股票'].values[0])
        total_cap += sse_cap
    except Exception as e:
        print(f"获取上交所市值失败: {e}")

    try:
        # 2. 深圳证券交易所市场总貌 (需要传日期)
        szse_df = stock_szse_summary(date=yesterday_str)
        # 筛选证券类别为“股票”或者“主板A股+创业板”的总市值
        # 深交所返回的单位通常是“元”，需要注意单位转换
        szse_cap_yuan = float(szse_df[szse_df['证券类别'] == '股票']['总市值'].values[0])
        total_cap += (szse_cap_yuan / 1e8)
    except Exception as e:
        print(f"获取深交所市值失败: {e}")
        
    # 将 亿元 转换为 万亿元
    return round(total_cap / 10000, 2)


if __name__ == "__main__":
    market_cap = get_a_market_cap_summary()
    print(f"当前 A 股实时总市值: {market_cap} 万亿 CNY")
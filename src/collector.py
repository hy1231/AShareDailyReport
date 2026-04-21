import efinance as ef
import pandas as pd
from datetime import datetime
import requests

class DataCollector:
    def __init__(self):
        self.today = datetime.now().strftime('%Y%m%d')
        # 强制创建一个不带任何代理信息的 Session
        self.session = requests.Session()
        self.session.trust_env = False  # 关键：无视系统环境变量和注册表
        self.session.proxies = {"http": None, "https": None} # 强制直连

    def get_market_sentiment(self):
        """获取市场涨跌分布和核心指数"""
        # 获取沪深京 A 股实时行情
        df = ef.stock.get_realtime_quotes('沪深京A股')
        
        # 强制转换为数字，'coerce' 会把无法转换的符号（如 '-') 变成 NaN
        df['涨跌幅'] = pd.to_numeric(df['涨跌幅'], errors='coerce')
        
        # 处理空值，防止计算出错
        df['涨跌幅'] = df['涨跌幅'].fillna(0)

        # 计算涨跌家数
        up_count = len(df[df['涨跌幅'] > 0])
        down_count = len(df[df['涨跌幅'] < 0])
        stay_count = len(df[df['涨跌幅'] == 0])
        
        # 获取成交额 (亿元)
        total_volume = df['成交额'].sum() / 1e8
        
        return {
            "up": up_count,
            "down": down_count,
            "stay": stay_count,
            "volume": round(total_volume, 2),
            "date": self.today
        }

    def get_top_industries(self, top_n=5):
        """获取领涨板块"""
        df_ind = ef.stock.get_realtime_quotes('板块')
        top_df = df_ind.sort_values('涨跌幅', ascending=False).head(top_n)
        return top_df[['板块名称', '涨跌幅', '总成交额']].to_dict(orient='records')
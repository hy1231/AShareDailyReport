import os
import pandas as pd
import akshare as ak
from datetime import datetime

class DataCollector:
    def __init__(self):
        self.today = datetime.now().strftime("%Y-%m-%d")
        self.cache_dir = "cache"
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)

    def get_market_sentiment(self):
        """
        获取全市场 A 股快照：改用通用接口，避开东财 IP 封锁
        """
        raw_cache_path = os.path.join(self.cache_dir, f"raw_market_{self.today}.csv")

        if os.path.exists(raw_cache_path):
            print(f"📦 [Cache] 命中个股快照缓存，正在加载...")
            df = pd.read_csv(raw_cache_path, dtype={'代码': str})
        else:
            print("🚀 [AkShare] 正在抓取全市场 A 股实时行情...")
            try:
                # 经验证，stock_zh_a_spot 是目前最稳的通用接口
                df = ak.stock_zh_a_spot()
                df.to_csv(raw_cache_path, index=False, encoding='utf-8-sig')
                print(f"💾 [Storage] 市场原始数据已备份: {raw_cache_path}")
            except Exception as e:
                print(f"❌ 市场数据采集失败: {e}")
                return None

        return self._process_market_data(df)

    def _process_market_data(self, df):
        """
        处理个股统计逻辑
        """
        try:
            # 1. 强制类型转换
            df['涨跌幅'] = pd.to_numeric(df['涨跌幅'], errors='coerce').fillna(0)
            df['成交额'] = pd.to_numeric(df['成交额'], errors='coerce').fillna(0)

            # 2. 计算市场分布
            up_count = len(df[df['涨跌幅'] > 0])
            down_count = len(df[df['涨跌幅'] < 0])
            stay_count = len(df[df['涨跌幅'] == 0])
            
            # 成交额换算：元 -> 亿
            total_vol = round(df['成交额'].sum() / 100000000, 2)

            print(f"📊 [Process] 市场扫描完成: {up_count}涨 / {down_count}跌 / 总成交{total_vol}亿")

            return {
                "date": self.today,
                "up": up_count,
                "down": down_count,
                "stay": stay_count,
                "volume": f"{total_vol}亿",
                "raw_df": df  # 供后续可视化使用
            }
        except Exception as e:
            print(f"❌ 市场数据清洗失败: {e}")
            return None

    def get_top_industries(self):
        """
        获取行业板块行情：改用新浪源，对齐“板块”和“总成交额”字段
        """
        raw_ind_cache = os.path.join(self.cache_dir, f"raw_industries_{self.today}.csv")

        if os.path.exists(raw_ind_cache):
            print(f"📦 [Cache] 命中行业快照缓存...")
            df = pd.read_csv(raw_ind_cache)
        else:
            print("🌐 [AkShare] 正在抓取新浪行业板块行情...")
            try:
                # 这个接口返回 49 个一级行业，反爬最松
                df = ak.stock_sector_spot()
                df.to_csv(raw_ind_cache, index=False, encoding='utf-8-sig')
                print(f"💾 [Storage] 行业板块行情原始数据已备份: {raw_ind_cache}")
            except Exception as e:
                print(f"❌ 行业抓取失败: {e}")
                return []

        return self._process_industry_data(df)

    def _process_industry_data(self, df):
        """
        处理行业板块数据：现在返回全量数据，以展示市场全貌
        """
        try:
            # 1. 字段映射
            column_map = {'板块': '行业名称', '总成交额': '成交额_元', '股票名称': '领涨股票'}
            df.rename(columns={k: v for k, v in column_map.items() if k in df.columns}, inplace=True)

            # 2. 数值转换
            df['涨跌幅'] = pd.to_numeric(df['涨跌幅'], errors='coerce').fillna(0)
            
            # 3. 成交额换算：元 -> 亿
            if '成交额_元' in df.columns:
                df['成交额_元'] = pd.to_numeric(df['成交额_元'], errors='coerce').fillna(0)
                df['成交额'] = round(df['成交额_元'] / 100000000, 2)
            else:
                df['成交额'] = 0

            # --- 关键改动：删除 .nlargest(15) ---
            # 直接返回全部 49 个行业的数据
            # 这样热力图会显示所有板块，读者能一眼看出哪些涨、哪些跌
            return df.to_dict('records')
            
        except Exception as e:
            print(f"❌ 行业清洗异常: {e}")
            return []
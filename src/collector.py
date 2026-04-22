import os
import json
from datetime import datetime
from curl_cffi import requests
import pandas as pd

class DataCollector:
    def __init__(self):
        self.today = datetime.now().strftime("%Y-%m-%d")
        self.cache_dir = "cache"
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)

    def _get_raw_cache_path(self):
        # 专门存储原始 JSON 响应
        return os.path.join(self.cache_dir, f"raw_sentiment_{self.today}.json")

    def get_market_sentiment(self):
        """
        主入口：负责获取数据并调用处理逻辑
        """
        raw_cache_path = self._get_raw_cache_path()
        raw_data = None

        # 1. 优先从本地读取原始源数据
        if os.path.exists(raw_cache_path):
            print(f"📦 [Cache] 发现本地原始源数据，跳过网络请求...")
            with open(raw_cache_path, 'r', encoding='utf-8') as f:
                raw_data = json.load(f)
        else:
            # 2. 本地没有，则发起网络请求
            print("🌐 [Network] 正在采集原始数据 (JA3 模拟模式)...")
            url = "http://push2.eastmoney.com/api/qt/clist/get?pn=1&pz=5000&po=1&np=1&fltt=2&invt=2&fid=f3&fs=m:0+t:6,m:0+t:80,m:1+t:2,m:1+t:23,m:0+t:81+s:2048&fields=f12,f14,f3,f6"
            
            try:
                response = requests.get(url, impersonate="chrome120", timeout=15)
                if response.status_code == 200:
                    raw_data = response.json()
                    # 立即保存原始数据，防止后续处理出错导致白抓
                    with open(raw_cache_path, 'w', encoding='utf-8') as f:
                        json.dump(raw_data, f, ensure_ascii=False, indent=4)
                    print(f"💾 [Storage] 原始源数据已备份至: {raw_cache_path}")
                else:
                    print(f"❌ 网络请求失败: {response.status_code}")
                    return None
            except Exception as e:
                print(f"❌ 采集过程发生异常: {e}")
                return None

        # 3. 调用处理逻辑（现在你可以随便改这个方法了）
        return self._process_raw_data(raw_data)

    def _process_raw_data(self, raw_data):
        """
        处理逻辑：你可以反复修改这里的清洗规则，不需要重新联网
        """
        try:
            stocks = raw_data['data']['diff']
            df = pd.DataFrame(stocks)
            
            # 重命名列名，匹配你的业务需求
            # f3: 涨跌幅, f6: 成交额, f12: 代码, f14: 名称
            column_map = {'f3': '涨跌幅', 'f6': '成交额', 'f12': '代码', 'f14': '名称'}
            df.rename(columns=column_map, inplace=True)

            # --- 核心处理过程（你想要调整的地方） ---
            
            # 强制转换为数字
            df['涨跌幅'] = pd.to_numeric(df['涨跌幅'], errors='coerce')
            df['涨跌幅'] = df['涨跌幅'].fillna(0)
            
            # 成交额转换（东财原始数据通常是分或者元，这里根据实际情况处理）
            df['成交额'] = pd.to_numeric(df['成交额'], errors='coerce').fillna(0)

            # 计算各项指标
            up_count = len(df[df['涨跌幅'] > 0])
            down_count = len(df[df['涨跌幅'] < 0])
            stay_count = len(df[df['涨跌幅'] == 0])
            total_vol = round(df['成交额'].sum() / 100000000, 2) # 亿

            print(f"📊 [Process] 数据清洗完成: {up_count}涨 / {down_count}跌")

            return {
                "date": self.today,
                "up": up_count,
                "down": down_count,
                "stay": stay_count,
                "volume": f"{total_vol}亿",
                "raw_df": df  # 如果 visualizer 需要，也可以把这个传出去
            }
        except Exception as e:
            print(f"❌ 数据处理失败: {e}")
            return None

    def get_top_industries(self):
        """
        获取行业板块排行（同样支持原始数据缓存）
        """
        raw_industry_cache = os.path.join(self.cache_dir, f"raw_industries_{self.today}.json")

        # 1. 检查缓存
        if os.path.exists(raw_industry_cache):
            print(f"📦 [Cache] 发现行业原始数据，直接加载...")
            with open(raw_industry_cache, 'r', encoding='utf-8') as f:
                raw_data = json.load(f)
        else:
            # 2. 抓取东财行业板块接口
            # fs=m:90+t:2 代表行业板块
            print("🌐 [Network] 正在采集行业板块数据...")
            url = "http://push2.eastmoney.com/api/qt/clist/get?pn=1&pz=100&po=1&np=1&fltt=2&invt=2&fid=f3&fs=m:90+t:2&fields=f12,f14,f3,f6"
            
            try:
                response = requests.get(url, impersonate="chrome120", timeout=15)
                if response.status_code == 200:
                    raw_data = response.json()
                    with open(raw_industry_cache, 'w', encoding='utf-8') as f:
                        json.dump(raw_data, f, ensure_ascii=False, indent=4)
                else:
                    return []
            except Exception as e:
                print(f"❌ 行业数据采集异常: {e}")
                return []

        # 3. 处理数据
        return self._process_industry_data(raw_data)

    def _process_industry_data(self, raw_data):
        """
        将行业原始 JSON 转换为可视化所需的格式
        """
        try:
            items = raw_data['data']['diff']
            df = pd.DataFrame(items)
            df.rename(columns={'f14': '行业名称', 'f3': '涨跌幅', 'f6': '总成交额'}, inplace=True)
            
            # 清洗
            df['涨跌幅'] = pd.to_numeric(df['涨跌幅'], errors='coerce').fillna(0)
            
            # 只取前 15 个热门行业或者涨幅居前的，防止图表太乱
            top_df = df.nlargest(15, '涨跌幅')
            
            return top_df.to_dict('records')
        except Exception as e:
            print(f"❌ 行业数据处理失败: {e}")
            return []
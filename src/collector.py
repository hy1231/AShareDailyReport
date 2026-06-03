import os
import pandas as pd
import akshare as ak
from datetime import datetime, timedelta
import yfinance as yf
import requests
class DataCollector:
    def __init__(self):
        self.today = datetime.now().strftime("%Y-%m-%d")
        self.cache_dir = os.path.join("data/cache", self.today)
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)

    def get_market_sentiment(self):
        """
        获取全市场 A 股快照：改用通用接口，避开东财 IP 封锁
        """
        raw_cache_path = os.path.join(self.cache_dir, "raw_market.csv")

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
        raw_ind_cache = os.path.join(self.cache_dir, "raw_industries.csv")

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

    def get_macro_data(self):
        """
        使用最稳定的数据源组合。
        汇率使用 AkShare 东财(EM)接口，原油使用 yfinance（更稳定）。
        支持缓存机制，避免重复调用接口。
        """
        try:
            # 检查缓存文件是否存在
            fx_cache_path = os.path.join(self.cache_dir, "fx_data.csv")
            oil_cache_path = os.path.join(self.cache_dir, "oil_data.csv")
            
            if os.path.exists(fx_cache_path) and os.path.exists(oil_cache_path):
                print(f"📋 使用缓存数据: {fx_cache_path}")
                fx_df = pd.read_csv(fx_cache_path, index_col=0, parse_dates=True)
                oil_df = pd.read_csv(oil_cache_path, index_col=0, parse_dates=True)
                
                return {
                    "oil": oil_df.tail(30),
                    "fx": fx_df.tail(30),
                    "current_fx": round(fx_df['Close'].iloc[-1], 4),
                    "current_oil": round(oil_df['Close'].iloc[-1], 2)
                }
            
            # 1. 抓取离岸人民币 - 使用新浪财经接口
            print("🔍 [Sina] 正在拉取汇率数据 (USD/CNH)...")
            
            import urllib3
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            
            url = "https://vip.stock.finance.sina.com.cn/forex/api/jsonp.php/var_/NewForexService.getDayKLine?symbol=fx_susdcnh"
            
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Referer": "https://finance.sina.com.cn/"
            }
            
            try:
                response = requests.get(url, headers=headers, timeout=10, verify=False)
                response.raise_for_status()
                
                # 用正则提取 var_(" ... ") 括号里面的数据
                import re
                match = re.search(r'var_\("(.*?)"\)', response.text, re.DOTALL)
                
                if match:
                    raw_string = match.group(1)
                    # 先用竖线 "|" 切分每一天
                    daily_records = [day for day in raw_string.split('|') if day]
                    # 用逗号切分，只取前5个元素
                    parsed_data = [record.split(',')[:5] for record in daily_records]
                    
                    # 塞入 DataFrame
                    fx_df = pd.DataFrame(parsed_data, columns=['日期', '开盘', '最低', '最高', '收盘'])
                    # 调整列顺序
                    fx_df = fx_df[['日期', '开盘', '收盘', '最高', '最低']]
                    
                    # 转换为数字类型
                    for col in ['开盘', '收盘', '最高', '最低']:
                        fx_df[col] = pd.to_numeric(fx_df[col])
                    
                    # 转换日期并重命名列
                    fx_df['Date'] = pd.to_datetime(fx_df['日期'])
                    fx_df = fx_df.rename(columns={'收盘': 'Close'})
                    fx_df.set_index('Date', inplace=True)
                    fx_df = fx_df.drop(columns=['日期'], errors='ignore')
                    
                    # 确保排序正确
                    fx_df = fx_df.sort_index()
                    
                    print(f"📊 获取到 {len(fx_df)} 条汇率数据")
                else:
                    print("❌ 新浪接口返回格式异常，未提取到有效数据")
                    return None
                    
            except Exception as e:
                print(f"❌ 新浪接口请求失败: {e}")
                return None

            # 2. 抓取布伦特原油 - 使用 yfinance（更稳定）
            print("🔍 [YFinance] 正在拉取布伦特原油数据...")
            oil_df = yf.Ticker("BZ=F").history(period="max")
            
            # 确保日期索引是 datetime 类型
            if not isinstance(oil_df.index, pd.DatetimeIndex):
                oil_df.index = pd.to_datetime(oil_df.index)

            # 3. 缓存到本地文件
            fx_cache_path = os.path.join(self.cache_dir, "fx_data.csv")
            oil_cache_path = os.path.join(self.cache_dir, "oil_data.csv")
            fx_df.to_csv(fx_cache_path, encoding="utf-8-sig")
            oil_df.to_csv(oil_cache_path, encoding="utf-8-sig")
            print(f"💾 宏观数据已缓存: {fx_cache_path}, {oil_cache_path}")

            return {
                "oil": oil_df.tail(30),
                "fx": fx_df.tail(30),
                "current_fx": round(fx_df['Close'].iloc[-1], 4),
                "current_oil": round(oil_df['Close'].iloc[-1], 2)
            }
        except Exception as e:
            print(f"❌ 宏观数据采集报错: {e}")
            return None

    @staticmethod
    def calc_fx_stats(fx_df):
        """计算汇率关键统计"""
        close = fx_df['Close']
        current = close.iloc[-1]
        prev = close.iloc[-2] if len(close) > 1 else current
        
        # 当日趋势：相对于昨日收盘价
        daily_trend = "走强" if current > prev else ("走弱" if current < prev else "持平")
        
        # 长期趋势：近30日趋势
        long_term_trend = "升值" if current < close.iloc[-30] else "贬值"
        
        return {
            "当前汇率": round(current, 4),
            "日变化": round(current - prev, 4),
            "近30日均值": round(close.mean(), 4),
            "近30日最高": round(close.max(), 4),
            "近30日最低": round(close.min(), 4),
            "当日趋势": daily_trend,
            "长期趋势": long_term_trend
        }

    @staticmethod
    def calc_oil_stats(oil_df):
        """计算原油关键统计"""
        close = oil_df['Close']
        current = close.iloc[-1]
        prev = close.iloc[-2] if len(close) > 1 else current
        return {
            "当前油价": round(current, 2),
            "日变化": round(current - prev, 2),
            "近30日均值": round(close.mean(), 2),
            "近30日最高": round(close.max(), 2),
            "近30日最低": round(close.min(), 2),
            "趋势": "上涨" if current > close.iloc[-30] else "下跌"
        }
    
    @staticmethod
    def _stock_szse_summary(date: str):
        """
        深证证券交易所-总貌-证券类别统计
        https://www.szse.cn/market/overview/index.html
        """
        import warnings
        import io
        
        url = "http://www.szse.cn/api/report/ShowReport"
        params = {
            "SHOWTYPE": "xlsx",
            "CATALOGID": "1803_sczm",
            "TABKEY": "tab1",
            "txtQueryDate": "-".join([date[:4], date[4:6], date[6:]]),
            "random": "0.39339437497296137",
        }
        
        r = requests.get(url, params=params)
        
        with warnings.catch_warnings(record=True):
            warnings.simplefilter("always")
            temp_df = pd.read_excel(io.BytesIO(r.content), engine="openpyxl")
        
        temp_df["证券类别"] = temp_df["证券类别"].astype(str).str.strip()
        temp_df.iloc[:, 2:] = temp_df.iloc[:, 2:].map(lambda x: x.replace(",", "") if isinstance(x, str) else x)
        temp_df.columns = ["证券类别", "数量", "成交金额", "总市值", "流通市值"]
        
        temp_df["数量"] = pd.to_numeric(temp_df["数量"], errors="coerce")
        temp_df["成交金额"] = pd.to_numeric(temp_df["成交金额"], errors="coerce")
        temp_df["总市值"] = pd.to_numeric(temp_df["总市值"], errors="coerce")
        temp_df["流通市值"] = pd.to_numeric(temp_df["流通市值"], errors="coerce")
        
        return temp_df
    
    @staticmethod
    def calc_china_market_cap(raw_df):
        """获取A股总市值（万亿元人民币）- 使用交易所官方数据"""
        today = datetime.now().strftime("%Y-%m-%d")
        cache_dir = os.path.join("data/cache", today)
        cache_path = os.path.join(cache_dir, "china_market_cap.txt")
        
        # 检查缓存
        if os.path.exists(cache_path):
            print(f"📦 [Cache] 命中A股总市值缓存")
            with open(cache_path, 'r', encoding='utf-8') as f:
                value = f.read().strip()
                return float(value) if value != "None" else None
        
        try:
            print("🔍 正在获取A股市场概况...")
            
            yesterday = datetime.now() - timedelta(days=1)
            yesterday_str = yesterday.strftime("%Y%m%d")
            
            sse_cap = None
            szse_cap = None
            
            # 1. 上海证券交易所股票数据总貌
            try:
                sse_df = ak.stock_sse_summary()
                sse_cap = float(sse_df[sse_df['项目'] == '总市值']['股票'].values[0])
                print(f"📈 上交所市值: {sse_cap} 亿元")
            except Exception as e:
                print(f"❌ 获取上交所市值失败: {e}")
            
            # 2. 深圳证券交易所市场总貌
            try:
                szse_df = DataCollector._stock_szse_summary(date=yesterday_str)
                szse_cap_yuan = float(szse_df[szse_df['证券类别'] == '股票']['总市值'].values[0])
                szse_cap = szse_cap_yuan / 1e8  # 元转亿元
                print(f"📈 深交所市值: {szse_cap:.2f} 亿元")
            except Exception as e:
                print(f"❌ 获取深交所市值失败: {e}")
            
            # 只有当两个交易所数据都成功获取时，才返回总市值
            if sse_cap is not None and szse_cap is not None:
                total_cap = round((sse_cap + szse_cap) / 10000, 2)  # 亿元转万亿元
                print(f"📊 A股总市值: {total_cap} 万亿元")
                
                # 保存缓存
                if not os.path.exists(cache_dir):
                    os.makedirs(cache_dir)
                with open(cache_path, 'w', encoding='utf-8') as f:
                    f.write(str(total_cap))
                
                return total_cap
            else:
                print("⚠️ A股总市值数据不完整（上海或深圳接口失败）")
                # 保存失败标记到缓存
                if not os.path.exists(cache_dir):
                    os.makedirs(cache_dir)
                with open(cache_path, 'w', encoding='utf-8') as f:
                    f.write("None")
                return None
            
        except Exception as e:
            print(f"❌ 获取A股总市值失败: {e}")
            return None

    
    def get_market_fund_flow(self):
        """
        获取全市场（或大盘）盘中分时资金流向
        对应 image_10cf9d.png 中的机构、主力、大户、散户动态走势
        数据说明：
        - 机构 = 超大单净流入
        - 主力 = 大单净流入
        - 大户 = 中单净流入
        - 散户 = 小单净流入
        """
        fund_flow_cache = os.path.join(self.cache_dir, "market_fund_flow.csv")

        if os.path.exists(fund_flow_cache):
            print("📦 [Cache] 命中全市场资金流向缓存...")
            df = pd.read_csv(fund_flow_cache)
        else:
            print("🚀 [AkShare] 正在抓取今日全市场分时资金流向...")
            try:
                # 使用东财大盘资金流向接口
                # stock_market_fund_flow 返回历史资金流向汇总
                # 对于分时数据，我们使用 stock_zh_a_fund_flow 接口
                
                # 方案1：获取全市场资金流向快照（包含超大单、大单、中单、小单）
                df = ak.stock_market_fund_flow()
                
                # 方案2：如果需要分时数据，使用大盘指数的资金流向
                # 上证综指资金流向
                # sh_df = ak.stock_zh_index_fund_flow(symbol="sh000001")
                
                df.to_csv(fund_flow_cache, index=False, encoding='utf-8-sig')
                print(f"💾 [Storage] 资金流向数据已备份: {fund_flow_cache}")
            except Exception as e:
                print(f"❌ 资金流向抓取失败: {e}")
                return None
        
        return self._process_fund_flow_data(df)
    
    def _process_fund_flow_data(self, df):
        """
        处理资金流向数据，统一字段命名为机构、主力、大户、散户
        """
        if df is None or df.empty:
            return None
        
        try:
            # 映射东财字段到统一命名
            column_mapping = {
                '超大单净流入-金额': '机构',
                '大单净流入-金额': '主力', 
                '中单净流入-金额': '大户',
                '小单净流入-金额': '散户',
                '超大单净流入': '机构',
                '大单净流入': '主力',
                '中单净流入': '大户',
                '小单净流入': '散户',
                '超大单净额': '机构',
                '大单净额': '主力',
                '中单净额': '大户',
                '小单净额': '散户'
            }
            
            # 重命名列
            df = df.rename(columns={k: v for k, v in column_mapping.items() if k in df.columns})
            
            # 检查是否有必要的列
            required_cols = ['机构', '主力', '大户', '散户']
            missing_cols = [col for col in required_cols if col not in df.columns]
            
            if missing_cols:
                print(f"❌ 资金流向数据缺少必要字段: {missing_cols}")
                return None
            
            # 如果没有时间列，生成模拟时间
            if '时间' not in df.columns:
                df['时间'] = self._generate_time_sequence(len(df))
            
            # 确保数值类型正确（单位：元 -> 亿元）
            for col in required_cols:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
                # 如果数值太大（单位为元），转换为亿元
                if df[col].abs().max() > 10000:
                    df[col] = df[col] / 100000000
                # 如果数值适中（单位为万元），转换为亿元
                elif df[col].abs().max() > 1:
                    df[col] = df[col] / 10000
            
            return df
        except Exception as e:
            print(f"❌ 资金流向数据处理失败: {e}")
            return None
    
    def _generate_time_sequence(self, length):
        """生成时间序列"""
        times = []
        count = 0
        
        # 上午盘：09:30-11:30
        for hour in range(9, 12):
            for minute in range(0, 60, 15):
                if hour == 9 and minute < 30:
                    continue
                if count >= length:
                    break
                times.append(f"{hour:02d}:{minute:02d}")
                count += 1
            if count >= length:
                break
        
        # 下午盘：13:00-15:00
        for hour in range(13, 16):
            for minute in range(0, 60, 15):
                if count >= length:
                    break
                times.append(f"{hour:02d}:{minute:02d}")
                count += 1
            if count >= length:
                break
        
        return times

    @staticmethod
    def get_us_market_cap():
        """获取美股全市场总市值（万亿美元）- 使用威尔希尔5000指数"""
        today = datetime.now().strftime("%Y-%m-%d")
        cache_dir = os.path.join("data/cache", today)
        cache_path = os.path.join(cache_dir, "us_market_cap.txt")
        
        # 检查缓存
        if os.path.exists(cache_path):
            print(f"📦 [Cache] 命中美股总市值缓存")
            with open(cache_path, 'r', encoding='utf-8') as f:
                value = f.read().strip()
                return float(value) if value != "None" else None
        
        try:
            print("🔍 [YFinance] 正在获取美股总市值 (Wilshire 5000)...")
            ticker = yf.Ticker("^FTW5000")
            hist = ticker.history(period="1d")
            
            if hist is None or hist.empty:
                print("⚠️ 美股指数数据为空")
                # 保存失败标记到缓存
                if not os.path.exists(cache_dir):
                    os.makedirs(cache_dir)
                with open(cache_path, 'w', encoding='utf-8') as f:
                    f.write("None")
                return None
            
            close_price = hist['Close'].iloc[-1]
            # 威尔希尔5000指数：1点 ≈ 10亿美元市值
            # 所以指数点数 / 1000 = 万亿美元市值
            total_cap = round(close_price / 1000.0, 2)
            print(f"📊 美股总市值: {total_cap} 万亿美元")
            
            # 保存缓存
            if not os.path.exists(cache_dir):
                os.makedirs(cache_dir)
            with open(cache_path, 'w', encoding='utf-8') as f:
                f.write(str(total_cap))
            
            return total_cap
        except Exception as e:
            print(f"❌ 获取美股总市值失败: {e}")
            # 保存失败标记到缓存
            if not os.path.exists(cache_dir):
                os.makedirs(cache_dir)
            with open(cache_path, 'w', encoding='utf-8') as f:
                f.write("None")
            return None
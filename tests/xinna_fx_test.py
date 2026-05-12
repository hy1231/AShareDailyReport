import os
import akshare as ak

# 1. 确保新浪财经的域名不走代理
os.environ['no_proxy'] = 'sina.com.cn, finance.sina.com.cn'

def get_usd_cnh_data():
    try:
        # 使用新浪接口获取离岸人民币历史数据
        # 这个接口通常返回最近的历史日线数据，不需要复杂的 period 设置
        fx_df = ak.forex_sina_hist(symbol="USDCNH")
        
        if fx_df is not None and not fx_df.empty:
            # 统一字段名，方便你后续逻辑（新浪返回的是：日期, 开盘价, 最高价...）
            print(f"USDCNH: 成功获取 {len(fx_df)} 条数据")
            return fx_df
        else:
            print("未能获取到数据")
    except Exception as e:
        print(f"获取失败 - {e}")

df = get_usd_cnh_data()
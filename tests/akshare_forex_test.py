import akshare as ak
import os
from dotenv import load_dotenv

def clear_system_proxies():
    """清除代理，确保国内接口直连"""
    proxy_vars = [
        'http_proxy', 'https_proxy', 'all_proxy', 
        'HTTP_PROXY', 'HTTPS_PROXY', 'ALL_PROXY'
    ]
    
    for var in proxy_vars:
        if var in os.environ:
            del os.environ[var]
    
    os.environ['NO_PROXY'] = '*'
    os.environ['no_proxy'] = '*'
    
    print("🧹 代理已清除，进入直连模式。")

def setup_proxy():
    """设置全局代理（类似 settings.py 的逻辑）"""
    load_dotenv()
    GEMINI_PROXY = os.getenv("GEMINI_PROXY")
    
    if GEMINI_PROXY:
        os.environ["HTTP_PROXY"] = GEMINI_PROXY
        os.environ["HTTPS_PROXY"] = GEMINI_PROXY
        print(f"🌐 已设置代理: {GEMINI_PROXY}")
    else:
        print("⚠️ 未找到 GEMINI_PROXY 环境变量")

print("🔍 检查 AkShare 可用的外汇历史数据接口...")

# 测试1: 不使用代理（直连模式）
# print("\n=== 测试1: 直连模式 ===")
# clear_system_proxies()
# try:
#     df = ak.forex_hist_em(symbol="USDCNH")
#     print(f"✅ 直连模式成功! 数据形状: {df.shape}")
#     print(f"列名: {df.columns.tolist()}")
#     print(df.tail())
# except Exception as e:
#     print(f"❌ 直连模式失败: {str(e)}")

# 测试2: 使用代理模式
print("\n=== 测试2: 代理模式 ===")
setup_proxy()
try:
    df = ak.forex_hist_em(symbol="USDCNH")
    print(f"✅ 代理模式成功! 数据形状: {df.shape}")
    print(f"列名: {df.columns.tolist()}")
    print(df.tail())
except Exception as e:
    print(f"❌ 代理模式失败: {str(e)}")

# 列出所有可用接口
print("\n=== 可用接口列表 ===")
forex_funcs = [f for f in dir(ak) if "forex" in f.lower() and "hist" in f.lower()]
print(f"包含 'forex' 和 'hist' 的接口:")
print(forex_funcs)
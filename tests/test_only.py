# import requests
# from requests.sessions import Session
# import efinance as ef



# df = ef.stock.get_realtime_quotes('沪深京A股')
# a = 0

# curl -I "http://push2.eastmoney.com/api/qt/clist/get"

from curl_cffi import requests
import pandas as pd

def get_market_sentiment_hardcore():
    # 这是东财行情接口的真实 URL（简化版）
    url = "http://push2.eastmoney.com/api/qt/clist/get?pn=1&pz=200&po=1&np=1&fltt=2&invt=2&fid=f3&fs=m:0+t:6,m:0+t:80,m:1+t:2,m:1+t:23,m:0+t:81+s:2048&fields=f12,f14,f3"
    
    # 使用 curl_cffi 模拟 Chrome 的 TLS 指纹
    # impersonate="chrome120" 会让你的请求在协议底层看起来和真浏览器一模一样 或 chrome124
    response = requests.get(url, impersonate="chrome120", timeout=10)
    
    if response.status_code == 200:
        data = response.json()
        stocks = data['data']['diff']
        df = pd.DataFrame(stocks)
        # 这里你可以继续处理 df，对接你之后的 A-Canvas 逻辑
        print("✅ 成功！JA3 指纹绕过成功。")
        return df
    else:
        print(f"❌ 还是失败: {response.status_code}")


df = get_market_sentiment_hardcore()
a=0

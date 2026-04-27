import os
import httpx
from google import genai
import time

# --- 配置区 ---

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
MODEL_ID = os.getenv("GOOGLE_MODEL_ID")
GEMINI_PROXY = os.getenv("GEMINI_PROXY")

def test_proxy_injection():
    print(f"🚀 开始测试，目标代理: {GEMINI_PROXY}")
    
    # 1. 备份原有的环境变量
    old_http = os.environ.get('HTTP_PROXY')
    old_https = os.environ.get('HTTPS_PROXY')
    print(f"📦 初始状态: HTTP_PROXY={old_http}, HTTPS_PROXY={old_https}")

    # 2. 临时注入代理
    os.environ['HTTP_PROXY'] = GEMINI_PROXY
    os.environ['HTTPS_PROXY'] = GEMINI_PROXY
    print(f"🧪 注入完成: 环境变量已指向 {GEMINI_PROXY}")

    try:
        # --- 测试 A: 基础连接性 (绕过 SDK) ---
        print("\n--- 步骤 A: 基础 httpx 访问测试 ---")
        with httpx.Client(timeout=10.0) as client:
            # 尝试访问 google 首页
            start = time.time()
            resp = client.get("https://www.google.com")
            print(f"✅ httpx 访问成功! 耗时: {time.time()-start:.2f}s, 状态码: {resp.status_code}")

        # --- 测试 B: 模拟 SDK 初始化与调用 ---
        print("\n--- 步骤 B: SDK 真实调用测试 ---")
        client = genai.Client(api_key=GOOGLE_API_KEY)
        
        start = time.time()
        # 这里只发一个极其简单的请求
        response = client.models.generate_content(
            model=MODEL_ID,
            contents="Hello, this is a proxy test."
        )
        print(f"✅ SDK 调用成功! 耗时: {time.time()-start:.2f}s")
        print(f"🤖 AI 回复摘要: {response.text[:20]}...")

    except Exception as e:
        print(f"\n❌ 测试过程中发生错误!")
        print(f"错误类型: {type(e).__name__}")
        print(f"错误详情: {str(e)}")
        
        if "10060" in str(e):
            print("\n💡 [诊断建议]: WinError 10060 代表连接超时。")
            print("既然 curl 能通但这里不通，通常是因为 Python 的 httpx 尝试建立 HTTP/2 连接，但代理软件拒绝了。")

    finally:
        # 3. 立即还原
        if old_http: os.environ['HTTP_PROXY'] = old_http
        else: os.environ.pop('HTTP_PROXY', None)
        
        if old_https: os.environ['HTTPS_PROXY'] = old_https
        else: os.environ.pop('HTTPS_PROXY', None)
        
        print("\n♻️ 环境已还原。")
        print(f"当前状态: HTTP_PROXY={os.environ.get('HTTP_PROXY')}")

if __name__ == "__main__":
    test_proxy_injection()
import os
from pathlib import Path
from dotenv import load_dotenv
import os

def clear_system_proxies():
    """
    【安全钩子】强制清除当前进程的环境变量代理，防止国内接口被封 IP
    """
    # 定义所有可能影响 Python 网络库的代理变量名
    proxy_vars = [
        'http_proxy', 'https_proxy', 'all_proxy', 
        'HTTP_PROXY', 'HTTPS_PROXY', 'ALL_PROXY'
    ]
    
    # 逐一删除
    for var in proxy_vars:
        if var in os.environ:
            del os.environ[var]
    
    # 额外加一层保险：告诉 requests 库，对所有请求都不要尝试寻找代理
    os.environ['NO_PROXY'] = '*'
    os.environ['no_proxy'] = '*'
    
    print("🧹 [System] 进程级环境变量已清理，国内接口进入直连模式。")


# 路径自动管理
BASE_DIR = Path(__file__).resolve().parent.parent

# 加载 .env 环境变量
load_dotenv(BASE_DIR / ".env")

# 调用清理方法（确保全局环境默认是干净的）
#clear_system_proxies()

# AI相关配置
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
MODEL_ID = os.getenv("GOOGLE_MODEL_ID")
GEMINI_PROXY = os.getenv("GEMINI_PROXY")

## 全局代理
os.environ["HTTP_PROXY"] = GEMINI_PROXY
os.environ["HTTPS_PROXY"] = GEMINI_PROXY

# GDP 基准数据 (单位：万亿)
# 用于计算巴菲特指标 = 总市值 / GDP * 100%
CHINA_GDP_2025 = 140.19  # 万亿元人民币 (2025年名义GDP)
US_GDP_2025 = 30.77      # 万亿美元 (2025年名义GDP)

# 巴菲特指标估值状态阈值
# 中国A股阈值（由于大量核心资产在港股/美股上市，天然低于美股）
CHINA_BUFFETT_VERY_LOW = 50   # 历史极度低估
CHINA_BUFFETT_LOW = 75         # 偏高
# 美股阈值（科技股和全球化中枢上移）
US_BUFFETT_REASONABLE = 130    # 合理估值
US_BUFFETT_HIGH = 170          # 显著高估

# 业务逻辑常量
# 绘图颜色方案 (统一在这里修改 UI 风格)
REPORT_COLORS = {
    "up": "#ff4d4f",      # A股标志性的亮红色
    "down": "#52c41a",    # 亮绿色
    "neutral": "#f0f0f0"  # 平盘或背景灰
}

# 数据抓取限制
REQUEST_TIMEOUT = 15      # 针对 efinance 网络波动
MAX_RETRY = 3             # 失败重试次数

# --- 4. 自动初始化必要文件夹 ---
# 这样你第一次跑代码时，程序会自动帮你建好 output 和 data 文件夹
OUTPUT_DIR = BASE_DIR / "output"
CACHE_DIR = BASE_DIR / "data" / "cache"
TEMPLATE_DIR = BASE_DIR / "templates"

# 自动创建目录逻辑 (类似 C++ 的 mkdir -p)
for folder in [OUTPUT_DIR, CACHE_DIR, TEMPLATE_DIR]:
    folder.mkdir(parents=True, exist_ok=True)

# --- 5. 开发者调试信息 ---
if os.getenv("ENV_TYPE") == "dev":
    print(f"🚀 [A-Canvas] 项目根目录: {BASE_DIR}")
    print(f"🤖 [A-Canvas] 当前模型: {MODEL_ID}")
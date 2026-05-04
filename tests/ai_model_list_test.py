from google import genai  # 你现在的导入方式
from dotenv import load_dotenv
import os

# 加载配置
load_dotenv()
GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY")

# --- 关键改动：创建 Client 对象 ---
client = genai.Client(api_key=GEMINI_API_KEY)

print("--- 当前可用的模型列表 ---")

# --- 关键改动：使用 client.models.list() ---
for m in client.models.list():
    # 新版 SDK 的模型对象属性与旧版略有不同
    # 我们可以直接打印名称来看看
    print(f"可用模型 ID: {m.name}")


#     --- 当前可用的模型列表 ---
# 可用模型 ID: models/gemini-2.5-flash
# 可用模型 ID: models/gemini-2.5-pro
# 可用模型 ID: models/gemini-2.0-flash
# 可用模型 ID: models/gemini-2.0-flash-001
# 可用模型 ID: models/gemini-2.0-flash-lite-001
# 可用模型 ID: models/gemini-2.0-flash-lite
# 可用模型 ID: models/gemini-2.5-flash-preview-tts
# 可用模型 ID: models/gemini-2.5-pro-preview-tts
# 可用模型 ID: models/gemma-3-1b-it
# 可用模型 ID: models/gemma-3-4b-it
# 可用模型 ID: models/gemma-3-12b-it
# 可用模型 ID: models/gemma-3-27b-it
# 可用模型 ID: models/gemma-3n-e4b-it
# 可用模型 ID: models/gemma-3n-e2b-it
# 可用模型 ID: models/gemma-4-26b-a4b-it
# 可用模型 ID: models/gemma-4-31b-it
# 可用模型 ID: models/gemini-flash-latest
# 可用模型 ID: models/gemini-flash-lite-latest
# 可用模型 ID: models/gemini-pro-latest
# 可用模型 ID: models/gemini-2.5-flash-lite
# 可用模型 ID: models/gemini-2.5-flash-image
# 可用模型 ID: models/gemini-3-pro-preview
# 可用模型 ID: models/gemini-3-flash-preview
# 可用模型 ID: models/gemini-3.1-pro-preview
# 可用模型 ID: models/gemini-3.1-pro-preview-customtools
# 可用模型 ID: models/gemini-3.1-flash-lite-preview
# 可用模型 ID: models/gemini-3-pro-image-preview
# 可用模型 ID: models/nano-banana-pro-preview
# 可用模型 ID: models/gemini-3.1-flash-image-preview
# 可用模型 ID: models/lyria-3-clip-preview
# 可用模型 ID: models/lyria-3-pro-preview
# 可用模型 ID: models/gemini-3.1-flash-tts-preview
# 可用模型 ID: models/gemini-robotics-er-1.5-preview
# 可用模型 ID: models/gemini-robotics-er-1.6-preview
# 可用模型 ID: models/gemini-2.5-computer-use-preview-10-2025
# 可用模型 ID: models/deep-research-max-preview-04-2026
# 可用模型 ID: models/deep-research-preview-04-2026
# 可用模型 ID: models/deep-research-pro-preview-12-2025
# 可用模型 ID: models/gemini-embedding-001
# 可用模型 ID: models/gemini-embedding-2-preview
# 可用模型 ID: models/aqa
# 可用模型 ID: models/imagen-4.0-generate-001
# 可用模型 ID: models/imagen-4.0-ultra-generate-001
# 可用模型 ID: models/imagen-4.0-fast-generate-001
# 可用模型 ID: models/veo-3.0-generate-001
# 可用模型 ID: models/veo-3.0-fast-generate-001
# 可用模型 ID: models/veo-3.1-fast-generate-preview
# 可用模型 ID: models/veo-3.1-lite-generate-preview
# 可用模型 ID: models/gemini-2.5-flash-native-audio-latest
# 可用模型 ID: models/gemini-2.5-flash-native-audio-preview-09-2025
# 可用模型 ID: models/gemini-2.5-flash-native-audio-preview-12-2025
# 可用模型 ID: models/gemini-3.1-flash-live-preview
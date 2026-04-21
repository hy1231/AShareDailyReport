from google import genai
from google.genai import types
from src import settings
import httpx
class AIAnalyst:
    def __init__(self):
        # 初始化最新的 Google GenAI 客户端
        self.http_client = httpx.Client(
                proxies=settings.GEMINI_PROXY,
                timeout=30.0  # 稍微延长超时，防止网络波动
            )

        self.client = genai.Client(
            api_key=settings.GOOGLE_API_KEY,
            http_client=self.http_client # <--- 这一步是灵魂
        )

        #self.client = genai.Client(api_key=settings.GOOGLE_API_KEY)
        self.model_id = settings.MODEL_ID

    def get_market_review(self, market_data):
        """调用 Gemini 进行深度复盘"""
        prompt = f"""
        你是一位身经百战的 A 股首席策略分析师。
        请根据以下今日市场数据，撰写一份结构清晰、见解深刻的 Markdown 复盘简报。

        今日数据摘要：
        {market_data}

        要求：
        1. 标题要吸睛，段落要短促有力。
        2. 结合涨跌家数分析“赚钱效应”是否真实存在。
        3. 评价成交量是否足以支撑当前趋势。
        4. 最后给出一句“明日生存指南”。
        5. 严禁废话，直接输出 Markdown 内容。
        """

        try:
            response = self.client.models.generate_content(
                model=self.model_id,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.7,  # 保持一定的分析灵活性
                    top_p=0.95,
                )
            )
            return response.text
        except Exception as e:
            return f"> ⚠️ AI 分析暂时离线：{str(e)}"
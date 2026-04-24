import httpx
from google import genai
from google.genai import types
from src import settings

class AIAnalyst:
    def __init__(self):
        """
        初始化 Google GenAI 客户端
        集成 httpx 代理以解决国内网络环境下无法访问 Gemini API 的问题
        """
        # 1. 配置代理客户端
        self.http_client = httpx.Client(
            proxies=settings.GEMINI_PROXY,
            timeout=30.0  # 增加超时时间以应对复杂分析任务
        )

        # 2. 初始化 GenAI Client (SDK v2.x 风格)
        self.client = genai.Client(
            api_key=settings.GOOGLE_API_KEY,
            http_client=self.http_client
        )

        self.model_id = settings.MODEL_ID

    def get_market_review(self, market_data, industry_data):
        """
        调用 Gemini 1.5/2.0 进行深度复盘分析
        
        :param market_data: dict, 包含 up, down, stay, volume, date
        :param industry_data: List[dict], 包含 行业名称, 涨跌幅, 成交额, 领涨股票
        :return: Markdown 格式的复盘文案
        """
        if not market_data or not industry_data:
            return "> ⚠️ 数据源不完整，AI 无法进行深度研判。"

        # 1. 选取前 10 个核心行业数据传给 AI，防止上下文过长导致重点模糊
        # 注意：这里我们使用的是排序后的前 10 名，包含了今日的最强热点
        top_industries = industry_data[:10]

        # 2. 构建深度 Prompt
        # 融入了首席策略分析师的角色设定，并要求点评具体个股
        prompt = f"""
        你是一位身经百战的 A 股首席策略分析师，擅长从量价关系和板块轮动中洞察市场本质。
        请根据以下真实数据，撰写一份结构清晰、见解深刻、具备自媒体传播力的 Markdown 复盘简报。

        ---
        ### 📌 今日市场核心数据
        - **复盘日期**：{market_data.get('date')}
        - **涨跌分布**：上涨 {market_data.get('up')} 家 / 下跌 {market_data.get('down')} 家 / 平盘 {market_data.get('stay')} 家
        - **全天成交**：{market_data.get('volume')} (单位：亿)

        ### 🔥 重点行业异动 (Top {len(top_industries)})
        {self._format_industry_for_ai(top_industries)}

        ---
        ### ✍️ 写作要求：
        1. **吸睛标题**：根据今日行情特点起一个锐利的标题（例如：缩量阴跌、船舶独强、普涨狂欢等）。
        2. **情绪研判**：结合涨跌家数对比，评价今日“赚钱效应”如何，是核心资产抱团还是游资题材炒作？
        3. **灵魂点评**：**必须引用数据中的具体行业和领涨股票**（例如：{top_industries[0]['行业名称'] if top_industries else '某'}板块），点评其带动力和持续性。
        4. **量价逻辑**：结合 {market_data.get('volume')} 的成交额，判断当前位置是“蓄势”还是“衰竭”。
        5. **生存指南**：给出一句既犀利又实操的明日策略建议（拒绝“谨慎乐观看待”等废话）。
        6. **风格规范**：段落短小，多用 **加粗** 和 列表，直接输出 Markdown 内容，禁止任何前导或后续废话。
        """

        try:
            # 3. 调用模型生成
            response = self.client.models.generate_content(
                model=self.model_id,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.7,  # 适度发散，增加文案的文学色彩
                    top_p=0.95,
                    max_output_tokens=2048
                )
            )
            return response.text
        except Exception as e:
            print(f"❌ [AI Analyst Error]: {e}")
            return f"> ⚠️ AI 复盘生成失败：可能是 API 密钥无效或网络不稳定。错误详情: {str(e)}"

    def _format_industry_for_ai(self, data):
        """将行业列表格式化为 AI 更易理解的文本块"""
        lines = []
        for item in data:
            line = f"- 【{item['行业名称']}】涨跌幅: {item['涨跌幅']:.2f}% | 成交: {item['成交额']}亿 | 领涨股: {item['领涨股票']}"
            lines.append(line)
        return "\n".join(lines)
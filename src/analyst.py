import os
import httpx
from google import genai
from google.genai import types
from src import settings
import textwrap

class AIAnalyst:
    def __init__(self):
        # 初始化 Client
        self.client = genai.Client(api_key=settings.GOOGLE_API_KEY)
        self.model_id = settings.MODEL_ID
        
        # 确保缓存目录存在
        self.cache_dir = "data/cache"
        os.makedirs(self.cache_dir, exist_ok=True)

    def get_market_review(self, market_data, industry_data):
        """
        调用 Gemini 进行深度复盘，优先读取本地缓存
        """
        if not market_data or not industry_data:
            return "> ⚠️ 数据源不完整，AI 无法进行深度研判。"

        # 1. 检查缓存：根据日期生成缓存文件名
        date_str = market_data.get('date', 'unknown')
        cache_path = f"{self.cache_dir}/ai_review_{date_str}.txt"

        if os.path.exists(cache_path):
            print(f"📦 [Cache Hit] 发现 {date_str} 的本地复盘缓存，直接读取。")
            with open(cache_path, 'r', encoding='utf-8') as f:
                return f.read()

        # --- 如果缓存不存在，则执行 AI 生成逻辑 ---
        print(f"🧠 [Cache Miss] 正在请求 Gemini 生成 {date_str} 的专业复盘...")

        # 提取个股洞察
        insights = market_data.get('stock_insights', {})
        formatted_industries = self._format_industry_for_ai(industry_data)

        # 构建增强版 Prompt
        prompt = f"""
你是一位身经百战的 A 股首席策略分析师。请结合以下【宏观、行业、个股】多维数据撰写 Markdown 复盘简报。

---
### 📊 市场快照
- **日期**：{market_data.get('date')}
- **多空分布**：上涨 {market_data.get('up')} / 下跌 {market_data.get('down')}
- **成交总量**：{market_data.get('volume')}

### 🔥 全市场行业纵览 (49个一级行业)
{formatted_industries }

### 🎯 个股异动 (蒸馏情报)
- **领涨先锋**：{self._format_stocks(insights.get('gainers', []))}
- **跌幅重灾**：{self._format_stocks(insights.get('losers', []))}
- **资金焦点**：{self._format_stocks(insights.get('active', []))}

---
### ✍️ 写作要求：
1. **标题**：起一个锐利且带观点、有自媒体传播力的标题。
2. **赚钱效应**：结合个股涨跌比和【领涨先锋】榜单，评价今日是“真强”还是“虚火”。
3. **灵魂点评**：**必须引用数据中的具体行业和代表性个股**。重点分析【资金焦点】榜单里的权重股表现，判断大资金态度。
4. **量价逻辑**：结合 {market_data.get('volume')} 成交量，评价市场的承接力。
5. **生存指南**：给出一句既犀利又实操的明日策略建议。
6. **风格**：多用 **加粗**，段落短促，直接输出 Markdown 内容。
"""

        # 调试开关，或者直接打印
        # print(f"🚀 [Debug] 正在请求 Gemini ({self.model_id})...")
        # print(f"📊 宏观数据日期: {market_data.get('date')}")
        # print(f"📈 传入行业数量: {len(industry_data)}")
        
        # # 打印完整的 Prompt 方便检查格式
        # print("-" * 50)
        # print(prompt)
        # print("-" * 50)

        try:
            response = self.client.models.generate_content(
                model=self.model_id,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.7,
                    top_p=0.95
                )
            )
            
            result_text = response.text
            
            # 2. 成功获取后，存入缓存
            if result_text and "⚠️" not in result_text:
                with open(cache_path, 'w', encoding='utf-8') as f:
                    f.write(result_text)
                print(f"💾 今日复盘已存入缓存: {cache_path}")
                
            return result_text

        except Exception as e:
            print(f"⚠️ AI 复盘生成失败: {str(e)}")
            return f"> ⚠️ AI 复盘生成失败：{str(e)}"

    def _format_industry_for_ai(self, data):
        """格式化全量 49 个行业数据，保持精简"""
        lines = []
        for item in data:
            line = f"- {item['行业名称']}: {item['涨跌幅']:.2f}% (领涨: {item['领涨股票']})"
            lines.append(line)
        return "\n".join(lines)

    def _format_stocks(self, stocks):
        """将个股列表转为简短字符串"""
        if not stocks: return "无"
        return "、".join([f"{s['名称']}({s['涨跌幅']:.1f}%)" for s in stocks])
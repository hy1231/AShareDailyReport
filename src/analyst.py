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
        daily_cache_dir = os.path.join(self.cache_dir, date_str)
        os.makedirs(daily_cache_dir, exist_ok=True)
        cache_path = os.path.join(daily_cache_dir, "ai_review.txt")

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
        # 构建宏观数据描述
        macro_section = ""
        if market_data.get('macro'):
            fx = market_data['macro'].get('fx')
            oil = market_data['macro'].get('oil')
            buffett = market_data['macro'].get('buffett')
            
            if fx:
                macro_section += f"""### 🌍 宏观环境观察
- **美元兑离岸人民币 (USD/CNH)**：{fx['当前汇率']}，日变化 {fx['日变化']:+.4f}，当日趋势 {fx['当日趋势']}，长期趋势 {fx['长期趋势']}，近30日均值 {fx['近30日均值']}，区间 [{fx['近30日最低']}, {fx['近30日最高']}]
"""
            if oil:
                macro_section += f"""- **布伦特原油**：${oil['当前油价']}/桶，日变化 ${oil['日变化']:+.2f}，近30日均值 ${oil['近30日均值']}，趋势 {oil['趋势']}
"""
            if fx or oil:
                macro_section += "\n> 请结合宏观环境，分析汇率、原油和估值水位对市场情绪的影响。\n"

        prompt = f"""
你是一位拥有 10 年经验的资深宏观策略分析师，风格冷静、客观，擅长透过数据表象看清资金本质。请结合以下【宏观、行业、个股】多维数据撰写 Markdown 复盘简报。

----
### 📊 市场快照
- **日期**：{market_data.get('date')}
- **多空分布**：上涨 {market_data.get('up')} / 下跌 {market_data.get('down')}
- **成交总量**：{market_data.get('volume')}
{macro_section}
### 🔥 全市场行业纵览 (49个一级行业)
{formatted_industries }

### 🎯 个股异动 (蒸馏情报)
- **领涨先锋**：{self._format_stocks(insights.get('gainers', []))}
- **跌幅重灾**：{self._format_stocks(insights.get('losers', []))}
- **成交额榜**：{self._format_stocks(insights.get('active', []))}

----
### ✍️ 写作要求（字数控制在 300 字以内）：
1. **核心逻辑**：用一句话概括今日盘面本质（如：缩量震荡、情绪退潮、蓝筹护盘等）。
2. **复盘要点**：
    - 结合成交量和涨跌比，点明【赚钱效应】真实度。
    - 必须点出 1-2 个最具代表性的行业或权重股及其所反映的资金意图。
    - 简述汇率/原油对今日盘面的具体干扰。
3. **行动策略**：基于风险收益比，给出一句针对性建议。不追求预判涨跌，而追求应对逻辑。
4. 复盘要点按照小点列出
"""
        # 调试开关，或者直接打印
        # print(f"🚀 [Debug] 正在请求 Gemini ({self.model_id})...")
        # print(f"📊 宏观数据日期: {market_data.get('date')}")
        # print(f"📈 传入行业数量: {len(industry_data)}")
        
        # 打印完整的 Prompt 方便检查格式
        print("-" * 50)
        print(prompt)
        print("-" * 50)

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
            return "AI_REVIEW_FAILED"

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
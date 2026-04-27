from src import settings ## 放到最前面，里面设置代理
from dotenv import load_dotenv
from jinja2 import Template
from src.collector import DataCollector
from src.visualizer import Visualizer
from src.analyst import AIAnalyst

import urllib.request
urllib.request.getproxies = lambda: {}

from google import genai

load_dotenv()



def prepare_stock_insights(raw_df):
    """
    数据蒸馏：从 5500+ 只个股中提取 AI 最关心的核心特征
    """
    if raw_df is None or raw_df.empty:
        return {}

    # 1. 涨幅榜 Top 10 (寻找市场最强赚钱效应)
    top_gainers = raw_df.nlargest(10, '涨跌幅')[['名称', '涨跌幅', '成交额']]
    
    # 2. 跌幅榜 Top 10 (识别市场风险点)
    top_losers = raw_df.nsmallest(10, '涨跌幅')[['名称', '涨跌幅', '成交额']]
    
    # 3. 成交额榜 Top 10 (观察权重股与大资金动向)
    top_active = raw_df.nlargest(10, '成交额')[['名称', '涨跌幅', '成交额']]

    return {
        "gainers": top_gainers.to_dict('records'),
        "losers": top_losers.to_dict('records'),
        "active": top_active.to_dict('records')
    }

def main():
    # 采集数据
    collector = DataCollector()

    # 今日市场整体数据
    market_data = collector.get_market_sentiment() 

    # 增加防御：如果抓取失败，停止后续操作
    if not market_data or 'raw_df' not in market_data:
        print("🛑 关键数据 (market_data) 缺失，停止生成日报。")
        return

    # 今日行业领涨数据
    full_industries = collector.get_top_industries()

    # 增加防御：如果抓取失败，停止后续操作
    if not full_industries:
        print("🛑 关键数据 (market_data) 缺失，停止生成日报。")
        return


    # 生成交互图表

    # 绘图用全量
    treemap_html = Visualizer.generate_industry_treemap(full_industries)
    # 给 AI 点评用前 10 名
    top_10_for_ai = full_industries[:10]


    # 创建本地ai记忆库，每次喂给ai

    # 构造传给 AI 的增强版数据包
    stock_insights = prepare_stock_insights(market_data['raw_df'])
    ai_input_data = {
        "date": market_data['date'],
        "up": market_data['up'],
        "down": market_data['down'],
        "volume": market_data['volume'],
        "stock_insights": stock_insights  # 注入涨跌停、活跃股情报
    }

    # AI 深度分析阶段
    analyst = AIAnalyst()
    print("🧠 正在请求 Gemini 进行专业复盘...")

    # 同时传入宏观情报包和行业列表
    review_markdown = analyst.get_market_review(ai_input_data, full_industries)

    # 渲染 Markdown
    with open('templates/report_template.md', 'r', encoding='utf-8') as f:
        tmpl = Template(f.read())

    # 开始注入数据
    final_report = tmpl.render(
        # 基础宏观数据
        date=market_data['date'], 
        up=market_data['up'],
        down=market_data['down'],
        volume=market_data['volume'],
        
        # 核心分析：把 AI 写好的 Markdown 文案传进去
        ai_review=review_markdown,
        
        # 可视化图表：把 Plotly 生成的 HTML 片段传进去
        chart_html=treemap_html
    )

    # 保存最终报告
    output_filename = f"output/A股深度复盘_{market_data['date']}.md"
    with open(output_filename, 'w', encoding='utf-8') as f:
        f.write(final_report)

    print(f"🎉 报告生成成功：{output_filename}")


if __name__ == "__main__":
    main()
from src import settings ## 放到最前面，里面设置代理
from dotenv import load_dotenv
from jinja2 import Template
from src.collector import DataCollector
from src.visualizer import Visualizer
from src.analyst import AIAnalyst
import os
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
    # 1. 采集数据
    collector = DataCollector()
    market_data = collector.get_market_sentiment() 

    if not market_data or 'raw_df' not in market_data:
        print("🛑 关键数据缺失，停止生成日报。")
        return
    if not market_data or 'raw_df' not in market_data: return
    
    full_industries = collector.get_top_industries()
    if not full_industries:
        print("🛑 行业数据缺失，停止生成日报。")
        return
    date_str = market_data['date']

    # 2. 生成行业热力图并存入缓存 (data/cache)
    fig = Visualizer.generate_industry_treemap(full_industries) 
    cache_dir = "data/cache"
    os.makedirs(cache_dir, exist_ok=True)
    image_filename = f"hotmap_{date_str}.png"
    image_cache_path = f"{cache_dir}/{image_filename}"
    
    fig.write_image(image_cache_path, scale=3) 
    print(f"📸 行业热力图已缓存至: {image_cache_path}")

    # 3. 获取原油数据并生成走势图
    oil_data = collector.get_oil_data()
    oil_chart_path = ""
    if oil_data is not None and not oil_data.empty:
        oil_fig = Visualizer.generate_line_chart(oil_data)
        oil_filename = f"oil_{date_str}.png"
        oil_chart_path = f"{cache_dir}/{oil_filename}"
        oil_fig.write_image(oil_chart_path, scale=3)
        print(f"📈 原油走势图已缓存至: {oil_chart_path}")
    else:
        print("⚠️ 原油数据获取失败，跳过图表生成")

    # 3. 构造 AI 输入并获取分析
    stock_insights = prepare_stock_insights(market_data['raw_df'])
    ai_input_data = {
        "date": date_str,
        "up": market_data['up'],
        "down": market_data['down'],
        "volume": market_data['volume'],
        "stock_insights": stock_insights
    }

    analyst = AIAnalyst()
    print("🧠 正在请求 Gemini 进行专业复盘...")
    review_markdown = analyst.get_market_review(ai_input_data, full_industries)

    # 4. 渲染 Markdown
    with open('templates/report_template.md', 'r', encoding='utf-8') as f:
        tmpl = Template(f.read())
    rel_image_path = f"../data/cache/{image_filename}"
    rel_oil_path = f"../data/cache/oil_{date_str}.png" if oil_chart_path else ""

    final_report = tmpl.render(
        date=date_str, 
        up=market_data['up'],
        down=market_data['down'],
        volume=market_data['volume'],
        ai_review=review_markdown,
        chart_image_path=rel_image_path,
        oil_chart_path=rel_oil_path
    )

    # 5. 保存最终报告到 output
    output_filename = f"output/A股深度复盘_{date_str}.md"
    with open(output_filename, 'w', encoding='utf-8') as f:
        f.write(final_report)

    print(f"🎉 报告生成成功：{output_filename}")

if __name__ == "__main__":
    main()
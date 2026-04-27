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

    full_industries = collector.get_top_industries()
    if not full_industries:
        print("🛑 行业数据缺失，停止生成日报。")
        return

    # 2. 生成图表
    # 注意：建议修改 Visualizer 类，让它先返回 fig 对象，方便同时保存 HTML 和图片
    # 这里我们假设你已经按建议修改了 Visualizer，或者直接在这里处理
    
    # 获取 plotly 的 fig 对象
    fig = Visualizer.generate_industry_treemap(full_industries) # 建议新增这个方法返回 fig
    
    # 保存为 HTML (留着本地看)
    #treemap_html = fig.to_html(full_html=False, include_plotlyjs='cdn')
    
    # 保存为静态图片 (给公众号用)
    # 我们把图片存放在 output/images/ 目录下
    date_str = market_data['date']
    image_dir = "output/images"
    os.makedirs(image_dir, exist_ok=True)
    image_path = f"{image_dir}/hotmap_{date_str}.png"
    
    # 使用 kaleido 引擎保存图片
    fig.write_image(image_path, scale=2) 
    print(f"📸 静态图片已生成: {image_path}")

    # 3. 构造 AI 输入并获取分析 (   后续添加： # 创建本地ai记忆库，每次喂给ai)
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

    # 计算图片相对于 .md 文件的路径 (为了在预览时能看到图)
    # 因为 .md 在 output/，图片在 output/images/，所以相对路径是 images/xxx.png
    rel_image_path = f"images/hotmap_{date_str}.png"

    final_report = tmpl.render(
        date=date_str, 
        up=market_data['up'],
        down=market_data['down'],
        volume=market_data['volume'],
        ai_review=review_markdown,
        # 传递图片路径，对应模板里的 ![今日 A 股热力图]({{ chart_image_path }})
        chart_image_path=rel_image_path
    )

    # 5. 保存最终报告
    output_filename = f"output/A股深度复盘_{date_str}.md"
    with open(output_filename, 'w', encoding='utf-8') as f:
        f.write(final_report)

    print(f"🎉 报告生成成功：{output_filename}")

if __name__ == "__main__":
    main()
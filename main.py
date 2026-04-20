import os
from dotenv import load_dotenv
from jinja2 import Template
from src.collector import DataCollector
from src.visualizer import Visualizer
from src.analyst import AIAnalyst

load_dotenv()

def main():
    # 1. 采集数据
    collector = DataCollector()
    market_data = collector.get_market_sentiment()
    industries = collector.get_top_industries()

    # 2. 生成交互图表
    viz = Visualizer()
    chart_html = viz.generate_industry_treemap()

    # 3. AI 分析 (可选)
    analyst = AIAnalyst(api_key=os.getenv("AI_API_KEY"))
    ai_review = analyst.get_market_review(market_data)

    # 4. 渲染 Markdown
    with open('templates/report_template.md', 'r', encoding='utf-8') as f:
        tmpl = Template(f.read())
    
    final_report = tmpl.render(
        date=market_data['date'],
        up=market_data['up'],
        down=market_data['down'],
        volume=market_data['volume'],
        chart_html=chart_html,
        ai_review=ai_review
    )

    # 5. 保存结果
    with open(f"output/report_{market_data['date']}.md", 'w', encoding='utf-8') as f:
        f.write(final_report)
    
    print(f"✅ 日报已生成：output/report_{market_data['date']}.md")

if __name__ == "__main__":
    main()
import os
from dotenv import load_dotenv
from jinja2 import Template
from src.collector import DataCollector
from src.visualizer import Visualizer
from src.analyst import AIAnalyst
from src import settings

import urllib.request
urllib.request.getproxies = lambda: {}


load_dotenv()

def main():
    # 1. 采集数据
    collector = DataCollector()
    market_data = collector.get_market_sentiment()
    industries = collector.get_top_industries()

    # 增加防御：如果抓取失败，停止后续操作
    if not market_data.get('raw_data'):
        print("🛑 关键数据缺失，停止生成日报。")
        return


    # 2. 生成交互图表
    # viz = Visualizer()
    # chart_html = viz.generate_industry_treemap()

    # 创建本地ai记忆库，每次喂给ai

    # 3. AI 分析 (可选)
    analyst = AIAnalyst()
    ai_review = analyst.get_market_review(market_data)

    # 4. 渲染 Markdown
    with open('templates/report_template.md', 'r', encoding='utf-8') as f:
        tmpl = Template(f.read())
    
    final_report = tmpl.render(
        date=market_data['date'],
        up=market_data['up'],
        down=market_data['down'],
        volume=market_data['volume'],
        #chart_html=chart_html,
        #ai_review=ai_review
    )

    # 5. 保存结果
    with open(f"output/report_{market_data['date']}.md", 'w', encoding='utf-8') as f:
        f.write(final_report)
    
    print(f"✅ 日报已生成：output/report_{market_data['date']}.md")

if __name__ == "__main__":
    main()
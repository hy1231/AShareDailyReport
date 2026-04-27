import pandas as pd
import plotly.express as px

class Visualizer:
    @staticmethod
    def generate_industry_treemap(industry_data):
        """
        生成行业板块涨跌热力图
        :param industry_data: List[dict]，由 DataCollector.get_top_industries() 返回
        :return: plotly.graph_objects.Figure 对象，失败则返回 None
        """
        if not industry_data:
            print("⚠️ [Visualizer] 收到空数据，跳过热力图生成。")
            return None

        # 1. 转换为 DataFrame
        df = pd.DataFrame(industry_data)

        # 2. 核心字段校验与清洗
        required_cols = ['行业名称', '涨跌幅', '成交额']
        for col in required_cols:
            if col not in df.columns:
                print(f"❌ [Visualizer] 缺少必要列: {col}")
                return None

        # 3. 绘图参数设置
        fig = px.treemap(
            df,
            path=[px.Constant("A股行业分布"), '行业名称'],
            values='成交额',
            color='涨跌幅',
            # 经典的绿-白-红配色
            color_continuous_scale=['#52c41a', '#f5f5f5', '#ff4d4f'],
            color_continuous_midpoint=0,
            range_color=[-5, 5],
            hover_data={
                '行业名称': True,
                '涨跌幅': ':.2f%',
                '成交额': ':.2f亿',
                '领涨股票': True 
            }
        )

        # 4. 样式美化
        fig.update_layout(
            margin=dict(t=30, l=10, r=10, b=10),
            height=600,
            title_text="今日行业板块资金流向与涨幅分布 (49个一级分类)"
        )
        
        # 5. 直接返回 fig 对象
        # 调用方可以根据需要执行 fig.to_html() 或 fig.write_image()
        return fig
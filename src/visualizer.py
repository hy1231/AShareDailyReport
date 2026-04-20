import plotly.express as px
import plotly.graph_objects as go

class Visualizer:
    @staticmethod
    def generate_industry_treemap():
        """生成板块涨跌热力图"""
        df = ef.stock.get_realtime_quotes('沪深A股')
        # 转换数据类型
        df['涨跌幅'] = pd.to_numeric(df['涨跌幅'], errors='coerce')
        df['成交额'] = pd.to_numeric(df['成交额'], errors='coerce')
        df = df.dropna(subset=['涨跌幅', '所属板块'])

        fig = px.treemap(
            df,
            path=['所属板块', '股票名称'],
            values='成交额',
            color='涨跌幅',
            color_continuous_scale=['#52c41a', '#ffffff', '#ff4d4f'],
            color_continuous_midpoint=0,
            range_color=[-7, 7] # 限制颜色极值，防止个别妖股拉偏色阶
        )
        
        fig.update_layout(margin=dict(t=0, l=0, r=0, b=0))
        # 导出为 HTML 片段
        return fig.to_html(full_html=False, include_plotlyjs='cdn')
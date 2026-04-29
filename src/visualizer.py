import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

class Visualizer:
    @staticmethod
    def generate_industry_treemap(industry_data):
        """
        生成针对公众号优化的高清行业热力图
        修复内容：NaN% 显示 bug、文字模糊、配色对比度
        """
        if not industry_data:
            print("⚠️ [Visualizer] 收到空数据，跳过热力图生成。")
            return None

        # 1. 转换为 DataFrame
        df = pd.DataFrame(industry_data)

        # 2. 【核心修复】数据清洗：强制转为数字并填充空值
        # 即使 dtype 是 float64，fillna(0) 也能解决根节点或异常行导致的 NaN 问题
        df['涨跌幅'] = pd.to_numeric(df['涨跌幅'], errors='coerce').fillna(0.0)
        df['成交额'] = pd.to_numeric(df['成交额'], errors='coerce').fillna(0.0)

        # 3. 绘图参数设置
        fig = px.treemap(
            df,
            path=[px.Constant("A股行业分布"), '行业名称'],
            values='成交额',
            color='涨跌幅',
            # 强化配色：深绿 - 纯白 - 深红
            color_continuous_scale=['#237804', '#ffffff', '#cf1322'], 
            color_continuous_midpoint=0,
            range_color=[-4, 4],
            # 将涨跌幅放入 custom_data，这是解决 NaN% 显示的关键保险
            custom_data=['涨跌幅'] 
        )

        # 4. 公众号视觉优化（高清布局）
        fig.update_layout(
            width=1000,    # 固定宽度，确保文字比例一致
            height=800,
            margin=dict(t=80, l=20, r=20, b=20),
            title_text="今日行业板块资金流向与涨幅分布",
            title_font=dict(size=28, family="SimHei", color="black"),
            # 设置全局字体为黑体，加粗感更强
            font=dict(size=20, family="SimHei", color="black"),
            # 优化右侧色标条
            coloraxis_colorbar=dict(
                title="涨跌幅 (%)",
                thicknessmode="pixels", thickness=20,
                lenmode="pixels", len=400
            )
        )

        # 5. 【核心修复】强制显示加粗文字，并从 custom_data 取值避开 NaN
        fig.update_traces(
            texttemplate="<b>%{label}</b><br>%{customdata[0]:.2f}%",
            textfont=dict(size=22),
            marker_line_width=2,
            selector=dict(type='treemap')
        )

        return fig

    @staticmethod
    def generate_line_chart(data, title, color="#cf1322"):
        rgb = tuple(int(color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
        fill_color = f"rgba{rgb + (0.1,)}"

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=data.index,
            y=data['Close'],
            mode='lines',
            line=dict(color=color, width=4),
            fill='tozeroy',
            fillcolor=fill_color
        ))

        fig.update_layout(
            title=title,
            width=1000,
            height=400,
            template="plotly_white",
            margin=dict(t=60, l=50, r=20, b=40),
            font=dict(family="SimHei", size=18),
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=True, gridcolor="#f0f0f0")
        )
        return fig
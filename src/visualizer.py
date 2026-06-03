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

        # 计算 Y 轴范围，放大波动幅度（关键！）
        close_min = data['Close'].min()
        close_max = data['Close'].max()
        # 添加 10% 的边距，确保趋势清晰可见
        range_padding = (close_max - close_min) * 0.1 if close_max > close_min else 0.01
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=data.index,
            y=data['Close'],
            mode='lines',
            line=dict(color=color, width=4),
            fill='none'
        ))

        fig.update_layout(
            title=title,
            width=1000,
            height=400,
            template="plotly_white",
            margin=dict(t=60, l=50, r=20, b=40),
            font=dict(family="SimHei", size=18),
            xaxis=dict(showgrid=False),
            yaxis=dict(
                showgrid=True,
                gridcolor="#f0f0f0",
                tickformat=".4f",
                # 手动设置 Y 轴范围，只显示数据附近的区域
                range=[close_min - range_padding, close_max + range_padding]
            )
        )
        return fig

    @staticmethod
    def generate_fund_flow_chart(df):
        """
        根据分时数据，生成类似 image_10cf9d.png 的全市场资金流向图
        假设 df 包含列：'时间' (09:30-15:00), '机构', '主力', '大户', '散户'
        数据的数值单位通常为"元"，在画图时转换成"亿元"
        """
        if df is None or df.empty:
            print("⚠️ [Visualizer] 资金流向数据为空，跳过图表生成。")
            return None

        fig = go.Figure()

        # 1. 定义配色（尽量对齐 image_10cf9d.png 的视觉）
        colors = {
            '机构': '#ff4d4f',  # 红色 - 超大单
            '主力': '#ffec3d',  # 黄色 - 大单
            '大户': '#13c2c2',  # 青蓝色 - 中单
            '散户': '#73d13d'   # 绿色 - 小单
        }

        # 2. 添加 4 条资金流向曲线
        for role in ['机构', '主力', '大户', '散户']:
            if role in df.columns:
                fig.add_trace(go.Scatter(
                    x=df['时间'],
                    y=df[role],  # 已经在 collector 中转换为亿元
                    mode='lines',
                    name=f"{role}",
                    line=dict(color=colors[role], width=3),
                    hovertemplate='%{x}<br>' + role + ': %{y:.1f}亿<extra></extra>',
                    fill='none'
                ))

        # 3. 完美复刻暗黑主题样式
        fig.update_layout(
            title=dict(
                text="<b>全市场资金流向动态走势 (亿元)</b>",
                font=dict(color='#ffffff', size=18, family="SimHei"),
                x=0.5,
                y=0.95
            ),
            paper_bgcolor='#141414',  # 深色背景
            plot_bgcolor='#141414',
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1,
                font=dict(color='#ffffff', size=14),
                bgcolor='rgba(0,0,0,0)'
            ),
            xaxis=dict(
                gridcolor='#262626',
                tickcolor='#8c8c8c',
                tickfont=dict(color='#ffffff', size=12),
                title=dict(
                    text='时间',
                    font=dict(color='#8c8c8c')
                ),
                # 强制显示关键时间节点
                tickmode='array',
                tickvals=['09:30', '10:30', '11:30', '13:00', '14:00', '15:00']
            ),
            yaxis=dict(
                gridcolor='#262626',
                tickfont=dict(color='#ffffff', size=12),
                title=dict(
                    text='净流入 (亿元)',
                    font=dict(color='#8c8c8c')
                ),
                zerolinecolor='#595959',
                tickformat='.0f'
            ),
            margin=dict(l=60, r=30, t=80, b=50)
        )

        # 4. 仿照图片，在中午休盘 13:00 处加一条垂直虚线
        fig.add_vline(x='13:00', line_width=2, line_dash="dash", line_color="#8c8c8c")

        # 5. 添加最终数值标注（显示在图例旁边）
        final_values = []
        for role in ['机构', '主力', '大户', '散户']:
            if role in df.columns and len(df[role]) > 0:
                final_val = df[role].iloc[-1]
                final_values.append(f"{role}: {final_val:.1f}亿")
        
        # 在图表上方添加最终数值
        fig.add_annotation(
            x=0.02,
            y=0.92,
            xref='paper',
            yref='paper',
            text=' | '.join(final_values),
            showarrow=False,
            font=dict(color='#ffffff', size=12),
            align='left'
        )

        return fig
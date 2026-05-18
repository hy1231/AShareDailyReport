# A股每日复盘自动生成系统

基于 AkShare + Gemini AI 的 A股市场每日复盘报告自动生成工具。

## 功能特性

- **数据采集**：通过 AkShare 获取全市场 A股实时行情和行业板块数据
- **宏观数据**：支持布伦特原油（yfinance）、美元兑离岸人民币汇率（新浪财经）趋势分析
- **AI 分析**：调用 Google Gemini 生成专业市场复盘
- **可视化**：行业热力图（Treemap）+ 宏观走势图
- **报告生成**：Markdown 格式日报，自动渲染

## 效果展示
![行业热力图示例](assets/1.png)
![汇率走势图](assets/2.png)
![原油走势图](assets/3.png)
![AI复盘示例](assets/4.png)

## 目录结构

```
AShareDailyReport/
├── main.py                 # 主入口
├── src/
│   ├── collector.py       # 数据采集（AkShare + yfinance + 新浪财经）
│   ├── analyst.py          # AI 分析（Gemini）
│   ├── visualizer.py       # 图表生成（Plotly）
│   └── settings.py         # 配置管理
├── templates/
│   └── report_template.md  # 报告模板
├── tests/                  # 测试脚本
├── data/cache/             # 数据缓存目录
└── requirements.txt       # 依赖列表
```

## 环境配置

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

复制 `.env.example` 为 `.env`，并填入你的配置：

```bash
cp .env.example .env
```

编辑 `.env` 文件：

```env
GOOGLE_API_KEY=your-google-api-key-here
GOOGLE_MODEL_ID=gemini-2.0-flash
GEMINI_PROXY=http://127.0.0.1:7890
```

## 使用方法

### 运行主程序

```bash
python main.py
```

生成的报告保存在 `output/A股深度复盘_{日期}.md`

### 运行测试

```bash
# 测试汇率接口
python tests/investpy_forex_test.py
```

## 数据缓存

数据按日期分类存储在 `data/cache/{日期}/` 目录下：

| 文件 | 说明 |
|------|------|
| `raw_market.csv` | 市场原始数据 |
| `raw_industries.csv` | 行业板块数据 |
| `fx_data.csv` | 汇率数据 |
| `oil_data.csv` | 原油数据 |
| `hotmap.png` | 行业热力图 |
| `fx.png` | 汇率走势图 |
| `oil.png` | 原油走势图 |

## 数据来源

| 数据类型 | 数据源 | 说明 |
|----------|--------|------|
| A股行情 | AkShare (东方财富) | 全市场实时行情 |
| 行业板块 | AkShare (东方财富) | 行业板块资金分布 |
| 布伦特原油 | yfinance (Yahoo Finance) | BZ=F 连续合约 |
| 离岸人民币 | 新浪财经 | USD/CNH 日K线 |
| AI 分析 | Google Gemini | 专业市场复盘 |

## 报告模板

编辑 `templates/report_template.md` 可自定义报告格式。

## 依赖列表

- `google-genai` - Gemini API
- `akshare` - A股和行业数据源
- `yfinance` - 原油数据源
- `investpy` - 汇率数据源（备选）
- `requests` - HTTP 请求
- `pandas` - 数据处理
- `plotly` - 数据可视化
- `jinja2` - 模板渲染
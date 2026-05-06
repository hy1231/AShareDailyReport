# A股每日复盘自动生成系统

基于 AkShare + Gemini AI 的 A股市场每日复盘报告自动生成工具。

## 功能特性

- **数据采集**：通过 AkShare 获取全市场 A股实时行情和行业板块数据
- **宏观数据**：支持布伦特原油、美元兑离岸人民币汇率趋势分析
- **AI 分析**：调用 Google Gemini 生成专业市场复盘
- **可视化**：行业热力图（Treemap）+ 宏观走势图
- **报告生成**：Markdown 格式日报，自动渲染

## 目录结构

```
AShareDailyReport/
├── main.py                 # 主入口
├── src/
│   ├── collector.py       # 数据采集（AkShare + yfinance）
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

生成的报告保存在 `output/{日期}_daily_report.md`

### 运行测试

```bash
# 测试汇率数据接口
python tests/akshare_forex_test.py

# 测试 AkShare 接口
python tests/akshare_test.py

# 测试 yfinance 汇率接口
python tests/yfinance_cnh_test.py
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
| `ai_review.txt` | AI 复盘缓存 |

## 报告模板

编辑 `templates/report_template.md` 可自定义报告格式。

## 依赖列表

- `google-genai` - Gemini API
- `akshare` - 金融数据源
- `yfinance` - 全球市场数据
- `pandas` - 数据处理
- `plotly` - 数据可视化
- `jinja2` - 模板渲染
- `requests` - HTTP 请求
# 📈 A-Canvas 每日市场看板 | {{ date }}

## 🌡️ 市场温度
- **上涨/下跌：** <span style="color:red">{{ up }}</span> / <span style="color:green">{{ down }}</span>
- **全天成交：** `{{ volume }} 亿`
- **赚钱效应：** {{ "极佳" if up > down * 2 else "一般" }}

---

## 🗺️ 板块资金流向 (交互式)
{{ chart_html }}

---

## 🤖 AI 深度复盘
{{ ai_review }}

---

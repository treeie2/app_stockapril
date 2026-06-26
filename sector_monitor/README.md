# A股板块资金流入监控

基于 Python + Streamlit + AKShare + ECharts 的板块资金流向监控工具。

## 安装

```bash
cd sector_monitor
pip install -r requirements.txt
```

## 启动

```bash
streamlit run app.py
```

默认端口 8501，浏览器打开 http://localhost:8501

## 功能

- 实时展示 8 大热门板块当日主力资金流入/流出
- 折线图（盘中轮询快照累积走势）+ 柱状图（净流入/流出对比）
- 每 5 分钟自动刷新，支持手动刷新
- 数据缓存容错（请求失败回退到本地缓存）
- 深色专业金融界面

## 数据来源

AKShare → 东方财富板块资金流排名

## 默认监控板块

芯片 / 光伏 / 储能 / AI / 新能源车 / 医疗 / 银行 / 军工

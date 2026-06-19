FROM python:3.9-slim

WORKDIR /app

# 安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目文件
COPY . .
RUN mkdir -p data_cache

# 暴露端口 (7860=Flask, 8501=Streamlit)
EXPOSE 7860 8501

# 启动命令：同时运行 Flask 和 Streamlit
CMD python -m streamlit run sector_monitor/app.py --server.port=8501 --server.headless=true & python main.py

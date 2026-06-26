# Cloudflare R2 同步专用 Docker 镜像
# 使用 Python 3.11 + 更新 OpenSSL 避免 SSL 问题

FROM python:3.11-bookworm

# 安装更新的 OpenSSL 和 CA 证书
RUN apt-get update && apt-get install -y \
    openssl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# 设置工作目录
WORKDIR /app

# 安装 Python 依赖
RUN pip install --no-cache-dir boto3 python-dotenv

# 复制同步脚本
COPY scripts/sync_to_r2.py /app/scripts/
COPY config.json /app/

# 创建 raw_material 目录
RUN mkdir -p /app/raw_material

# 设置环境变量
ENV PYTHONUNBUFFERED=1
ENV R2_CONFIG_PATH=/app/config.json
ENV SSL_CERT_FILE=/etc/ssl/certs/ca-certificates.crt
ENV REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt

# 入口点
ENTRYPOINT ["python", "/app/scripts/sync_to_r2.py"]
CMD ["--mode", "list"]

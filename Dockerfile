# 使用 Python 3.11 官方鏡像
FROM python:3.11-slim

# 設置工作目錄
WORKDIR /app

# 設置環境變數
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

# 安裝系統依賴
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 複製 requirements.txt 並安裝 Python 依賴
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 複製應用程式代碼
COPY . .

# 複製健康檢查腳本和啟動腳本
COPY health-check.sh /usr/local/bin/health-check.sh
COPY docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh
RUN chmod +x /usr/local/bin/health-check.sh /usr/local/bin/docker-entrypoint.sh

# 創建日誌目錄
RUN mkdir -p /app/logs

# 創建非 root 用戶（但先保持 root 權限執行初始化）
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app

# 暴露端口
EXPOSE 8000

# 健康檢查
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD /usr/local/bin/health-check.sh

# 默認啟動命令（將在腳本內切換到 appuser）
CMD ["/usr/local/bin/docker-entrypoint.sh"]

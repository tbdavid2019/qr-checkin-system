#!/bin/bash
# Docker 容器健康檢查腳本

# 檢查 API 服務健康狀態
check_api_health() {
    local max_attempts=3
    local attempt=0
    
    while [ $attempt -lt $max_attempts ]; do
        if curl -f -s http://localhost:8000/health > /dev/null; then
            return 0
        fi
        attempt=$((attempt + 1))
        sleep 1
    done
    return 1
}

# 檢查資料庫連接
check_database() {
    python3 -c "
import os
import sys
from sqlalchemy import create_engine, text

try:
    engine = create_engine(os.getenv('DATABASE_URL'))
    with engine.connect() as conn:
        result = conn.execute(text('SELECT 1'))
        sys.exit(0)
except Exception as e:
    print(f'Database check failed: {e}')
    sys.exit(1)
"
}

# 主健康檢查
main() {
    # 檢查 API 健康狀態
    if ! check_api_health; then
        echo "API health check failed"
        exit 1
    fi
    
    # 如果是 API 容器，也檢查資料庫連接
    if [ -f "/app/app/main.py" ]; then
        if ! check_database; then
            echo "Database connectivity check failed"
            exit 1
        fi
    fi
    
    echo "Health check passed"
    exit 0
}

main "$@"

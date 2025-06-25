#!/bin/bash
set -e

echo "🚀 Starting QR Check-in System initialization..."

# 等待資料庫準備就緒
echo "⏳ Waiting for database to be ready..."
while ! pg_isready -h db -p 5432 -U qr_admin -d qr_system; do
    echo "Database is not ready yet. Waiting..."
    sleep 2
done
echo "✅ Database is ready!"

# 執行 Alembic migration
echo "📊 Running database migrations..."
alembic upgrade head
echo "✅ Database migrations completed!"

# 檢查是否需要建立示範資料
echo "🔍 Checking if demo data exists..."
MERCHANT_COUNT=$(python -c "
import sys
sys.path.append('/app')
from app.database import get_db
from models.merchant import Merchant
db = next(get_db())
count = db.query(Merchant).count()
db.close()
print(count)
")

if [ "$MERCHANT_COUNT" -eq "0" ]; then
    echo "📋 No demo data found. Creating demo data..."
    python setup_multi_tenant.py
    echo "✅ Demo data created!"
else
    echo "✅ Demo data already exists (found $MERCHANT_COUNT merchants)"
fi

echo "🎉 Initialization completed! Starting API server..."

# 切換到非 root 用戶並啟動 API 服務
exec su appuser -c "uvicorn app.main:app --host 0.0.0.0 --port 8000 --access-log"

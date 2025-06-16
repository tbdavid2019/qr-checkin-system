#!/bin/bash
# AWS Linux 部署腳本
# 使用方法: chmod +x deploy_aws.sh && ./deploy_aws.sh

echo "🚀 QR Check-in System AWS Linux 部署腳本"
echo "================================================"

# 檢查是否為 root 用戶
if [ "$EUID" -eq 0 ]; then
    echo "❌ 請不要使用 root 用戶運行此腳本"
    exit 1
fi

# 1. 配置環境文件
echo "📝 配置環境文件..."
if [ ! -f .env ]; then
    cp .env.template .env
    echo "✅ 已創建 .env 文件"
    echo "⚠️  請編輯 .env 文件設置您的配置"
else
    echo "✅ .env 文件已存在"
fi

if [ ! -f alembic.ini ]; then
    cp alembic.ini.template alembic.ini
    echo "✅ 已創建 alembic.ini 文件"
else
    echo "✅ alembic.ini 文件已存在"
fi

# 2. 設置默認配置
echo "🔧 設置默認配置..."
cat > .env << EOF
# QR Check-in System AWS Linux 配置

# 資料庫配置
DATABASE_URL=postgresql://qr_admin:qr_pass@localhost:5432/qr_system

# JWT 配置  
SECRET_KEY=aws-production-secret-key-$(openssl rand -hex 16)
ACCESS_TOKEN_EXPIRE_MINUTES=43200

# API 配置 (單租戶模式使用)
API_KEY=aws-api-key-$(openssl rand -hex 8)

# 多租戶功能 (1=啟用, 0=停用)
ENABLE_MULTI_TENANT=1

# Gradio 管理介面配置
ADMIN_PASSWORD=admin-$(openssl rand -hex 4)
GRADIO_PORT=7860

# QR Code 配置
QR_TOKEN_EXPIRE_HOURS=168

# 服務設定
DEBUG=False
ENVIRONMENT=production
EOF

# 3. 設置 alembic.ini
sed -i 's/postgresql:\/\/DB_USER:DB_PASSWORD@DB_HOST:DB_PORT\/DB_NAME/postgresql:\/\/qr_admin:qr_pass@localhost:5432\/qr_system/' alembic.ini

echo "✅ 配置文件已設置完成"

# 4. 檢查 Docker 和 PostgreSQL
echo "🐳 檢查 Docker 服務..."
if ! docker --version > /dev/null 2>&1; then
    echo "❌ Docker 未安裝或未運行"
    exit 1
fi

echo "🗄️  啟動 PostgreSQL..."
docker-compose up -d

# 等待 PostgreSQL 啟動
echo "⏳ 等待 PostgreSQL 啟動..."
sleep 10

# 檢查 PostgreSQL 連接
echo "🔗 測試資料庫連接..."
if docker-compose exec -T db psql -U qr_admin -d qr_system -c "SELECT 1;" > /dev/null 2>&1; then
    echo "✅ PostgreSQL 連接成功"
else
    echo "❌ PostgreSQL 連接失敗，請檢查容器狀態"
    docker-compose logs db
    exit 1
fi

# 5. 運行資料庫遷移
echo "📊 運行資料庫遷移..."
if [ -f "myenv/bin/activate" ]; then
    source myenv/bin/activate
fi

alembic upgrade head
if [ $? -eq 0 ]; then
    echo "✅ 資料庫遷移完成"
else
    echo "❌ 資料庫遷移失敗"
    exit 1
fi

# 6. 設置多租戶示例數據
echo "🏢 設置多租戶示例數據..."
python setup_multi_tenant.py

# 7. 顯示配置信息
echo ""
echo "🎉 部署完成！"
echo "================================================"
echo "📋 系統配置信息："
echo "   - 資料庫: PostgreSQL (Docker)"
echo "   - 多租戶模式: 已啟用"
echo "   - API 端口: 8000"
echo "   - 管理介面端口: 7860"
echo ""
echo "🔑 重要信息："
grep "API_KEY=" .env
grep "ADMIN_PASSWORD=" .env
echo ""
echo "🚀 啟動命令："
echo "   # 啟動 API 服務"
echo "   uvicorn app.main:app --host 0.0.0.0 --port 8000"
echo ""
echo "   # 啟動管理介面"
echo "   python gradio_admin.py"
echo ""
echo "🌐 訪問地址："
echo "   - API 文檔: http://your-server-ip:8000/docs"
echo "   - 管理介面: http://your-server-ip:7860"
echo "   - 健康檢查: http://your-server-ip:8000/health"
echo ""
echo "🧪 測試系統："
echo "   python test_multi_tenant.py"
echo ""
echo "📚 更多文檔請查看 README.md 和 MULTI_TENANT_REPORT.md"

#!/bin/bash

# QR Check-in System 多租戶模式啟動腳本

echo "🚀 QR Check-in System 多租戶模式啟動"
echo "=================================="

# 檢查虛擬環境
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "⚠️  請先啟動虛擬環境："
    echo "   source myenv/bin/activate"
    exit 1
fi

# 檢查 .env 文件
if [ ! -f ".env" ]; then
    echo "📝 創建 .env 配置文件..."
    cp .env.template .env
    echo "✅ .env 文件已創建，請檢查配置"
else
    echo "✅ .env 配置文件存在"
fi

# 檢查資料庫連接
echo "🔍 檢查資料庫連接..."
python -c "
from app.database import get_db
try:
    db = next(get_db())
    print('✅ 資料庫連接成功')
    db.close()
except Exception as e:
    print(f'❌ 資料庫連接失敗: {e}')
    exit(1)
"

# 運行資料庫遷移
echo "📊 更新資料庫架構..."
alembic upgrade head

# 設置多租戶示例數據
echo "🏢 設置多租戶示例數據..."
python setup_multi_tenant.py

echo ""
echo "🎉 多租戶系統設置完成！"
echo ""
echo "📖 使用指南："
echo "1. 啟動API服務："
echo "   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
echo ""
echo "2. 訪問API文檔："
echo "   http://localhost:8000/docs"
echo ""
echo "3. 運行多租戶測試："
echo "   python test_multi_tenant.py"
echo ""
echo "4. 查看可用的API Keys："
echo "   詳見 setup_multi_tenant.py 輸出"
echo ""
echo "📋 系統狀態："
echo "   - 多租戶模式: 已啟用"
echo "   - 管理員密碼: admin123 (可在 .env 修改)"
echo "   - API文檔: http://localhost:8000/docs"
echo ""

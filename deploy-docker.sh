#!/bin/bash
# QR Check-in System Docker 快速部署腳本

set -e  # 遇到錯誤立即退出

# 顏色輸出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 輸出函數
info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 檢查系統要求
check_requirements() {
    info "檢查系統要求..."
    
    # 檢查 Docker
    if ! command -v docker &> /dev/null; then
        error "Docker 未安裝，請先安裝 Docker"
        exit 1
    fi
    
    # 檢查 Docker Compose
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        error "Docker Compose 未安裝，請先安裝 Docker Compose"
        exit 1
    fi
    
    # 檢查 Docker 服務
    if ! docker info &> /dev/null; then
        error "Docker 服務未運行，請啟動 Docker 服務"
        exit 1
    fi
    
    success "系統要求檢查通過"
}

# 生成安全密鑰
generate_secrets() {
    info "生成安全密鑰..."
    
    if command -v openssl &> /dev/null; then
        SECRET_KEY=$(openssl rand -hex 32)
        API_KEY=$(openssl rand -hex 16)
        success "安全密鑰生成完成"
    else
        warning "OpenSSL 未安裝，將使用預設密鑰（生產環境請手動修改）"
        SECRET_KEY="docker-production-secret-key-change-in-production"
        API_KEY="docker-api-key-change-in-production"
    fi
}

# 配置環境文件
setup_env() {
    info "配置環境文件..."
    
    if [ ! -f .env ]; then
        if [ -f .env.production ]; then
            cp .env.production .env
            info "已複製 .env.production 為 .env"
        elif [ -f .env.template ]; then
            cp .env.template .env
            info "已複製 .env.template 為 .env"
        else
            warning "未找到環境配置模板，創建基本配置文件"
            cat > .env << EOF
DATABASE_URL=postgresql://qr_admin:qr_pass@db:5432/qr_system
ENABLE_MULTI_TENANT=1
SECRET_KEY=${SECRET_KEY}
API_KEY=${API_KEY}
ADMIN_PASSWORD=admin123
DEBUG=False
ENVIRONMENT=production
EOF
        fi
        
        # 更新密鑰
        sed -i.bak "s/SECRET_KEY=.*/SECRET_KEY=${SECRET_KEY}/" .env
        sed -i.bak "s/API_KEY=.*/API_KEY=${API_KEY}/" .env
        rm -f .env.bak
        
        success "環境配置文件設置完成"
    else
        info "環境配置文件已存在，跳過設置"
    fi
}

# 創建必要目錄
create_directories() {
    info "創建必要目錄..."
    
    mkdir -p logs
    mkdir -p backups
    mkdir -p init-db
    
    # 設置日誌目錄權限
    chmod 755 logs backups
    
    success "目錄創建完成"
}

# 部署服務
deploy_services() {
    info "開始部署 Docker 服務..."
    
    # 停止現有服務
    if docker-compose ps | grep -q "Up"; then
        warning "檢測到正在運行的服務，正在停止..."
        docker-compose down
    fi
    
    # 構建並啟動服務
    info "構建 Docker 映像..."
    docker-compose build --no-cache
    
    info "啟動服務..."
    docker-compose up -d
    
    success "服務部署完成"
}

# 等待服務就緒
wait_for_services() {
    info "等待服務啟動..."
    
    # 等待資料庫就緒
    info "等待資料庫啟動..."
    timeout=60
    while [ $timeout -gt 0 ]; do
        if docker-compose exec -T db pg_isready -U qr_admin -d qr_system &>/dev/null; then
            success "資料庫已就緒"
            break
        fi
        sleep 2
        timeout=$((timeout-2))
    done
    
    if [ $timeout -le 0 ]; then
        error "資料庫啟動超時"
        exit 1
    fi
    
    # 等待 API 服務就緒
    info "等待 API 服務啟動..."
    timeout=120
    while [ $timeout -gt 0 ]; do
        if curl -f http://localhost:8000/health &>/dev/null; then
            success "API 服務已就緒"
            break
        fi
        sleep 3
        timeout=$((timeout-3))
    done
    
    if [ $timeout -le 0 ]; then
        error "API 服務啟動超時"
        docker-compose logs api
        exit 1
    fi
    
    # 等待 Gradio 服務就緒
    info "等待管理介面啟動..."
    timeout=60
    while [ $timeout -gt 0 ]; do
        if curl -f http://localhost:7860 &>/dev/null; then
            success "管理介面已就緒"
            break
        fi
        sleep 3
        timeout=$((timeout-3))
    done
    
    if [ $timeout -le 0 ]; then
        warning "管理介面啟動超時，但不影響核心功能"
    fi
}

# 驗證部署
verify_deployment() {
    info "驗證部署..."
    
    # 檢查服務狀態
    info "檢查服務狀態..."
    docker-compose ps
    
    # 測試 API 健康檢查
    if curl -f http://localhost:8000/health &>/dev/null; then
        success "API 健康檢查通過"
    else
        error "API 健康檢查失敗"
        exit 1
    fi
    
    # 測試資料庫連接
    if docker-compose exec -T db psql -U qr_admin -d qr_system -c "SELECT 1;" &>/dev/null; then
        success "資料庫連接測試通過"
    else
        error "資料庫連接測試失敗"
        exit 1
    fi
    
    # 運行多租戶測試（如果測試文件存在）
    if [ -f "test_multi_tenant.py" ]; then
        info "運行多租戶功能測試..."
        if python test_multi_tenant.py; then
            success "多租戶功能測試通過"
        else
            warning "多租戶功能測試失敗，請檢查日誌"
        fi
    fi
}

# 顯示部署信息
show_deployment_info() {
    echo ""
    echo "=========================================="
    echo "🎉 QR Check-in System 部署完成！"
    echo "=========================================="
    echo ""
    echo "📍 服務訪問地址："
    echo "  - API 服務:     http://localhost:8000"
    echo "  - API 文檔:     http://localhost:8000/docs"
    echo "  - 管理介面:     http://localhost:7860"
    echo "  - 健康檢查:     http://localhost:8000/health"
    echo ""
    echo "🔐 預設管理員帳號："
    echo "  - 密碼: admin123 (請儘快修改)"
    echo ""
    echo "📊 有用的指令："
    echo "  - 查看服務狀態: docker-compose ps"
    echo "  - 查看日誌:     docker-compose logs -f"
    echo "  - 停止服務:     docker-compose down"
    echo "  - 重啟服務:     docker-compose restart"
    echo ""
    echo "📁 重要文件："
    echo "  - 環境配置:     .env"
    echo "  - 應用日誌:     logs/"
    echo "  - 資料備份:     backups/"
    echo ""
    echo "⚠️  安全提醒："
    echo "  - 請修改 .env 中的預設密碼"
    echo "  - 生產環境請使用 HTTPS"
    echo "  - 定期備份資料庫"
    echo ""
    echo "📚 更多信息請查看："
    echo "  - Docker 部署指南: DOCKER_DEPLOYMENT.md"
    echo "  - 系統說明文檔:   README.md"
    echo ""
}

# 主函數
main() {
    echo "🐳 QR Check-in System Docker 快速部署"
    echo "========================================"
    echo ""
    
    # 執行部署步驟
    check_requirements
    generate_secrets
    setup_env
    create_directories
    deploy_services
    wait_for_services
    verify_deployment
    show_deployment_info
    
    success "部署流程完成！"
}

# 處理中斷信號
trap 'error "部署被中斷"; exit 1' INT TERM

# 執行主函數
main "$@"

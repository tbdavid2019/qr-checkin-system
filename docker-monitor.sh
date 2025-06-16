#!/bin/bash
# Docker 服務監控腳本

set -e

# 顏色輸出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

info() { echo -e "${BLUE}[INFO]${NC} $1"; }
success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; }

# 檢查服務狀態
check_services() {
    info "檢查 Docker 服務狀態..."
    echo ""
    
    # 獲取服務狀態
    docker-compose ps --format "table {{.Name}}\t{{.Status}}\t{{.Ports}}"
    echo ""
    
    # 檢查關鍵服務
    local services=("db" "api" "gradio")
    local all_healthy=true
    
    for service in "${services[@]}"; do
        local status=$(docker-compose ps -q $service | xargs docker inspect --format='{{.State.Health.Status}}' 2>/dev/null || echo "no-health-check")
        local running=$(docker-compose ps -q $service | xargs docker inspect --format='{{.State.Running}}' 2>/dev/null || echo "false")
        
        if [ "$running" = "true" ]; then
            if [ "$status" = "healthy" ] || [ "$status" = "no-health-check" ]; then
                success "$service 服務運行正常"
            else
                warning "$service 服務運行但健康檢查失敗 (狀態: $status)"
                all_healthy=false
            fi
        else
            error "$service 服務未運行"
            all_healthy=false
        fi
    done
    
    return $([[ "$all_healthy" = true ]] && echo 0 || echo 1)
}

# 檢查資源使用情況
check_resources() {
    info "檢查資源使用情況..."
    echo ""
    
    # Docker 統計信息
    docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}\t{{.NetIO}}"
    echo ""
}

# 檢查日誌
check_logs() {
    info "檢查最近的錯誤日誌..."
    echo ""
    
    # 檢查 API 服務日誌中的錯誤
    local api_errors=$(docker-compose logs --tail=100 api 2>/dev/null | grep -i "error\|exception\|failed" | tail -5)
    if [ -n "$api_errors" ]; then
        warning "API 服務最近的錯誤："
        echo "$api_errors"
        echo ""
    else
        success "API 服務日誌正常"
    fi
    
    # 檢查資料庫日誌中的錯誤
    local db_errors=$(docker-compose logs --tail=100 db 2>/dev/null | grep -i "error\|fatal" | tail -5)
    if [ -n "$db_errors" ]; then
        warning "資料庫最近的錯誤："
        echo "$db_errors"
        echo ""
    else
        success "資料庫日誌正常"
    fi
}

# 執行功能測試
run_functional_tests() {
    info "執行基本功能測試..."
    
    # 測試 API 健康檢查
    if curl -f -s http://localhost:8000/health > /dev/null; then
        success "API 健康檢查通過"
    else
        error "API 健康檢查失敗"
        return 1
    fi
    
    # 測試 API 文檔頁面
    if curl -f -s http://localhost:8000/docs > /dev/null; then
        success "API 文檔頁面可訪問"
    else
        warning "API 文檔頁面無法訪問"
    fi
    
    # 測試 Gradio 介面
    if curl -f -s http://localhost:7860 > /dev/null; then
        success "Gradio 管理介面可訪問"
    else
        warning "Gradio 管理介面無法訪問"
    fi
    
    # 測試資料庫連接
    if docker-compose exec -T db psql -U qr_admin -d qr_system -c "SELECT 1;" > /dev/null 2>&1; then
        success "資料庫連接正常"
    else
        error "資料庫連接失敗"
        return 1
    fi
    
    return 0
}

# 顯示系統信息
show_system_info() {
    info "系統信息："
    echo "  - Docker 版本: $(docker --version)"
    echo "  - Docker Compose 版本: $(docker-compose --version 2>/dev/null || docker compose version)"
    echo "  - 系統時間: $(date)"
    echo "  - 系統負載: $(uptime | awk '{print $10,$11,$12}')"
    echo ""
    
    info "磁碟空間："
    df -h / | tail -1 | awk '{print "  - 根目錄使用率: "$5" (可用: "$4")"}'
    
    # Docker 磁碟使用
    local docker_size=$(docker system df --format "table {{.Type}}\t{{.Size}}" | tail -n +2 | awk '{sum+=$2} END {print sum"B"}' 2>/dev/null || echo "unknown")
    echo "  - Docker 使用空間: $docker_size"
    echo ""
}

# 主監控函數
main() {
    echo "🐳 QR Check-in System Docker 監控報告"
    echo "======================================="
    echo "生成時間: $(date)"
    echo ""
    
    # 檢查 Docker 是否運行
    if ! docker info > /dev/null 2>&1; then
        error "Docker 服務未運行"
        exit 1
    fi
    
    # 檢查 docker-compose 文件是否存在
    if [ ! -f "docker-compose.yml" ]; then
        error "docker-compose.yml 文件不存在"
        exit 1
    fi
    
    # 執行各項檢查
    show_system_info
    check_services
    echo ""
    check_resources
    echo ""
    check_logs
    echo ""
    
    # 執行功能測試
    if run_functional_tests; then
        echo ""
        success "🎉 所有檢查通過，系統運行正常！"
        echo ""
        info "服務訪問地址："
        echo "  - API 服務: http://localhost:8000"
        echo "  - API 文檔: http://localhost:8000/docs"
        echo "  - 管理介面: http://localhost:7860"
        echo ""
    else
        echo ""
        error "⚠️ 檢查發現問題，請查看上述錯誤信息"
        echo ""
        info "故障排除建議："
        echo "  - 查看詳細日誌: docker-compose logs -f"
        echo "  - 重啟服務: docker-compose restart"
        echo "  - 檢查配置: cat .env"
        echo ""
        exit 1
    fi
}

# 處理命令行參數
case "${1:-}" in
    "services")
        check_services
        ;;
    "resources")
        check_resources
        ;;
    "logs")
        check_logs
        ;;
    "test")
        run_functional_tests
        ;;
    "info")
        show_system_info
        ;;
    *)
        main
        ;;
esac

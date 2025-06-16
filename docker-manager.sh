#!/bin/bash
# QR Check-in System Docker 管理工具

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

# 顯示幫助信息
show_help() {
    echo "🐳 QR Check-in System Docker 管理工具"
    echo "======================================"
    echo ""
    echo "使用方式: $0 <命令> [選項]"
    echo ""
    echo "可用命令："
    echo "  start           啟動所有服務"
    echo "  stop            停止所有服務"
    echo "  restart         重啟所有服務"
    echo "  status          查看服務狀態"
    echo "  logs [service]  查看日誌 (可指定服務名稱)"
    echo "  shell <service> 進入服務容器"
    echo "  db              連接資料庫"
    echo "  backup          執行備份"
    echo "  restore <file>  還原備份"
    echo "  monitor         系統監控"
    echo "  update          更新並重新部署"
    echo "  clean           清理 Docker 資源"
    echo "  reset           重置所有數據 (危險操作)"
    echo "  test            執行功能測試"
    echo ""
    echo "範例："
    echo "  $0 start                    # 啟動所有服務"
    echo "  $0 logs api                 # 查看 API 服務日誌"
    echo "  $0 shell api                # 進入 API 容器"
    echo "  $0 backup                   # 執行備份"
    echo "  $0 restore backup.sql.gz    # 還原備份"
    echo ""
}

# 啟動服務
start_services() {
    info "啟動 QR Check-in System 服務..."
    
    if [ ! -f "docker-compose.yml" ]; then
        error "docker-compose.yml 文件不存在"
        exit 1
    fi
    
    # 檢查環境文件
    if [ ! -f ".env" ]; then
        warning "環境文件 .env 不存在，使用預設配置"
        if [ -f ".env.production" ]; then
            cp .env.production .env
            info "已複製 .env.production 為 .env"
        fi
    fi
    
    docker-compose up -d
    success "服務啟動完成"
    
    # 等待服務就緒
    info "等待服務啟動完成..."
    sleep 10
    
    # 檢查健康狀態
    ./docker-monitor.sh services
}

# 停止服務
stop_services() {
    info "停止 QR Check-in System 服務..."
    docker-compose down
    success "服務已停止"
}

# 重啟服務
restart_services() {
    info "重啟 QR Check-in System 服務..."
    docker-compose restart
    success "服務重啟完成"
    
    # 等待服務就緒
    sleep 10
    ./docker-monitor.sh services
}

# 查看服務狀態
show_status() {
    info "服務狀態："
    docker-compose ps
    echo ""
    
    # 顯示健康狀態
    ./docker-monitor.sh services
}

# 查看日誌
show_logs() {
    local service="$1"
    
    if [ -z "$service" ]; then
        info "顯示所有服務日誌 (最近 100 行)..."
        docker-compose logs --tail=100 -f
    else
        info "顯示 $service 服務日誌..."
        docker-compose logs --tail=100 -f "$service"
    fi
}

# 進入容器 shell
enter_shell() {
    local service="$1"
    
    if [ -z "$service" ]; then
        error "請指定服務名稱"
        echo "可用服務: api, gradio, db"
        exit 1
    fi
    
    info "進入 $service 容器..."
    
    case "$service" in
        "db")
            docker-compose exec db bash
            ;;
        "api"|"gradio")
            docker-compose exec "$service" bash
            ;;
        *)
            error "未知服務: $service"
            echo "可用服務: api, gradio, db"
            exit 1
            ;;
    esac
}

# 連接資料庫
connect_database() {
    info "連接到 PostgreSQL 資料庫..."
    
    if ! docker-compose ps db | grep -q "Up"; then
        error "資料庫服務未運行"
        exit 1
    fi
    
    docker-compose exec db psql -U qr_admin -d qr_system
}

# 執行備份
run_backup() {
    info "執行系統備份..."
    ./docker-backup.sh
}

# 還原備份
restore_backup() {
    local backup_file="$1"
    
    if [ -z "$backup_file" ]; then
        error "請指定備份文件"
        echo "使用方式: $0 restore <backup_file.sql.gz>"
        exit 1
    fi
    
    ./docker-backup.sh restore "$backup_file"
}

# 系統監控
run_monitor() {
    ./docker-monitor.sh
}

# 更新系統
update_system() {
    info "更新 QR Check-in System..."
    
    # 備份現有數據
    warning "更新前自動備份..."
    ./docker-backup.sh
    
    # 拉取最新代碼
    if [ -d ".git" ]; then
        info "拉取最新代碼..."
        git pull
    fi
    
    # 重新構建並啟動
    info "重新構建容器..."
    docker-compose build --no-cache
    
    info "重啟服務..."
    docker-compose up -d
    
    # 執行遷移
    info "執行資料庫遷移..."
    docker-compose run --rm migrate alembic upgrade head
    
    success "系統更新完成"
    
    # 檢查健康狀態
    sleep 15
    ./docker-monitor.sh
}

# 清理 Docker 資源
clean_docker() {
    warning "清理 Docker 資源..."
    
    read -p "確定要清理未使用的 Docker 資源嗎？(y/N): " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        info "清理未使用的容器..."
        docker container prune -f
        
        info "清理未使用的映像..."
        docker image prune -f
        
        info "清理未使用的網路..."
        docker network prune -f
        
        info "清理未使用的卷 (保留資料庫卷)..."
        docker volume prune -f --filter "label!=com.docker.compose.project=qr-checkin-system"
        
        success "Docker 資源清理完成"
    else
        info "清理操作已取消"
    fi
}

# 重置系統 (危險操作)
reset_system() {
    error "⚠️  危險操作：重置系統將刪除所有數據！"
    echo ""
    warning "這個操作將："
    echo "  - 停止並刪除所有容器"
    echo "  - 刪除所有數據 (包括資料庫)"
    echo "  - 刪除所有 Docker 卷"
    echo ""
    
    read -p "確定要重置系統嗎？這將無法恢復！(yes/no): " -r
    echo
    
    if [ "$REPLY" = "yes" ]; then
        info "執行系統重置..."
        
        # 停止並刪除所有容器
        docker-compose down -v --remove-orphans
        
        # 刪除映像
        docker-compose down --rmi all
        
        # 刪除 logs 目錄
        rm -rf logs
        
        success "系統重置完成"
        echo ""
        info "重新部署系統："
        echo "  $0 start"
    else
        info "重置操作已取消"
    fi
}

# 執行功能測試
run_tests() {
    info "執行功能測試..."
    
    # 檢查服務是否運行
    if ! docker-compose ps | grep -q "Up"; then
        error "服務未運行，請先啟動服務"
        echo "使用: $0 start"
        exit 1
    fi
    
    # 等待服務就緒
    info "等待服務就緒..."
    sleep 5
    
    # 執行基本健康檢查
    ./docker-monitor.sh test
    
    # 如果存在測試腳本，執行多租戶測試
    if [ -f "test_multi_tenant.py" ]; then
        info "執行多租戶功能測試..."
        python test_multi_tenant.py
    fi
    
    success "功能測試完成"
}

# 主函數
main() {
    local command="$1"
    shift || true
    
    case "$command" in
        "start")
            start_services
            ;;
        "stop")
            stop_services
            ;;
        "restart")
            restart_services
            ;;
        "status")
            show_status
            ;;
        "logs")
            show_logs "$1"
            ;;
        "shell")
            enter_shell "$1"
            ;;
        "db")
            connect_database
            ;;
        "backup")
            run_backup
            ;;
        "restore")
            restore_backup "$1"
            ;;
        "monitor")
            run_monitor
            ;;
        "update")
            update_system
            ;;
        "clean")
            clean_docker
            ;;
        "reset")
            reset_system
            ;;
        "test")
            run_tests
            ;;
        "help"|"-h"|"--help"|"")
            show_help
            ;;
        *)
            error "未知命令: $command"
            echo ""
            show_help
            exit 1
            ;;
    esac
}

# 檢查必要的腳本是否存在
check_dependencies() {
    local missing_deps=()
    
    if [ ! -f "docker-monitor.sh" ]; then
        missing_deps+=("docker-monitor.sh")
    fi
    
    if [ ! -f "docker-backup.sh" ]; then
        missing_deps+=("docker-backup.sh")
    fi
    
    if [ ${#missing_deps[@]} -gt 0 ]; then
        error "缺少必要的腳本文件:"
        for dep in "${missing_deps[@]}"; do
            echo "  - $dep"
        done
        exit 1
    fi
}

# 執行主函數
check_dependencies
main "$@"

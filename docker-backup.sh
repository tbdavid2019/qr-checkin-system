#!/bin/bash
# Docker 環境資料備份腳本

set -e

# 配置
BACKUP_DIR="./backups"
DATE=$(date +%Y%m%d_%H%M%S)
RETENTION_DAYS=7

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

# 創建備份目錄
create_backup_dir() {
    if [ ! -d "$BACKUP_DIR" ]; then
        mkdir -p "$BACKUP_DIR"
        info "創建備份目錄: $BACKUP_DIR"
    fi
}

# 備份資料庫
backup_database() {
    info "開始備份資料庫..."
    
    local backup_file="$BACKUP_DIR/db_backup_$DATE.sql"
    
    # 檢查資料庫容器是否運行
    if ! docker-compose ps db | grep -q "Up"; then
        error "資料庫容器未運行"
        return 1
    fi
    
    # 執行備份
    if docker-compose exec -T db pg_dump -U qr_admin -h localhost -d qr_system > "$backup_file"; then
        success "資料庫備份完成: $backup_file"
        
        # 壓縮備份文件
        gzip "$backup_file"
        success "備份文件已壓縮: ${backup_file}.gz"
        
        # 顯示備份文件大小
        local size=$(du -h "${backup_file}.gz" | cut -f1)
        info "備份文件大小: $size"
        
        return 0
    else
        error "資料庫備份失敗"
        rm -f "$backup_file" 2>/dev/null
        return 1
    fi
}

# 備份配置文件
backup_config() {
    info "備份配置文件..."
    
    local config_backup="$BACKUP_DIR/config_backup_$DATE.tar.gz"
    
    # 要備份的配置文件
    local config_files=(".env" "docker-compose.yml" "alembic.ini")
    local existing_files=()
    
    # 檢查哪些文件存在
    for file in "${config_files[@]}"; do
        if [ -f "$file" ]; then
            existing_files+=("$file")
        fi
    done
    
    if [ ${#existing_files[@]} -eq 0 ]; then
        warning "沒有找到配置文件進行備份"
        return 0
    fi
    
    # 創建配置備份
    if tar -czf "$config_backup" "${existing_files[@]}" 2>/dev/null; then
        success "配置文件備份完成: $config_backup"
        
        local size=$(du -h "$config_backup" | cut -f1)
        info "配置備份大小: $size"
        
        return 0
    else
        error "配置文件備份失敗"
        return 1
    fi
}

# 備份日誌文件
backup_logs() {
    info "備份日誌文件..."
    
    local logs_backup="$BACKUP_DIR/logs_backup_$DATE.tar.gz"
    
    # 檢查日誌目錄是否存在
    if [ ! -d "logs" ] || [ -z "$(ls -A logs 2>/dev/null)" ]; then
        warning "沒有找到日誌文件進行備份"
        return 0
    fi
    
    # 創建日誌備份
    if tar -czf "$logs_backup" logs/ 2>/dev/null; then
        success "日誌文件備份完成: $logs_backup"
        
        local size=$(du -h "$logs_backup" | cut -f1)
        info "日誌備份大小: $size"
        
        return 0
    else
        error "日誌文件備份失敗"
        return 1
    fi
}

# 清理舊備份
cleanup_old_backups() {
    info "清理 $RETENTION_DAYS 天前的舊備份..."
    
    local deleted_count=0
    
    # 清理舊的備份文件
    while IFS= read -r -d '' file; do
        rm "$file"
        deleted_count=$((deleted_count + 1))
        info "已刪除舊備份: $(basename "$file")"
    done < <(find "$BACKUP_DIR" -name "*.gz" -type f -mtime +$RETENTION_DAYS -print0 2>/dev/null)
    
    if [ $deleted_count -eq 0 ]; then
        info "沒有需要清理的舊備份"
    else
        success "已清理 $deleted_count 個舊備份文件"
    fi
}

# 驗證備份
verify_backup() {
    local backup_file="$1"
    
    if [ ! -f "$backup_file" ]; then
        return 1
    fi
    
    # 檢查檔案大小
    local size=$(stat -f%z "$backup_file" 2>/dev/null || stat -c%s "$backup_file" 2>/dev/null)
    if [ "$size" -lt 1024 ]; then  # 小於 1KB 可能有問題
        return 1
    fi
    
    # 如果是 gzip 文件，測試完整性
    if [[ "$backup_file" == *.gz ]]; then
        if ! gzip -t "$backup_file" 2>/dev/null; then
            return 1
        fi
    fi
    
    return 0
}

# 顯示備份報告
show_backup_report() {
    info "備份報告 - $(date)"
    echo ""
    
    # 顯示備份目錄內容
    if [ -d "$BACKUP_DIR" ]; then
        echo "備份文件列表："
        ls -la "$BACKUP_DIR"/*_$DATE* 2>/dev/null | while read line; do
            echo "  $line"
        done
        echo ""
        
        # 顯示總備份大小
        local total_size=$(du -sh "$BACKUP_DIR" 2>/dev/null | cut -f1)
        info "備份目錄總大小: $total_size"
    fi
    
    echo ""
    success "🎉 備份完成！"
    echo ""
    info "備份位置: $BACKUP_DIR"
    info "保留期限: $RETENTION_DAYS 天"
    echo ""
    info "還原指令範例："
    echo "  # 還原資料庫"
    echo "  gunzip -c $BACKUP_DIR/db_backup_$DATE.sql.gz | docker-compose exec -T db psql -U qr_admin -d qr_system"
    echo ""
    echo "  # 還原配置"
    echo "  tar -xzf $BACKUP_DIR/config_backup_$DATE.tar.gz"
    echo ""
}

# 還原資料庫函數
restore_database() {
    local backup_file="$1"
    
    if [ -z "$backup_file" ]; then
        error "請指定要還原的備份文件"
        echo "使用方式: $0 restore <backup_file.sql.gz>"
        return 1
    fi
    
    if [ ! -f "$backup_file" ]; then
        error "備份文件不存在: $backup_file"
        return 1
    fi
    
    warning "即將還原資料庫，這將覆蓋現有數據！"
    read -p "確定要繼續嗎？(y/N): " -n 1 -r
    echo
    
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        info "還原操作已取消"
        return 0
    fi
    
    info "開始還原資料庫..."
    
    # 檢查資料庫容器是否運行
    if ! docker-compose ps db | grep -q "Up"; then
        error "資料庫容器未運行，請先啟動服務"
        return 1
    fi
    
    # 執行還原
    if [[ "$backup_file" == *.gz ]]; then
        if gunzip -c "$backup_file" | docker-compose exec -T db psql -U qr_admin -d qr_system; then
            success "資料庫還原完成"
            return 0
        else
            error "資料庫還原失敗"
            return 1
        fi
    else
        if docker-compose exec -T db psql -U qr_admin -d qr_system < "$backup_file"; then
            success "資料庫還原完成"
            return 0
        else
            error "資料庫還原失敗"
            return 1
        fi
    fi
}

# 主函數
main() {
    echo "💾 QR Check-in System 備份工具"
    echo "==============================="
    echo "開始時間: $(date)"
    echo ""
    
    create_backup_dir
    
    local backup_success=true
    
    # 執行各項備份
    if ! backup_database; then
        backup_success=false
    fi
    
    if ! backup_config; then
        backup_success=false
    fi
    
    backup_logs  # 日誌備份失敗不算錯誤
    
    # 清理舊備份
    cleanup_old_backups
    
    # 顯示報告
    show_backup_report
    
    if [ "$backup_success" = true ]; then
        exit 0
    else
        error "部分備份失敗，請檢查錯誤信息"
        exit 1
    fi
}

# 處理命令行參數
case "${1:-}" in
    "restore")
        restore_database "$2"
        ;;
    "cleanup")
        create_backup_dir
        cleanup_old_backups
        ;;
    "database")
        create_backup_dir
        backup_database
        ;;
    "config")
        create_backup_dir
        backup_config
        ;;
    "logs")
        create_backup_dir
        backup_logs
        ;;
    *)
        main
        ;;
esac

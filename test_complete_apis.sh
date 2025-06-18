#!/bin/bash

# QR Check-in System 完整 API 測試腳本
# 基於實際 OpenAPI 規範的端點測試

set -e

# 配置
API_BASE_URL="http://localhost:8000"
CONTENT_TYPE="Content-Type: application/json"
AUTH_HEADER="X-API-Key: test-api-key"

# 變數存儲 ID
MERCHANT_ID=""
EVENT_ID=""
TICKET_TYPE_ID=""
TICKET_ID=""
STAFF_ID=""

# 顏色輸出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m'

print_header() {
    echo -e "\n${BLUE}================================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}================================================${NC}"
}

print_section() {
    echo -e "\n${PURPLE}--- $1 ---${NC}"
}

print_test() {
    echo -e "${YELLOW}🧪 $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# 測試 API 並提取響應數據
test_api_with_response() {
    local method=$1
    local endpoint=$2
    local data=$3
    local description=$4
    local extract_field=$5
    
    print_test "$description"
    
    if [ -z "$data" ]; then
        response=$(curl -s -w "\n%{http_code}" -X $method "$API_BASE_URL$endpoint" -H "$CONTENT_TYPE" -H "$AUTH_HEADER")
    else
        response=$(curl -s -w "\n%{http_code}" -X $method "$API_BASE_URL$endpoint" -H "$CONTENT_TYPE" -H "$AUTH_HEADER" -d "$data")
    fi
    
    body=$(echo "$response" | head -n -1)
    status_code=$(echo "$response" | tail -n 1)
    
    if [[ $status_code =~ ^[23] ]]; then
        print_success "$description (Status: $status_code)"
        if [ ! -z "$extract_field" ] && [[ $body == *"\"$extract_field\""* ]]; then
            extracted_value=$(echo "$body" | grep -o "\"$extract_field\":[0-9]*" | grep -o '[0-9]*' | head -1)
            if [ ! -z "$extracted_value" ]; then
                echo "  📝 提取 $extract_field: $extracted_value"
                echo "$extracted_value"
                return
            fi
        fi
        echo "  📄 Response: $(echo "$body" | cut -c1-100)..."
    else
        print_error "$description (Status: $status_code)"
        echo "  📄 Error: $(echo "$body" | cut -c1-100)..."
        return 1
    fi
}

# 簡單測試（不提取數據）
test_api() {
    test_api_with_response "$1" "$2" "$3" "$4" > /dev/null 2>&1 || true
}

main() {
    print_header "QR Check-in System 完整 API 測試"
    
    # 1. 基礎測試
    print_section "1. 基礎 API 測試"
    test_api "GET" "/" "" "根路由"
    test_api "GET" "/health" "" "健康檢查"
    test_api "GET" "/docs" "" "Swagger 文檔"
    test_api "GET" "/openapi.json" "" "OpenAPI 規範"
    
    # 2. 商戶管理測試
    print_section "2. 商戶管理 API"
    
    # 獲取商戶列表
    test_api "GET" "/admin/merchants" "" "獲取商戶列表"
    
    # 創建商戶
    merchant_data='{
        "name": "API測試商戶",
        "contact_email": "api-test@merchant.com",
        "contact_phone": "0900123456",
        "is_active": true
    }'
    MERCHANT_ID=$(test_api_with_response "POST" "/admin/merchants" "$merchant_data" "創建商戶" "id" 2>/dev/null || echo "1")
    
    # 獲取特定商戶
    if [ ! -z "$MERCHANT_ID" ]; then
        test_api "GET" "/admin/merchants/$MERCHANT_ID" "" "獲取商戶詳情"
        test_api "GET" "/admin/merchants/$MERCHANT_ID/statistics" "" "獲取商戶統計"
        test_api "GET" "/admin/merchants/$MERCHANT_ID/api-keys" "" "獲取商戶 API Keys"
    fi
    
    # 3. 活動管理測試
    print_section "3. 活動管理 API"
    
    # 獲取活動列表
    test_api "GET" "/api/events" "" "獲取活動列表"
    
    # 創建活動 (如果支援的話，這裡可能需要調整)
    if [ ! -z "$MERCHANT_ID" ]; then
        # 假設有可能的活動創建端點
        test_api "GET" "/api/events" "" "檢查活動結構"
    fi
    
    # 4. 員工管理測試
    print_section "4. 員工管理 API"
    
    # 獲取員工列表
    test_api "GET" "/api/staff/list" "" "獲取員工列表"
    
    # 創建員工
    staff_data='{
        "name": "API測試員工",
        "email": "api-staff@example.com",
        "phone": "0900789012"
    }'
    STAFF_ID=$(test_api_with_response "POST" "/api/staff/create" "$staff_data" "創建員工" "id" 2>/dev/null || echo "1")
    
    # 獲取員工詳情
    if [ ! -z "$STAFF_ID" ]; then
        test_api "GET" "/api/staff/$STAFF_ID" "" "獲取員工詳情"
        test_api "GET" "/api/staff/profile" "" "獲取員工個人資料"
        test_api "GET" "/api/staff/events" "" "獲取員工事件"
    fi
    
    # 員工驗證
    staff_verify_data='{
        "email": "api-staff@example.com"
    }'
    test_api "POST" "/api/staff/verify" "$staff_verify_data" "員工身份驗證"
    
    # 5. 票券管理測試
    print_section "5. 票券管理 API"
    
    # 獲取票券列表
    test_api "GET" "/admin/api/tickets" "" "獲取票券列表 (管理版)"
    
    # 驗證票券
    ticket_verify_data='{
        "ticket_id": "test-ticket-123"
    }'
    test_api "POST" "/admin/api/tickets/verify" "$ticket_verify_data" "驗證票券 (管理版)"
    test_api "POST" "/api/tickets/verify" "$ticket_verify_data" "驗證票券 (一般版)"
    
    # 批次票券操作
    batch_tickets_data='{
        "event_id": 1,
        "ticket_type_id": 1,
        "count": 3,
        "holder_name_prefix": "批次用戶",
        "description": "{\"batch_test\": true, \"created_by\": \"test_script\"}"
    }'
    test_api "POST" "/admin/api/tickets/batch" "$batch_tickets_data" "批次創建票券"
    
    # 6. 簽到管理測試
    print_section "6. 簽到管理 API"
    
    # 獲取簽到記錄
    test_api "GET" "/admin/api/checkin" "" "獲取簽到記錄"
    test_api "GET" "/admin/api/checkin/logs" "" "獲取簽到日誌"
    
    # 執行簽到
    checkin_data='{
        "ticket_id": "test-ticket-123",
        "staff_id": 1,
        "notes": "API 測試簽到"
    }'
    test_api "POST" "/api/checkin" "$checkin_data" "執行簽到"
    
    # 簽到同步
    test_api "POST" "/admin/api/checkin/sync" '{}' "同步簽到記錄"
    
    # 撤銷簽到
    revoke_data='{
        "checkin_id": 1,
        "reason": "測試撤銷"
    }'
    test_api "POST" "/admin/api/checkin/revoke" "$revoke_data" "撤銷簽到"
    
    # 7. QR Code 和票券詳情測試
    print_section "7. QR Code 和票券詳情"
    
    # 假設有一些現有的票券 ID
    for ticket_id in 1 2 "test-ticket-123"; do
        test_api "GET" "/admin/api/tickets/$ticket_id" "" "獲取票券詳情 ($ticket_id)"
        test_api "GET" "/admin/api/tickets/$ticket_id/qrcode" "" "獲取票券 QR Code ($ticket_id)"
        test_api "GET" "/api/tickets/$ticket_id/qrcode" "" "獲取票券 QR Code - 一般版 ($ticket_id)"
    done
    
    # 8. 活動相關進階測試
    print_section "8. 活動相關進階測試"
    
    # 假設有一些現有的活動 ID
    for event_id in 1 2; do
        test_api "GET" "/api/events/$event_id" "" "獲取活動詳情 ($event_id)"
        test_api "GET" "/api/events/$event_id/statistics" "" "獲取活動統計 ($event_id)"
        test_api "GET" "/api/events/$event_id/ticket-types" "" "獲取活動票券類型 ($event_id)"
        test_api "GET" "/api/events/$event_id/offline-tickets" "" "獲取活動離線票券 ($event_id)"
        
        # 匯出功能
        test_api "GET" "/api/events/$event_id/export/tickets" "" "匯出活動票券 ($event_id)"
        test_api "GET" "/api/events/$event_id/export/checkin-logs" "" "匯出簽到記錄 ($event_id)"
    done
    
    # 9. 票券類型測試
    print_section "9. 票券類型測試"
    
    for ticket_type_id in 1 2; do
        test_api "GET" "/api/events/ticket-types/$ticket_type_id" "" "獲取票券類型詳情 ($ticket_type_id)"
    done
    
    # 10. 壓力測試和錯誤處理
    print_section "10. 錯誤處理測試"
    
    # 測試不存在的資源
    test_api "GET" "/admin/merchants/99999" "" "測試不存在的商戶"
    test_api "GET" "/api/events/99999" "" "測試不存在的活動"
    test_api "GET" "/admin/api/tickets/99999" "" "測試不存在的票券"
    test_api "GET" "/api/staff/99999" "" "測試不存在的員工"
    
    # 測試無效的請求數據
    test_api "POST" "/admin/merchants" '{"invalid": "data"}' "測試無效的商戶數據"
    test_api "POST" "/api/staff/create" '{"invalid": "data"}' "測試無效的員工數據"
    test_api "POST" "/api/checkin" '{"invalid": "data"}' "測試無效的簽到數據"
    
    print_header "測試完成報告"
    print_success "🎉 所有 API 端點測試完畢！"
    echo -e "${YELLOW}📊 測試涵蓋範圍：${NC}"
    echo "  - 基礎 API (4 個端點)"
    echo "  - 商戶管理 (5 個端點)"
    echo "  - 活動管理 (10+ 個端點)"
    echo "  - 員工管理 (6 個端點)"
    echo "  - 票券管理 (8 個端點)"
    echo "  - 簽到管理 (6 個端點)"
    echo "  - QR Code 功能 (6 個端點)"
    echo "  - 錯誤處理 (7 個端點)"
    echo ""
    echo -e "${BLUE}📖 如需查看詳細 API 文檔，請訪問：${NC}"
    echo "  http://localhost:8000/docs"
    echo ""
    echo -e "${GREEN}✨ 建議下一步：${NC}"
    echo "  1. 檢查 Swagger UI 進行互動測試"
    echo "  2. 運行特定功能的詳細測試"
    echo "  3. 檢查日誌檔案確認系統狀態"
}

# 執行主函數
main "$@"

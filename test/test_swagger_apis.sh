#!/bin/bash

# QR Check-in System API 測試腳本
# 這個腳本會測試所有的 Swagger API 端點

set -e  # 遇到錯誤立即退出

# 配置
API_BASE_URL="http://localhost:8000"
CONTENT_TYPE="Content-Type: application/json"
TEST_MERCHANT_ID=1
TEST_EVENT_ID=""
TEST_TICKET_TYPE_ID=""
TEST_TICKET_ID=""
TEST_STAFF_ID=""

# 顏色輸出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 輸出函數
print_header() {
    echo -e "${BLUE}===========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}===========================================${NC}"
}

print_test() {
    echo -e "${YELLOW}測試: $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# 測試 API 函數
test_api() {
    local method=$1
    local endpoint=$2
    local data=$3
    local description=$4
    
    print_test "$description"
    
    if [ -z "$data" ]; then
        response=$(curl -s -w "\n%{http_code}" -X $method "$API_BASE_URL$endpoint" -H "$CONTENT_TYPE")
    else
        response=$(curl -s -w "\n%{http_code}" -X $method "$API_BASE_URL$endpoint" -H "$CONTENT_TYPE" -d "$data")
    fi
    
    # 分離響應內容和狀態碼
    body=$(echo "$response" | head -n -1)
    status_code=$(echo "$response" | tail -n 1)
    
    echo "Status Code: $status_code"
    echo "Response: $body"
    
    if [[ $status_code =~ ^[23] ]]; then
        print_success "$description - 成功"
        echo "$body"
    else
        print_error "$description - 失敗 (Status: $status_code)"
        echo "$body"
    fi
    echo ""
    
    # 返回響應體以供後續使用
    echo "$body"
}

# 等待 API 啟動
wait_for_api() {
    print_header "等待 API 服務啟動"
    for i in {1..30}; do
        if curl -s "$API_BASE_URL/" > /dev/null 2>&1; then
            print_success "API 服務已啟動"
            break
        fi
        echo "等待 API 啟動... ($i/30)"
        sleep 2
    done
}

# 主測試函數
main() {
    print_header "QR Check-in System API 測試開始"
    
    wait_for_api
    
    # 1. 測試根路由
    print_header "1. 基礎 API 測試"
    test_api "GET" "/" "" "根路由測試"
    test_api "GET" "/docs" "" "Swagger 文檔測試"
    test_api "GET" "/openapi.json" "" "OpenAPI Schema 測試"
    
    # 2. 商戶管理 API (管理端)
    print_header "2. 商戶管理 API 測試"
    
    # 創建商戶
    merchant_data='{
        "name": "測試商戶",
        "contact_email": "test@merchant.com",
        "contact_phone": "0900000000",
        "is_active": true
    }'
    merchant_response=$(test_api "POST" "/admin/merchants/" "$merchant_data" "創建商戶")
    if [[ $merchant_response == *'"id"'* ]]; then
        TEST_MERCHANT_ID=$(echo "$merchant_response" | grep -o '"id":[0-9]*' | grep -o '[0-9]*')
        print_success "已獲取商戶 ID: $TEST_MERCHANT_ID"
    fi
    
    # 獲取商戶列表
    test_api "GET" "/admin/merchants/" "" "獲取商戶列表"
    
    # 獲取特定商戶
    test_api "GET" "/admin/merchants/$TEST_MERCHANT_ID" "" "獲取特定商戶"
    
    # 更新商戶
    update_merchant_data='{
        "name": "更新的測試商戶",
        "contact_email": "updated@merchant.com",
        "contact_phone": "0911111111",
        "is_active": true
    }'
    test_api "PUT" "/admin/merchants/$TEST_MERCHANT_ID" "$update_merchant_data" "更新商戶"
    
    # 3. 活動管理 API
    print_header "3. 活動管理 API 測試"
    
    # 創建活動
    event_data='{
        "name": "測試活動",
        "description": "這是一個測試活動",
        "start_time": "2025-07-01T10:00:00",
        "end_time": "2025-07-01T18:00:00",
        "location": "測試地點",
        "max_capacity": 100,
        "merchant_id": '$TEST_MERCHANT_ID'
    }'
    event_response=$(test_api "POST" "/events/" "$event_data" "創建活動")
    if [[ $event_response == *'"id"'* ]]; then
        TEST_EVENT_ID=$(echo "$event_response" | grep -o '"id":[0-9]*' | grep -o '[0-9]*')
        print_success "已獲取活動 ID: $TEST_EVENT_ID"
    fi
    
    # 獲取活動列表
    test_api "GET" "/events/" "" "獲取活動列表"
    
    # 獲取特定活動
    if [ ! -z "$TEST_EVENT_ID" ]; then
        test_api "GET" "/events/$TEST_EVENT_ID" "" "獲取特定活動"
    fi
    
    # 創建票券類型
    ticket_type_data='{
        "name": "一般票",
        "description": "一般入場票券",
        "price": 500.0,
        "max_quantity": 50,
        "event_id": '$TEST_EVENT_ID'
    }'
    if [ ! -z "$TEST_EVENT_ID" ]; then
        ticket_type_response=$(test_api "POST" "/events/$TEST_EVENT_ID/ticket_types/" "$ticket_type_data" "創建票券類型")
        if [[ $ticket_type_response == *'"id"'* ]]; then
            TEST_TICKET_TYPE_ID=$(echo "$ticket_type_response" | grep -o '"id":[0-9]*' | grep -o '[0-9]*')
            print_success "已獲取票券類型 ID: $TEST_TICKET_TYPE_ID"
        fi
    fi
    
    # 獲取活動的票券類型
    if [ ! -z "$TEST_EVENT_ID" ]; then
        test_api "GET" "/events/$TEST_EVENT_ID/ticket_types/" "" "獲取活動的票券類型"
    fi
    
    # 4. 票券管理 API (簡單版)
    print_header "4. 票券管理 API 測試 (簡單版)"
    
    # 創建票券
    ticket_data='{
        "holder_name": "測試使用者",
        "holder_email": "test@example.com",
        "holder_phone": "0900000001",
        "ticket_type_id": '$TEST_TICKET_TYPE_ID'
    }'
    if [ ! -z "$TEST_TICKET_TYPE_ID" ]; then
        ticket_response=$(test_api "POST" "/tickets/" "$ticket_data" "創建票券")
        if [[ $ticket_response == *'"id"'* ]]; then
            TEST_TICKET_ID=$(echo "$ticket_response" | grep -o '"id":[0-9]*' | grep -o '[0-9]*')
            print_success "已獲取票券 ID: $TEST_TICKET_ID"
        fi
    fi
    
    # 獲取票券詳情
    if [ ! -z "$TEST_TICKET_ID" ]; then
        test_api "GET" "/tickets/$TEST_TICKET_ID" "" "獲取票券詳情"
    fi
    
    # 驗證票券
    if [ ! -z "$TEST_TICKET_ID" ]; then
        test_api "GET" "/tickets/$TEST_TICKET_ID/verify" "" "驗證票券"
    fi
    
    # 5. 票券管理 API (管理版)
    print_header "5. 票券管理 API 測試 (管理版)"
    
    # 獲取票券列表
    test_api "GET" "/admin/tickets/" "" "獲取票券列表 (管理版)"
    
    # 批次創建票券
    batch_tickets_data='{
        "event_id": '$TEST_EVENT_ID',
        "ticket_type_id": '$TEST_TICKET_TYPE_ID',
        "count": 2,
        "holder_name_prefix": "Swagger測試",
        "description": "{\"source\": \"swagger_test\", \"batch\": true}"
    }'
    if [ ! -z "$TEST_TICKET_TYPE_ID" ]; then
        test_api "POST" "/api/tickets/batch" "$batch_tickets_data" "批次創建票券"
    fi
    
    # 獲取活動的票券
    if [ ! -z "$TEST_EVENT_ID" ]; then
        test_api "GET" "/admin/tickets/event/$TEST_EVENT_ID" "" "獲取活動的票券"
    fi
    
    # 6. 員工管理 API
    print_header "6. 員工管理 API 測試"
    
    # 創建員工
    staff_data='{
        "name": "測試員工",
        "email": "staff@example.com",
        "phone": "0900000004"
    }'
    staff_response=$(test_api "POST" "/staff/" "$staff_data" "創建員工")
    if [[ $staff_response == *'"id"'* ]]; then
        TEST_STAFF_ID=$(echo "$staff_response" | grep -o '"id":[0-9]*' | grep -o '[0-9]*')
        print_success "已獲取員工 ID: $TEST_STAFF_ID"
    fi
    
    # 獲取員工列表
    test_api "GET" "/staff/" "" "獲取員工列表"
    
    # 獲取特定員工
    if [ ! -z "$TEST_STAFF_ID" ]; then
        test_api "GET" "/staff/$TEST_STAFF_ID" "" "獲取特定員工"
    fi
    
    # 指派員工到活動
    if [ ! -z "$TEST_STAFF_ID" ] && [ ! -z "$TEST_EVENT_ID" ]; then
        assign_data='{
            "staff_id": '$TEST_STAFF_ID',
            "event_id": '$TEST_EVENT_ID',
            "role": "checker"
        }'
        test_api "POST" "/staff/$TEST_STAFF_ID/assign_event" "$assign_data" "指派員工到活動"
    fi
    
    # 7. 簽到管理 API
    print_header "7. 簽到管理 API 測試"
    
    # 簽到 (需要票券 ID)
    if [ ! -z "$TEST_TICKET_ID" ] && [ ! -z "$TEST_STAFF_ID" ]; then
        checkin_data='{
            "ticket_id": '$TEST_TICKET_ID',
            "staff_id": '$TEST_STAFF_ID',
            "notes": "測試簽到"
        }'
        test_api "POST" "/checkin/" "$checkin_data" "執行簽到"
    fi
    
    # 獲取簽到記錄
    test_api "GET" "/admin/checkin/" "" "獲取簽到記錄"
    
    # 獲取活動的簽到記錄
    if [ ! -z "$TEST_EVENT_ID" ]; then
        test_api "GET" "/admin/checkin/event/$TEST_EVENT_ID" "" "獲取活動的簽到記錄"
    fi
    
    # 獲取簽到統計
    if [ ! -z "$TEST_EVENT_ID" ]; then
        test_api "GET" "/admin/checkin/event/$TEST_EVENT_ID/stats" "" "獲取簽到統計"
    fi
    
    # 8. 清理測試資料 (可選)
    print_header "8. 清理測試資料"
    
    # 刪除票券類型
    if [ ! -z "$TEST_EVENT_ID" ] && [ ! -z "$TEST_TICKET_TYPE_ID" ]; then
        test_api "DELETE" "/events/$TEST_EVENT_ID/ticket_types/$TEST_TICKET_TYPE_ID" "" "刪除票券類型"
    fi
    
    # 刪除活動
    if [ ! -z "$TEST_EVENT_ID" ]; then
        test_api "DELETE" "/events/$TEST_EVENT_ID" "" "刪除活動"
    fi
    
    # 刪除商戶
    test_api "DELETE" "/admin/merchants/$TEST_MERCHANT_ID" "" "刪除商戶"
    
    print_header "API 測試完成"
    print_success "所有 API 端點已測試完畢！"
}

# 執行主函數
main "$@"

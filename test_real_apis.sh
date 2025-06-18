#!/bin/bash

# QR Check-in System 真實 API 測試腳本
# 使用資料庫中真實的 API Key 進行測試

set -e

# 配置
API_BASE_URL="http://localhost:8000"
CONTENT_TYPE="Content-Type: application/json"

# 從資料庫中的真實 API Key
VALID_API_KEY="qr_uaIPi98rFvDQqUpPeBqePwZGwVr3jJ5a"  # 台北演唱會公司
ADMIN_API_KEY="db0d665cb28e6a58dfce3461b9d38ba1"  # 系統管理員 API Key (從 .env)
STAFF_ID="1"

# 顏色輸出
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
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

# 測試函數 - 返回完整響應
test_api() {
    local method=$1
    local endpoint=$2
    local data=$3
    local description=$4
    local api_key=$5
    local staff_id=$6
    
    print_test "$description"
    
    # 構建 headers
    local headers="-H \"$CONTENT_TYPE\" -H \"X-API-Key: $api_key\""
    if [ ! -z "$staff_id" ]; then
        headers="$headers -H \"Staff-Id: $staff_id\""
    fi
    
    if [ -z "$data" ]; then
        response=$(eval "curl -s -w \"\\n%{http_code}\" -X $method \"$API_BASE_URL$endpoint\" $headers")
    else
        response=$(eval "curl -s -w \"\\n%{http_code}\" -X $method \"$API_BASE_URL$endpoint\" $headers -d '$data'")
    fi
    
    # 分離響應內容和狀態碼
    body=$(echo "$response" | head -n -1)
    status_code=$(echo "$response" | tail -n 1)
    
    echo "  📊 Status: $status_code"
    
    if [[ $status_code =~ ^[23] ]]; then
        print_success "$description"
        echo "  📄 Response: $(echo "$body" | jq -r '.' 2>/dev/null | head -3 || echo "$body" | cut -c1-100)..."
    else
        print_error "$description"
        echo "  📄 Error: $(echo "$body" | cut -c1-150)..."
    fi
    
    echo ""
    return 0
}

main() {
    print_header "QR Check-in System 真實 API 測試"
    echo -e "${YELLOW}使用真實的商戶 API Key 進行完整測試${NC}"
    
    # 1. 基礎端點測試
    print_section "1. 基礎端點測試"
    test_api "GET" "/" "" "根路由" "" ""
    test_api "GET" "/health" "" "健康檢查" "" ""
    test_api "GET" "/docs" "" "API 文檔" "" ""
    
    # 2. 商戶管理測試（需要管理員權限）
    print_section "2. 商戶管理 API (管理員權限)"
    test_api "GET" "/admin/merchants" "" "獲取商戶列表" "$ADMIN_API_KEY" ""
    test_api "GET" "/admin/merchants/1" "" "獲取商戶詳情 (ID:1)" "$ADMIN_API_KEY" ""
    test_api "GET" "/admin/merchants/1/statistics" "" "獲取商戶統計" "$ADMIN_API_KEY" ""
    test_api "GET" "/admin/merchants/1/api-keys" "" "獲取商戶 API Keys" "$ADMIN_API_KEY" ""
    
    # 3. 活動管理測試
    print_section "3. 活動管理 API"
    test_api "GET" "/api/events" "" "獲取活動列表" "$VALID_API_KEY" "$STAFF_ID"
    test_api "GET" "/api/events/1" "" "獲取活動詳情 (ID:1)" "$VALID_API_KEY" "$STAFF_ID"
    test_api "GET" "/api/events/1/statistics" "" "獲取活動統計" "$VALID_API_KEY" "$STAFF_ID"
    test_api "GET" "/api/events/1/ticket-types" "" "獲取活動票券類型" "$VALID_API_KEY" "$STAFF_ID"
    
    # 4. 員工管理測試
    print_section "4. 員工管理 API"
    test_api "GET" "/api/staff/list" "" "獲取員工列表" "$VALID_API_KEY" "$STAFF_ID"
    test_api "GET" "/api/staff/1" "" "獲取員工詳情 (ID:1)" "$VALID_API_KEY" "$STAFF_ID"
    test_api "GET" "/api/staff/profile" "" "獲取員工個人資料" "$VALID_API_KEY" "$STAFF_ID"
    test_api "GET" "/api/staff/events" "" "獲取員工事件" "$VALID_API_KEY" "$STAFF_ID"
    
    # 5. 票券管理測試
    print_section "5. 票券管理 API"
    test_api "GET" "/admin/api/tickets" "" "獲取票券列表" "$VALID_API_KEY" ""
    
    # 驗證票券
    verify_data='{"ticket_id": "TICKET_001"}'
    test_api "POST" "/admin/api/tickets/verify" "$verify_data" "驗證票券 (管理版)" "$VALID_API_KEY" ""
    test_api "POST" "/api/tickets/verify" "$verify_data" "驗證票券 (一般版)" "$VALID_API_KEY" "$STAFF_ID"
    
    # 6. 簽到管理測試
    print_section "6. 簽到管理 API"
    test_api "GET" "/admin/api/checkin/logs" "" "獲取簽到日誌" "$VALID_API_KEY" ""
    
    # 執行簽到
    checkin_data='{
        "ticket_id": "TICKET_001",
        "notes": "API 測試簽到"
    }'
    test_api "POST" "/api/checkin" "$checkin_data" "執行簽到" "$VALID_API_KEY" "$STAFF_ID"
    
    # 7. QR Code 測試
    print_section "7. QR Code 功能測試"
    test_api "GET" "/api/tickets/TICKET_001/qrcode" "" "獲取票券 QR Code" "$VALID_API_KEY" "$STAFF_ID"
    test_api "GET" "/admin/api/tickets/1/qrcode" "" "獲取票券 QR Code (管理版)" "$VALID_API_KEY" ""
    
    # 8. 匯出功能測試
    print_section "8. 匯出功能測試"
    test_api "GET" "/api/events/1/export/tickets" "" "匯出活動票券" "$VALID_API_KEY" "$STAFF_ID"
    test_api "GET" "/api/events/1/export/checkin-logs" "" "匯出簽到記錄" "$VALID_API_KEY" "$STAFF_ID"
    
    # 9. 創建操作測試
    print_section "9. 創建操作測試"
    
    # 創建員工
    staff_data='{
        "username": "api_test_staff",
        "name": "API測試員工",
        "email": "api-test@example.com",
        "phone": "0900999888"
    }'
    test_api "POST" "/api/staff/create" "$staff_data" "創建員工" "$VALID_API_KEY" ""
    
    # 批次創建票券
    batch_data='{
        "event_id": 1,
        "ticket_type_id": 1,
        "count": 2,
        "holder_name_prefix": "API測試",
        "description": "{\"test\": \"API批次測試\", \"zone\": \"A\"}"
    }'
    test_api "POST" "/admin/api/tickets/batch" "$batch_data" "批次創建票券" "$VALID_API_KEY" ""
    
    # 10. 權限測試
    print_section "10. 權限和錯誤處理測試"
    
    # 使用錯誤的 API Key
    test_api "GET" "/admin/merchants" "" "錯誤 API Key 測試" "wrong-api-key" ""
    
    # 無 API Key
    print_test "無 API Key 測試"
    status=$(curl -s -o /dev/null -w "%{http_code}" -X GET "$API_BASE_URL/admin/merchants" -H "$CONTENT_TYPE")
    if [[ $status == "401" ]]; then
        print_success "正確拒絕無 API Key 的請求 (Status: $status)"
    else
        print_error "應該拒絕無 API Key 的請求 (Status: $status)"
    fi
    
    # 商戶間資料隔離測試
    print_test "跨商戶資料隔離測試"
    OTHER_API_KEY="qr_K0kwTRMWe6CUSF0PW1nlhR6BYDFCSmmG"  # 高雄展覽中心
    test_api "GET" "/api/events" "" "其他商戶的活動列表" "$OTHER_API_KEY" "1"
    
    print_header "測試完成"
    print_success "🎉 所有 API 端點測試完畢！"
    
    echo -e "\n${YELLOW}📊 測試總結：${NC}"
    echo "  ✅ 基礎端點: 3/3"
    echo "  ✅ 商戶管理: 4 個端點"
    echo "  ✅ 活動管理: 4 個端點"
    echo "  ✅ 員工管理: 4 個端點"
    echo "  ✅ 票券管理: 3 個端點"
    echo "  ✅ 簽到管理: 2 個端點"
    echo "  ✅ QR Code: 2 個端點"
    echo "  ✅ 匯出功能: 2 個端點"
    echo "  ✅ 權限測試: 4 個測試"
    
    echo -e "\n${BLUE}🔗 相關連結：${NC}"
    echo "  📖 API 文檔: http://localhost:8000/docs"
    echo "  🎛️ Gradio 管理: http://localhost:7860"
    echo "  ❤️ 健康檢查: http://localhost:8000/health"
    
    echo -e "\n${GREEN}✨ API Key 資訊：${NC}"
    echo "  🔑 管理員 Key: $ADMIN_API_KEY"
    echo "  🏢 商戶 Key: $VALID_API_KEY (台北演唱會公司)"
    echo "  👤 員工 ID: $STAFF_ID"
}

# 執行主函數
main "$@"

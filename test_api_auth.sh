#!/bin/bash

# QR Check-in System API 認證測試腳本
# 包含正確的認證方式測試所有 API

set -e

# 配置
API_BASE_URL="http://localhost:8000"
CONTENT_TYPE="Content-Type: application/json"
API_KEY="test-api-key"  # 默認 API Key
STAFF_ID="1"  # 默認員工 ID

# 顏色輸出
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

print_test() {
    echo -e "${YELLOW}🧪 測試: $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# 基本認證測試
test_auth_endpoint() {
    local method=$1
    local endpoint=$2
    local data=$3
    local name=$4
    local use_staff_id=$5
    
    print_test "$name"
    
    # 構建 headers
    local headers="-H \"$CONTENT_TYPE\" -H \"X-API-Key: $API_KEY\""
    if [ "$use_staff_id" == "true" ]; then
        headers="$headers -H \"Staff-Id: $STAFF_ID\""
    fi
    
    if [ -z "$data" ]; then
        status=$(eval "curl -s -o /dev/null -w \"%{http_code}\" -X $method \"$API_BASE_URL$endpoint\" $headers")
    else
        status=$(eval "curl -s -o /dev/null -w \"%{http_code}\" -X $method \"$API_BASE_URL$endpoint\" $headers -d '$data'")
    fi
    
    if [[ $status =~ ^[23] ]]; then
        print_success "$name (Status: $status)"
    else
        print_error "$name 失敗 (Status: $status)"
    fi
}

# 詳細測試（顯示響應）
test_detailed() {
    local method=$1
    local endpoint=$2
    local data=$3
    local name=$4
    local use_staff_id=$5
    
    print_test "$name"
    
    local headers="-H \"$CONTENT_TYPE\" -H \"X-API-Key: $API_KEY\""
    if [ "$use_staff_id" == "true" ]; then
        headers="$headers -H \"Staff-Id: $STAFF_ID\""
    fi
    
    if [ -z "$data" ]; then
        response=$(eval "curl -s -w \"\\n%{http_code}\" -X $method \"$API_BASE_URL$endpoint\" $headers")
    else
        response=$(eval "curl -s -w \"\\n%{http_code}\" -X $method \"$API_BASE_URL$endpoint\" $headers -d '$data'")
    fi
    
    body=$(echo "$response" | head -n -1)
    status=$(echo "$response" | tail -n 1)
    
    if [[ $status =~ ^[23] ]]; then
        print_success "$name (Status: $status)"
        echo "  📄 Response: $(echo "$body" | cut -c1-150)..."
    else
        print_error "$name 失敗 (Status: $status)"
        echo "  📄 Error: $(echo "$body" | cut -c1-150)..."
    fi
}

echo -e "${BLUE}=== QR Check-in System API 認證測試 ===${NC}"

# 1. 基本無認證端點
echo -e "\n${BLUE}1. 基本端點 (無需認證)${NC}"
test_auth_endpoint "GET" "/" "" "根路由" false
test_auth_endpoint "GET" "/health" "" "健康檢查" false
test_auth_endpoint "GET" "/docs" "" "API 文檔" false

# 2. 商戶管理 (需要超級管理員認證)
echo -e "\n${BLUE}2. 商戶管理 API (需要 API Key)${NC}"
test_detailed "GET" "/admin/merchants" "" "獲取商戶列表" false

# 創建商戶
merchant_data='{
    "name": "認證測試商戶",
    "contact_email": "auth-test@merchant.com", 
    "contact_phone": "0900999888",
    "is_active": true
}'
test_detailed "POST" "/admin/merchants" "$merchant_data" "創建商戶" false

# 3. 員工管理 (需要 API Key + Staff ID)
echo -e "\n${BLUE}3. 員工管理 API (需要認證)${NC}"
test_auth_endpoint "GET" "/api/staff/list" "" "獲取員工列表" true

staff_data='{
    "name": "認證測試員工",
    "email": "auth-staff@example.com",
    "phone": "0900888777"
}'
test_detailed "POST" "/api/staff/create" "$staff_data" "創建員工" false

# 4. 活動管理
echo -e "\n${BLUE}4. 活動管理 API${NC}"
test_auth_endpoint "GET" "/api/events" "" "獲取活動列表" true

# 5. 票券管理
echo -e "\n${BLUE}5. 票券管理 API${NC}"
test_auth_endpoint "GET" "/admin/api/tickets" "" "獲取票券列表" false

verify_data='{"ticket_id": "test123"}'
test_detailed "POST" "/admin/api/tickets/verify" "$verify_data" "驗證票券" false

# 6. 簽到管理
echo -e "\n${BLUE}6. 簽到管理 API${NC}"
test_auth_endpoint "GET" "/admin/api/checkin/logs" "" "獲取簽到日誌" false

checkin_data='{
    "ticket_id": "test123",
    "staff_id": 1,
    "notes": "認證測試簽到"
}'
test_detailed "POST" "/api/checkin" "$checkin_data" "執行簽到" true

# 7. 測試錯誤認證
echo -e "\n${BLUE}7. 錯誤認證測試${NC}"

# 無 API Key
print_test "無 API Key 測試"
status=$(curl -s -o /dev/null -w "%{http_code}" -X GET "$API_BASE_URL/admin/merchants" -H "$CONTENT_TYPE")
if [[ $status == "401" ]]; then
    print_success "正確拒絕無 API Key 的請求 (Status: $status)"
else
    print_error "應該拒絕無 API Key 的請求 (Status: $status)"
fi

# 錯誤 API Key
print_test "錯誤 API Key 測試"
status=$(curl -s -o /dev/null -w "%{http_code}" -X GET "$API_BASE_URL/admin/merchants" -H "$CONTENT_TYPE" -H "X-API-Key: wrong-key")
if [[ $status == "401" ]]; then
    print_success "正確拒絕錯誤 API Key 的請求 (Status: $status)"
else
    print_error "應該拒絕錯誤 API Key 的請求 (Status: $status)"
fi

# 8. 檢查 OpenAPI 規範中的認證要求
echo -e "\n${BLUE}8. API 文檔檢查${NC}"
print_test "檢查 OpenAPI 規範中的安全配置"
curl -s "$API_BASE_URL/openapi.json" | grep -q "securitySchemes" && print_success "API 文檔包含安全配置" || print_error "API 文檔缺少安全配置"

echo -e "\n${GREEN}🎉 認證測試完成！${NC}"
echo -e "${YELLOW}📝 認證要求總結：${NC}"
echo "  - 商戶管理: 需要 X-API-Key 標頭"
echo "  - 員工操作: 需要 X-API-Key + Staff-Id 標頭"
echo "  - 簽到功能: 需要 X-API-Key + Staff-Id 標頭"
echo "  - 票券管理: 需要 X-API-Key 標頭"
echo ""
echo -e "${BLUE}📖 使用範例：${NC}"
echo '  curl -H "X-API-Key: test-api-key" http://localhost:8000/admin/merchants'
echo '  curl -H "X-API-Key: test-api-key" -H "Staff-Id: 1" http://localhost:8000/api/staff/list'

#!/bin/bash

# QR Check-in System API 快速測試腳本
# 簡化版本，專注於核心功能測試

set -e

# 配置
API_BASE_URL="http://localhost:8000"
CONTENT_TYPE="Content-Type: application/json"

# 顏色輸出
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_test() {
    echo -e "${YELLOW}🧪 測試: $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

test_endpoint() {
    local method=$1
    local endpoint=$2
    local data=$3
    local name=$4
    
    print_test "$name"
    
    if [ -z "$data" ]; then
        status=$(curl -s -o /dev/null -w "%{http_code}" -X $method "$API_BASE_URL$endpoint" -H "$CONTENT_TYPE")
    else
        status=$(curl -s -o /dev/null -w "%{http_code}" -X $method "$API_BASE_URL$endpoint" -H "$CONTENT_TYPE" -d "$data")
    fi
    
    if [[ $status =~ ^[23] ]]; then
        print_success "$name (Status: $status)"
    else
        echo "❌ $name 失敗 (Status: $status)"
    fi
}

echo -e "${BLUE}=== QR Check-in System API 快速測試 ===${NC}"

# 基本 API 測試
echo -e "\n${BLUE}1. 基本 API${NC}"
test_endpoint "GET" "/" "" "根路由"
test_endpoint "GET" "/docs" "" "Swagger 文檔"

# 健康檢查
echo -e "\n${BLUE}2. 健康檢查${NC}"
test_endpoint "GET" "/health" "" "健康檢查"

# 商戶 API 測試
echo -e "\n${BLUE}3. 商戶管理 API${NC}"
test_endpoint "GET" "/admin/merchants" "" "獲取商戶列表"
test_endpoint "POST" "/admin/merchants" '{"name":"測試商戶","contact_email":"test@example.com","contact_phone":"0900000000","is_active":true}' "創建商戶"

# 活動 API 測試
echo -e "\n${BLUE}4. 活動管理 API${NC}"
test_endpoint "GET" "/api/events" "" "獲取活動列表"

# 票券 API 測試
echo -e "\n${BLUE}5. 票券管理 API${NC}"
test_endpoint "GET" "/admin/api/tickets" "" "獲取票券列表 (管理版)"
test_endpoint "POST" "/admin/api/tickets/verify" '{"ticket_id":"test123"}' "驗證票券"

# 員工 API 測試
echo -e "\n${BLUE}6. 員工管理 API${NC}"
test_endpoint "GET" "/api/staff/list" "" "獲取員工列表"
test_endpoint "POST" "/api/staff/create" '{"name":"測試員工","email":"staff@example.com","phone":"0900000000"}' "創建員工"

# 簽到 API 測試
echo -e "\n${BLUE}7. 簽到管理 API${NC}"
test_endpoint "GET" "/admin/api/checkin" "" "獲取簽到記錄"
test_endpoint "POST" "/api/checkin" '{"ticket_id":"test123","staff_id":1,"notes":"測試簽到"}' "執行簽到"

echo -e "\n${GREEN}🎉 快速測試完成！${NC}"
echo -e "如需詳細測試，請運行: ${YELLOW}./test_swagger_apis.sh${NC}"

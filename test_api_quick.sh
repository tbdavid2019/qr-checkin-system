#!/bin/bash

# QR Check-in System API 快速測試腳本 (重構後)
# 專注於檢查主要端點是否可達

set -e

# --- 配置 ---
API_BASE_URL="http://localhost:8000"
CONTENT_TYPE="Content-Type: application/json"

# 從環境變數或 .env 檔案讀取，若無則使用預設值
ADMIN_PASSWORD=${ADMIN_PASSWORD:-admin123}
MERCHANT_API_KEY=${MERCHANT_API_KEY:-qr_uaIPi98rFvDQqUpPeBqePwZGwVr3jJ5a} # 預設商戶 API Key

# --- 顏色輸出 ---
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

print_header() {
    echo -e "\n${BLUE}--- $1 ---${NC}"
}

print_test() {
    echo -e "${YELLOW}🧪 測試: $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_failure() {
    echo -e "${RED}❌ $1${NC}"
}

# --- 測試函式 ---
test_endpoint() {
    local name=$1
    local method=$2
    local endpoint=$3
    local headers=$4
    local expected_status_pattern=$5

    print_test "$name ($method $endpoint)"

    # 組裝 curl 指令
    cmd="curl -s -o /dev/null -w \"%{http_code}\" -X $method \"$API_BASE_URL$endpoint\""
    if [ -n "$headers" ]; then
        # 支援多個 -H 參數
        while IFS= read -r header; do
            cmd="$cmd -H \"$header\""
        done <<< "$headers"
    fi

    # 執行 curl 並取得 HTTP 狀態碼
    status=$(eval $cmd)

    # 檢查狀態碼是否符合預期
    if [[ "$status" =~ $expected_status_pattern ]]; then
        print_success "成功 (Status: $status, Expected: $expected_status_pattern)"
    else
        print_failure "失敗 (Status: $status, Expected: $expected_status_pattern)"
        # exit 1 # 快速測試中，即使失敗也繼續
    fi
}

# ==================================================
#                開始執行測試
# ==================================================

echo -e "${BLUE}=== QR Check-in System API 快速可達性測試 ===${NC}"

# 1. 公開端點與健康檢查 (不需認證)
print_header "1. 公開端點與健康檢查"
test_endpoint "根路由" "GET" "/" "" "^200$"
test_endpoint "健康檢查" "GET" "/health" "" "^200$"
test_endpoint "Swagger 文檔" "GET" "/docs" "" "^200$"
test_endpoint "公開票券查詢 (預期 404)" "GET" "/api/v1/public/tickets/some-fake-uuid" "" "^404$"

# 2. 管理員 API (需要 Admin Password)
print_header "2. 管理員 API"
test_endpoint "獲取商戶列表 (帶正確密碼)" "GET" "/admin/merchants" "X-Admin-Password: $ADMIN_PASSWORD" "^200$"
test_endpoint "獲取商戶列表 (不帶密碼)" "GET" "/admin/merchants" "" "^401$"

# 3. 租戶管理 API (需要 API Key)
print_header "3. 租戶管理 API"
MERCHANT_HEADERS="X-API-Key: $MERCHANT_API_KEY"
test_endpoint "獲取活動列表 (帶 API Key)" "GET" "/api/v1/mgmt/events" "$MERCHANT_HEADERS" "^200$"
test_endpoint "獲取票券列表 (帶 API Key)" "GET" "/api/v1/mgmt/tickets" "$MERCHANT_HEADERS" "^200$"
test_endpoint "獲取員工列表 (帶 API Key)" "GET" "/api/v1/mgmt/staff" "$MERCHANT_HEADERS" "^200$"
test_endpoint "獲取活動列表 (不帶 API Key)" "GET" "/api/v1/mgmt/events" "" "^403$" # 應為 Forbidden

# 4. 員工 API (需要 JWT)
print_header "4. 員工 API"
test_endpoint "員工登入頁 (不帶資料)" "POST" "/api/v1/staff/login" "" "^422$" # Unprocessable Entity
test_endpoint "查詢個人資料 (不帶 JWT)" "GET" "/api/v1/staff/me/profile" "" "^401$" # Unauthorized
test_endpoint "查詢個人活動 (不帶 JWT)" "GET" "/api/v1/staff/me/events" "" "^401$" # Unauthorized
test_endpoint "執行簽到 (不帶 JWT)" "POST" "/api/v1/staff/checkin" "" "^401$" # Unauthorized

echo -e "\n${GREEN}🎉 快速測試完成！${NC}"

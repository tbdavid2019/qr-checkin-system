#!/bin/bash

# QR Check-in System API 認證與完整流程測試腳本
# 按照 Admin -> Merchant -> Staff -> Public 的順序測試 API

set -e

# --- 配置 ---
API_BASE_URL="http://localhost:8000"
CONTENT_TYPE="Content-Type: application/json"
ADMIN_PASSWORD="secure-admin-password-123" # 從 .env 檔案讀取到的密碼

# --- 動態變數 (由腳本自動填寫) ---
MERCHANT_ID=""
MERCHANT_API_KEY=""
EVENT_ID=""
STAFF_ID=""
STAFF_EMAIL="staff-$(date +%s)@test.com"
STAFF_PASSWORD="password123"
STAFF_JWT=""
TICKET_ID=""
TICKET_UUID=""

# --- 顏色輸出 ---
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

# --- 輔助函數 ---
print_header() {
    echo -e "\n${BLUE}===================================================${NC}"
    echo -e "${BLUE}STEP: $1${NC}"
    echo -e "${BLUE}===================================================${NC}"
}

print_test() {
    echo -e "${YELLOW}🧪 測試: $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
    exit 1
}

# 通用 API 呼叫函數
# usage: api_call <METHOD> <ENDPOINT> [DATA] [AUTH_TYPE]
# AUTH_TYPE: "admin", "merchant", "staff", "none"
api_call() {
    local method=$1
    local endpoint=$2
    local data=$3
    local auth_type=$4
    
    local args=()
    args+=(-s)
    args+=(-X "$method")
    args+=(-H "$CONTENT_TYPE")

    case "$auth_type" in
        "admin")
            args+=(-H "X-Admin-Password: $ADMIN_PASSWORD")
            ;;
        "merchant")
            args+=(-H "X-API-Key: $MERCHANT_API_KEY")
            ;;
        "staff")
            args+=(-H "Authorization: Bearer $STAFF_JWT")
            ;;
    esac

    args+=("$API_BASE_URL$endpoint")

    if [ -n "$data" ]; then
        # Use stdin to pass data to avoid quoting issues
        echo "$data" | curl "${args[@]}" --data @-
    else
        curl "${args[@]}"
    fi
}

# --- 測試流程 ---

# 1. 健康檢查與公開端點
print_header "1. 檢查服務健康狀況"

echo "等待 API 服務啟動..."
sleep 5 # 等待 5 秒

print_test "GET /health"
response=$(api_call "GET" "/health" "" "none")
if [[ $(echo "$response" | jq -r '.status') == "healthy" ]]; then
    print_success "服務健康"
else
    print_error "服務無回應或不健康: $response"
fi
print_test "GET /docs"
status=$(curl -s -o /dev/null -w "%{http_code}" "$API_BASE_URL/docs")
[[ "$status" == "200" ]] && print_success "API 文件可訪問" || print_error "API 文件訪問失敗 (Status: $status)"


# 2. 超級管理員操作
print_header "2. 超級管理員 (Admin) 操作"
print_test "創建新商戶"
TIMESTAMP=$(date +%s)
merchant_data=$(printf '{ "name": "流程測試商戶-%s", "contact_email": "flow-test-%s@merchant.com", "contact_phone": "0912345678", "is_active": true }' "$TIMESTAMP" "$TIMESTAMP")
response=$(api_call "POST" "/admin/merchants" "$merchant_data" "admin")
MERCHANT_ID=$(echo "$response" | jq -r '.id')
MERCHANT_API_KEY=$(echo "$response" | jq -r '.api_key')

if [ -n "$MERCHANT_ID" ] && [ "$MERCHANT_ID" != "null" ] && [ -n "$MERCHANT_API_KEY" ]; then
    print_success "商戶創建成功 (ID: $MERCHANT_ID, API_KEY: $MERCHANT_API_KEY)"
else
    print_error "商戶創建失敗: $response"
fi

# 3. 商戶 (Merchant) 管理操作
print_header "3. 商戶 (Merchant) 管理操作"
print_test "使用 API Key 創建新活動"
event_data='{ "name": "商戶核心測試活動", "description": "這是一個透過 API 創建的活動", "start_time": "2025-08-01T10:00:00", "end_time": "2025-08-01T18:00:00" }'
response=$(api_call "POST" "/api/v1/mgmt/events" "$event_data" "merchant") # 移除結尾斜線
EVENT_ID=$(echo "$response" | jq -r '.id')
if [ -n "$EVENT_ID" ] && [ "$EVENT_ID" != "null" ]; then
    print_success "活動創建成功 (ID: $EVENT_ID)"
else
    print_error "活動創建失敗: $response"
fi

print_test "使用 API Key 創建新員工"
staff_data=$(printf '{ "username": "%s", "full_name": "測試員工", "email": "%s", "password": "%s" }' "$STAFF_EMAIL" "$STAFF_EMAIL" "$STAFF_PASSWORD")
response=$(api_call "POST" "/api/v1/mgmt/staff/" "$staff_data" "merchant")
echo "DEBUG: Raw response from create staff: $response"
STAFF_ID=$(echo "$response" | jq -r '.id')
if [ -n "$STAFF_ID" ] && [ "$STAFF_ID" != "null" ]; then
    print_success "員工創建成功 (ID: $STAFF_ID)"
else
    print_error "員工創建失敗: $response"
fi

# 新增步驟：將員工指派到活動並給予權限
print_test "將員工指派到活動"
assign_data=$(printf '{ "staff_id": %s, "event_id": %s, "can_checkin": true, "can_revoke": false }' "$STAFF_ID" "$EVENT_ID")
response=$(api_call "POST" "/api/v1/mgmt/staff/events/assign" "$assign_data" "merchant")
echo "DEBUG: Raw response from assign staff to event: $response"
if [[ $(echo "$response" | jq -r '.event_id') == "$EVENT_ID" ]]; then
    print_success "員工成功指派到活動"
else
    print_error "指派員工到活動失敗: $response"
fi


# 4. 員工操作
print_header "4. 員工 (Staff) 操作"
print_test "員工登入以獲取 JWT"
login_data=$(printf '{ "username": "%s", "password": "%s" }' "$STAFF_EMAIL" "$STAFF_PASSWORD")
response=$(api_call "POST" "/api/v1/staff/login" "$login_data" "none")
STAFF_JWT=$(echo "$response" | jq -r '.access_token')
if [ -n "$STAFF_JWT" ] && [ "$STAFF_JWT" != "null" ]; then
    print_success "員工登入成功，獲取 JWT"
else
    print_error "員工登入失敗: $response"
fi

print_test "使用 JWT 獲取員工個人資料"
response=$(api_call "GET" "/api/v1/staff/me/profile" "" "staff")
echo "DEBUG: Raw response from get profile: $response"
profile_id=$(echo "$response" | jq -r '.id')
if [ "$profile_id" == "$STAFF_ID" ]; then
    print_success "成功獲取員工資料"
else
    print_error "獲取員工個人資料失敗: $response"
fi

# 5. 票券創建與簽到
print_header "5. 票券創建與簽到"
print_test "商戶為活動創建票券"
# Corrected field names to holder_name and holder_email, removed trailing slash from URL, and removed optional ticket_type_id
# Also added a debug echo statement.
ticket_data=$(printf '{ "event_id": %s, "holder_name": "王大明", "holder_email": "ming@test.com" }' "$EVENT_ID")
response=$(api_call "POST" "/api/v1/mgmt/tickets" "$ticket_data" "merchant")
echo "DEBUG: Raw response from create ticket: $response"
TICKET_ID=$(echo "$response" | jq -r '.id')
TICKET_UUID=$(echo "$response" | jq -r '.uuid')
if [ -n "$TICKET_ID" ] && [ "$TICKET_ID" != "null" ] && [ -n "$TICKET_UUID" ] && [ "$TICKET_UUID" != "null" ]; then
    print_success "票券創建成功 (ID: $TICKET_ID, UUID: $TICKET_UUID)"
else
    print_error "票券創建失敗: $response"
fi

print_test "為票券獲取 QR Token"
echo "DEBUG: Calling /api/v1/public/tickets/$TICKET_UUID/qr-token"
response=$(api_call "GET" "/api/v1/public/tickets/$TICKET_UUID/qr-token" "" "none")
echo "DEBUG: Raw response from get qr token: $response"
QR_TOKEN=$(echo "$response" | jq -r '.qr_token')
if [ -n "$QR_TOKEN" ] && [ "$QR_TOKEN" != "null" ]; then
    print_success "成功獲取 QR Token"
else
    print_error "獲取 QR Token 失敗: $response"
fi


print_test "員工使用 JWT 進行簽到"
checkin_data=$(printf '{ "qr_token": "%s", "event_id": %s }' "$QR_TOKEN" "$EVENT_ID")
response=$(api_call "POST" "/api/v1/staff/checkin/" "$checkin_data" "staff")
if [[ $(echo "$response" | jq -r '.message') == "Check-in successful" ]]; then
    print_success "簽到成功"
else
    print_error "簽到失敗: $response"
fi

# 6. 公開端點測試
print_header "6. 公開 (Public) 端點測試"
print_test "查詢公開票券資訊"
response=$(api_call "GET" "/api/v1/public/tickets/$TICKET_UUID" "" "none")
if [[ $(echo "$response" | jq -r '.uuid') == "$TICKET_UUID" ]]; then
    print_success "成功獲取公開票券資訊"
else
    print_error "獲取公開票券資訊失敗: $response"
fi

# 7. 認證失敗測試
print_header "7. 認證失敗測試"
print_test "無 Admin Password 訪問 Admin API"
status=$(curl -s -o /dev/null -w "%{http_code}" -X GET "$API_BASE_URL/admin/merchants")
if [[ "$status" == "422" ]]; then
    print_success "正確拒絕無 Admin Password 的請求 (Status: $status)"
else
    print_error "應拒絕無 Admin Password 的請求，但收到 (Status: $status)"
fi

print_test "無 API Key 訪問 Merchant API"
status=$(curl -s -o /dev/null -w "%{http_code}" -X GET "$API_BASE_URL/api/v1/mgmt/events")
if [[ "$status" == "422" ]]; then
    print_success "正確拒絕無 API Key 的請求 (Status: $status)"
else
    print_error "應拒絕無 API Key 的請求，但收到 (Status: $status)"
fi

print_test "無 JWT 訪問 Staff API"
checkin_data_fail=$(printf '{ "qr_token": "%s", "event_id": %s }' "$QR_TOKEN" "$EVENT_ID")
status=$(curl -s -o /dev/null -w "%{http_code}" -X POST -H "$CONTENT_TYPE" -d "$checkin_data_fail" "$API_BASE_URL/api/v1/staff/checkin/")
if [[ "$status" == "401" ]]; then
    print_success "正確拒絕無 JWT 的請求 (Status: $status)"
else
    print_error "應拒絕無 JWT 的請求，但收到 (Status: $status)"
fi

echo -e "\n${GREEN}🎉🎉🎉 所有 API 流程與認證測試成功完成！ 🎉🎉🎉${NC}\n"

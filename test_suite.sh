#!/bin/bash

# QR Check-in System 測試套件
# 包含所有可用的測試腳本

set -e

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

print_info() {
    echo -e "${YELLOW}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

show_menu() {
    print_header "QR Check-in System 測試套件"
    echo -e "${PURPLE}選擇要執行的測試：${NC}"
    echo ""
    echo "1) 快速 API 測試 (test_api_quick.sh)"
    echo "2) 認證機制測試 (test_api_auth.sh)"
    echo "3) 真實 API 測試 (test_real_apis.sh)"
    echo "4) 完整 API 測試 (test_complete_apis.sh)"
    echo "5) 多租戶功能測試 (test_multi_tenant_apis.py)"
    echo "6) 運行所有測試"
    echo "7) 檢查服務狀態"
    echo "8) 顯示 API 文檔連結"
    echo "0) 退出"
    echo ""
}

check_services() {
    print_header "檢查服務狀態"
    
    echo -e "${YELLOW}📊 Docker 容器狀態：${NC}"
    docker-compose ps
    
    echo -e "\n${YELLOW}🔗 服務連線測試：${NC}"
    
    # 測試 API 服務
    if curl -s http://localhost:8000/health > /dev/null; then
        print_success "API 服務 (http://localhost:8000) - 正常"
    else
        echo -e "${RED}❌ API 服務 (http://localhost:8000) - 無法連線${NC}"
    fi
    
    # 測試 Gradio 服務
    if curl -s http://localhost:7860 > /dev/null; then
        print_success "Gradio 管理介面 (http://localhost:7860) - 正常"
    else
        echo -e "${RED}❌ Gradio 管理介面 (http://localhost:7860) - 無法連線${NC}"
    fi
    
    # 測試資料庫連線
    if docker exec qr-checkin-system-db-1 pg_isready -U qr_admin > /dev/null 2>&1; then
        print_success "PostgreSQL 資料庫 - 正常"
    else
        echo -e "${RED}❌ PostgreSQL 資料庫 - 無法連線${NC}"
    fi
}

show_api_docs() {
    print_header "API 文檔和服務連結"
    
    echo -e "${BLUE}📖 API 文檔：${NC}"
    echo "  🔗 Swagger UI: http://localhost:8000/docs"
    echo "  📋 ReDoc: http://localhost:8000/redoc"
    echo "  📄 OpenAPI Schema: http://localhost:8000/openapi.json"
    
    echo -e "\n${BLUE}🎛️ 管理介面：${NC}"
    echo "  🖥️ Gradio 管理: http://localhost:7860"
    
    echo -e "\n${BLUE}🔧 服務端點：${NC}"
    echo "  ❤️ 健康檢查: http://localhost:8000/health"
    echo "  🏠 API 根路由: http://localhost:8000/"
    
    echo -e "\n${BLUE}🔑 認證資訊：${NC}"
    echo "  📝 管理員 API Key: db0d665cb28e6a58dfce3461b9d38ba1"
    echo "  🏢 商戶 API Key: qr_uaIPi98rFvDQqUpPeBqePwZGwVr3jJ5a"
    echo "  👤 範例員工 ID: 1"
    
    echo -e "\n${YELLOW}💡 使用範例：${NC}"
    echo '  curl -H "X-API-Key: db0d665cb28e6a58dfce3461b9d38ba1" http://localhost:8000/admin/merchants'
    echo '  curl -H "X-API-Key: qr_uaIPi98rFvDQqUpPeBqePwZGwVr3jJ5a" -H "Staff-Id: 1" http://localhost:8000/api/events'
}

run_all_tests() {
    print_header "執行所有測試"
    
    echo -e "${YELLOW}1/5 執行快速 API 測試...${NC}"
    ./test_api_quick.sh > /tmp/quick_test.log 2>&1
    if [ $? -eq 0 ]; then
        print_success "快速測試完成"
    else
        echo -e "${RED}❌ 快速測試失敗${NC}"
    fi
    
    echo -e "\n${YELLOW}2/5 執行認證測試...${NC}"
    ./test_api_auth.sh > /tmp/auth_test.log 2>&1
    if [ $? -eq 0 ]; then
        print_success "認證測試完成"
    else
        echo -e "${RED}❌ 認證測試失敗${NC}"
    fi
    
    echo -e "\n${YELLOW}3/5 執行真實 API 測試...${NC}"
    ./test_real_apis.sh > /tmp/real_test.log 2>&1
    if [ $? -eq 0 ]; then
        print_success "真實 API 測試完成"
    else
        echo -e "${RED}❌ 真實 API 測試失敗${NC}"
    fi
    
    echo -e "\n${YELLOW}4/5 執行多租戶測試...${NC}"
    if [ -f "test_multi_tenant_apis.py" ]; then
        python3 test_multi_tenant_apis.py > /tmp/multi_tenant_test.log 2>&1
        if [ $? -eq 0 ]; then
            print_success "多租戶測試完成"
        else
            echo -e "${RED}❌ 多租戶測試失敗${NC}"
        fi
    else
        echo -e "${YELLOW}⚠️ 多租戶測試腳本不存在${NC}"
    fi
    
    echo -e "\n${YELLOW}5/5 檢查服務狀態...${NC}"
    check_services
    
    echo -e "\n${GREEN}🎉 所有測試執行完畢！${NC}"
    echo -e "${YELLOW}📄 詳細日誌檔案：${NC}"
    echo "  - /tmp/quick_test.log"
    echo "  - /tmp/auth_test.log"
    echo "  - /tmp/real_test.log"
    echo "  - /tmp/multi_tenant_test.log"
}

main() {
    while true; do
        show_menu
        read -p "請選擇 [0-8]: " choice
        
        case $choice in
            1)
                print_info "執行快速 API 測試..."
                ./test_api_quick.sh
                ;;
            2)
                print_info "執行認證機制測試..."
                ./test_api_auth.sh
                ;;
            3)
                print_info "執行真實 API 測試..."
                ./test_real_apis.sh
                ;;
            4)
                print_info "執行完整 API 測試..."
                ./test_complete_apis.sh
                ;;
            5)
                if [ -f "test_multi_tenant_apis.py" ]; then
                    print_info "執行多租戶功能測試..."
                    python3 test_multi_tenant_apis.py
                else
                    echo -e "${RED}❌ 多租戶測試腳本不存在${NC}"
                fi
                ;;
            6)
                run_all_tests
                ;;
            7)
                check_services
                ;;
            8)
                show_api_docs
                ;;
            0)
                echo -e "${GREEN}再見！${NC}"
                exit 0
                ;;
            *)
                echo -e "${RED}無效選擇，請重試${NC}"
                ;;
        esac
        
        echo ""
        read -p "按 Enter 繼續..."
    done
}

# 檢查必要的測試腳本是否存在
missing_scripts=()
for script in "test_api_quick.sh" "test_api_auth.sh" "test_real_apis.sh" "test_complete_apis.sh"; do
    if [ ! -f "$script" ]; then
        missing_scripts+=("$script")
    fi
done

if [ ${#missing_scripts[@]} -gt 0 ]; then
    echo -e "${RED}❌ 缺少以下測試腳本：${NC}"
    for script in "${missing_scripts[@]}"; do
        echo "  - $script"
    done
    echo ""
    echo -e "${YELLOW}請確保所有測試腳本都存在於當前目錄中${NC}"
    exit 1
fi

# 確保測試腳本有執行權限
chmod +x test_api_quick.sh test_api_auth.sh test_real_apis.sh test_complete_apis.sh 2>/dev/null || true

# 執行主函數
main "$@"

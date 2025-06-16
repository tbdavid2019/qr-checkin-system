#!/bin/bash
# Docker 一鍵部署腳本 (AWS Linux 專用)

set -e

# 顏色輸出
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}🐳 QR Check-in System AWS Docker 部署${NC}"
echo "============================================="

# 檢查是否為 root 或有 sudo 權限
if [[ $EUID -eq 0 ]]; then
   echo -e "${GREEN}✅ Root 權限確認${NC}"
elif sudo -n true 2>/dev/null; then
   echo -e "${GREEN}✅ Sudo 權限確認${NC}"
else
   echo -e "${RED}❌ 需要 root 或 sudo 權限${NC}"
   exit 1
fi

# 更新系統
echo -e "${BLUE}📦 更新系統套件...${NC}"
if command -v yum &> /dev/null; then
    # Amazon Linux / CentOS / RHEL
    sudo yum update -y
elif command -v apt &> /dev/null; then
    # Ubuntu / Debian
    sudo apt update && sudo apt upgrade -y
fi

# 安裝 Docker
if ! command -v docker &> /dev/null; then
    echo -e "${BLUE}🐳 安裝 Docker...${NC}"
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo systemctl start docker
    sudo systemctl enable docker
    sudo usermod -aG docker $USER
    rm get-docker.sh
    echo -e "${GREEN}✅ Docker 安裝完成${NC}"
else
    echo -e "${GREEN}✅ Docker 已安裝${NC}"
fi

# 安裝 Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo -e "${BLUE}🔧 安裝 Docker Compose...${NC}"
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    echo -e "${GREEN}✅ Docker Compose 安裝完成${NC}"
else
    echo -e "${GREEN}✅ Docker Compose 已安裝${NC}"
fi

# 創建工作目錄
PROJECT_DIR="/opt/qr-checkin-system"
sudo mkdir -p $PROJECT_DIR
sudo chown $USER:$USER $PROJECT_DIR
cd $PROJECT_DIR

# 如果當前目錄不是專案目錄，則複製文件
if [ ! -f "docker-compose.yml" ]; then
    echo -e "${BLUE}📁 請將專案文件上傳到 $PROJECT_DIR${NC}"
    echo "您可以使用以下方法之一："
    echo "1. git clone 您的倉庫"
    echo "2. scp 上傳文件"
    echo "3. 使用 rsync 同步"
    echo ""
    echo "完成後請重新運行此腳本"
    exit 0
fi

# 設置環境變數
if [ ! -f ".env" ]; then
    echo -e "${BLUE}⚙️ 設置環境變數...${NC}"
    
    # 生成安全密鑰
    SECRET_KEY=$(openssl rand -hex 32)
    API_KEY=$(openssl rand -hex 16)
    
    cat > .env << EOF
# 生產環境配置
DATABASE_URL=postgresql://qr_admin:qr_pass@db:5432/qr_system
POSTGRES_USER=qr_admin
POSTGRES_PASSWORD=qr_pass
POSTGRES_DB=qr_system

# 多租戶設定
ENABLE_MULTI_TENANT=1

# 安全設定
SECRET_KEY=${SECRET_KEY}
API_KEY=${API_KEY}
ADMIN_PASSWORD=admin123

# 服務設定
API_PORT=8000
GRADIO_PORT=7860
DEBUG=False
ENVIRONMENT=production
EOF
    
    echo -e "${GREEN}✅ 環境變數配置完成${NC}"
    echo -e "${RED}⚠️  請記住修改 ADMIN_PASSWORD${NC}"
fi

# 創建必要目錄
mkdir -p logs backups
chmod 755 logs backups

# 配置防火牆 (如果需要)
if command -v firewall-cmd &> /dev/null; then
    echo -e "${BLUE}🔥 配置防火牆...${NC}"
    sudo firewall-cmd --permanent --add-port=8000/tcp
    sudo firewall-cmd --permanent --add-port=7860/tcp
    sudo firewall-cmd --reload
elif command -v ufw &> /dev/null; then
    echo -e "${BLUE}🔥 配置防火牆...${NC}"
    sudo ufw allow 8000
    sudo ufw allow 7860
fi

# 部署服務
echo -e "${BLUE}🚀 部署 Docker 服務...${NC}"
docker-compose down 2>/dev/null || true
docker-compose up -d --build

# 等待服務啟動
echo -e "${BLUE}⏳ 等待服務啟動...${NC}"
sleep 30

# 檢查服務狀態
echo -e "${BLUE}🔍 檢查服務狀態...${NC}"
docker-compose ps

# 健康檢查
if curl -f http://localhost:8000/health &>/dev/null; then
    echo -e "${GREEN}✅ API 服務正常${NC}"
else
    echo -e "${RED}❌ API 服務異常${NC}"
    docker-compose logs api
fi

if curl -f http://localhost:7860 &>/dev/null; then
    echo -e "${GREEN}✅ 管理介面正常${NC}"
else
    echo -e "${RED}⚠️  管理介面可能需要更多時間啟動${NC}"
fi

# 顯示完成信息
echo ""
echo "============================================="
echo -e "${GREEN}🎉 部署完成！${NC}"
echo "============================================="
echo ""
echo "📍 服務訪問："
echo "  - API: http://$(curl -s ifconfig.me):8000"
echo "  - 管理介面: http://$(curl -s ifconfig.me):7860"
echo "  - API 文檔: http://$(curl -s ifconfig.me):8000/docs"
echo ""
echo "🔐 管理員密碼: admin123 (請立即修改)"
echo ""
echo "📊 管理指令："
echo "  - 查看狀態: docker-compose ps"
echo "  - 查看日誌: docker-compose logs -f"
echo "  - 停止服務: docker-compose down"
echo "  - 重啟服務: docker-compose restart"
echo ""
echo "📁 重要路徑："
echo "  - 專案目錄: $PROJECT_DIR"
echo "  - 環境配置: $PROJECT_DIR/.env"
echo "  - 日誌目錄: $PROJECT_DIR/logs"
echo ""

# 設置系統服務 (可選)
read -p "是否設置為系統服務？(y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    cat > /tmp/qr-checkin.service << EOF
[Unit]
Description=QR Check-in System
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=$PROJECT_DIR
ExecStart=/usr/local/bin/docker-compose up -d
ExecStop=/usr/local/bin/docker-compose down
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
EOF

    sudo mv /tmp/qr-checkin.service /etc/systemd/system/
    sudo systemctl daemon-reload
    sudo systemctl enable qr-checkin.service
    
    echo -e "${GREEN}✅ 系統服務設置完成${NC}"
    echo "使用 'sudo systemctl start qr-checkin' 啟動"
    echo "使用 'sudo systemctl status qr-checkin' 查看狀態"
fi

echo ""
echo -e "${GREEN}🚀 QR Check-in System 已成功部署到 AWS！${NC}"

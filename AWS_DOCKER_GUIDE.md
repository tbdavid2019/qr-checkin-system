# QR Check-in System AWS Docker 部署快速指南

## 🚀 一鍵部署到 AWS Linux

### 1. 準備 AWS EC2 實例
```bash
# 建議配置：
# - Instance Type: t3.medium 或更高
# - OS: Amazon Linux 2 或 Ubuntu 20.04+
# - Storage: 20GB+
# - Security Group: 開放 22, 8000, 7860 端口
```

### 2. 上傳專案文件
```bash
# 方法一：使用 git (推薦)
ssh -i your-key.pem ec2-user@your-ec2-ip
git clone https://github.com/your-repo/qr-checkin-system.git
cd qr-checkin-system

# 方法二：使用 scp 上傳
scp -i your-key.pem -r /path/to/qr-checkin-system ec2-user@your-ec2-ip:~/

# 方法三：使用 rsync
rsync -avz -e "ssh -i your-key.pem" /path/to/qr-checkin-system/ ec2-user@your-ec2-ip:~/qr-checkin-system/
```

### 3. 一鍵部署
```bash
# 在 EC2 實例上執行
chmod +x aws-docker-deploy.sh
./aws-docker-deploy.sh
```

## 🔧 手動部署步驟

### 1. 安裝 Docker
```bash
# Amazon Linux 2
sudo yum update -y
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker $USER

# Ubuntu
sudo apt update
sudo apt install docker.io docker-compose -y
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker $USER
```

### 2. 安裝 Docker Compose
```bash
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### 3. 配置環境
```bash
# 複製環境配置
cp .env.production .env

# 生成安全密鑰
SECRET_KEY=$(openssl rand -hex 32)
API_KEY=$(openssl rand -hex 16)

# 更新配置
sed -i "s/SECRET_KEY=.*/SECRET_KEY=${SECRET_KEY}/" .env
sed -i "s/API_KEY=.*/API_KEY=${API_KEY}/" .env
```

### 4. 部署服務
```bash
# 創建必要目錄
mkdir -p logs backups

# 啟動服務
docker-compose up -d --build

# 檢查狀態
docker-compose ps
docker-compose logs -f
```

## 🔍 驗證部署

### 1. 健康檢查
```bash
# API 健康檢查
curl http://localhost:8000/health

# 預期輸出
{"status": "healthy"}
```

### 2. 功能測試
```bash
# 運行多租戶測試
python test_multi_tenant.py

# 預期看到
🎉 所有測試都通過了！
```

### 3. 服務訪問
- **API 服務**: http://your-ec2-ip:8000
- **API 文檔**: http://your-ec2-ip:8000/docs
- **管理介面**: http://your-ec2-ip:7860

## 🔒 安全配置

### 1. 環境變數安全
```bash
# 修改預設密碼
nano .env

# 更新以下項目：
ADMIN_PASSWORD=your-strong-password
SECRET_KEY=your-generated-secret
API_KEY=your-generated-api-key
```

### 2. 防火牆配置
```bash
# Amazon Linux (firewalld)
sudo firewall-cmd --permanent --add-port=8000/tcp
sudo firewall-cmd --permanent --add-port=7860/tcp
sudo firewall-cmd --reload

# Ubuntu (ufw)
sudo ufw allow 8000
sudo ufw allow 7860
sudo ufw enable
```

### 3. SSL/HTTPS 設置
```bash
# 安裝 Nginx
sudo yum install nginx -y  # Amazon Linux
sudo apt install nginx -y  # Ubuntu

# 配置反向代理
sudo nano /etc/nginx/sites-available/qr-checkin
```

Nginx 配置範例：
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    location /admin {
        proxy_pass http://localhost:7860;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 📊 監控和維護

### 1. 服務監控
```bash
# 查看服務狀態
docker-compose ps

# 查看資源使用
docker stats

# 查看日誌
docker-compose logs -f api
docker-compose logs -f gradio
```

### 2. 備份策略
```bash
# 資料庫備份
docker-compose exec db pg_dump -U qr_admin qr_system > backup_$(date +%Y%m%d).sql

# 設置定時備份
crontab -e
# 添加：0 2 * * * /path/to/backup-script.sh
```

### 3. 更新部署
```bash
# 更新代碼
git pull

# 重新部署
docker-compose down
docker-compose up -d --build

# 運行遷移
docker-compose exec api alembic upgrade head
```

## 🔧 故障排除

### 常見問題

#### 1. 端口被佔用
```bash
# 檢查端口使用
sudo netstat -tulpn | grep :8000
sudo netstat -tulpn | grep :7860

# 停止衝突服務或修改端口
```

#### 2. Docker 權限問題
```bash
# 添加用戶到 docker 組
sudo usermod -aG docker $USER

# 重新登錄或執行
newgrp docker
```

#### 3. 記憶體不足
```bash
# 檢查記憶體使用
free -h

# 升級 EC2 實例或優化配置
```

#### 4. 服務無法啟動
```bash
# 查看詳細日誌
docker-compose logs --details

# 檢查配置文件
docker-compose config
```

## 📈 效能優化

### 1. 資源限制
```yaml
# docker-compose.yml 中的資源配置已優化
deploy:
  resources:
    limits:
      memory: 1G
      cpus: '1.0'
```

### 2. 資料庫優化
```sql
-- 執行索引優化
CREATE INDEX CONCURRENTLY idx_tickets_event_merchant ON tickets(event_id, merchant_id);
CREATE INDEX CONCURRENTLY idx_checkin_logs_event ON checkin_logs(event_id);
```

### 3. 快取配置
```bash
# 可選：添加 Redis 快取
# 在 docker-compose.yml 中添加 Redis 服務
```

## 🎯 生產環境檢查清單

- [ ] ✅ EC2 實例配置充足 (t3.medium+)
- [ ] ✅ 安全組配置正確 (22, 8000, 7860)
- [ ] ✅ Docker 和 Docker Compose 已安裝
- [ ] ✅ 環境變數配置安全
- [ ] ✅ 防火牆規則設置
- [ ] ✅ SSL/HTTPS 配置 (生產環境)
- [ ] ✅ 備份策略實施
- [ ] ✅ 監控系統設置
- [ ] ✅ 日誌輪轉配置
- [ ] ✅ 域名和 DNS 設置

---

**🎉 AWS Docker 部署完成！**

您的 QR Check-in System 現在運行在 AWS 雲端環境中，具備企業級的可靠性和擴展性。

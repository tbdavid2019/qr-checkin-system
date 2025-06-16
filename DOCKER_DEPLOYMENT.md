# QR Check-in System Docker 部署指南

## 🐳 Docker 容器化部署

Docker 部署方案具有以下優勢：
- ✅ 環境一致性，避免「在我機器上可以運行」的問題
- ✅ 資源隔離，更好的穩定性和安全性
- ✅ 易於擴展和遷移
- ✅ 簡化部署流程

## 📋 準備工作

### 1. 系統要求
- Docker 20.10+
- Docker Compose 2.0+
- 最小 2GB RAM
- 10GB 可用磁碟空間

### 2. 安裝 Docker
```bash
# Ubuntu/Debian
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# 安裝 Docker Compose
sudo apt-get install docker-compose-plugin

# 添加用戶到 docker 組
sudo usermod -aG docker $USER
```

## 🚀 快速部署

### 1. 下載和配置
```bash
# 克隆專案
git clone <your-repo-url>
cd qr-checkin-system

# 配置環境變數
cp .env.template .env
nano .env
```

### 2. 環境變數配置
編輯 `.env` 文件：
```bash
# 資料庫設定
DATABASE_URL=postgresql://qr_admin:qr_pass@db:5432/qr_system

# 多租戶設定
ENABLE_MULTI_TENANT=1

# 安全設定 (請修改為安全的值)
SECRET_KEY=your-super-secret-key-change-this-in-production
API_KEY=your-api-key-change-this-in-production
ADMIN_PASSWORD=your-admin-password-change-this

# 服務設定
GRADIO_PORT=7860
DEBUG=False
ENVIRONMENT=production
```

### 3. 一鍵部署
```bash
# 構建並啟動所有服務
docker-compose up -d

# 查看服務狀態
docker-compose ps

# 查看日誌
docker-compose logs -f
```

## 🔧 詳細配置說明

### Docker Compose 服務架構
```yaml
services:
  db:          # PostgreSQL 資料庫
  migrate:     # 資料庫遷移 (一次性)
  setup:       # 多租戶初始化 (一次性)
  api:         # FastAPI 主服務
  gradio:      # Gradio 管理介面
```

### 服務端口說明
- **8000**: FastAPI API 服務
- **7860**: Gradio 管理介面
- **5432**: PostgreSQL 資料庫 (僅內部網路)

### 資料持久化
- `db_data`: PostgreSQL 資料持久化卷

## ✅ 部署驗證

### 1. 健康檢查
```bash
# API 健康檢查
curl http://localhost:8000/health

# 預期回應
{"status": "healthy"}
```

### 2. 服務可用性檢查
```bash
# API 文檔
curl http://localhost:8000/docs

# Gradio 管理介面
curl http://localhost:7860
```

### 3. 多租戶功能測試
```bash
# 運行完整測試
python test_multi_tenant.py
```

## 🛠️ 運維指令

### 基本操作
```bash
# 啟動服務
docker-compose up -d

# 停止服務
docker-compose down

# 重啟服務
docker-compose restart

# 查看服務狀態
docker-compose ps

# 查看日誌
docker-compose logs -f [service_name]
```

### 資料庫操作
```bash
# 連接資料庫
docker-compose exec db psql -U qr_admin -d qr_system

# 資料庫備份
docker-compose exec db pg_dump -U qr_admin qr_system > backup.sql

# 資料庫還原
docker-compose exec -T db psql -U qr_admin -d qr_system < backup.sql
```

### 更新部署
```bash
# 更新代碼
git pull

# 重新構建並啟動
docker-compose up -d --build

# 運行新遷移
docker-compose run --rm migrate alembic upgrade head
```

## 🔒 生產環境安全設定

### 1. 環境變數安全
```bash
# 生成安全的密鑰
openssl rand -hex 32  # SECRET_KEY
openssl rand -hex 16  # API_KEY

# 設定安全的密碼
# ADMIN_PASSWORD 建議使用強密碼
```

### 2. 網路安全
```bash
# 僅暴露必要端口
# 在生產環境中，建議使用反向代理 (Nginx)
# 資料庫端口 5432 不應對外暴露
```

### 3. SSL/HTTPS 配置
建議在生產環境使用 Nginx 作為反向代理：
```nginx
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl;
    server_name your-domain.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    location /admin {
        proxy_pass http://localhost:7860;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 📊 監控和日誌

### 1. 日誌管理
```bash
# 查看 API 日誌
docker-compose logs -f api

# 查看 Gradio 日誌
docker-compose logs -f gradio

# 查看資料庫日誌
docker-compose logs -f db

# 導出日誌
docker-compose logs > system.log
```

### 2. 容器監控
```bash
# 查看資源使用
docker stats

# 查看容器詳情
docker-compose exec api ps aux
docker-compose exec api df -h
```

## 🔍 故障排除

### 常見問題

#### 1. 服務無法啟動
```bash
# 檢查端口衝突
netstat -tulpn | grep :8000
netstat -tulpn | grep :7860

# 檢查 Docker 狀態
sudo systemctl status docker

# 清理 Docker 緩存
docker system prune -a
```

#### 2. 資料庫連接失敗
```bash
# 檢查資料庫容器狀態
docker-compose logs db

# 測試資料庫連接
docker-compose exec db psql -U qr_admin -d qr_system -c "SELECT 1;"
```

#### 3. 遷移失敗
```bash
# 手動運行遷移
docker-compose run --rm migrate alembic upgrade head

# 檢查遷移狀態
docker-compose run --rm migrate alembic current
```

### 調試模式
```bash
# 開啟調試模式
export DEBUG=True

# 查看詳細日誌
docker-compose up --build
```

## 📈 性能優化

### 1. 資源配置
```yaml
# docker-compose.yml 中添加資源限制
services:
  api:
    deploy:
      resources:
        limits:
          memory: 512M
          cpus: '0.5'
        reservations:
          memory: 256M
          cpus: '0.25'
```

### 2. 資料庫優化
```sql
-- 創建索引以提升查詢性能
CREATE INDEX IF NOT EXISTS idx_tickets_event_id ON tickets(event_id);
CREATE INDEX IF NOT EXISTS idx_checkin_logs_event_id ON checkin_logs(event_id);
CREATE INDEX IF NOT EXISTS idx_staff_merchant_id ON staff(merchant_id);
```

## 🔄 備份策略

### 1. 自動備份腳本
```bash
#!/bin/bash
# backup.sh
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups"

# 創建備份目錄
mkdir -p $BACKUP_DIR

# 資料庫備份
docker-compose exec -T db pg_dump -U qr_admin qr_system > $BACKUP_DIR/db_backup_$DATE.sql

# 壓縮備份
gzip $BACKUP_DIR/db_backup_$DATE.sql

# 清理舊備份 (保留 7 天)
find $BACKUP_DIR -name "*.sql.gz" -mtime +7 -delete

echo "Backup completed: db_backup_$DATE.sql.gz"
```

### 2. 設定定時備份
```bash
# 添加到 crontab
crontab -e

# 每天凌晨 2 點備份
0 2 * * * /path/to/backup.sh
```

## 🌐 AWS/雲端部署

### 1. AWS EC2 部署
```bash
# 1. 創建 EC2 實例 (t3.medium 推薦)
# 2. 安裝 Docker
sudo yum update -y
sudo yum install -y docker
sudo systemctl start docker
sudo systemctl enable docker

# 3. 部署應用
git clone <your-repo>
cd qr-checkin-system
docker-compose up -d
```

### 2. 環境變數配置
```bash
# AWS 環境變數
export DATABASE_URL="postgresql://user:pass@rds-endpoint:5432/dbname"
export SECRET_KEY="$(openssl rand -hex 32)"
export API_KEY="$(openssl rand -hex 16)"
```

## 📚 相關文檔

- [AWS 部署指南](AWS_DEPLOYMENT.md)
- [多租戶功能文檔](MULTI_TENANT_REPORT.md)
- [安全配置說明](SECURITY.md)
- [API 文檔](README.md#api-使用說明)

---

**Docker 部署完成！🎉**

您的 QR Check-in System 現在運行在容器化環境中，具備：
- ✅ 高可用性和穩定性
- ✅ 資源隔離和安全性
- ✅ 易於擴展和維護
- ✅ 完整的多租戶支援

訪問您的服務：
- API 服務: http://localhost:8000
- 管理介面: http://localhost:7860
- API 文檔: http://localhost:8000/docs

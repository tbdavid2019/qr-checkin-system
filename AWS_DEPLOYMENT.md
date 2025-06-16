# AWS Linux 部署指南

## 🚀 快速部署 (推薦)

### 1. 準備 AWS Linux 實例

```bash
# 在 AWS 上創建 EC2 實例 (Amazon Linux 2023)
# 實例類型: t3.small 或更高
# 安全組開放端口: 22, 8000, 7860, 5432

# SSH 連接到實例
ssh -i your-key.pem ec2-user@your-instance-ip
```

### 2. 一鍵部署腳本

```bash
# 1. 安裝必要軟件
sudo yum update -y
sudo yum install -y docker python3 python3-pip git

# 2. 啟動 Docker
sudo service docker start
sudo usermod -a -G docker ec2-user

# 3. 安裝 Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 4. 重新登入 (使 docker 群組生效)
exit
# 重新 SSH 連接

# 5. 上傳項目文件
# 方法1: Git clone (如果代碼在 Git 倉庫)
git clone <your-repository>
cd qr-checkin-system

# 方法2: SCP 上傳 (如果是本地代碼)
# 在本地執行: scp -i your-key.pem -r qr-checkin-system ec2-user@your-instance-ip:~/

# 6. 運行部署腳本
chmod +x deploy_aws.sh
./deploy_aws.sh
```

## 📋 手動部署步驟

### 1. 環境配置

```bash
# 創建 Python 虛擬環境
python3 -m venv myenv
source myenv/bin/activate

# 安裝 Python 依賴
pip install -r requirements.txt
```

### 2. 配置文件設置

```bash
# 複製配置模板
cp .env.template .env
cp alembic.ini.template alembic.ini

# 編輯 .env 文件
nano .env
```

#### .env 配置示例 (AWS 環境)

```bash
# 資料庫配置
DATABASE_URL=postgresql://qr_admin:qr_pass@localhost:5432/qr_system

# JWT 配置  
SECRET_KEY=your-super-secure-production-key-change-this
ACCESS_TOKEN_EXPIRE_MINUTES=43200

# API 配置
API_KEY=your-production-api-key-change-this

# 多租戶功能
ENABLE_MULTI_TENANT=1

# Gradio 管理介面配置
ADMIN_PASSWORD=your-admin-password-change-this
GRADIO_PORT=7860

# QR Code 配置
QR_TOKEN_EXPIRE_HOURS=168

# 生產環境設定
DEBUG=False
ENVIRONMENT=production
```

#### alembic.ini 配置

```bash
# 編輯 alembic.ini
nano alembic.ini

# 修改資料庫 URL
sqlalchemy.url = postgresql://qr_admin:qr_pass@localhost:5432/qr_system
```

### 3. 啟動 PostgreSQL

```bash
# 啟動 PostgreSQL 容器
docker-compose up -d

# 檢查容器狀態
docker-compose ps

# 查看日誌 (如有問題)
docker-compose logs db
```

### 4. 初始化資料庫

```bash
# 運行資料庫遷移
alembic upgrade head

# 設置多租戶示例數據
python setup_multi_tenant.py
```

### 5. 啟動服務

```bash
# 方法1: 前台運行 (測試用)
uvicorn app.main:app --host 0.0.0.0 --port 8000

# 方法2: 後台運行 (生產用)
nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 > api.log 2>&1 &

# 啟動管理介面 (另一個終端)
source myenv/bin/activate
nohup python gradio_admin.py > gradio.log 2>&1 &
```

## 🔒 AWS 安全組設置

### 入站規則

| 類型 | 協議 | 端口範圍 | 來源 | 說明 |
|------|------|----------|------|------|
| SSH | TCP | 22 | Your IP | SSH 連接 |
| HTTP | TCP | 8000 | 0.0.0.0/0 | API 服務 |
| Custom TCP | TCP | 7860 | Your IP | 管理介面 |
| PostgreSQL | TCP | 5432 | 127.0.0.1/32 | 資料庫 (本機) |

### 出站規則

| 類型 | 協議 | 端口範圍 | 目標 | 說明 |
|------|------|----------|------|------|
| All traffic | All | All | 0.0.0.0/0 | 允許所有出站 |

## 🧪 驗證部署

### 1. 健康檢查

```bash
# 檢查 API 服務
curl http://localhost:8000/health

# 檢查資料庫連接
docker-compose exec db psql -U qr_admin -d qr_system -c "SELECT 1;"

# 運行完整測試
python test_multi_tenant.py
```

### 2. 訪問服務

- **API 文檔**: `http://your-server-ip:8000/docs`
- **管理介面**: `http://your-server-ip:7860`
- **健康檢查**: `http://your-server-ip:8000/health`

## 🛠️ 生產環境優化

### 1. 系統服務設置

```bash
# 創建 systemd 服務文件
sudo nano /etc/systemd/system/qr-checkin-api.service
```

```ini
[Unit]
Description=QR Check-in API Service
After=network.target

[Service]
Type=simple
User=ec2-user
WorkingDirectory=/home/ec2-user/qr-checkin-system
Environment=PATH=/home/ec2-user/qr-checkin-system/myenv/bin
ExecStart=/home/ec2-user/qr-checkin-system/myenv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# 啟用服務
sudo systemctl daemon-reload
sudo systemctl enable qr-checkin-api
sudo systemctl start qr-checkin-api

# 檢查服務狀態
sudo systemctl status qr-checkin-api
```

### 2. Nginx 反向代理 (可選)

```bash
# 安裝 Nginx
sudo yum install -y nginx

# 配置 Nginx
sudo nano /etc/nginx/conf.d/qr-checkin.conf
```

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /admin-ui {
        proxy_pass http://127.0.0.1:7860;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
# 啟動 Nginx
sudo systemctl enable nginx
sudo systemctl start nginx
```

### 3. 備份設置

```bash
# 創建備份腳本
nano backup.sh
```

```bash
#!/bin/bash
BACKUP_DIR="/home/ec2-user/backups"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# 備份資料庫
docker-compose exec -T db pg_dump -U qr_admin qr_system > $BACKUP_DIR/db_backup_$DATE.sql

# 備份配置文件
tar -czf $BACKUP_DIR/config_backup_$DATE.tar.gz .env alembic.ini

# 保留最近 7 天的備份
find $BACKUP_DIR -name "*.sql" -mtime +7 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete

echo "備份完成: $DATE"
```

```bash
# 設置定時備份
chmod +x backup.sh
(crontab -l 2>/dev/null; echo "0 2 * * * /home/ec2-user/qr-checkin-system/backup.sh") | crontab -
```

## 🔍 故障排除

### 常見問題

1. **Docker 權限問題**
   ```bash
   sudo usermod -a -G docker ec2-user
   # 重新登入
   ```

2. **PostgreSQL 連接失敗**
   ```bash
   docker-compose logs db
   docker-compose restart db
   ```

3. **Python 依賴問題**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt --force-reinstall
   ```

4. **端口被占用**
   ```bash
   sudo netstat -tlnp | grep :8000
   sudo kill -9 <PID>
   ```

### 日誌查看

```bash
# API 服務日誌
tail -f api.log

# Gradio 服務日誌
tail -f gradio.log

# 系統服務日誌
sudo journalctl -u qr-checkin-api -f

# Docker 日誌
docker-compose logs -f
```

## 📞 技術支援

- **API 文檔**: `/docs` 端點
- **健康檢查**: `/health` 端點
- **測試腳本**: `test_multi_tenant.py`
- **詳細文檔**: `README.md`, `MULTI_TENANT_REPORT.md`

---

部署完成後，您將擁有一個完整的企業級多租戶票券管理系統！🎉

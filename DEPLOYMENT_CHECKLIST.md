# QR Check-in System 部署檢查清單

## 📋 Docker 部署前檢查

### 開發環境 (Mac) - 準備階段
- [ ] ✅ 所有代碼已完成並測試
- [ ] ✅ 環境配置文件已準備 (.env.production)
- [ ] ✅ Docker 文件已完善 (Dockerfile, docker-compose.yml)
- [ ] ✅ 部署腳本已設置執行權限
- [ ] ✅ 代碼已推送到 Git 倉庫
- [ ] ✅ 敏感文件已加入 .gitignore

### AWS 環境 - 部署階段
- [ ] 🎯 EC2 實例已創建並運行
  - [ ] Instance Type: t3.medium 或更高
  - [ ] Storage: 20GB+
  - [ ] Security Group: 22, 8000, 7860 端口已開放
- [ ] 🔐 SSH 密鑰已配置
- [ ] 🌐 彈性 IP 已分配 (可選，但建議)

## 🚀 AWS 部署步驟

### 1. 連接到 EC2
```bash
ssh -i your-key.pem ec2-user@your-ec2-ip
```

### 2. 下載專案
```bash
# 使用 Git (推薦)
git clone https://github.com/your-repo/qr-checkin-system.git
cd qr-checkin-system

# 或上傳文件 (從本機)
scp -i your-key.pem -r /path/to/qr-checkin-system ec2-user@your-ec2-ip:~/
```

### 3. 執行一鍵部署
```bash
chmod +x aws-docker-deploy.sh
./aws-docker-deploy.sh
```

## ✅ 部署後驗證

### 服務檢查
- [ ] 🔍 API 健康檢查: `curl http://localhost:8000/health`
- [ ] 🔍 管理介面: `curl http://localhost:7860`
- [ ] 🔍 資料庫連接: `docker-compose exec db psql -U qr_admin -d qr_system -c "SELECT 1;"`
- [ ] 🔍 服務狀態: `docker-compose ps`

### 功能測試
- [ ] 🧪 多租戶測試: `python test_multi_tenant.py`
- [ ] 🧪 API 文檔訪問: `http://your-ip:8000/docs`
- [ ] 🧪 管理介面登入: `http://your-ip:7860`

### 外部訪問
- [ ] 🌐 外部 API 訪問: `curl http://your-ec2-ip:8000/health`
- [ ] 🌐 外部管理介面: `http://your-ec2-ip:7860`

## 🔒 安全配置

### 必須完成
- [ ] ⚠️ 修改預設管理員密碼
- [ ] ⚠️ 檢查 .env 中的安全設置
- [ ] ⚠️ 確認敏感端口僅對需要的 IP 開放

### 建議完成
- [ ] 🛡️ 設置 SSL/HTTPS (Nginx + Let's Encrypt)
- [ ] 🛡️ 配置防火牆規則
- [ ] 🛡️ 設置資料庫備份
- [ ] 🛡️ 配置日誌輪轉

## 📊 監控設置

### 基本監控
- [ ] 📈 設置 CloudWatch 監控 (AWS)
- [ ] 📈 配置日誌收集
- [ ] 📈 設置磁碟空間監控

### 應用監控
- [ ] 🔔 健康檢查端點監控
- [ ] 🔔 資料庫連接監控
- [ ] 🔔 錯誤日誌警報

## 🔄 備份策略

### 資料備份
- [ ] 💾 設置自動資料庫備份
- [ ] 💾 測試備份恢復流程
- [ ] 💾 設置異地備份 (S3)

### 配置備份
- [ ] 💾 備份 .env 配置文件
- [ ] 💾 備份 Docker 配置文件
- [ ] 💾 備份部署腳本

## 📚 文檔和交接

### 部署文檔
- [ ] 📝 記錄最終的服務訪問地址
- [ ] 📝 記錄管理員帳號資訊
- [ ] 📝 記錄重要的環境變數
- [ ] 📝 記錄常用運維指令

### 維護指南
- [ ] 📖 創建運維手冊
- [ ] 📖 記錄故障排除步驟
- [ ] 📖 記錄更新部署流程

## 🎯 最終檢查

### 系統穩定性
- [ ] ⏰ 系統已運行 30 分鐘以上
- [ ] ⏰ 無錯誤日誌產生
- [ ] ⏰ 記憶體和 CPU 使用正常

### 功能完整性
- [ ] ✨ 所有 API 端點正常響應
- [ ] ✨ 多租戶功能工作正常
- [ ] ✨ 管理介面功能完整
- [ ] ✨ 資料庫讀寫正常

### 效能表現
- [ ] 🚀 API 響應時間 < 500ms
- [ ] 🚀 頁面載入時間 < 3s
- [ ] 🚀 並發處理能力測試通過

---

## 🎉 部署完成確認

當所有檢查項目都完成後，您的 QR Check-in System 就成功部署到 AWS 了！

### 📍 最終訪問地址
- **API 服務**: `http://your-ec2-ip:8000`
- **API 文檔**: `http://your-ec2-ip:8000/docs`
- **管理介面**: `http://your-ec2-ip:7860`
- **健康檢查**: `http://your-ec2-ip:8000/health`

### 🔐 重要資訊
- **管理員密碼**: 記錄在 `.env` 文件中
- **API Key**: 記錄在 `.env` 文件中
- **資料庫密碼**: 記錄在 `.env` 文件中

### 📞 支援資訊
- **部署文檔**: `AWS_DOCKER_GUIDE.md`
- **系統文檔**: `README.md`
- **多租戶說明**: `MULTI_TENANT_REPORT.md`
- **安全說明**: `SECURITY.md`

**恭喜！您的 QR Check-in System 已成功部署並可投入生產使用！** 🎊

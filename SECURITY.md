# 安全配置說明

## ⚠️ 重要安全提醒

### 1. 敏感文件已被忽略
以下文件包含敏感資訊，已在 `.gitignore` 中設置為不追蹤：
- `alembic.ini` - 包含資料庫連接帳號密碼
- `.env` - 包含環境變數和密鑰
- `*.env.local`, `*.env.production` - 環境特定配置

### 2. 配置文件設置
1. **複製模板文件**：
   ```bash
   cp alembic.ini.template alembic.ini
   cp .env.template .env
   ```

2. **編輯 alembic.ini**：
   - 將 `postgresql://DB_USER:DB_PASSWORD@DB_HOST:DB_PORT/DB_NAME` 
   - 替換為實際的資料庫連接資訊
   - 例如：`postgresql://qr_admin:qr_pass@localhost:5432/qr_system`

3. **編輯 .env**：
   - 設置 `DATABASE_URL`
   - 更改 `SECRET_KEY` 為安全的隨機字串
   - 更改 `API_KEY` 為您的API密鑰

### 3. 生產環境安全建議
- 使用強密碼和複雜的密鑰
- 定期更換密鑰和密碼
- 使用 HTTPS 保護 API 通信
- 設置防火牆和網路安全規則
- 定期備份資料庫

### 4. 開發環境注意事項
- 不要在程式碼中硬編碼密碼
- 使用環境變數管理敏感配置
- 定期檢查 `.gitignore` 設置
- 避免在提交歷史中包含敏感資訊

## 📋 檢查清單
- [ ] 已複製並配置 `alembic.ini`
- [ ] 已複製並配置 `.env`
- [ ] 已驗證敏感文件不在 Git 追蹤中
- [ ] 已測試資料庫連接正常
- [ ] 已更改預設密鑰為安全值

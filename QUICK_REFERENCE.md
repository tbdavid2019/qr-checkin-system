# 🔐 當前測試憑證快速參考

## 📅 最後更新: 2025-06-23 02:58:39

## 🚀 一鍵測試
```bash
# 執行完整自動化測試
bash test_api_auth.sh
```

## 🔑 當前有效憑證

### 超級管理員
```
Admin Password: secure-admin-password-123
```

### 商戶 (最新測試生成)
```
商戶 ID: 53
API Key: qr_EKoHBUDPnRtnonUUrWFeB9vExlWjSXGE
商戶名稱: 測試商戶1750647514
```

### 員工 (最新測試生成)
```
員工 ID: 50
用戶名: staff-1750647514@test.com
密碼: password123
姓名: 測試員工
```

### 活動 (最新測試生成)
```
活動 ID: 46
活動名稱: 商戶核心測試活動
```

### 票券 (最新測試生成)
```
票券 ID: 69
票券 UUID: 98a82c23-f65e-4003-abbf-0c4729d047dd
票券代碼: 63RCJ0MX9MXK
持有人: 王大明
狀態: 已使用 (已簽到)
```

## 🌐 服務端點
- **API 文檔**: http://localhost:8000/docs
- **健康檢查**: http://localhost:8000/health
- **Gradio 管理**: http://localhost:7860

## 📋 快速 API 測試

### 1. 查詢票券資訊
```bash
curl http://localhost:8000/api/v1/public/tickets/98a82c23-f65e-4003-abbf-0c4729d047dd
```

### 2. 獲取 QR Token
```bash
curl http://localhost:8000/api/v1/public/tickets/98a82c23-f65e-4003-abbf-0c4729d047dd/qr-token
```

### 3. 員工登入
```bash
curl -X POST http://localhost:8000/api/v1/staff/login \
  -H "Content-Type: application/json" \
  -d '{"username":"staff-1750647514@test.com","password":"password123"}'
```

### 4. 創建新商戶
```bash
curl -X POST http://localhost:8000/admin/merchants \
  -H "X-Admin-Password: secure-admin-password-123" \
  -H "Content-Type: application/json" \
  -d '{"name":"新商戶","email":"new@test.com"}'
```

## ✅ 測試狀態
- 🟢 服務健康檢查
- 🟢 超級管理員操作  
- 🟢 商戶管理功能
- 🟢 員工登入與操作
- 🟢 票券創建與簽到
- 🟢 公開端點查詢
- 🟢 認證安全測試

**所有測試已通過！系統可正常使用。**

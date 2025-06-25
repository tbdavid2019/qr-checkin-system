# 會員票券查詢功能 - 技術文件

## 📋 功能概覽

會員票券查詢功能是 QR Check-in System 的一個重要組成部分，提供了一個用戶友善的網頁介面，讓持票人能夠輕鬆查詢自己的票券資訊。

## 🏗️ 架構設計

### 前端技術
- **HTML5**: 語意化標記結構
- **CSS3**: 現代化樣式設計，包含響應式布局
- **Vanilla JavaScript**: 純 JavaScript 實現，無外部依賴

### 後端整合
- **FastAPI StaticFiles**: 靜態檔案服務
- **FileResponse**: 特定路由回應
- **公開 API**: 整合現有的票券查詢 API

## 📁 檔案結構

```
app/
├── main.py              # FastAPI 主程式（包含靜態檔案設定）
└── static/
    └── member_ticket.html   # 會員查詢頁面
```

## 🔧 技術實現

### FastAPI 設定 (app/main.py)

```python
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# 掛載靜態檔案目錄
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# 會員票券查詢頁面路由
@app.get("/member-ticket", include_in_schema=False)
async def get_member_ticket_page():
    """Serves the member ticket lookup page."""
    return FileResponse('app/static/member_ticket.html')
```

### 前端功能 (member_ticket.html)

#### 1. 用戶介面設計
- **響應式布局**: 支援各種螢幕尺寸
- **現代化設計**: 漸層背景、卡片式布局、陰影效果
- **無障礙設計**: 適當的標籤和對比度

#### 2. JavaScript 功能
```javascript
async function lookupTicket() {
    const uuid = document.getElementById('ticketUuid').value.trim();
    
    // 呼叫公開 API
    const response = await fetch('/api/v1/public/tickets/' + uuid);
    const ticket = await response.json();
    
    // 顯示票券資訊
    displayTicketInfo(ticket);
}
```

#### 3. API 整合
- **票券查詢**: `GET /api/v1/public/tickets/{uuid}`
- **QR Code**: `GET /api/v1/public/tickets/{uuid}/qr`
- **錯誤處理**: 適當的 HTTP 狀態碼處理

## ✨ 功能特色

### 1. 直觀的用戶體驗
- **單一輸入框**: 只需輸入票券 UUID
- **即時回饋**: 查詢中狀態顯示
- **Enter 鍵支援**: 支援鍵盤快捷操作
- **自動聚焦**: 頁面載入時自動聚焦輸入框

### 2. 豐富的資訊顯示
- **活動資訊區塊**: 突出顯示活動詳情
- **票券狀態標籤**: 視覺化狀態指示
- **持票人資訊**: 安全顯示相關資訊
- **QR Code 區域**: 動態顯示入場憑證

### 3. 智慧化處理
- **狀態感知**: 已使用票券隱藏 QR Code
- **錯誤提示**: 友善的錯誤訊息
- **載入狀態**: 查詢過程中的視覺回饋
- **資料格式化**: 自動格式化日期時間

## 🎨 視覺設計

### 色彩方案
- **主色調**: 藍紫色漸層 (#667eea → #764ba2)
- **狀態色**: 綠色（有效）、紅色（已使用）
- **背景色**: 白色卡片 + 漸層背景
- **文字色**: 深灰色系，確保可讀性

### 布局設計
- **置中設計**: 主要內容居中顯示
- **卡片式**: 內容區域使用卡片設計
- **區塊分離**: 不同類型資訊使用不同背景色
- **圓角設計**: 現代化的圓角風格

## 📱 響應式設計

### 桌面版 (≥768px)
- 最大寬度 500px 的居中容器
- 充足的內邊距和間距
- 大尺寸的按鈕和輸入框

### 行動版 (<768px)
- 適應螢幕寬度的容器
- 調整內邊距適應小螢幕
- 優化觸控操作的元素大小

## 🔒 安全考量

### 資料保護
- **無敏感資料儲存**: 頁面不儲存任何敏感資訊
- **HTTPS 準備**: 支援 HTTPS 部署
- **API 限制**: 僅能存取公開 API 端點

### 隱私保護
- **最小化顯示**: 只顯示必要的票券資訊
- **無追蹤**: 不包含任何分析或追蹤代碼
- **本地處理**: 所有資料處理在本地進行

## 🚀 部署說明

### Docker 部署
靜態檔案會自動包含在 Docker 映像檔中：

```dockerfile
# Dockerfile 中已包含
COPY app/ /app/
```

### 手動部署
確保 `app/static/` 目錄存在並包含 HTML 檔案：

```bash
mkdir -p app/static/
# 複製 member_ticket.html 到 app/static/
```

## 🔧 自訂化選項

### 樣式自訂
- 修改 CSS 變數調整色彩方案
- 調整布局參數適應不同需求
- 加入公司 Logo 或品牌元素

### 功能擴展
- 加入多語言支援
- 整合社群分享功能
- 加入票券下載功能
- 整合推播通知

## 📊 效能最佳化

### 載入最佳化
- **單一檔案**: 所有資源包含在一個 HTML 檔案中
- **無外部依賴**: 不需要額外的 CSS/JS 檔案
- **快取友善**: 靜態檔案支援瀏覽器快取

### 網路最佳化
- **最小化 API 呼叫**: 單次查詢獲取所有資訊
- **錯誤處理**: 避免重複無效請求
- **逾時處理**: 適當的請求逾時設定

## 🧪 測試建議

### 功能測試
- 有效 UUID 查詢測試
- 無效 UUID 錯誤處理測試
- 已使用票券顯示測試
- 網路錯誤處理測試

### 跨瀏覽器測試
- Chrome、Firefox、Safari 相容性
- 行動瀏覽器測試
- 較舊瀏覽器相容性檢查

### 響應式測試
- 不同螢幕尺寸測試
- 橫豎屏切換測試
- 觸控操作測試

## 🔮 未來擴展

### 功能增強
- **PWA 支援**: 離線查詢能力
- **多主題**: 可切換的視覺主題
- **國際化**: 多語言支援
- **無障礙增強**: 更好的輔助技術支援

### 整合選項
- **第三方登入**: 社群帳號整合
- **支付整合**: 現場購票功能
- **地圖整合**: 活動地點地圖顯示
- **日曆整合**: 活動日程加入行事曆

---

*此文件最後更新：2025年6月25日*

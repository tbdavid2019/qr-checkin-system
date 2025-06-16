"""
Gradio 管理介面 - 多租戶管理
"""
import gradio as gr
import pandas as pd
from typing import List, Optional
from sqlalchemy.orm import Session
from datetime import datetime
from app.database import get_db
from services.merchant_service import MerchantService
from services.staff_service import StaffService
from services.event_service import EventService
from schemas.merchant import MerchantCreate, MerchantUpdate, ApiKeyCreate
from app.config import settings

class GradioAdmin:
    def __init__(self):
        self.db = next(get_db())
    
    def authenticate_admin(self, password: str) -> tuple:
        """管理員認證"""
        if password == settings.ADMIN_PASSWORD:
            return "登入成功！", True
        return "密碼錯誤！", False
    
    def get_merchants_data(self) -> pd.DataFrame:
        """獲取商戶數據"""
        merchants = MerchantService.get_merchants(self.db)
        data = []
        for merchant in merchants:
            stats = MerchantService.get_merchant_statistics(self.db, merchant.id)
            data.append({
                "ID": merchant.id,
                "商戶名稱": merchant.name,
                "描述": merchant.description or "",
                "電子郵件": merchant.contact_email or "",
                "狀態": "啟用" if merchant.is_active else "停用",
                "活動數": stats["total_events"],
                "門票數": stats["total_tickets"],
                "員工數": stats["total_staff"],
                "API Keys": stats["active_api_keys"],
                "創建時間": merchant.created_at.strftime("%Y-%m-%d %H:%M") if merchant.created_at else ""
            })
        return pd.DataFrame(data)
    
    def create_merchant(self, name: str, description: str, contact_email: str, contact_phone: str = None) -> tuple:
        """創建新商戶"""
        try:
            if not name or not contact_email:
                return "請填寫所有必填欄位", self.get_merchants_data()
            
            merchant_data = MerchantCreate(
                name=name,
                description=description,
                contact_email=contact_email,
                contact_phone=contact_phone
            )
            
            merchant = MerchantService.create_merchant(self.db, merchant_data)
            
            # 自動創建預設API Key
            MerchantService.create_api_key(
                db=self.db,
                merchant_id=merchant.id,
                key_name="預設API Key",
                permissions={
                    "events": ["read", "write"],
                    "tickets": ["read", "write"], 
                    "staff": ["read", "write"]
                }
            )
            
            return f"成功創建商戶: {merchant.name}", self.get_merchants_data()
        except Exception as e:
            return f"創建失敗: {str(e)}", self.get_merchants_data()
    
    def get_merchant_api_keys(self, merchant_id: int) -> pd.DataFrame:
        """獲取商戶API Keys"""
        if not merchant_id:
            return pd.DataFrame()
        
        api_keys = MerchantService.get_merchant_api_keys(self.db, merchant_id)
        data = []
        for key in api_keys:
            data.append({
                "ID": key.id,
                "名稱": key.key_name,
                "API Key": key.api_key[:16] + "..." if key.api_key else "",
                "狀態": "啟用" if key.is_active else "停用",
                "最後使用": key.last_used_at.strftime("%Y-%m-%d %H:%M") if key.last_used_at else "從未使用",
                "使用次數": key.usage_count,
                "過期時間": key.expires_at.strftime("%Y-%m-%d %H:%M") if key.expires_at else "永不過期",
                "創建時間": key.created_at.strftime("%Y-%m-%d %H:%M") if key.created_at else ""
            })
        return pd.DataFrame(data)
    
    def create_api_key(self, merchant_id: int, key_name: str, expires_days: int = None) -> tuple:
        """創建API Key"""
        try:
            if not merchant_id or not key_name:
                return "請選擇商戶並輸入API Key名稱", self.get_merchant_api_keys(merchant_id)
            
            api_key_data = ApiKeyCreate(
                key_name=key_name,
                expires_days=expires_days if expires_days and expires_days > 0 else None
            )
            
            api_key = MerchantService.create_api_key(
                db=self.db,
                merchant_id=merchant_id,
                key_name=key_name,
                expires_days=expires_days
            )
            
            return f"成功創建API Key: {api_key.api_key}", self.get_merchant_api_keys(merchant_id)
        except Exception as e:
            return f"創建失敗: {str(e)}", self.get_merchant_api_keys(merchant_id)
    
    def get_system_overview(self) -> dict:
        """獲取系統概覽"""
        merchants = MerchantService.get_merchants(self.db)
        total_merchants = len(merchants)
        active_merchants = len([m for m in merchants if m.is_active])
        
        total_events = 0
        total_tickets = 0
        total_staff = 0
        
        for merchant in merchants:
            stats = MerchantService.get_merchant_statistics(self.db, merchant.id)
            total_events += stats["total_events"]
            total_tickets += stats["total_tickets"]
            total_staff += stats["total_staff"]
        
        return {
            "多租戶模式": "啟用" if settings.ENABLE_MULTI_TENANT else "停用",
            "總商戶數": total_merchants,
            "活躍商戶": active_merchants,
            "總活動數": total_events,
            "總門票數": total_tickets,
            "總員工數": total_staff
        }
    
    def create_interface(self):
        """創建Gradio界面"""
        with gr.Blocks(title="QR Check-in 管理介面", theme=gr.themes.Soft()) as app:
            gr.Markdown("# QR Check-in 系統管理介面")
            
            # 認證區域
            with gr.Tab("登入"):
                password_input = gr.Textbox(label="管理員密碼", type="password")
                login_btn = gr.Button("登入", variant="primary")
                login_status = gr.Textbox(label="登入狀態", interactive=False)
                auth_state = gr.State(False)
            
            # 系統概覽
            with gr.Tab("系統概覽"):
                overview_btn = gr.Button("刷新概覽")
                overview_data = gr.JSON(label="系統概覽")
            
            # 商戶管理
            with gr.Tab("商戶管理"):
                with gr.Row():
                    with gr.Column():
                        gr.Markdown("## 創建新商戶")
                        merchant_name = gr.Textbox(label="商戶名稱", placeholder="請輸入商戶名稱")
                        merchant_description = gr.Textbox(label="商戶描述", placeholder="請輸入商戶描述")
                        contact_email = gr.Textbox(label="聯絡電子郵件", placeholder="請輸入電子郵件")
                        contact_phone = gr.Textbox(label="聯絡電話（選填）", placeholder="請輸入電話號碼")
                        create_merchant_btn = gr.Button("創建商戶", variant="primary")
                        merchant_status = gr.Textbox(label="操作狀態", interactive=False)
                    
                    with gr.Column():
                        gr.Markdown("## 商戶列表")
                        refresh_merchants_btn = gr.Button("刷新列表")
                        merchants_table = gr.DataFrame(
                            headers=["ID", "商戶名稱", "描述", "電子郵件", "狀態", "活動數", "門票數", "員工數", "API Keys", "創建時間"],
                            label="商戶列表"
                        )
            
            # API Key 管理
            with gr.Tab("API Key 管理"):
                with gr.Row():
                    with gr.Column():
                        gr.Markdown("## 選擇商戶")
                        merchant_dropdown = gr.Dropdown(label="選擇商戶", choices=[], interactive=True)
                        refresh_dropdown_btn = gr.Button("刷新商戶列表")
                        
                        gr.Markdown("## 創建API Key")
                        api_key_name = gr.Textbox(label="API Key名稱", placeholder="請輸入API Key名稱")
                        expires_days = gr.Number(label="過期天數（選填，留空表示永不過期）", minimum=1)
                        create_api_key_btn = gr.Button("創建API Key", variant="primary")
                        api_key_status = gr.Textbox(label="操作狀態", interactive=False)
                    
                    with gr.Column():
                        gr.Markdown("## API Key列表")
                        refresh_api_keys_btn = gr.Button("刷新API Key列表")
                        api_keys_table = gr.DataFrame(
                            headers=["ID", "名稱", "API Key", "狀態", "最後使用", "使用次數", "過期時間", "創建時間"],
                            label="API Key列表"
                        )
            
            # 事件處理
            def handle_login(password):
                return self.authenticate_admin(password)
            
            def update_merchant_dropdown():
                merchants = MerchantService.get_merchants(self.db)
                choices = [(f"{m.name} (ID: {m.id})", m.id) for m in merchants]
                return gr.update(choices=choices)
            
            # 綁定事件
            login_btn.click(
                handle_login,
                inputs=[password_input],
                outputs=[login_status, auth_state]
            )
            
            overview_btn.click(
                self.get_system_overview,
                outputs=[overview_data]
            )
            
            create_merchant_btn.click(
                self.create_merchant,
                inputs=[merchant_name, merchant_description, contact_email, contact_phone],
                outputs=[merchant_status, merchants_table]
            )
            
            refresh_merchants_btn.click(
                self.get_merchants_data,
                outputs=[merchants_table]
            )
            
            refresh_dropdown_btn.click(
                update_merchant_dropdown,
                outputs=[merchant_dropdown]
            )
            
            create_api_key_btn.click(
                self.create_api_key,
                inputs=[merchant_dropdown, api_key_name, expires_days],
                outputs=[api_key_status, api_keys_table]
            )
            
            refresh_api_keys_btn.click(
                self.get_merchant_api_keys,
                inputs=[merchant_dropdown],
                outputs=[api_keys_table]
            )
            
            merchant_dropdown.change(
                self.get_merchant_api_keys,
                inputs=[merchant_dropdown],
                outputs=[api_keys_table]
            )
            
            # 初始載入
            app.load(
                lambda: (self.get_system_overview(), self.get_merchants_data(), update_merchant_dropdown()),
                outputs=[overview_data, merchants_table, merchant_dropdown]
            )
        
        return app

def main():
    """啟動Gradio管理介面"""
    admin = GradioAdmin()
    app = admin.create_interface()
    
    print(f"啟動Gradio管理介面...")
    print(f"訪問地址: http://localhost:{settings.GRADIO_PORT}")
    print(f"管理員密碼: {settings.ADMIN_PASSWORD}")
    
    app.launch(
        server_name="0.0.0.0",
        server_port=settings.GRADIO_PORT,
        share=False
    )

if __name__ == "__main__":
    main()

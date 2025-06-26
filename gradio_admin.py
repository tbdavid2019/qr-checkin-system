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
from services.ticket_service import TicketService
from schemas.merchant import MerchantCreate, MerchantUpdate, ApiKeyCreate
from schemas.staff import StaffCreate
from schemas.event import EventCreate
from app.config import settings

class GradioAdmin:
    def __init__(self):
        # 使用 sessionmaker 來管理數據庫會話
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        from app.config import settings
        
        self.engine = create_engine(settings.DATABASE_URL)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
    
    def get_db_session(self):
        """獲取新的數據庫會話"""
        return self.SessionLocal()
    
    def authenticate_admin(self, password: str) -> tuple:
        """管理員認證"""
        if password == settings.ADMIN_PASSWORD:
            return "登入成功！", True
        return "密碼錯誤！", False
    
    def get_merchants_data(self) -> pd.DataFrame:
        """獲取商戶數據"""
        db = self.get_db_session()
        try:
            merchants = MerchantService.get_merchants(db)
            data = []
            for merchant in merchants:
                stats = MerchantService.get_merchant_statistics(db, merchant.id)
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
        except Exception as e:
            print(f"Error in get_merchants_data: {e}")
            db.rollback()
            return pd.DataFrame()
        finally:
            db.close()
    
    def create_merchant(self, name: str, description: str, contact_email: str, contact_phone: str = None) -> tuple:
        """創建新商戶"""
        db = self.get_db_session()
        try:
            if not name or not contact_email:
                return "請填寫所有必填欄位", self.get_merchants_data()
            
            merchant_data = MerchantCreate(
                name=name,
                description=description,
                contact_email=contact_email,
                contact_phone=contact_phone
            )
            
            merchant = MerchantService.create_merchant(db, merchant_data)
            
            # 自動創建預設API Key
            MerchantService.create_api_key(
                db=db,
                merchant_id=merchant.id,
                key_name="預設API Key",
                permissions={
                    "events": ["read", "write"],
                    "tickets": ["read", "write"], 
                    "staff": ["read", "write"]
                }
            )
            
            db.commit()
            return f"成功創建商戶: {merchant.name}", self.get_merchants_data()
        except Exception as e:
            print(f"Error in create_merchant: {e}")
            db.rollback()
            return f"創建失敗: {str(e)}", self.get_merchants_data()
        finally:
            db.close()
    
    def get_merchant_api_keys(self, merchant_id: int) -> pd.DataFrame:
        """獲取商戶API Keys"""
        if not merchant_id:
            return pd.DataFrame()
        
        db = self.get_db_session()
        try:
            api_keys = MerchantService.get_merchant_api_keys(db, merchant_id)
            data = []
            for key in api_keys:
                data.append({
                    "ID": key.id,
                    "名稱": key.key_name,
                    "API Key": key.api_key if key.api_key else "",  # 顯示完整 API Key
                    "狀態": "啟用" if key.is_active else "停用",
                    "最後使用": key.last_used_at.strftime("%Y-%m-%d %H:%M") if key.last_used_at else "從未使用",
                    "使用次數": key.usage_count,
                    "過期時間": key.expires_at.strftime("%Y-%m-%d %H:%M") if key.expires_at else "永不過期",
                    "創建時間": key.created_at.strftime("%Y-%m-%d %H:%M") if key.created_at else ""
                })
            return pd.DataFrame(data)
        except Exception as e:
            print(f"Error in get_merchant_api_keys: {e}")
            db.rollback()
            return pd.DataFrame()
        finally:
            db.close()
    
    def create_api_key(self, merchant_id: int, key_name: str, expires_days: int = None) -> tuple:
        """創建API Key"""
        db = self.get_db_session()
        try:
            if not merchant_id or not key_name:
                return "請選擇商戶並輸入API Key名稱", self.get_merchant_api_keys(merchant_id)
            
            api_key_data = ApiKeyCreate(
                key_name=key_name,
                expires_days=expires_days if expires_days and expires_days > 0 else None
            )
            
            api_key = MerchantService.create_api_key(
                db=db,
                merchant_id=merchant_id,
                key_name=key_name,
                expires_days=expires_days
            )
            
            db.commit()
            return f"成功創建API Key: {api_key.api_key}", self.get_merchant_api_keys(merchant_id)
        except Exception as e:
            print(f"Error in create_api_key: {e}")
            db.rollback()
            return f"創建失敗: {str(e)}", self.get_merchant_api_keys(merchant_id)
        finally:
            db.close()
    
    def get_system_overview(self) -> dict:
        """獲取系統概覽"""
        db = self.get_db_session()
        try:
            merchants = MerchantService.get_merchants(db)
            total_merchants = len(merchants)
            active_merchants = len([m for m in merchants if m.is_active])
            
            total_events = 0
            total_tickets = 0
            total_staff = 0
            
            for merchant in merchants:
                stats = MerchantService.get_merchant_statistics(db, merchant.id)
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
        except Exception as e:
            print(f"Error in get_system_overview: {e}")
            db.rollback()
            return {
                "錯誤": f"無法載入系統概覽: {str(e)}"
            }
        finally:
            db.close()
    
    # 員工管理
    def get_staff_data(self, merchant_id: int) -> pd.DataFrame:
        db = self.get_db_session()
        try:
            staff_list = StaffService.get_staff_by_merchant(db, merchant_id)
            data = []
            for staff in staff_list:
                data.append({
                    "ID": staff.id,
                    "帳號": staff.username,
                    "姓名": staff.full_name,
                    "Email": staff.email,
                    "狀態": "啟用" if staff.is_active else "停用",
                    "管理員": "是" if staff.is_admin else "否",
                    "建立時間": staff.created_at.strftime("%Y-%m-%d %H:%M") if staff.created_at else ""
                })
            return pd.DataFrame(data)
        except Exception as e:
            print(f"Error in get_staff_data: {e}")
            db.rollback()
            return pd.DataFrame()
        finally:
            db.close()

    def create_staff(self, merchant_id: int, username: str, password: str, full_name: str, email: str, is_admin: bool) -> str:
        db = self.get_db_session()
        try:
            staff_data = StaffCreate(username=username, password=password, full_name=full_name, email=email, is_admin=is_admin)
            StaffService.create_staff(db, staff_data, merchant_id)
            db.commit()
            return "員工新增成功"
        except Exception as e:
            print(f"Error in create_staff: {e}")
            db.rollback()
            return f"員工新增失敗: {str(e)}"
        finally:
            db.close()

    def delete_staff(self, staff_id: int) -> str:
        db = self.get_db_session()
        try:
            StaffService.delete_staff(db, staff_id)
            db.commit()
            return "員工刪除成功"
        except Exception as e:
            print(f"Error in delete_staff: {e}")
            db.rollback()
            return f"員工刪除失敗: {str(e)}"
        finally:
            db.close()

    # 活動管理
    def get_events_data(self, merchant_id: int) -> pd.DataFrame:
        db = self.get_db_session()
        try:
            events = EventService.get_events_by_merchant(db, merchant_id)
            data = []
            for event in events:
                data.append({
                    "ID": event.id,
                    "活動名稱": event.name,
                    "描述": event.description or "",
                    "地點": event.location or "",
                    "開始時間": event.start_time.strftime("%Y-%m-%d %H:%M") if event.start_time else "",
                    "結束時間": event.end_time.strftime("%Y-%m-%d %H:%M") if event.end_time else "",
                    "狀態": "啟用" if event.is_active else "停用",
                    "創建時間": event.created_at.strftime("%Y-%m-%d %H:%M") if event.created_at else "",
                    "更新時間": event.updated_at.strftime("%Y-%m-%d %H:%M") if event.updated_at else ""
                })
            return pd.DataFrame(data)
        except Exception as e:
            print(f"Error in get_events_data: {e}")
            db.rollback()
            return pd.DataFrame()
        finally:
            db.close()

    def create_event(self, merchant_id: int, name: str, description: str, location: str, start_time: str, end_time: str) -> str:
        db = self.get_db_session()
        try:
            from datetime import datetime
            start_dt = datetime.strptime(start_time, "%Y-%m-%d %H:%M")
            end_dt = datetime.strptime(end_time, "%Y-%m-%d %H:%M")
            
            event_data = EventCreate(
                name=name, 
                description=description,
                location=location,
                start_time=start_dt, 
                end_time=end_dt
            )
            EventService.create_event(db, event_data, merchant_id)
            db.commit()
            return "活動新增成功"
        except ValueError as e:
            db.rollback()
            return f"日期格式錯誤: {str(e)}"
        except Exception as e:
            print(f"Error in create_event: {e}")
            db.rollback()
            return f"新增失敗: {str(e)}"
        finally:
            db.close()

    def delete_event(self, event_id: int) -> str:
        db = self.get_db_session()
        try:
            EventService.delete_event(db, event_id)
            db.commit()
            return "活動已刪除"
        except Exception as e:
            print(f"Error in delete_event: {e}")
            db.rollback()
            return f"刪除失敗: {str(e)}"
        finally:
            db.close()

    # 門票管理
    def get_tickets_data(self, event_id: int, merchant_id: int = None) -> pd.DataFrame:
        """獲取票券數據"""
        if not event_id:
            return pd.DataFrame()
        
        db = self.get_db_session()
        try:
            # 如果有指定商戶ID，使用多租戶查詢，否則查詢所有票券
            if merchant_id:
                tickets = TicketService.get_tickets_by_event_and_merchant(db, event_id, merchant_id)
            else:
                # 為了相容性，如果沒有商戶ID，則查詢該活動的所有票券
                from models.ticket import Ticket
                from models.ticket_type import TicketType
                tickets = (db.query(Ticket)
                          .join(TicketType)
                          .filter(TicketType.event_id == event_id)
                          .all())
            
            data = []
            for ticket in tickets:
                data.append({
                    "ID": ticket.id,
                    "UUID": str(ticket.uuid) if ticket.uuid else "",
                    "票種": ticket.ticket_type.name if ticket.ticket_type else "未知",
                    "持有人": ticket.holder_name,
                    "描述": ticket.description or "",
                    "狀態": "已使用" if ticket.is_used else "未使用",
                    "建立時間": ticket.created_at.strftime("%Y-%m-%d %H:%M") if ticket.created_at else ""
                })
            return pd.DataFrame(data)
        except Exception as e:
            print(f"Error in get_tickets_data: {e}")
            db.rollback()
            return pd.DataFrame()
        finally:
            db.close()

    # 簽到記錄查看
    def get_checkin_records(self, event_id: int, merchant_id: int = None) -> pd.DataFrame:
        """獲取簽到記錄"""
        if not event_id:
            return pd.DataFrame()
        
        db = self.get_db_session()
        try:
            # 如果有指定商戶ID，使用多租戶查詢，否則查詢所有簽到記錄
            if merchant_id:
                tickets = TicketService.get_tickets_by_event_and_merchant(db, event_id, merchant_id)
            else:
                # 為了相容性，如果沒有商戶ID，則查詢該活動的所有票券
                from models.ticket import Ticket
                from models.ticket_type import TicketType
                tickets = (db.query(Ticket)
                          .join(TicketType)
                          .filter(TicketType.event_id == event_id)
                          .all())
            
            data = []
            for ticket in tickets:
                if ticket.checked_in:
                    data.append({
                        "票號": ticket.id,
                        "姓名": ticket.holder_name,
                        "簽到時間": ticket.checkin_time.strftime("%Y-%m-%d %H:%M") if ticket.checkin_time else ""
                    })
            return pd.DataFrame(data)
        except Exception as e:
            print(f"Error in get_checkin_records: {e}")
            db.rollback()
            return pd.DataFrame()
        finally:
            db.close()
    
    # 票種管理
    def get_ticket_types_data(self, event_id: int) -> pd.DataFrame:
        """獲取票種數據"""
        if not event_id:
            return pd.DataFrame()
        
        db = self.get_db_session()
        try:
            from models.ticket_type import TicketType
            ticket_types = db.query(TicketType).filter(TicketType.event_id == event_id).all()
            
            data = []
            for tt in ticket_types:
                # 計算已使用票券數量
                from models.ticket import Ticket
                used_count = db.query(Ticket).filter(
                    Ticket.ticket_type_id == tt.id
                ).count()
                
                data.append({
                    "ID": tt.id,
                    "票種名稱": tt.name,
                    "價格": float(tt.price) if tt.price else 0.0,
                    "配額": tt.quota,
                    "已產出": used_count,
                    "剩餘": tt.quota - used_count if tt.quota > 0 else "無限制",
                    "狀態": "啟用" if tt.is_active else "停用"
                })
            return pd.DataFrame(data)
        except Exception as e:
            print(f"Error in get_ticket_types_data: {e}")
            return pd.DataFrame()
        finally:
            db.close()
    
    def create_ticket_type(self, event_id: int, name: str, price: float, quota: int) -> str:
        """創建票種"""
        if not event_id or not name:
            return "請填寫完整資訊"
        
        db = self.get_db_session()
        try:
            from schemas.event import TicketTypeCreate
            from services.event_service import EventService
            
            ticket_type_data = TicketTypeCreate(
                name=name,
                price=price if price > 0 else 0,
                quota=quota if quota > 0 else 0,
                event_id=event_id
            )
            
            ticket_type = EventService.create_ticket_type(db, ticket_type_data)
            return f"成功創建票種: {ticket_type.name}"
        except Exception as e:
            print(f"Error in create_ticket_type: {e}")
            return f"創建失敗: {str(e)}"
        finally:
            db.close()
    
    def create_single_ticket(self, event_id: int, ticket_type_id: int, holder_name: str, 
                           holder_email: str = None, holder_phone: str = None, notes: str = None) -> str:
        """創建單張票券"""
        if not event_id or not holder_name:
            return "請填寫活動ID和持有人姓名"
        
        db = self.get_db_session()
        try:
            from schemas.ticket import TicketCreate
            
            ticket_data = TicketCreate(
                event_id=event_id,
                ticket_type_id=ticket_type_id if ticket_type_id > 0 else None,
                holder_name=holder_name,
                holder_email=holder_email if holder_email else None,
                holder_phone=holder_phone if holder_phone else None,
                notes=notes if notes else None
            )
            
            ticket = TicketService.create_ticket(db, ticket_data)
            return f"成功創建票券: {ticket.ticket_code} (持有人: {ticket.holder_name})"
        except Exception as e:
            print(f"Error in create_single_ticket: {e}")
            return f"創建失敗: {str(e)}"
        finally:
            db.close()
    
    def create_batch_tickets(self, event_id: int, ticket_type_id: int, count: int, 
                           name_prefix: str = "批次票券") -> str:
        """批次創建票券"""
        if not event_id or count <= 0:
            return "請填寫正確的活動ID和票券數量"
        
        db = self.get_db_session()
        try:
            from schemas.ticket import BatchTicketCreate
            
            batch_data = BatchTicketCreate(
                event_id=event_id,
                ticket_type_id=ticket_type_id if ticket_type_id > 0 else None,
                count=count,
                holder_name_prefix=name_prefix
            )
            
            tickets = TicketService.create_batch_tickets(db, batch_data)
            return f"成功創建 {len(tickets)} 張票券"
        except Exception as e:
            print(f"Error in create_batch_tickets: {e}")
            return f"創建失敗: {str(e)}"
        finally:
            db.close()
    
    def get_ticket_types_for_event(self, event_id: int) -> list:
        """獲取活動的票種選項"""
        if not event_id:
            return []
        
        db = self.get_db_session()
        try:
            from models.ticket_type import TicketType
            ticket_types = db.query(TicketType).filter(
                TicketType.event_id == event_id,
                TicketType.is_active == True
            ).all()
            
            choices = [(f"{tt.name} (ID: {tt.id})", tt.id) for tt in ticket_types]
            return choices
        except Exception as e:
            print(f"Error in get_ticket_types_for_event: {e}")
            return []
        finally:
            db.close()

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
                    
                    with gr.Column():
                        gr.Markdown("## 創建API Key")
                        api_key_name = gr.Textbox(label="API Key名稱", placeholder="請輸入API Key名稱")
                        expires_days = gr.Number(label="過期天數（選填，留空表示永不過期）", minimum=1)
                        create_api_key_btn = gr.Button("創建API Key", variant="primary")
                        api_key_status = gr.Textbox(label="操作狀態", interactive=False)
                
                # API Key 列表放在下方以便顯示完整內容
                gr.Markdown("## API Key列表")
                refresh_api_keys_btn = gr.Button("刷新API Key列表")
                api_keys_table = gr.DataFrame(
                    headers=["ID", "名稱", "API Key", "狀態", "最後使用", "使用次數", "過期時間", "創建時間"],
                    label="API Key列表"
                )
            
            # 員工管理
            with gr.Tab("員工管理"):
                merchant_id_input = gr.Number(label="商戶ID")
                staff_table = gr.Dataframe(headers=["ID", "帳號", "姓名", "Email", "狀態", "管理員", "建立時間"])
                staff_refresh_btn = gr.Button("刷新員工列表")
                staff_refresh_btn.click(self.get_staff_data, inputs=[merchant_id_input], outputs=[staff_table])
                # 新增員工
                staff_username = gr.Textbox(label="帳號")
                staff_password = gr.Textbox(label="密碼", type="password")
                staff_full_name = gr.Textbox(label="姓名")
                staff_email = gr.Textbox(label="Email")
                staff_is_admin = gr.Checkbox(label="管理員")
                staff_create_btn = gr.Button("新增員工")
                staff_create_status = gr.Textbox(label="狀態")
                staff_create_btn.click(self.create_staff, inputs=[merchant_id_input, staff_username, staff_password, staff_full_name, staff_email, staff_is_admin], outputs=[staff_create_status])
                # 刪除員工
                staff_id_delete = gr.Number(label="員工ID")
                staff_delete_btn = gr.Button("刪除員工")
                staff_delete_status = gr.Textbox(label="狀態")
                staff_delete_btn.click(self.delete_staff, inputs=[staff_id_delete], outputs=[staff_delete_status])

            # 活動管理
            with gr.Tab("活動管理"):
                event_merchant_id = gr.Number(label="商戶ID")
                event_table = gr.Dataframe(headers=["ID", "活動名稱", "描述", "地點", "開始時間", "結束時間", "狀態", "創建時間", "更新時間"])
                event_refresh_btn = gr.Button("刷新活動列表")
                event_refresh_btn.click(self.get_events_data, inputs=[event_merchant_id], outputs=[event_table])
                
                # 新增活動
                gr.Markdown("### 新增活動")
                event_name = gr.Textbox(label="活動名稱")
                event_description = gr.Textbox(label="活動描述")
                event_location = gr.Textbox(label="活動地點")
                event_start = gr.Textbox(label="開始時間 (YYYY-MM-DD HH:MM)", placeholder="2024-12-25 14:00")
                event_end = gr.Textbox(label="結束時間 (YYYY-MM-DD HH:MM)", placeholder="2024-12-25 18:00")
                event_create_btn = gr.Button("新增活動")
                event_create_status = gr.Textbox(label="狀態")
                event_create_btn.click(
                    self.create_event, 
                    inputs=[event_merchant_id, event_name, event_description, event_location, event_start, event_end], 
                    outputs=[event_create_status]
                )
                
                # 刪除活動
                gr.Markdown("### 刪除活動")
                event_id_delete = gr.Number(label="活動ID")
                event_delete_btn = gr.Button("刪除活動")
                event_delete_status = gr.Textbox(label="狀態")
                event_delete_btn.click(self.delete_event, inputs=[event_id_delete], outputs=[event_delete_status])

            # 票種管理
            with gr.Tab("票種管理"):
                with gr.Row():
                    with gr.Column():
                        gr.Markdown("## 查看票種")
                        tt_event_id = gr.Number(label="活動ID")
                        tt_refresh_btn = gr.Button("查看票種列表")
                        ticket_types_table = gr.DataFrame(
                            headers=["ID", "票種名稱", "價格", "配額", "已產出", "剩餘", "狀態"],
                            label="票種列表"
                        )
                    
                    with gr.Column():
                        gr.Markdown("## 新增票種")
                        tt_new_event_id = gr.Number(label="活動ID")
                        tt_name = gr.Textbox(label="票種名稱", placeholder="例如: 一般票、VIP票")
                        tt_price = gr.Number(label="價格", minimum=0, value=0)
                        tt_quota = gr.Number(label="配額 (0=無限制)", minimum=0, value=0)
                        tt_create_btn = gr.Button("創建票種", variant="primary")
                        tt_create_status = gr.Textbox(label="操作狀態", interactive=False)

            # 產票管理
            with gr.Tab("產票管理"):
                with gr.Row():
                    with gr.Column():
                        gr.Markdown("## 單張產票")
                        single_event_id = gr.Number(label="活動ID")
                        single_ticket_type = gr.Dropdown(label="票種", choices=[], interactive=True)
                        single_refresh_types_btn = gr.Button("刷新票種列表")
                        single_holder_name = gr.Textbox(label="持有人姓名", placeholder="請輸入持有人姓名")
                        single_holder_email = gr.Textbox(label="電子郵件 (選填)", placeholder="example@email.com")
                        single_holder_phone = gr.Textbox(label="電話 (選填)", placeholder="0912345678")
                        single_notes = gr.Textbox(label="備註 (選填)", placeholder="其他備註資訊")
                        single_create_btn = gr.Button("產生票券", variant="primary")
                        single_create_status = gr.Textbox(label="操作狀態", interactive=False)
                    
                    with gr.Column():
                        gr.Markdown("## 批次產票")
                        batch_event_id = gr.Number(label="活動ID")
                        batch_ticket_type = gr.Dropdown(label="票種", choices=[], interactive=True)
                        batch_refresh_types_btn = gr.Button("刷新票種列表")
                        batch_count = gr.Number(label="票券數量", minimum=1, maximum=100, value=1)
                        batch_name_prefix = gr.Textbox(label="持有人前綴", value="批次票券", placeholder="例如: 批次票券")
                        batch_create_btn = gr.Button("批次產票", variant="primary")
                        batch_create_status = gr.Textbox(label="操作狀態", interactive=False)

            # 門票管理
            with gr.Tab("門票管理"):
                with gr.Row():
                    ticket_merchant_id = gr.Number(label="商戶ID (選填)", info="留空則查詢所有商戶")
                    ticket_event_id = gr.Number(label="活動ID")
                ticket_table = gr.Dataframe(headers=["ID", "UUID", "票種", "持有人", "描述", "狀態", "建立時間"])
                ticket_refresh_btn = gr.Button("刷新門票列表")
                ticket_refresh_btn.click(self.get_tickets_data, inputs=[ticket_event_id, ticket_merchant_id], outputs=[ticket_table])

            # 簽到記錄
            with gr.Tab("簽到記錄"):
                with gr.Row():
                    checkin_merchant_id = gr.Number(label="商戶ID (選填)", info="留空則查詢所有商戶")
                    checkin_event_id = gr.Number(label="活動ID")
                checkin_table = gr.Dataframe(headers=["票號", "姓名", "簽到時間"])
                checkin_refresh_btn = gr.Button("刷新簽到記錄")
                checkin_refresh_btn.click(self.get_checkin_records, inputs=[checkin_event_id, checkin_merchant_id], outputs=[checkin_table])

            # 事件處理
            def handle_login(password):
                return self.authenticate_admin(password)
            
            def update_merchant_dropdown():
                db = self.get_db_session()
                try:
                    merchants = MerchantService.get_merchants(db)
                    choices = [(f"{m.name} (ID: {m.id})", m.id) for m in merchants]
                    return gr.update(choices=choices)
                except Exception as e:
                    print(f"Error in update_merchant_dropdown: {e}")
                    return gr.update(choices=[])
                finally:
                    db.close()
            
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
            
            # 票種管理事件處理
            tt_refresh_btn.click(
                self.get_ticket_types_data,
                inputs=[tt_event_id],
                outputs=[ticket_types_table]
            )
            
            tt_create_btn.click(
                self.create_ticket_type,
                inputs=[tt_new_event_id, tt_name, tt_price, tt_quota],
                outputs=[tt_create_status]
            )
            
            # 產票管理事件處理
            def update_ticket_types_for_single(event_id):
                choices = self.get_ticket_types_for_event(event_id)
                return gr.update(choices=choices)
            
            def update_ticket_types_for_batch(event_id):
                choices = self.get_ticket_types_for_event(event_id)
                return gr.update(choices=choices)
            
            single_refresh_types_btn.click(
                update_ticket_types_for_single,
                inputs=[single_event_id],
                outputs=[single_ticket_type]
            )
            
            batch_refresh_types_btn.click(
                update_ticket_types_for_batch,
                inputs=[batch_event_id],
                outputs=[batch_ticket_type]
            )
            
            single_create_btn.click(
                self.create_single_ticket,
                inputs=[single_event_id, single_ticket_type, single_holder_name, 
                       single_holder_email, single_holder_phone, single_notes],
                outputs=[single_create_status]
            )
            
            batch_create_btn.click(
                self.create_batch_tickets,
                inputs=[batch_event_id, batch_ticket_type, batch_count, batch_name_prefix],
                outputs=[batch_create_status]
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

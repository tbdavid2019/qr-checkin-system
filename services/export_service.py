"""
導出服務
"""
import csv
import io
from typing import List, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import func, case
from models import CheckInLog, Ticket, Staff, Event, TicketType
from services.checkin_service import CheckInService
from services.ticket_service import TicketService

class ExportService:
    
    @staticmethod
    def export_checkin_logs_csv(db: Session, event_id: int) -> str:
        """導出簽到記錄為CSV格式"""
        # 獲取簽到記錄
        logs = CheckInService.get_checkin_logs_by_event(db, event_id, skip=0, limit=10000)
        
        # 創建CSV字符串
        output = io.StringIO()
        writer = csv.writer(output)
        
        # 寫入標題行
        writer.writerow([
            '簽到ID', '票券ID', '票券代碼', '持票人姓名', '票種', 
            '簽到時間', '簽到員工', 'IP地址', '是否已撤銷', '撤銷時間'
        ])
        
        # 寫入數據行
        for log in logs:
            ticket = TicketService.get_ticket_by_id(db, log.ticket_id)
            staff = db.query(Staff).filter(Staff.id == log.staff_id).first() if log.staff_id else None
            ticket_type_name = ""
            
            if ticket and ticket.ticket_type:
                ticket_type_name = ticket.ticket_type.name
            
            writer.writerow([
                log.id,
                log.ticket_id,
                ticket.ticket_code if ticket else '',
                ticket.holder_name if ticket else '',
                ticket_type_name,
                log.checkin_time.strftime('%Y-%m-%d %H:%M:%S') if log.checkin_time else '',
                staff.full_name if staff else '',
                log.ip_address or '',
                '是' if log.is_revoked else '否',
                log.revoked_at.strftime('%Y-%m-%d %H:%M:%S') if log.revoked_at else ''
            ])
        
        return output.getvalue()
    
    @staticmethod
    def export_tickets_csv(db: Session, event_id: int) -> str:
        """導出票券清單為CSV格式"""
        # 獲取票券列表
        tickets = TicketService.get_tickets_by_event(db, event_id, skip=0, limit=10000)
        
        # 創建CSV字符串
        output = io.StringIO()
        writer = csv.writer(output)
        
        # 寫入標題行
        writer.writerow([
            '票券ID', '票券代碼', '持票人姓名', '持票人信箱', '持票人電話',
            '票種', '票價', '是否已使用', '建立時間', '外部用戶ID', '備註'
        ])
        
        # 寫入數據行
        for ticket in tickets:
            ticket_type_name = ""
            ticket_price = 0
            
            if ticket.ticket_type:
                ticket_type_name = ticket.ticket_type.name
                ticket_price = ticket.ticket_type.price
            
            writer.writerow([
                ticket.id,
                ticket.ticket_code,
                ticket.holder_name,
                ticket.holder_email or '',
                ticket.holder_phone or '',
                ticket_type_name,
                ticket_price,
                '是' if ticket.is_used else '否',
                ticket.created_at.strftime('%Y-%m-%d %H:%M:%S') if ticket.created_at else '',
                ticket.external_user_id or '',
                ticket.notes or ''
            ])
        
        return output.getvalue()
    
    @staticmethod
    def get_event_statistics(db: Session, event_id: int) -> Dict[str, Any]:
        """獲取活動統計資訊"""
        # 總票券數
        total_tickets = (db.query(Ticket)
                        .filter(Ticket.event_id == event_id)
                        .count())
        
        # 已使用票券數
        used_tickets = (db.query(Ticket)
                       .filter(Ticket.event_id == event_id)
                       .filter(Ticket.is_used == True)
                       .count())
        
        # 簽到記錄數（不含撤銷）
        checkin_count = (db.query(CheckInLog)
                        .join(Ticket, CheckInLog.ticket_id == Ticket.id)
                        .filter(Ticket.event_id == event_id)
                        .filter(CheckInLog.is_revoked == False)
                        .count())
        
        # 撤銷記錄數
        revoked_count = (db.query(CheckInLog)
                        .join(Ticket, CheckInLog.ticket_id == Ticket.id)
                        .filter(Ticket.event_id == event_id)
                        .filter(CheckInLog.is_revoked == True)
                        .count())
        
        # 簡化的票種統計
        ticket_types = db.query(TicketType).filter(TicketType.event_id == event_id).all()
        ticket_type_stats = []
        
        for ticket_type in ticket_types:
            # 每個票種的統計
            sold_count = (db.query(Ticket)
                         .filter(Ticket.ticket_type_id == ticket_type.id)
                         .count())
            
            used_count = (db.query(Ticket)
                         .filter(Ticket.ticket_type_id == ticket_type.id)
                         .filter(Ticket.is_used == True)
                         .count())
            
            ticket_type_stats.append({
                'name': ticket_type.name,
                'price': float(ticket_type.price),
                'quota': ticket_type.quota,
                'sold_count': sold_count,
                'used_count': used_count,
                'available_count': ticket_type.quota - sold_count
            })
        
        return {
            'total_tickets': total_tickets,
            'used_tickets': used_tickets,
            'unused_tickets': total_tickets - used_tickets,
            'checkin_count': checkin_count,
            'revoked_count': revoked_count,
            'usage_rate': round((used_tickets / total_tickets * 100) if total_tickets > 0 else 0, 2),
            'ticket_types': ticket_type_stats
        }

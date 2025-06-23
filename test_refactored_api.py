#!/usr/bin/env python3
"""
重構後 API 架構完整測試腳本
測試新的四層API架構：Admin, Management, Staff, Public
"""
import requests
import json
import sys
import time
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

# API 配置
BASE_URL = "http://localhost:8000"
ADMIN_PASSWORD = "secure-admin-password-123"

class RefactoredAPITester:
    """重構後 API 測試器"""
    
    def __init__(self):
        self.base_url = BASE_URL
        self.admin_password = ADMIN_PASSWORD
        self.merchant_id: Optional[int] = None
        self.api_key: Optional[str] = None
        self.staff_id: Optional[int] = None
        self.jwt_token: Optional[str] = None
        self.event_id: Optional[int] = None
        self.ticket_id: Optional[int] = None
        self.ticket_uuid: Optional[str] = None
        self.qr_token: Optional[str] = None
        
    def print_step(self, step: str):
        """列印測試步驟"""
        print(f"\n{'='*60}")
        print(f"🧪 {step}")
        print('='*60)
        
    def print_result(self, success: bool, message: str, data: Any = None):
        """列印測試結果"""
        status = "✅ 成功" if success else "❌ 失敗"
        print(f"{status}: {message}")
        if data and isinstance(data, dict):
            print(f"   回應: {json.dumps(data, indent=2, ensure_ascii=False)}")
        elif data:
            print(f"   資料: {data}")
            
    def test_health_check(self) -> bool:
        """測試系統健康檢查"""
        self.print_step("系統健康檢查")
        
        try:
            response = requests.get(f"{self.base_url}/health")
            if response.status_code == 200:
                self.print_result(True, "系統健康檢查通過", response.json())
                return True
            else:
                self.print_result(False, f"健康檢查失敗 (Status: {response.status_code})")
                return False
        except Exception as e:
            self.print_result(False, f"健康檢查異常: {e}")
            return False
            
    def test_admin_create_merchant(self) -> bool:
        """測試超級管理員創建商戶"""
        self.print_step("超級管理員 - 創建商戶")
        
        merchant_data = {
            "name": f"測試商戶_{int(time.time())}",
            "email": f"test_{int(time.time())}@example.com",
            "description": "API重構測試商戶"
        }
        
        headers = {
            "X-Admin-Password": self.admin_password,
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/admin/merchants",
                headers=headers,
                json=merchant_data
            )
            
            if response.status_code in [200, 201]:
                data = response.json()
                self.merchant_id = data['id']
                self.api_key = data['api_key']
                self.print_result(True, f"商戶創建成功 (ID: {self.merchant_id})", data)
                return True
            else:
                self.print_result(False, f"商戶創建失敗 (Status: {response.status_code})", response.text)
                return False
                
        except Exception as e:
            self.print_result(False, f"商戶創建異常: {e}")
            return False
            
    def test_mgmt_create_event(self) -> bool:
        """測試商戶管理 - 創建活動"""
        self.print_step("商戶管理 - 創建活動")
        
        if not self.api_key:
            self.print_result(False, "缺少 API Key，無法測試")
            return False
            
        event_data = {
            "name": f"重構測試活動_{int(time.time())}",
            "description": "API重構後的測試活動",
            "start_time": (datetime.now() + timedelta(hours=1)).isoformat(),
            "end_time": (datetime.now() + timedelta(hours=5)).isoformat(),
            "location": "測試地點"
        }
        
        headers = {
            "X-API-Key": self.api_key,
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/api/v1/mgmt/events",
                headers=headers,
                json=event_data
            )
            
            if response.status_code in [200, 201]:
                data = response.json()
                self.event_id = data['id']
                self.print_result(True, f"活動創建成功 (ID: {self.event_id})", data)
                return True
            else:
                self.print_result(False, f"活動創建失敗 (Status: {response.status_code})", response.text)
                return False
                
        except Exception as e:
            self.print_result(False, f"活動創建異常: {e}")
            return False
            
    def test_mgmt_create_staff(self) -> bool:
        """測試商戶管理 - 創建員工"""
        self.print_step("商戶管理 - 創建員工")
        
        if not self.api_key:
            self.print_result(False, "缺少 API Key，無法測試")
            return False
            
        staff_data = {
            "username": f"staff_{int(time.time())}@test.com",
            "password": "test123456",
            "email": f"staff_{int(time.time())}@test.com",
            "full_name": "重構測試員工"
        }
        
        headers = {
            "X-API-Key": self.api_key,
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/api/v1/mgmt/staff",
                headers=headers,
                json=staff_data
            )
            
            if response.status_code in [200, 201]:
                data = response.json()
                self.staff_id = data['id']
                self.staff_username = staff_data['username']
                self.staff_password = staff_data['password']
                self.print_result(True, f"員工創建成功 (ID: {self.staff_id})", data)
                return True
            else:
                self.print_result(False, f"員工創建失敗 (Status: {response.status_code})", response.text)
                return False
                
        except Exception as e:
            self.print_result(False, f"員工創建異常: {e}")
            return False
            
    def test_mgmt_assign_staff_event(self) -> bool:
        """測試商戶管理 - 指派員工到活動"""
        self.print_step("商戶管理 - 指派員工到活動")
        
        if not self.api_key or not self.staff_id or not self.event_id:
            self.print_result(False, "缺少必要資料，無法測試")
            return False
            
        assign_data = {
            "staff_id": self.staff_id,
            "event_id": self.event_id,
            "can_checkin": True,
            "can_revoke": False
        }
        
        headers = {
            "X-API-Key": self.api_key,
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/api/v1/mgmt/staff/events/assign",
                headers=headers,
                json=assign_data
            )
            
            if response.status_code in [200, 201]:
                data = response.json()
                self.print_result(True, "員工活動權限指派成功", data)
                return True
            else:
                self.print_result(False, f"員工活動權限指派失敗 (Status: {response.status_code})", response.text)
                return False
                
        except Exception as e:
            self.print_result(False, f"員工活動權限指派異常: {e}")
            return False
            
    def test_staff_login(self) -> bool:
        """測試員工 - 登入獲取JWT"""
        self.print_step("員工操作 - 登入獲取JWT")
        
        if not hasattr(self, 'staff_username') or not hasattr(self, 'staff_password'):
            self.print_result(False, "缺少員工帳密，無法測試")
            return False
            
        login_data = {
            "username": self.staff_username,
            "password": self.staff_password
        }
        
        headers = {
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/api/v1/staff/login",
                headers=headers,
                json=login_data
            )
            
            if response.status_code == 200:
                data = response.json()
                self.jwt_token = data['access_token']
                self.print_result(True, f"員工登入成功，獲取JWT", {"access_token": self.jwt_token[:50] + "..."})
                return True
            else:
                self.print_result(False, f"員工登入失敗 (Status: {response.status_code})", response.text)
                return False
                
        except Exception as e:
            self.print_result(False, f"員工登入異常: {e}")
            return False
            
    def test_staff_profile(self) -> bool:
        """測試員工 - 獲取個人資料"""
        self.print_step("員工操作 - 獲取個人資料")
        
        if not self.jwt_token:
            self.print_result(False, "缺少JWT Token，無法測試")
            return False
            
        headers = {
            "Authorization": f"Bearer {self.jwt_token}"
        }
        
        try:
            response = requests.get(
                f"{self.base_url}/api/v1/staff/me/profile",
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                self.print_result(True, "員工個人資料獲取成功", data)
                return True
            else:
                self.print_result(False, f"員工個人資料獲取失敗 (Status: {response.status_code})", response.text)
                return False
                
        except Exception as e:
            self.print_result(False, f"員工個人資料獲取異常: {e}")
            return False
            
    def test_mgmt_create_ticket(self) -> bool:
        """測試商戶管理 - 創建票券"""
        self.print_step("商戶管理 - 創建票券")
        
        if not self.api_key or not self.event_id:
            self.print_result(False, "缺少必要資料，無法測試")
            return False
            
        ticket_data = {
            "event_id": self.event_id,
            "holder_name": "重構測試持票人",
            "holder_email": "ticket_holder@test.com",
            "description": "API重構測試票券"
        }
        
        headers = {
            "X-API-Key": self.api_key,
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/api/v1/mgmt/tickets",
                headers=headers,
                json=ticket_data
            )
            
            if response.status_code in [200, 201]:
                data = response.json()
                self.ticket_id = data['id']
                self.ticket_uuid = data['uuid']
                self.print_result(True, f"票券創建成功 (ID: {self.ticket_id}, UUID: {self.ticket_uuid})", data)
                return True
            else:
                self.print_result(False, f"票券創建失敗 (Status: {response.status_code})", response.text)
                return False
                
        except Exception as e:
            self.print_result(False, f"票券創建異常: {e}")
            return False
            
    def test_public_ticket_info(self) -> bool:
        """測試公開端點 - 查詢票券資訊"""
        self.print_step("公開端點 - 查詢票券資訊")
        
        if not self.ticket_uuid:
            self.print_result(False, "缺少票券UUID，無法測試")
            return False
            
        try:
            response = requests.get(f"{self.base_url}/api/v1/public/tickets/{self.ticket_uuid}")
            
            if response.status_code == 200:
                data = response.json()
                self.print_result(True, "票券資訊查詢成功", data)
                return True
            else:
                self.print_result(False, f"票券資訊查詢失敗 (Status: {response.status_code})", response.text)
                return False
                
        except Exception as e:
            self.print_result(False, f"票券資訊查詢異常: {e}")
            return False
            
    def test_public_qr_token(self) -> bool:
        """測試公開端點 - 獲取QR Token"""
        self.print_step("公開端點 - 獲取QR Token")
        
        if not self.ticket_uuid:
            self.print_result(False, "缺少票券UUID，無法測試")
            return False
            
        try:
            response = requests.get(f"{self.base_url}/api/v1/public/tickets/{self.ticket_uuid}/qr-token")
            
            if response.status_code == 200:
                data = response.json()
                self.qr_token = data['qr_token']
                self.print_result(True, f"QR Token獲取成功", {"qr_token": self.qr_token[:50] + "..."})
                return True
            else:
                self.print_result(False, f"QR Token獲取失敗 (Status: {response.status_code})", response.text)
                return False
                
        except Exception as e:
            self.print_result(False, f"QR Token獲取異常: {e}")
            return False
            
    def test_staff_checkin(self) -> bool:
        """測試員工 - 簽到票券"""
        self.print_step("員工操作 - 簽到票券")
        
        if not self.jwt_token or not self.qr_token or not self.event_id:
            self.print_result(False, "缺少必要資料，無法測試")
            return False
            
        checkin_data = {
            "qr_token": self.qr_token,
            "event_id": self.event_id
        }
        
        headers = {
            "Authorization": f"Bearer {self.jwt_token}",
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/api/v1/staff/checkin/",
                headers=headers,
                json=checkin_data
            )
            
            if response.status_code == 200:
                data = response.json()
                self.print_result(True, "票券簽到成功", data)
                return True
            else:
                self.print_result(False, f"票券簽到失敗 (Status: {response.status_code})", response.text)
                return False
                
        except Exception as e:
            self.print_result(False, f"票券簽到異常: {e}")
            return False
            
    def test_authentication_failures(self) -> bool:
        """測試認證失敗情況"""
        self.print_step("認證安全測試")
        
        tests = [
            {
                "name": "無Admin Password訪問Admin API",
                "url": f"{self.base_url}/admin/merchants",
                "method": "GET",
                "headers": {},
                "expected_status": 422
            },
            {
                "name": "無API Key訪問管理API", 
                "url": f"{self.base_url}/api/v1/mgmt/events",
                "method": "GET",
                "headers": {},
                "expected_status": 422
            },
            {
                "name": "無JWT訪問員工API",
                "url": f"{self.base_url}/api/v1/staff/me/profile",
                "method": "GET", 
                "headers": {},
                "expected_status": 401
            }
        ]
        
        all_passed = True
        for test in tests:
            try:
                if test["method"] == "GET":
                    response = requests.get(test["url"], headers=test["headers"])
                elif test["method"] == "POST":
                    response = requests.post(test["url"], headers=test["headers"], json={})
                    
                if response.status_code == test["expected_status"]:
                    self.print_result(True, f"{test['name']} - 正確拒絕 (Status: {response.status_code})")
                else:
                    self.print_result(False, f"{test['name']} - 預期 {test['expected_status']}，實際 {response.status_code}")
                    all_passed = False
                    
            except Exception as e:
                self.print_result(False, f"{test['name']} - 測試異常: {e}")
                all_passed = False
                
        return all_passed
        
    def run_all_tests(self) -> bool:
        """執行所有測試"""
        print(f"\n🚀 開始執行重構後API架構完整測試")
        print(f"目標URL: {self.base_url}")
        print(f"Admin Password: {self.admin_password}")
        
        tests = [
            self.test_health_check,
            self.test_admin_create_merchant,
            self.test_mgmt_create_event,
            self.test_mgmt_create_staff,
            self.test_mgmt_assign_staff_event,
            self.test_staff_login,
            self.test_staff_profile,
            self.test_mgmt_create_ticket,
            self.test_public_ticket_info,
            self.test_public_qr_token,
            self.test_staff_checkin,
            self.test_authentication_failures
        ]
        
        passed = 0
        total = len(tests)
        
        for test in tests:
            if test():
                passed += 1
            time.sleep(0.5)  # 避免請求過快
            
        # 最終結果
        print(f"\n{'='*60}")
        print(f"🏁 測試完成！")
        print(f"📊 結果: {passed}/{total} 項測試通過")
        
        if passed == total:
            print("🎉 所有測試都通過了！API重構成功！")
            return True
        else:
            print(f"❌ 有 {total-passed} 項測試失敗，請檢查問題")
            return False

def main():
    """主函數"""
    tester = RefactoredAPITester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()

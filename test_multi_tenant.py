"""
多租戶功能測試腳本
"""
import requests
import json
import sys
from datetime import datetime

# API 基礎URL
BASE_URL = "http://localhost:8000"

# 測試數據
test_merchants = [
    {
        "name": "測試商戶A",
        "contact_name": "測試聯絡人A",
        "contact_email": "test-a@example.com",
        "contact_phone": "123-456-7890"
    },
    {
        "name": "測試商戶B", 
        "contact_name": "測試聯絡人B",
        "contact_email": "test-b@example.com",
        "contact_phone": "098-765-4321"
    }
]

class MultiTenantTester:
    def __init__(self):
        self.admin_api_key = "test-api-key"  # 管理員API Key
        self.merchants = []
        self.api_keys = {}
        
    def test_health_check(self):
        """測試系統健康檢查"""
        print("🏥 測試系統健康檢查...")
        try:
            response = requests.get(f"{BASE_URL}/health")
            if response.status_code == 200:
                print("✅ 系統健康檢查通過")
                return True
            else:
                print(f"❌ 系統健康檢查失敗: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ 系統健康檢查異常: {e}")
            return False
    
    def test_create_merchants(self):
        """測試創建商戶"""
        print("\n🏢 測試創建商戶...")
        
        for merchant_data in test_merchants:
            try:
                response = requests.post(
                    f"{BASE_URL}/admin/merchants",
                    json=merchant_data,
                    headers={"X-API-Key": self.admin_api_key}
                )
                
                if response.status_code == 200:
                    merchant = response.json()
                    self.merchants.append(merchant)
                    print(f"✅ 成功創建商戶: {merchant['name']} (ID: {merchant['id']})")
                else:
                    print(f"❌ 創建商戶失敗: {response.status_code} - {response.text}")
                    
            except Exception as e:
                print(f"❌ 創建商戶異常: {e}")
        
        return len(self.merchants) > 0
    
    def test_create_api_keys(self):
        """測試創建API Keys"""
        print("\n🔑 測試創建API Keys...")
        
        for merchant in self.merchants:
            try:
                api_key_data = {
                    "key_name": f"{merchant['name']} - 主要API Key",
                    "expires_days": None  # 永不過期
                }
                
                response = requests.post(
                    f"{BASE_URL}/admin/merchants/{merchant['id']}/api-keys",
                    json=api_key_data,
                    headers={"X-API-Key": self.admin_api_key}
                )
                
                if response.status_code == 200:
                    api_key = response.json()
                    self.api_keys[merchant['id']] = api_key['api_key']
                    print(f"✅ 為商戶 {merchant['name']} 創建API Key: {api_key['api_key'][:16]}...")
                else:
                    print(f"❌ 創建API Key失敗: {response.status_code} - {response.text}")
                    
            except Exception as e:
                print(f"❌ 創建API Key異常: {e}")
        
        return len(self.api_keys) > 0
    
    def test_create_staff(self):
        """測試創建員工"""
        print("\n👤 測試創建員工...")
        
        for merchant in self.merchants:
            merchant_id = merchant['id']
            api_key = self.api_keys.get(merchant_id)
            
            if not api_key:
                print(f"❌ 商戶 {merchant['name']} 沒有API Key，跳過員工創建")
                continue
            
            staff_data = {
                "username": f"staff_{merchant_id}_test",
                "password": "test123456",
                "name": f"{merchant['name']} - 測試員工",
                "email": f"staff_test_{merchant_id}@example.com",
                "role": "admin"
            }
            
            try:
                response = requests.post(
                    f"{BASE_URL}/api/staff/create",
                    json=staff_data,
                    headers={"X-API-Key": api_key}
                )
                
                if response.status_code == 200:
                    staff = response.json()
                    print(f"✅ 為商戶 {merchant['name']} 創建員工: {staff['full_name']} (ID: {staff['id']})")
                    # 保存員工信息以供後續測試
                    merchant['test_staff'] = staff
                else:
                    print(f"❌ 創建員工失敗: {response.status_code} - {response.text}")
                    
            except Exception as e:
                print(f"❌ 創建員工異常: {e}")
    
    def test_create_events(self):
        """測試創建活動"""
        print("\n🎪 測試創建活動...")
        
        for merchant in self.merchants:
            merchant_id = merchant['id']
            api_key = self.api_keys.get(merchant_id)
            staff = merchant.get('test_staff')
            
            if not api_key or not staff:
                print(f"❌ 商戶 {merchant['name']} 缺少API Key或員工，跳過活動創建")
                continue
            
            event_data = {
                "name": f"{merchant['name']} - 測試活動",
                "description": "多租戶測試活動",
                "start_time": "2024-08-01T10:00:00",
                "end_time": "2024-08-01T18:00:00",
                "location": f"{merchant['name']}測試場地"
            }
            
            try:
                response = requests.post(
                    f"{BASE_URL}/api/events",
                    json=event_data,
                    headers={
                        "X-API-Key": api_key,
                        "staff-id": str(staff['id'])
                    }
                )
                
                if response.status_code == 200:
                    event = response.json()
                    print(f"✅ 為商戶 {merchant['name']} 創建活動: {event['name']} (ID: {event['id']})")
                    merchant['test_event'] = event
                else:
                    print(f"❌ 創建活動失敗: {response.status_code} - {response.text}")
                    
            except Exception as e:
                print(f"❌ 創建活動異常: {e}")
    
    def test_tenant_isolation(self):
        """測試租戶隔離"""
        print("\n🔒 測試租戶隔離...")
        
        if len(self.merchants) < 2:
            print("❌ 需要至少2個商戶才能測試租戶隔離")
            return
        
        merchant_a = self.merchants[0]
        merchant_b = self.merchants[1]
        
        api_key_a = self.api_keys.get(merchant_a['id'])
        api_key_b = self.api_keys.get(merchant_b['id'])
        
        if not api_key_a or not api_key_b:
            print("❌ 缺少API Key，無法測試租戶隔離")
            return
        
        # 測試商戶A嘗試訪問商戶B的數據
        print(f"🔍 測試商戶A ({merchant_a['name']}) 是否能訪問商戶B的數據...")
        
        try:
            # 嘗試用商戶A的API Key獲取商戶B的統計信息
            response = requests.get(
                f"{BASE_URL}/admin/merchants/{merchant_b['id']}/statistics",
                headers={"X-API-Key": api_key_a}
            )
            
            if response.status_code == 401:
                print("✅ 租戶隔離測試通過：商戶A無法訪問商戶B的數據")
            else:
                print(f"❌ 租戶隔離失敗：商戶A可以訪問商戶B的數據 (狀態碼: {response.status_code})")
                
        except Exception as e:
            print(f"❌ 租戶隔離測試異常: {e}")
    
    def test_merchant_statistics(self):
        """測試商戶統計"""
        print("\n📊 測試商戶統計...")
        
        for merchant in self.merchants:
            merchant_id = merchant['id']
            
            try:
                response = requests.get(
                    f"{BASE_URL}/admin/merchants/{merchant_id}/statistics",
                    headers={"X-API-Key": self.admin_api_key}
                )
                
                if response.status_code == 200:
                    stats = response.json()
                    print(f"✅ 商戶 {merchant['name']} 統計:")
                    print(f"   - 活動數: {stats['total_events']}")
                    print(f"   - 門票數: {stats['total_tickets']}")
                    print(f"   - 員工數: {stats['total_staff']}")
                    print(f"   - API Keys: {stats['active_api_keys']}")
                else:
                    print(f"❌ 獲取商戶統計失敗: {response.status_code} - {response.text}")
                    
            except Exception as e:
                print(f"❌ 獲取商戶統計異常: {e}")
    
    def test_api_key_management(self):
        """測試API Key管理"""
        print("\n🔐 測試API Key管理...")
        
        if not self.merchants:
            print("❌ 沒有可用的商戶")
            return
        
        merchant = self.merchants[0]
        merchant_id = merchant['id']
        
        # 獲取商戶的API Keys
        try:
            response = requests.get(
                f"{BASE_URL}/admin/merchants/{merchant_id}/api-keys",
                headers={"X-API-Key": self.admin_api_key}
            )
            
            if response.status_code == 200:
                api_keys = response.json()
                print(f"✅ 獲取商戶 {merchant['name']} 的API Keys: {len(api_keys)} 個")
                
                for key in api_keys:
                    print(f"   - {key['key_name']}: {key['api_key'][:16]}... (狀態: {'啟用' if key['is_active'] else '停用'})")
            else:
                print(f"❌ 獲取API Keys失敗: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"❌ 獲取API Keys異常: {e}")
    
    def run_all_tests(self):
        """運行所有測試"""
        print("🚀 開始多租戶功能測試")
        print("=" * 60)
        
        # 測試順序
        tests = [
            ("系統健康檢查", self.test_health_check),
            ("創建商戶", self.test_create_merchants),
            ("創建API Keys", self.test_create_api_keys),
            ("創建員工", self.test_create_staff),
            ("創建活動", self.test_create_events),
            ("租戶隔離", self.test_tenant_isolation),
            ("商戶統計", self.test_merchant_statistics),
            ("API Key管理", self.test_api_key_management),
        ]
        
        passed = 0
        failed = 0
        
        for test_name, test_func in tests:
            try:
                result = test_func()
                if result is not False:  # None 或 True 都視為通過
                    passed += 1
                else:
                    failed += 1
            except Exception as e:
                print(f"❌ 測試 '{test_name}' 發生異常: {e}")
                failed += 1
        
        print("\n" + "=" * 60)
        print(f"🏁 測試完成！通過: {passed}, 失敗: {failed}")
        
        if failed == 0:
            print("🎉 所有測試都通過了！")
        else:
            print(f"⚠️  有 {failed} 個測試失敗，請檢查相關功能")
        
        # 輸出測試結果摘要
        print(f"\n📋 測試結果摘要:")
        print(f"   - 創建商戶數: {len(self.merchants)}")
        print(f"   - 創建API Key數: {len(self.api_keys)}")
        
        if self.api_keys:
            print(f"\n🔑 可用的API Keys:")
            for merchant_id, api_key in self.api_keys.items():
                merchant = next((m for m in self.merchants if m['id'] == merchant_id), None)
                if merchant:
                    print(f"   - {merchant['name']}: {api_key}")

def main():
    """主函數"""
    print("🧪 多租戶功能測試腳本")
    print("確保系統已啟動在 http://localhost:8000")
    
    # 確認是否繼續
    response = input("\n是否開始測試？(y/n): ")
    if response.lower() != 'y':
        print("測試取消")
        return
    
    tester = MultiTenantTester()
    tester.run_all_tests()

if __name__ == "__main__":
    main()

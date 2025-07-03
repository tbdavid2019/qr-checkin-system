"""
Snowflake ID 生成器
基於 Twitter Snowflake 演算法，生成 64-bit 唯一 ID
"""
import time
import threading
from typing import Optional

class SnowflakeIDGenerator:
    def __init__(self, machine_id: int = 1, datacenter_id: int = 1):
        # 64-bit 結構：1-bit符號 + 41-bit時間戳 + 5-bit資料中心 + 5-bit機器 + 12-bit序號
        self.machine_id = machine_id & 0x1F      # 5 bits
        self.datacenter_id = datacenter_id & 0x1F # 5 bits
        self.sequence = 0                         # 12 bits
        self.last_timestamp = -1
        self.epoch = 1609459200000  # 2021-01-01 00:00:00 UTC (毫秒)
        self.lock = threading.Lock()
    
    def generate_id(self) -> int:
        with self.lock:
            timestamp = int(time.time() * 1000)
            
            if timestamp < self.last_timestamp:
                raise Exception("時鐘回撥，無法生成 ID")
            
            if timestamp == self.last_timestamp:
                self.sequence = (self.sequence + 1) & 0xFFF  # 12 bits
                if self.sequence == 0:
                    # 等待下一毫秒
                    while timestamp <= self.last_timestamp:
                        timestamp = int(time.time() * 1000)
            else:
                self.sequence = 0
            
            self.last_timestamp = timestamp
            
            # 組合 ID
            return ((timestamp - self.epoch) << 22) | (self.datacenter_id << 17) | (self.machine_id << 12) | self.sequence

# 全域實例
_snowflake_generator = None

def get_snowflake_generator() -> SnowflakeIDGenerator:
    global _snowflake_generator
    if _snowflake_generator is None:
        _snowflake_generator = SnowflakeIDGenerator()
    return _snowflake_generator

def generate_snowflake_id() -> int:
    """生成 Snowflake ID"""
    return get_snowflake_generator().generate_id()
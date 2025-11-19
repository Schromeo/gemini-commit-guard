import sqlite3
import json
import os
from datetime import datetime

class AuditLogger:
    def __init__(self, db_path=".gemini_audit.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """初始化数据库表结构"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        # 创建 logs 表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                status TEXT,      -- PASS / FAIL
                message TEXT,     -- 简短总结
                diff TEXT,        -- 代码变更
                context TEXT,     -- 完整上下文
                ai_response TEXT  -- 完整的 JSON 响应
            )
        ''')
        conn.commit()
        conn.close()

    def log_event(self, status, message, diff, context, ai_response_dict):
        """记录一次提交审计事件"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO logs (timestamp, status, message, diff, context, ai_response)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            status,
            message,
            diff,
            context,
            json.dumps(ai_response_dict, ensure_ascii=False) # 存为 JSON 字符串
        ))
        
        conn.commit()
        conn.close()
        print(f"   💾 Audit log saved to {self.db_path}")

# 单元测试
if __name__ == "__main__":
    logger = AuditLogger()
    logger.log_event("TEST", "Test Message", "diff...", "context...", {"details": []})
    print("Test log created.")
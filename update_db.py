import sqlite3
import os

print("开始更新数据库结构...")

# 确保数据库文件存在
db_path = 'instance/zl_geniusmedvault.db'
if not os.path.exists(db_path):
    print(f"错误: 数据库文件 {db_path} 不存在")
    exit(1)

# 连接数据库
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    # 检查分析项目表是否存在
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='analysis_project'")
    if not cursor.fetchone():
        print("错误: analysis_project表不存在")
        conn.close()
        exit(1)
        
    # 检查列是否已存在
    cursor.execute("PRAGMA table_info(analysis_project)")
    columns = {col[1] for col in cursor.fetchall()}
    
    # 添加status列
    if 'status' not in columns:
        print("添加status列...")
        cursor.execute("ALTER TABLE analysis_project ADD COLUMN status VARCHAR(20) DEFAULT 'active'")
    else:
        print("status列已存在")
        
    # 添加is_multi_center列
    if 'is_multi_center' not in columns:
        print("添加is_multi_center列...")
        cursor.execute("ALTER TABLE analysis_project ADD COLUMN is_multi_center BOOLEAN DEFAULT 0")
    else:
        print("is_multi_center列已存在")
        
    # 添加collaborators列
    if 'collaborators' not in columns:
        print("添加collaborators列...")
        cursor.execute("ALTER TABLE analysis_project ADD COLUMN collaborators TEXT")
    else:
        print("collaborators列已存在")
    
    # 提交更改
    conn.commit()
    print("数据库结构更新成功!")
    
except Exception as e:
    print(f"更新数据库时出错: {e}")
    conn.rollback()
    
finally:
    conn.close() 
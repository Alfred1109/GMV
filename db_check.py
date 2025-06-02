import sqlite3
import json

# 连接到数据库
conn = sqlite3.connect('zl_geniusmedvault.db')
cursor = conn.cursor()

# 获取所有表
print("=== 数据库中的所有表 ===")
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print(tables)

# 检查data_set表是否存在，如果存在则检查其结构和数据
if ('data_set',) in tables:
    print("\n=== data_set表结构 ===")
    cursor.execute("PRAGMA table_info(data_set)")
    columns = cursor.fetchall()
    print(columns)
    
    print("\n=== data_set表数据 ===")
    cursor.execute("SELECT id, name, description, created_by, custom_fields, privacy_level, team_members FROM data_set LIMIT 5")
    rows = cursor.fetchall()
    for row in rows:
        print(f"ID: {row[0]}, 名称: {row[1]}, 描述: {row[2]}, 创建者: {row[3]}")
        if row[4]:  # custom_fields
            try:
                custom_fields = json.loads(row[4])
                print(f"自定义字段: {custom_fields}")
            except:
                print(f"自定义字段(原始): {row[4]}")
        print(f"隐私级别: {row[5]}, 团队成员: {row[6]}\n")
else:
    print("\ndata_set表不存在!")

# 检查dataset_entries表是否存在
if ('dataset_entries',) in tables:
    print("\n=== dataset_entries表结构 ===")
    cursor.execute("PRAGMA table_info(dataset_entries)")
    columns = cursor.fetchall()
    print(columns)
    
    print("\n=== dataset_entries表数据 ===")
    cursor.execute("SELECT * FROM dataset_entries LIMIT 5")
    rows = cursor.fetchall()
    for row in rows:
        print(row)
else:
    print("\ndataset_entries表不存在!")

# 关闭连接
conn.close() 
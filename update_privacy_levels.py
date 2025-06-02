import sqlite3
import os

def update_privacy_levels():
    """
    更新数据库中所有privacy_level为NULL或空的数据集记录，将其设置为'public'
    """
    conn = None
    try:
        # 获取数据库路径
        db_path = os.path.join('instance', 'zl_geniusmedvault.db')
        print(f"正在连接数据库: {db_path}")
        
        if not os.path.exists(db_path):
            print(f"错误: 数据库文件不存在: {db_path}")
            return False
            
        # 连接到SQLite数据库
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 检查数据集表是否存在
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='data_set'")
        if not cursor.fetchone():
            print("错误: 数据集表(data_set)不存在")
            conn.close()
            return False
        else:
            print("找到数据集表(data_set)")
            
        # 检查privacy_level列是否存在
        cursor.execute("PRAGMA table_info(data_set)")
        columns = [row[1] for row in cursor.fetchall()]
        if 'privacy_level' not in columns:
            print("错误: privacy_level列不存在于data_set表中")
            conn.close()
            return False
        else:
            print("找到privacy_level列")
        
        # 显示所有数据集的当前状态
        print("\n当前数据集状态:")
        cursor.execute("SELECT id, name, privacy_level FROM data_set")
        datasets = cursor.fetchall()
        for dataset in datasets:
            privacy = dataset[2] if dataset[2] else "NULL/空"
            print(f"ID: {dataset[0]}, 名称: {dataset[1]}, 隐私级别: {privacy}")
            
        # 查询所有privacy_level为NULL或空的记录
        cursor.execute("SELECT id, name FROM data_set WHERE privacy_level IS NULL OR privacy_level = ''")
        null_records = cursor.fetchall()
        
        if not null_records:
            print("\n没有找到privacy_level为NULL或空的记录，无需更新")
            conn.close()
            return True
        
        print(f"\n找到 {len(null_records)} 条privacy_level为NULL或空的记录")
            
        # 更新所有privacy_level为NULL或空的记录为'public'
        cursor.execute("UPDATE data_set SET privacy_level = 'public' WHERE privacy_level IS NULL OR privacy_level = ''")
        conn.commit()
        
        # 验证更新
        updated_count = len(null_records)
        print(f"成功更新了 {updated_count} 条记录的privacy_level为'public'")
        
        # 显示更新的记录
        print("\n已更新的记录:")
        for record_id, name in null_records:
            print(f"ID: {record_id}, 名称: {name}")
            
        # 显示更新后的状态
        print("\n更新后的数据集状态:")
        cursor.execute("SELECT id, name, privacy_level FROM data_set")
        updated_datasets = cursor.fetchall()
        for dataset in updated_datasets:
            print(f"ID: {dataset[0]}, 名称: {dataset[1]}, 隐私级别: {dataset[2]}")
            
        conn.close()
        return True
        
    except sqlite3.Error as e:
        print(f"SQLite错误: {e}")
        if conn:
            conn.close()
        return False
    except Exception as e:
        print(f"发生错误: {e}")
        if conn:
            conn.close()
        return False

if __name__ == "__main__":
    print("开始更新数据集privacy_level...")
    if update_privacy_levels():
        print("更新完成")
    else:
        print("更新失败") 
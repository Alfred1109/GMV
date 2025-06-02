import sqlite3
import json
import os

def check_dataset(dataset_id=2):
    """
    检查指定ID的数据集信息
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
        
        # 获取数据集信息
        cursor.execute("""
            SELECT id, name, description, created_by, version, privacy_level, custom_fields, preview_data
            FROM data_set WHERE id = ?
        """, (dataset_id,))
        
        dataset = cursor.fetchone()
        
        if not dataset:
            print(f"错误: 数据集ID={dataset_id}不存在")
            conn.close()
            return False
        
        # 打印数据集基本信息
        print("\n数据集基本信息:")
        print(f"ID: {dataset[0]}")
        print(f"名称: {dataset[1]}")
        print(f"描述: {dataset[2] or '无'}")
        print(f"创建者ID: {dataset[3]}")
        print(f"版本: {dataset[4] or '1.0'}")
        print(f"隐私级别: {dataset[5] or 'public'}")
        
        # 解析并打印自定义字段
        custom_fields = dataset[6]
        if custom_fields:
            try:
                fields = json.loads(custom_fields)
                print("\n自定义字段:")
                for i, field in enumerate(fields):
                    print(f"{i+1}. {field['name']} ({field['type']}): {field.get('description', '')}")
                    if 'range' in field:
                        print(f"   取值范围: {field['range']}")
                    if 'required' in field:
                        print(f"   必填: {'是' if field['required'] else '否'}")
            except json.JSONDecodeError as e:
                print(f"\n自定义字段JSON解析错误: {e}")
                print(f"原始数据: {custom_fields}")
        else:
            print("\n无自定义字段")
        
        # 解析并打印预览数据
        preview_data = dataset[7]
        if preview_data:
            try:
                preview = json.loads(preview_data)
                print("\n预览数据:")
                print(f"列: {preview.get('columns', [])}")
                print(f"行数: {len(preview.get('rows', []))}")
                for i, row in enumerate(preview.get('rows', [])):
                    print(f"行 {i+1}: {row}")
            except json.JSONDecodeError as e:
                print(f"\n预览数据JSON解析错误: {e}")
                print(f"原始数据: {preview_data}")
        else:
            print("\n无预览数据")
        
        conn.close()
        return True
    
    except sqlite3.Error as e:
        print(f"SQLite错误: {e}")
        if conn:
            conn.close()
        return False
    except Exception as e:
        print(f"发生错误: {e}")
        import traceback
        traceback.print_exc()
        if conn:
            conn.close()
        return False

if __name__ == "__main__":
    print("检查数据集信息...")
    check_dataset(2)
    print("\n检查完成") 
import sqlite3
import json

# 连接数据库
conn = sqlite3.connect('instance/zl_geniusmedvault.db')
cursor = conn.cursor()

# 获取数据集信息
cursor.execute('SELECT id, name, custom_fields FROM data_set WHERE id = 1')
row = cursor.fetchone()

print(f'数据集ID: {row[0]}, 名称: {row[1]}')
print('自定义字段数量:')
fields = json.loads(row[2])
print(len(fields))

print('字段类型统计:')
types = {}
for field in fields:
    t = field.get('type', 'unknown')
    types[t] = types.get(t, 0) + 1
print(types)

print('\n前5个字段示例:')
for i, field in enumerate(fields[:5]):
    print(f"{i+1}. {field['name']} ({field['type']}): {field.get('description', '无描述')}")

conn.close() 
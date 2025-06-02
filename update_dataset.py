import sqlite3

# 连接到SQLite数据库
conn = sqlite3.connect('instance/zl_geniusmedvault.db')
cursor = conn.cursor()

# 更新数据集2的privacy_level为public
cursor.execute('UPDATE data_set SET privacy_level = "public" WHERE id = 2')
conn.commit()

# 验证更新
cursor.execute('SELECT id, name, privacy_level FROM data_set WHERE id = 2')
result = cursor.fetchone()
if result:
    print(f"数据集ID={result[0]}, 名称={result[1]}, 权限级别={result[2]}")
else:
    print("未找到ID为2的数据集")

# 关闭连接
conn.close() 
import requests
import json

# 设置API URL
base_url = 'http://localhost:80'
dataset_id = 1  # 使用第一个数据集

# 测试获取数据集变量API
variables_url = f'{base_url}/api/test/datasets/{dataset_id}/variables'
response = requests.get(variables_url)
print(f"获取变量API状态码: {response.status_code}")

# 打印API响应
if response.status_code == 200:
    try:
        data = response.json()
        print("API响应:")
        print(json.dumps(data, indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"解析JSON失败: {e}")
        print(f"响应内容: {response.text[:500]}")
else:
    print(f"API请求失败: {response.text[:500]}") 
import json
import sys
import urllib.request
import urllib.error

def test_view_data_api(dataset_id=2):
    """
    测试/api/datasets/<int:dataset_id>/view_data API端点
    
    Args:
        dataset_id: 要测试的数据集ID
    """
    try:
        # API端点URL
        url = f"http://127.0.0.1:6000/api/datasets/{dataset_id}/view_data"
        print(f"请求URL: {url}")
        
        # 发送GET请求
        try:
            # 创建请求对象
            req = urllib.request.Request(url)
            # 添加一些HTTP头，模拟浏览器请求
            req.add_header('User-Agent', 'Mozilla/5.0')
            
            # 发送请求
            response = urllib.request.urlopen(req)
            status_code = response.getcode()
            print(f"状态码: {status_code}")
            
            # 如果请求成功
            if status_code == 200:
                # 读取响应内容
                response_data = response.read().decode('utf-8')
                
                # 输出原始响应内容（用于调试）
                print("\n原始响应内容:")
                print(response_data[:200] + "..." if len(response_data) > 200 else response_data)
                
                # 解析JSON响应
                try:
                    data = json.loads(response_data)
                    
                    # 打印数据集信息
                    if data.get('success'):
                        dataset = data.get('dataset', {})
                        print(f"\n数据集信息:")
                        print(f"ID: {dataset.get('id')}")
                        print(f"名称: {dataset.get('name')}")
                        print(f"描述: {dataset.get('description', '无')}")
                        print(f"版本: {dataset.get('version', '1.0')}")
                        print(f"隐私级别: {dataset.get('privacy_level', 'public')}")
                        
                        # 打印自定义字段
                        fields = data.get('fields', [])
                        if fields:
                            print(f"\n自定义字段 ({len(fields)}):")
                            for i, field in enumerate(fields):
                                print(f"{i+1}. {field.get('name')} ({field.get('type')}): {field.get('description', '')}")
                        else:
                            print("\n无自定义字段")
                        
                        # 打印数据条目
                        entries = data.get('entries', [])
                        if entries:
                            print(f"\n数据条目 ({len(entries)}):")
                            for i, entry in enumerate(entries[:3]):  # 只显示前3条
                                print(f"条目 {i+1}:")
                                print(f"  ID: {entry.get('id')}")
                                print(f"  用户: {entry.get('username')}")
                                print(f"  创建时间: {entry.get('created_at')}")
                                print(f"  数据: {json.dumps(entry.get('data', {}), ensure_ascii=False)[:100]}...")
                            
                            if len(entries) > 3:
                                print(f"... 还有 {len(entries) - 3} 条记录")
                        else:
                            print("\n无数据条目")
                    else:
                        print(f"\n请求失败: {data.get('message', '未知错误')}")
                except json.JSONDecodeError as e:
                    print(f"\nJSON解析错误: {e}")
                    print("响应内容不是有效的JSON格式。这可能是因为需要登录认证。")
            else:
                print(f"\n请求失败: HTTP {status_code}")
                
        except urllib.error.HTTPError as e:
            print(f"\n请求失败: HTTP {e.code}")
            print(f"错误信息: {e.reason}")
            
            # 如果是401错误，提示需要登录认证
            if e.code == 401:
                print("\n需要登录认证。这个API端点需要用户登录后才能访问。")
                print("建议使用浏览器登录系统后，通过浏览器的开发者工具测试API。")
            
            # 读取错误响应内容
            try:
                error_data = e.read().decode('utf-8')
                print("\n错误响应内容:")
                print(error_data)
            except:
                pass
                
        except urllib.error.URLError as e:
            print(f"\n连接错误: {e.reason}")
            print("请确保Flask应用正在运行，且端口为6000")
            
    except Exception as e:
        print(f"发生错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # 如果提供了命令行参数，使用它作为数据集ID
    dataset_id = int(sys.argv[1]) if len(sys.argv) > 1 else 2
    print(f"测试数据集ID={dataset_id}的view_data API...")
    test_view_data_api(dataset_id) 
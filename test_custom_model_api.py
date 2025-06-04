"""
测试自定义统计模型API功能
"""

import requests
import json
import sys
import argparse
from pprint import pprint

def test_custom_model_api(base_url, username, password):
    """测试自定义统计模型API
    
    Args:
        base_url: API基础URL
        username: 登录用户名
        password: 登录密码
    """
    # 登录获取会话
    session = requests.Session()
    login_url = f"{base_url}/login"
    
    # 获取CSRF令牌
    csrf_response = session.get(login_url)
    if csrf_response.status_code != 200:
        print(f"获取登录页面失败: {csrf_response.status_code}")
        return
    
    # 从HTML中提取CSRF令牌
    csrf_token = None
    for line in csrf_response.text.split('\n'):
        if 'name="csrf_token"' in line:
            parts = line.split('value="')
            if len(parts) > 1:
                csrf_token = parts[1].split('"')[0]
                break
    
    if not csrf_token:
        print("无法获取CSRF令牌")
        return
    
    # 登录
    login_data = {
        'username': username,
        'password': password,
        'role': 'doctor',
        'csrf_token': csrf_token
    }
    
    login_response = session.post(login_url, data=login_data, allow_redirects=True)
    if login_response.status_code != 200:
        print(f"登录失败: {login_response.status_code}")
        return
    
    print("登录成功")
    
    # 测试创建自定义模型
    test_create_custom_model(session, base_url)
    
    # 测试获取模型列表
    model_id = test_list_custom_models(session, base_url)
    
    if model_id:
        # 测试获取特定模型
        test_get_custom_model(session, base_url, model_id)
        
        # 测试更新模型
        test_update_custom_model(session, base_url, model_id)
        
        # 测试应用模型
        test_apply_custom_model(session, base_url, model_id)
        
        # 测试删除模型
        test_delete_custom_model(session, base_url, model_id)

def test_create_custom_model(session, base_url):
    """测试创建自定义统计模型
    
    Args:
        session: 请求会话
        base_url: API基础URL
    """
    print("\n测试创建自定义统计模型...")
    
    # 准备请求数据
    model_data = {
        "name": "测试回归模型",
        "description": "这是一个用于测试的回归分析模型",
        "model_type": "regression",
        "config": {
            "regression_type": "linear",
            "target_variable": "bmi",
            "include_intercept": True
        },
        "variables": ["age", "gender", "height", "weight"],
        "is_public": True
    }
    
    # 发送请求
    create_url = f"{base_url}/api/custom_models"
    create_response = session.post(create_url, json=model_data)
    
    print(f"响应状态码: {create_response.status_code}")
    
    try:
        response_data = create_response.json()
        print("\n响应数据:")
        print(f"成功: {response_data.get('success', False)}")
        print(f"消息: {response_data.get('message', '无消息')}")
        
        if response_data.get('success'):
            print("\n创建的模型信息:")
            model = response_data.get('model', {})
            print(f"ID: {model.get('id')}")
            print(f"名称: {model.get('name')}")
            print(f"类型: {model.get('model_type')}")
            print(f"创建时间: {model.get('created_at')}")
            
            # 返回创建的模型ID
            return model.get('id')
    except ValueError:
        print("响应不是有效的JSON格式")
        print(create_response.text)
    
    return None

def test_list_custom_models(session, base_url):
    """测试获取自定义统计模型列表
    
    Args:
        session: 请求会话
        base_url: API基础URL
        
    Returns:
        int: 第一个模型的ID，如果没有则返回None
    """
    print("\n测试获取自定义统计模型列表...")
    
    # 发送请求
    list_url = f"{base_url}/api/custom_models"
    list_response = session.get(list_url)
    
    print(f"响应状态码: {list_response.status_code}")
    
    try:
        response_data = list_response.json()
        print("\n响应数据:")
        print(f"成功: {response_data.get('success', False)}")
        
        if response_data.get('success'):
            models = response_data.get('models', [])
            
            if models:
                print(f"\n找到{len(models)}个模型:")
                for i, model in enumerate(models):
                    print(f"\n模型 {i+1}:")
                    print(f"ID: {model.get('id')}")
                    print(f"名称: {model.get('name')}")
                    print(f"类型: {model.get('model_type')}")
                    print(f"创建时间: {model.get('created_at')}")
                
                # 返回第一个模型的ID
                return models[0].get('id')
            else:
                print("\n没有找到模型")
    except ValueError:
        print("响应不是有效的JSON格式")
        print(list_response.text)
    
    return None

def test_get_custom_model(session, base_url, model_id):
    """测试获取特定的自定义统计模型
    
    Args:
        session: 请求会话
        base_url: API基础URL
        model_id: 模型ID
    """
    print(f"\n测试获取自定义统计模型 (ID={model_id})...")
    
    # 发送请求
    get_url = f"{base_url}/api/custom_models/{model_id}"
    get_response = session.get(get_url)
    
    print(f"响应状态码: {get_response.status_code}")
    
    try:
        response_data = get_response.json()
        print("\n响应数据:")
        print(f"成功: {response_data.get('success', False)}")
        
        if response_data.get('success'):
            model = response_data.get('model', {})
            print("\n模型详情:")
            print(f"ID: {model.get('id')}")
            print(f"名称: {model.get('name')}")
            print(f"描述: {model.get('description')}")
            print(f"类型: {model.get('model_type')}")
            print(f"配置: {json.dumps(model.get('config', {}), indent=2)}")
            print(f"变量: {model.get('variables')}")
            print(f"创建者: {model.get('created_by')}")
            print(f"创建时间: {model.get('created_at')}")
            print(f"更新时间: {model.get('updated_at')}")
            print(f"数据集ID: {model.get('dataset_id')}")
            print(f"是否公开: {model.get('is_public')}")
    except ValueError:
        print("响应不是有效的JSON格式")
        print(get_response.text)

def test_update_custom_model(session, base_url, model_id):
    """测试更新自定义统计模型
    
    Args:
        session: 请求会话
        base_url: API基础URL
        model_id: 模型ID
    """
    print(f"\n测试更新自定义统计模型 (ID={model_id})...")
    
    # 准备请求数据
    update_data = {
        "name": "更新后的回归模型",
        "description": "这是一个更新后的回归分析模型",
        "config": {
            "regression_type": "linear",
            "target_variable": "bmi",
            "include_intercept": True,
            "standardize": True
        }
    }
    
    # 发送请求
    update_url = f"{base_url}/api/custom_models/{model_id}"
    update_response = session.put(update_url, json=update_data)
    
    print(f"响应状态码: {update_response.status_code}")
    
    try:
        response_data = update_response.json()
        print("\n响应数据:")
        print(f"成功: {response_data.get('success', False)}")
        print(f"消息: {response_data.get('message', '无消息')}")
        
        if response_data.get('success'):
            model = response_data.get('model', {})
            print("\n更新后的模型信息:")
            print(f"名称: {model.get('name')}")
            print(f"描述: {model.get('description')}")
            print(f"配置: {json.dumps(model.get('config', {}), indent=2)}")
            print(f"更新时间: {model.get('updated_at')}")
    except ValueError:
        print("响应不是有效的JSON格式")
        print(update_response.text)

def test_apply_custom_model(session, base_url, model_id):
    """测试应用自定义统计模型
    
    Args:
        session: 请求会话
        base_url: API基础URL
        model_id: 模型ID
    """
    print(f"\n测试应用自定义统计模型 (ID={model_id})...")
    
    # 获取一个可用的数据集ID
    datasets_url = f"{base_url}/api/datasets"
    datasets_response = session.get(datasets_url)
    
    dataset_id = None
    if datasets_response.status_code == 200:
        try:
            datasets_data = datasets_response.json()
            if datasets_data.get('success') and datasets_data.get('datasets'):
                dataset_id = datasets_data['datasets'][0]['id']
        except:
            pass
    
    if not dataset_id:
        print("无法获取数据集ID，跳过应用模型测试")
        return
    
    # 准备请求数据
    apply_data = {
        "dataset_id": dataset_id,
        "parameters": {
            "additional_param": "test_value"
        }
    }
    
    # 发送请求
    apply_url = f"{base_url}/api/custom_models/{model_id}/apply"
    apply_response = session.post(apply_url, json=apply_data)
    
    print(f"响应状态码: {apply_response.status_code}")
    
    try:
        response_data = apply_response.json()
        print("\n响应数据:")
        print(f"成功: {response_data.get('success', False)}")
        print(f"消息: {response_data.get('message', '无消息')}")
        
        if response_data.get('success'):
            result = response_data.get('result', {})
            print("\n应用结果:")
            print(f"模型类型: {result.get('model_type')}")
            print(f"消息: {result.get('message')}")
            print(f"变量: {result.get('variables')}")
            print(f"参数: {result.get('parameters')}")
    except ValueError:
        print("响应不是有效的JSON格式")
        print(apply_response.text)

def test_delete_custom_model(session, base_url, model_id):
    """测试删除自定义统计模型
    
    Args:
        session: 请求会话
        base_url: API基础URL
        model_id: 模型ID
    """
    print(f"\n测试删除自定义统计模型 (ID={model_id})...")
    
    # 发送请求
    delete_url = f"{base_url}/api/custom_models/{model_id}"
    delete_response = session.delete(delete_url)
    
    print(f"响应状态码: {delete_response.status_code}")
    
    try:
        response_data = delete_response.json()
        print("\n响应数据:")
        print(f"成功: {response_data.get('success', False)}")
        print(f"消息: {response_data.get('message', '无消息')}")
        
        if response_data.get('success'):
            print("\n模型删除成功")
            
            # 验证模型是否真的被删除
            get_url = f"{base_url}/api/custom_models/{model_id}"
            get_response = session.get(get_url)
            
            if get_response.status_code == 404:
                print("验证成功：模型已被删除")
            else:
                print(f"验证失败：模型可能未被删除，状态码: {get_response.status_code}")
    except ValueError:
        print("响应不是有效的JSON格式")
        print(delete_response.text)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='测试自定义统计模型API')
    parser.add_argument('--url', type=str, default='http://127.0.0.1:6000', help='API基础URL')
    parser.add_argument('--username', type=str, required=True, help='登录用户名')
    parser.add_argument('--password', type=str, required=True, help='登录密码')
    
    args = parser.parse_args()
    
    test_custom_model_api(args.url, args.username, args.password) 
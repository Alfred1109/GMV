"""
测试风险评估API功能
"""

import requests
import json
import sys
import argparse
from pprint import pprint

def test_risk_assessment_api(base_url, username, password, dataset_id, model_type='logistic'):
    """测试风险评估API
    
    Args:
        base_url: API基础URL
        username: 登录用户名
        password: 登录密码
        dataset_id: 数据集ID
        model_type: 模型类型 (logistic, decision_tree, random_forest)
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
    
    # 获取数据集字段信息
    fields_url = f"{base_url}/api/datasets/{dataset_id}/variables"
    fields_response = session.get(fields_url)
    
    if fields_response.status_code != 200:
        print(f"获取数据集字段失败: {fields_response.status_code}")
        return
    
    fields_data = fields_response.json()
    
    if not fields_data.get('success'):
        print(f"获取数据集字段失败: {fields_data.get('message')}")
        return
    
    # 提取字段信息
    fields = fields_data.get('fields', [])
    
    # 选择一个目标变量（二分类变量）和预测变量
    target_variable = None
    predictor_variables = []
    
    # 寻找二分类变量作为目标变量
    for field in fields:
        field_name = field.get('name')
        field_type = field.get('type')
        
        if field_type in ['binary', 'categorical'] and not target_variable:
            target_variable = field_name
        elif field_type in ['binary', 'categorical', 'continuous'] and len(predictor_variables) < 5:
            predictor_variables.append(field_name)
    
    if not target_variable:
        # 如果没有找到二分类变量，选择第一个分类变量
        for field in fields:
            if field.get('type') in ['categorical'] and not target_variable:
                target_variable = field.get('name')
    
    if not target_variable or len(predictor_variables) == 0:
        print("未能找到合适的目标变量或预测变量")
        return
    
    # 确保目标变量不在预测变量列表中
    if target_variable in predictor_variables:
        predictor_variables.remove(target_variable)
    
    # 确保至少有一个预测变量
    if len(predictor_variables) == 0:
        print("没有足够的预测变量")
        return
    
    print(f"选择的目标变量: {target_variable}")
    print(f"选择的预测变量: {predictor_variables}")
    
    # 调用风险评估API
    risk_url = f"{base_url}/api/analysis/risk"
    
    # 准备请求数据
    request_data = {
        'dataset_id': dataset_id,
        'model_type': model_type,
        'target_variable': target_variable,
        'predictor_variables': predictor_variables,
        'validation_method': 'cross_validation',
        'validation_params': {
            'cv_folds': 5,
            'test_size': 0.3
        }
    }
    
    print("\n发送请求数据:")
    pprint(request_data)
    
    # 发送请求
    risk_response = session.post(risk_url, json=request_data)
    
    print(f"\n响应状态码: {risk_response.status_code}")
    
    try:
        response_data = risk_response.json()
        print("\n响应数据:")
        pprint(response_data)
        
        if response_data.get('success'):
            print("\n风险评估成功!")
            
            # 显示评估指标
            if 'result' in response_data and 'evaluation_metrics' in response_data['result']:
                print("\n评估指标:")
                metrics = response_data['result']['evaluation_metrics']
                for metric, value in metrics.items():
                    if metric != 'confusion_matrix':
                        print(f"  {metric}: {value:.4f}")
            
            # 显示特征重要性
            if 'result' in response_data and 'feature_importance' in response_data['result']:
                print("\n特征重要性:")
                importance = response_data['result']['feature_importance']
                for feature, value in importance.items():
                    print(f"  {feature}: {value:.4f}")
            
            # 显示风险分层信息
            if 'result' in response_data and 'risk_stratification' in response_data['result']:
                print("\n风险分层:")
                strat = response_data['result']['risk_stratification']
                if 'thresholds' in strat:
                    print(f"  低风险阈值: {strat['thresholds']['low']:.4f}")
                    print(f"  高风险阈值: {strat['thresholds']['high']:.4f}")
                
                if 'group_stats' in strat:
                    for group, stats in strat['group_stats'].items():
                        print(f"  {group}风险组:")
                        print(f"    样本数量: {stats['count']}")
                        print(f"    事件率: {stats['event_rate']:.4f}")
        else:
            print(f"\n风险评估失败: {response_data.get('message')}")
            
    except ValueError:
        print("响应不是有效的JSON格式")
        print(risk_response.text)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='测试风险评估API')
    parser.add_argument('--url', type=str, default='http://127.0.0.1:6000', help='API基础URL')
    parser.add_argument('--username', type=str, required=True, help='登录用户名')
    parser.add_argument('--password', type=str, required=True, help='登录密码')
    parser.add_argument('--dataset', type=int, required=True, help='数据集ID')
    parser.add_argument('--model', type=str, default='logistic', choices=['logistic', 'decision_tree', 'random_forest'], help='模型类型')
    
    args = parser.parse_args()
    
    test_risk_assessment_api(args.url, args.username, args.password, args.dataset, args.model) 
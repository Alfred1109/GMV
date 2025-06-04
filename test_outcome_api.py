"""
测试结局预测API功能
"""

import requests
import json
import sys
import argparse
from pprint import pprint

def test_outcome_prediction_api(base_url, username, password, dataset_id, model_type='random_forest'):
    """测试结局预测API
    
    Args:
        base_url: API基础URL
        username: 登录用户名
        password: 登录密码
        dataset_id: 数据集ID
        model_type: 模型类型 (random_forest, gradient_boosting, logistic)
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
    time_variable = None
    predictor_variables = []
    
    # 寻找二分类变量作为目标变量
    for field in fields:
        field_name = field.get('name')
        field_type = field.get('type')
        
        if field_type in ['binary', 'categorical'] and not target_variable:
            target_variable = field_name
        elif field_name.lower() in ['survival_time', 'follow_up', 'follow_up_days', 'time', 'days'] and not time_variable:
            time_variable = field_name
        elif field_type in ['binary', 'categorical', 'continuous'] and len(predictor_variables) < 5:
            if field_name != target_variable and field_name != time_variable:
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
    if time_variable:
        print(f"选择的时间变量: {time_variable}")
    print(f"选择的预测变量: {predictor_variables}")
    
    # 调用结局预测API
    prediction_url = f"{base_url}/api/analysis/outcome_prediction"
    
    # 准备请求数据
    request_data = {
        'dataset_id': dataset_id,
        'model_type': model_type,
        'target_variable': target_variable,
        'predictor_variables': predictor_variables,
        'validation_method': 'split',
        'validation_params': {
            'test_size': 0.3
        },
        'save_model': True
    }
    
    # 如果有时间变量，添加到请求中
    if time_variable:
        request_data['time_variable'] = time_variable
        request_data['prediction_horizon'] = 180  # 180天结局预测
    
    print("\n发送请求数据:")
    pprint(request_data)
    
    # 发送请求
    prediction_response = session.post(prediction_url, json=request_data)
    
    print(f"\n响应状态码: {prediction_response.status_code}")
    
    try:
        response_data = prediction_response.json()
        print("\n响应数据:")
        print(f"成功: {response_data.get('success', False)}")
        print(f"消息: {response_data.get('message', '无消息')}")
        
        if response_data.get('success'):
            print("\n结局预测成功!")
            
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
                for feature, value in sorted(importance.items(), key=lambda x: x[1], reverse=True):
                    print(f"  {feature}: {value:.4f}")
            
            # 显示风险分层信息
            if 'result' in response_data and 'risk_stratification' in response_data['result']:
                print("\n风险分层:")
                strat = response_data['result']['risk_stratification']
                if 'thresholds' in strat:
                    print(f"  Q1 (25%分位数): {strat['thresholds'].get('q1', 'N/A')}")
                    print(f"  Q2 (50%分位数): {strat['thresholds'].get('q2', 'N/A')}")
                    print(f"  Q3 (75%分位数): {strat['thresholds'].get('q3', 'N/A')}")
                
                if 'group_stats' in strat:
                    for group, stats in strat['group_stats'].items():
                        print(f"\n  {group}风险组:")
                        print(f"    样本数: {stats.get('count', 'N/A')}")
                        print(f"    事件率: {stats.get('event_rate', 'N/A')}")
                        print(f"    平均概率: {stats.get('mean_probability', 'N/A')}")
            
            # 如果模型已保存，则测试单个预测
            if 'model_info' in response_data and 'path' in response_data['model_info']:
                model_path = response_data['model_info']['path']
                print(f"\n模型已保存到: {model_path}")
                
                # 测试单个预测
                test_individual_prediction(session, base_url, model_path, predictor_variables)
        else:
            print(f"\n结局预测失败: {response_data.get('message')}")
            
    except ValueError:
        print("响应不是有效的JSON格式")
        print(prediction_response.text)

def test_individual_prediction(session, base_url, model_path, predictor_variables):
    """测试单个结局预测
    
    Args:
        session: 请求会话
        base_url: API基础URL
        model_path: 模型路径
        predictor_variables: 预测变量列表
    """
    print("\n测试单个结局预测...")
    
    # 创建一个模拟的患者数据
    patient_data = {}
    for var in predictor_variables:
        # 根据变量名生成合理的随机值
        if var.lower() in ['age']:
            patient_data[var] = 65  # 年龄
        elif var.lower() in ['gender', 'sex']:
            patient_data[var] = 1  # 性别（男）
        elif var.lower() in ['bmi']:
            patient_data[var] = 26.5  # BMI
        elif var.lower() in ['glucose', 'blood_glucose']:
            patient_data[var] = 130  # 血糖
        elif var.lower() in ['cholesterol', 'total_cholesterol']:
            patient_data[var] = 220  # 胆固醇
        elif var.lower() in ['sbp', 'systolic', 'systolic_bp']:
            patient_data[var] = 140  # 收缩压
        elif var.lower() in ['dbp', 'diastolic', 'diastolic_bp']:
            patient_data[var] = 90  # 舒张压
        elif var.lower() in ['smoking', 'smoker']:
            patient_data[var] = 1  # 吸烟
        else:
            # 默认值
            patient_data[var] = 1
    
    # 准备请求数据
    predict_url = f"{base_url}/api/analysis/outcome_prediction/predict"
    request_data = {
        'model_path': model_path,
        'patient_data': patient_data
    }
    
    print("\n患者数据:")
    pprint(patient_data)
    
    # 发送请求
    predict_response = session.post(predict_url, json=request_data)
    
    print(f"\n响应状态码: {predict_response.status_code}")
    
    try:
        response_data = predict_response.json()
        print("\n响应数据:")
        
        if response_data.get('success'):
            prediction = response_data.get('prediction', {})
            print(f"预测结局: {prediction.get('outcome_prediction')} (0=无事件, 1=有事件)")
            print(f"事件概率: {prediction.get('outcome_probability'):.4f}")
            print(f"风险等级: {prediction.get('risk_level')}")
        else:
            print(f"预测失败: {response_data.get('message')}")
            
    except ValueError:
        print("响应不是有效的JSON格式")
        print(predict_response.text)

def test_list_models(base_url, username, password):
    """测试列出所有保存的结局预测模型
    
    Args:
        base_url: API基础URL
        username: 登录用户名
        password: 登录密码
    """
    print("\n测试列出所有保存的结局预测模型...")
    
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
    
    # 调用列表API
    list_url = f"{base_url}/api/analysis/outcome_prediction/models"
    list_response = session.get(list_url)
    
    print(f"\n响应状态码: {list_response.status_code}")
    
    try:
        response_data = list_response.json()
        
        if response_data.get('success'):
            models = response_data.get('models', [])
            
            if models:
                print(f"\n找到{len(models)}个保存的模型:")
                for i, model in enumerate(models):
                    print(f"\n模型 {i+1}:")
                    print(f"  名称: {model.get('name')}")
                    print(f"  路径: {model.get('path')}")
                    print(f"  修改时间: {model.get('last_modified')}")
            else:
                print("\n没有找到保存的模型")
        else:
            print(f"\n获取模型列表失败: {response_data.get('message')}")
            
    except ValueError:
        print("响应不是有效的JSON格式")
        print(list_response.text)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='测试结局预测API')
    parser.add_argument('--url', type=str, default='http://127.0.0.1:6000', help='API基础URL')
    parser.add_argument('--username', type=str, required=True, help='登录用户名')
    parser.add_argument('--password', type=str, required=True, help='登录密码')
    parser.add_argument('--dataset', type=int, required=True, help='数据集ID')
    parser.add_argument('--model', type=str, default='random_forest', 
                       choices=['random_forest', 'gradient_boosting', 'logistic'], help='模型类型')
    parser.add_argument('--list-only', action='store_true', help='只列出保存的模型')
    
    args = parser.parse_args()
    
    if args.list_only:
        test_list_models(args.url, args.username, args.password)
    else:
        test_outcome_prediction_api(args.url, args.username, args.password, args.dataset, args.model) 
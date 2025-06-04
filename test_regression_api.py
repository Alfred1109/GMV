"""
回归分析API测试脚本

用于测试回归分析API功能
"""

import json
import requests
import pandas as pd
from pprint import pprint
import matplotlib.pyplot as plt
import seaborn as sns
import sys
import os

# 配置
BASE_URL = 'http://127.0.0.1:5000'  # 根据实际情况修改
DATASET_ID = 1  # 根据实际情况修改
USERNAME = 'admin'  # 根据实际情况修改
PASSWORD = 'admin'  # 根据实际情况修改

# 创建会话
session = requests.Session()

def login():
    """登录获取会话"""
    login_url = f"{BASE_URL}/login"
    
    # 先获取CSRF令牌
    response = session.get(login_url)
    if response.status_code != 200:
        print(f"获取登录页面失败: {response.status_code}")
        sys.exit(1)
    
    # 提取CSRF令牌的简单方法
    csrf_token = None
    for line in response.text.splitlines():
        if 'csrf_token' in line:
            csrf_start = line.find('value="') + 7
            csrf_end = line.find('"', csrf_start)
            if csrf_start > 7 and csrf_end > csrf_start:
                csrf_token = line[csrf_start:csrf_end]
                break
    
    if not csrf_token:
        print("无法获取CSRF令牌")
        sys.exit(1)
        
    print(f"获取到CSRF令牌: {csrf_token}")
    
    # 发送登录请求
    login_data = {
        'csrf_token': csrf_token,
        'username': USERNAME,
        'password': PASSWORD,
        'role': 'admin'  # 根据实际情况修改
    }
    
    response = session.post(login_url, data=login_data, allow_redirects=True)
    
    if response.status_code != 200:
        print(f"登录失败: {response.status_code}")
        sys.exit(1)
        
    if "仪表盘" not in response.text and "Dashboard" not in response.text:
        print("登录似乎失败，无法找到仪表盘页面标识")
        sys.exit(1)
        
    print("登录成功!")

def test_linear_regression():
    """测试线性回归API"""
    api_url = f"{BASE_URL}/api/analysis/regression"
    
    # 测试数据
    test_data = {
        "dataset_id": DATASET_ID,
        "regression_type": "linear",
        "dependent_variable": "bmi",  # 根据实际数据集修改
        "independent_variables": ["age", "height", "weight"]  # 根据实际数据集修改
    }
    
    # 发送请求
    response = session.post(
        api_url,
        json=test_data,
        headers={'Content-Type': 'application/json'}
    )
    
    # 检查响应
    if response.status_code != 200:
        print(f"API请求失败: HTTP状态码 {response.status_code}")
        print(response.text)
        return
    
    try:
        result = response.json()
        
        if not result.get('success'):
            print(f"API返回错误: {result.get('message', '未知错误')}")
            return
            
        print("\n===== 线性回归分析结果 =====")
        
        # 打印基本信息
        print(f"回归类型: {result.get('regression_type')}")
        print(f"因变量: {result.get('dependent_variable', {}).get('name')}")
        print(f"自变量: {[var.get('name') for var in result.get('independent_variables', [])]}")
        print(f"样本量: {result.get('sample_size')}")
        
        # 打印模型拟合信息
        model_fit = result.get('results', {}).get('model_fit', {})
        print("\n模型拟合指标:")
        print(f"R² (决定系数): {model_fit.get('r_squared', 'N/A'):.4f}")
        print(f"调整后R²: {model_fit.get('adjusted_r_squared', 'N/A'):.4f}")
        print(f"F统计量: {model_fit.get('f_statistic', 'N/A'):.4f}")
        print(f"F统计量p值: {model_fit.get('f_p_value', 'N/A'):.4f}")
        
        # 打印回归系数
        coefficients = result.get('results', {}).get('coefficients', [])
        print("\n回归系数:")
        print(f"{'变量':<15} {'系数':<10} {'标准误':<10} {'t值':<10} {'p值':<10} {'显著性':<10}")
        print("-" * 65)
        
        for coef in coefficients:
            var_name = coef.get('variable_name', 'N/A')
            coefficient = coef.get('coefficient', 'N/A')
            std_error = coef.get('std_error', 'N/A')
            t_value = coef.get('t_value', 'N/A')
            p_value = coef.get('p_value', 'N/A')
            significant = coef.get('significant', False)
            
            print(f"{var_name:<15} {coefficient:<10.4f} {std_error:<10.4f} {t_value:<10.4f} {p_value:<10.4f} {'*' if significant else ''}")
        
        # 保存完整结果到文件
        with open('regression_result.json', 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
            
        print("\n完整结果已保存到 regression_result.json")
        
    except Exception as e:
        print(f"处理API响应时出错: {str(e)}")

def main():
    """主函数"""
    # 登录
    login()
    
    # 测试线性回归
    test_linear_regression()

if __name__ == "__main__":
    main() 
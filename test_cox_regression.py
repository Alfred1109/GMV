"""
Cox比例风险回归分析API测试脚本

用于测试Cox回归分析API功能
"""

import json
import requests
import pandas as pd
from pprint import pprint
import matplotlib.pyplot as plt
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

def test_cox_regression():
    """测试Cox回归分析API"""
    api_url = f"{BASE_URL}/api/analysis/survival"
    
    # 测试数据
    test_data = {
        "dataset_id": DATASET_ID,
        "survival_method": "cox_regression",
        "time_variable": "survival_time",  # 根据实际数据集修改
        "event_variable": "event_status",  # 根据实际数据集修改
        "covariates": ["age", "gender", "stage"]  # 根据实际数据集修改
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
            
        print("\n===== Cox比例风险回归分析结果 =====")
        
        # 打印基本信息
        print(f"分析方法: {result.get('survival_method')}")
        print(f"时间变量: {result.get('time_variable', {}).get('name')}")
        print(f"事件变量: {result.get('event_variable', {}).get('name')}")
        print(f"协变量: {[var.get('name') for var in result.get('covariates', [])]}")
        print(f"样本量: {result.get('sample_size')}")
        
        # 打印Cox回归结果
        cox_results = result.get('results', {})
        
        # 显示变量类型
        covariate_types = cox_results.get('covariate_types', {})
        print("\n协变量类型:")
        for var, var_type in covariate_types.items():
            print(f"  {var}: {var_type}")
        
        # 显示模型拟合指标
        model_fit = cox_results.get('model_fit', {})
        print("\n模型拟合指标:")
        print(f"  负对数似然: {model_fit.get('negative_log_likelihood'):.4f}")
        print(f"  C指数: {model_fit.get('c_index'):.4f}")
        print(f"  收敛: {'是' if model_fit.get('convergence') else '否'}")
        print(f"  迭代次数: {model_fit.get('iterations')}")
        
        # 显示回归系数和风险比
        coefficients = cox_results.get('coefficients', [])
        print("\n回归系数和风险比:")
        print(f"{'变量':<20} {'系数':<10} {'标准误':<10} {'Z值':<10} {'P值':<10} {'风险比HR':<10} {'95%CI下限':<10} {'95%CI上限':<10} {'显著性':<8}")
        print("-" * 100)
        
        for coef in coefficients:
            var_name = coef.get('variable', 'N/A')
            # 跳过截距项
            if var_name == '(Intercept)':
                continue
                
            coefficient = coef.get('coefficient', 'N/A')
            se = coef.get('se', 'N/A')
            z_value = coef.get('z_value', 'N/A')
            p_value = coef.get('p_value', 'N/A')
            hr = coef.get('hr', 'N/A')
            hr_lower = coef.get('hr_lower', 'N/A')
            hr_upper = coef.get('hr_upper', 'N/A')
            significant = coef.get('significant', False)
            
            print(f"{var_name:<20} {coefficient:<10.4f} {se:<10.4f} {z_value:<10.4f} {p_value:<10.4f} {hr:<10.4f} {hr_lower:<10.4f} {hr_upper:<10.4f} {'*' if significant else ''}")
        
        # 保存完整结果到文件
        with open('cox_regression_result.json', 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
            
        print("\n完整结果已保存到 cox_regression_result.json")
        
        # 如果存在分组生存曲线，可以尝试绘制
        if 'group_survival' in cox_results:
            try:
                group_results = cox_results.get('group_survival', {}).get('group_results', {})
                
                plt.figure(figsize=(10, 6))
                
                colors = ['blue', 'red', 'green', 'purple', 'orange']
                
                for i, (group_name, group_data) in enumerate(group_results.items()):
                    survival_curve = group_data.get('survival_curve', [])
                    if survival_curve:
                        times = [point.get('time') for point in survival_curve]
                        probs = [point.get('survival') for point in survival_curve]
                        
                        color = colors[i % len(colors)]
                        plt.step(times, probs, where='post', color=color, label=f'{group_name} (n={group_data.get("group_size")})')
                
                plt.ylim(0, 1.05)
                plt.xlabel('时间')
                plt.ylabel('生存概率')
                plt.title('Cox回归模型 - 按组分层的生存曲线')
                plt.grid(True, alpha=0.3)
                plt.legend(loc='best')
                
                # 添加Cox回归p值
                p_values = [coef.get('p_value') for coef in coefficients if coef.get('variable') != '(Intercept)']
                if p_values:
                    min_p = min(p_values)
                    plt.text(0.05, 0.05, f'Cox回归最小p值: {min_p:.4f}', 
                            transform=plt.gca().transAxes, bbox=dict(facecolor='white', alpha=0.8))
                
                plt.savefig('cox_regression_curves.png')
                print("Cox回归分层生存曲线已保存到 cox_regression_curves.png")
            except Exception as e:
                print(f"绘制生存曲线时出错: {str(e)}")
        
    except Exception as e:
        print(f"处理API响应时出错: {str(e)}")

def test_cox_regression_with_group():
    """测试带分组变量的Cox回归分析API"""
    api_url = f"{BASE_URL}/api/analysis/survival"
    
    # 测试数据
    test_data = {
        "dataset_id": DATASET_ID,
        "survival_method": "cox_regression",
        "time_variable": "survival_time",     # 根据实际数据集修改
        "event_variable": "event_status",     # 根据实际数据集修改
        "covariates": ["age", "stage"],       # 根据实际数据集修改
        "group_variable": "treatment_group"   # 根据实际数据集修改
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
            
        print("\n===== 带分组变量的Cox比例风险回归分析结果 =====")
        
        # 打印基本信息
        print(f"分析方法: {result.get('survival_method')}")
        print(f"时间变量: {result.get('time_variable', {}).get('name')}")
        print(f"事件变量: {result.get('event_variable', {}).get('name')}")
        print(f"分组变量: {result.get('group_variable', {}).get('name')}")
        print(f"协变量: {[var.get('name') for var in result.get('covariates', [])]}")
        print(f"样本量: {result.get('sample_size')}")
        
        # 保存完整结果到文件
        with open('cox_regression_with_group_result.json', 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
            
        print("\n完整结果已保存到 cox_regression_with_group_result.json")
        
        # 结果处理类似于test_cox_regression函数
        # 这里简化展示，不再重复代码
        
    except Exception as e:
        print(f"处理API响应时出错: {str(e)}")

def main():
    """主函数"""
    # 登录
    login()
    
    # 测试Cox回归分析
    test_cox_regression()
    
    # 测试带分组变量的Cox回归分析
    test_cox_regression_with_group()

if __name__ == "__main__":
    main() 
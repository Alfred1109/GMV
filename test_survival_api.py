"""
生存分析API测试脚本

用于测试生存分析API功能
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

def test_kaplan_meier():
    """测试Kaplan-Meier生存分析API"""
    api_url = f"{BASE_URL}/api/analysis/survival"
    
    # 测试数据
    test_data = {
        "dataset_id": DATASET_ID,
        "survival_method": "kaplan_meier",
        "time_variable": "survival_time",  # 根据实际数据集修改
        "event_variable": "event_status"   # 根据实际数据集修改
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
            
        print("\n===== Kaplan-Meier生存分析结果 =====")
        
        # 打印基本信息
        print(f"分析方法: {result.get('survival_method')}")
        print(f"时间变量: {result.get('time_variable', {}).get('name')}")
        print(f"事件变量: {result.get('event_variable', {}).get('name')}")
        print(f"样本量: {result.get('sample_size')}")
        
        # 打印生存结果
        survival_results = result.get('results', {})
        
        # 显示中位生存时间
        print(f"\n中位生存时间: {survival_results.get('median_survival')}")
        
        # 显示生存率
        survival_rates = survival_results.get('survival_rates', {})
        print("\n生存率:")
        for time_point, rate in sorted(survival_rates.items(), key=lambda x: int(x[0])):
            print(f"{time_point}天生存率: {rate:.4f}")
        
        # 显示事件统计
        print(f"\n总样本数: {survival_results.get('total_subjects')}")
        print(f"事件数: {survival_results.get('total_events')}")
        print(f"删失数: {survival_results.get('total_censored')}")
        
        # 生存曲线数据（简化显示）
        survival_curve = survival_results.get('survival_curve', [])
        if survival_curve:
            print("\n生存曲线数据 (前5个时间点):")
            print(f"{'时间':<10} {'生存率':<10} {'风险集':<10} {'事件':<10} {'删失':<10}")
            print("-" * 50)
            
            for i, point in enumerate(survival_curve[:5]):
                print(f"{point.get('time'):<10.2f} {point.get('survival'):<10.4f} {point.get('at_risk'):<10} {point.get('events'):<10} {point.get('censored'):<10}")
            
            if len(survival_curve) > 5:
                print("... 更多数据省略 ...")
        
        # 保存完整结果到文件
        with open('survival_result.json', 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
            
        print("\n完整结果已保存到 survival_result.json")
        
        # 可选：绘制生存曲线
        try:
            if survival_curve:
                plt.figure(figsize=(10, 6))
                times = [point.get('time') for point in survival_curve]
                probs = [point.get('survival') for point in survival_curve]
                
                plt.step(times, probs, where='post', color='blue')
                plt.ylim(0, 1.05)
                plt.xlabel('时间')
                plt.ylabel('生存概率')
                plt.title('Kaplan-Meier生存曲线')
                plt.grid(True, alpha=0.3)
                
                # 标记中位生存时间
                if survival_results.get('median_survival'):
                    median = survival_results.get('median_survival')
                    plt.axhline(y=0.5, color='r', linestyle='--', alpha=0.5)
                    plt.axvline(x=median, color='r', linestyle='--', alpha=0.5)
                    plt.text(median, 0.52, f'中位生存时间: {median:.2f}', color='red')
                
                plt.savefig('survival_curve.png')
                print("生存曲线已保存到 survival_curve.png")
        except Exception as e:
            print(f"绘制生存曲线时出错: {str(e)}")
        
    except Exception as e:
        print(f"处理API响应时出错: {str(e)}")

def test_grouped_kaplan_meier():
    """测试分组Kaplan-Meier生存分析API"""
    api_url = f"{BASE_URL}/api/analysis/survival"
    
    # 测试数据
    test_data = {
        "dataset_id": DATASET_ID,
        "survival_method": "kaplan_meier",
        "time_variable": "survival_time",  # 根据实际数据集修改
        "event_variable": "event_status",  # 根据实际数据集修改
        "group_variable": "treatment_group"  # 根据实际数据集修改
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
            
        print("\n===== 分组Kaplan-Meier生存分析结果 =====")
        
        # 打印基本信息
        print(f"分析方法: {result.get('survival_method')}")
        print(f"时间变量: {result.get('time_variable', {}).get('name')}")
        print(f"事件变量: {result.get('event_variable', {}).get('name')}")
        print(f"分组变量: {result.get('group_variable', {}).get('name')}")
        print(f"总样本量: {result.get('sample_size')}")
        
        # 打印分组结果
        survival_results = result.get('results', {})
        groups = survival_results.get('groups', [])
        group_results = survival_results.get('group_results', {})
        
        print(f"\n组别: {groups}")
        
        # 显示每个组的中位生存时间
        print("\n各组中位生存时间:")
        for group_name, group_data in group_results.items():
            median = group_data.get('median_survival')
            size = group_data.get('group_size')
            print(f"  {group_name}: {median} (样本量: {size})")
        
        # 显示组间比较结果
        comparison = survival_results.get('comparison', {})
        print("\n组间比较 (Log-rank检验):")
        print(f"  统计量: {comparison.get('statistic'):.4f}")
        print(f"  自由度: {comparison.get('df')}")
        print(f"  p值: {comparison.get('p_value'):.4f}")
        print(f"  显著性: {'是' if comparison.get('significant') else '否'}")
        
        # 保存完整结果到文件
        with open('grouped_survival_result.json', 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
            
        print("\n完整结果已保存到 grouped_survival_result.json")
        
        # 可选：绘制分组生存曲线
        try:
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
            plt.title('分组Kaplan-Meier生存曲线')
            plt.grid(True, alpha=0.3)
            plt.legend(loc='best')
            
            # 添加Log-rank检验结果
            p_value = comparison.get('p_value')
            if p_value is not None:
                plt.text(0.05, 0.05, f'Log-rank p值: {p_value:.4f}', 
                        transform=plt.gca().transAxes, bbox=dict(facecolor='white', alpha=0.8))
            
            plt.savefig('grouped_survival_curve.png')
            print("分组生存曲线已保存到 grouped_survival_curve.png")
        except Exception as e:
            print(f"绘制生存曲线时出错: {str(e)}")
        
    except Exception as e:
        print(f"处理API响应时出错: {str(e)}")

def main():
    """主函数"""
    # 登录
    login()
    
    # 测试单组Kaplan-Meier分析
    test_kaplan_meier()
    
    # 测试分组Kaplan-Meier分析
    test_grouped_kaplan_meier()

if __name__ == "__main__":
    main() 
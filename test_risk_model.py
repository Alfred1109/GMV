"""
测试风险评估模型功能
"""

import json
import random
import numpy as np
from risk_assessment_model import perform_risk_assessment

def test_logistic_regression():
    """测试逻辑回归风险评估模型"""
    print("测试逻辑回归风险评估模型...")
    
    # 生成模拟数据
    n_samples = 100
    data = {
        'age': [random.randint(20, 80) for _ in range(n_samples)],
        'gender': [random.randint(0, 1) for _ in range(n_samples)],
        'bmi': [random.uniform(18.5, 35.0) for _ in range(n_samples)],
        'smoker': [random.randint(0, 1) for _ in range(n_samples)],
        'outcome': []
    }
    
    # 模拟一个简单的关系：年龄越大、BMI越高、吸烟者患病风险越高
    for i in range(n_samples):
        age_factor = data['age'][i] / 80  # 标准化年龄
        bmi_factor = (data['bmi'][i] - 18.5) / (35 - 18.5)  # 标准化BMI
        smoker_factor = data['smoker'][i] * 0.3  # 吸烟者风险增加
        
        # 计算风险概率
        prob = 0.1 + 0.3 * age_factor + 0.3 * bmi_factor + smoker_factor
        prob = min(max(prob, 0), 1)  # 确保概率在0-1之间
        
        # 根据概率决定是否患病
        data['outcome'].append(1 if random.random() < prob else 0)
    
    # 测试不同验证方法
    validation_methods = ['cross_validation', 'split']
    
    for method in validation_methods:
        print(f"\n使用{method}验证方法:")
        result = perform_risk_assessment(
            data=data,
            target_variable='outcome',
            predictor_variables=['age', 'gender', 'bmi', 'smoker'],
            model_type='logistic',
            validation_method=method,
            validation_params={'cv_folds': 5, 'test_size': 0.3}
        )
        
        # 打印结果
        print(f"模型类型: {result['model_type']}")
        print(f"验证方法: {result['validation_method']}")
        print("\n评估指标:")
        for metric, value in result['evaluation_metrics'].items():
            if metric != 'confusion_matrix':
                print(f"  {metric}: {value:.4f}")
                
        if 'confusion_matrix' in result['evaluation_metrics']:
            cm = result['evaluation_metrics']['confusion_matrix']
            print("\n混淆矩阵:")
            print(f"  真阴性: {cm['true_negative']}")
            print(f"  假阳性: {cm['false_positive']}")
            print(f"  假阴性: {cm['false_negative']}")
            print(f"  真阳性: {cm['true_positive']}")
            
        print("\n特征重要性:")
        for feature, importance in result['feature_importance'].items():
            print(f"  {feature}: {importance:.4f}")
            
        print("\n风险分层:")
        strat = result['risk_stratification']
        print(f"  低风险阈值: {strat['thresholds']['low']:.4f}")
        print(f"  高风险阈值: {strat['thresholds']['high']:.4f}")
        
        for group, stats in strat['group_stats'].items():
            print(f"  {group}风险组:")
            print(f"    样本数量: {stats['count']}")
            print(f"    事件率: {stats['event_rate']:.4f}")

def test_decision_tree():
    """测试决策树风险评估模型"""
    print("\n测试决策树风险评估模型...")
    
    # 生成模拟数据（同上）
    n_samples = 100
    data = {
        'age': [random.randint(20, 80) for _ in range(n_samples)],
        'gender': [random.randint(0, 1) for _ in range(n_samples)],
        'bmi': [random.uniform(18.5, 35.0) for _ in range(n_samples)],
        'smoker': [random.randint(0, 1) for _ in range(n_samples)],
        'outcome': []
    }
    
    for i in range(n_samples):
        age_factor = data['age'][i] / 80
        bmi_factor = (data['bmi'][i] - 18.5) / (35 - 18.5)
        smoker_factor = data['smoker'][i] * 0.3
        
        prob = 0.1 + 0.3 * age_factor + 0.3 * bmi_factor + smoker_factor
        prob = min(max(prob, 0), 1)
        
        data['outcome'].append(1 if random.random() < prob else 0)
    
    # 使用决策树模型
    result = perform_risk_assessment(
        data=data,
        target_variable='outcome',
        predictor_variables=['age', 'gender', 'bmi', 'smoker'],
        model_type='decision_tree',
        validation_method='split',
        validation_params={'test_size': 0.3}
    )
    
    # 打印结果
    print(f"模型类型: {result['model_type']}")
    print("\n评估指标:")
    for metric, value in result['evaluation_metrics'].items():
        if metric != 'confusion_matrix':
            print(f"  {metric}: {value:.4f}")
            
    print("\n特征重要性:")
    for feature, importance in result['feature_importance'].items():
        print(f"  {feature}: {importance:.4f}")

def test_random_forest():
    """测试随机森林风险评估模型"""
    print("\n测试随机森林风险评估模型...")
    
    # 生成模拟数据（同上）
    n_samples = 100
    data = {
        'age': [random.randint(20, 80) for _ in range(n_samples)],
        'gender': [random.randint(0, 1) for _ in range(n_samples)],
        'bmi': [random.uniform(18.5, 35.0) for _ in range(n_samples)],
        'smoker': [random.randint(0, 1) for _ in range(n_samples)],
        'outcome': []
    }
    
    for i in range(n_samples):
        age_factor = data['age'][i] / 80
        bmi_factor = (data['bmi'][i] - 18.5) / (35 - 18.5)
        smoker_factor = data['smoker'][i] * 0.3
        
        prob = 0.1 + 0.3 * age_factor + 0.3 * bmi_factor + smoker_factor
        prob = min(max(prob, 0), 1)
        
        data['outcome'].append(1 if random.random() < prob else 0)
    
    # 使用随机森林模型
    result = perform_risk_assessment(
        data=data,
        target_variable='outcome',
        predictor_variables=['age', 'gender', 'bmi', 'smoker'],
        model_type='random_forest',
        validation_method='split',
        validation_params={'test_size': 0.3}
    )
    
    # 打印结果
    print(f"模型类型: {result['model_type']}")
    print("\n评估指标:")
    for metric, value in result['evaluation_metrics'].items():
        if metric != 'confusion_matrix':
            print(f"  {metric}: {value:.4f}")
            
    print("\n特征重要性:")
    for feature, importance in result['feature_importance'].items():
        print(f"  {feature}: {importance:.4f}")

if __name__ == "__main__":
    test_logistic_regression()
    test_decision_tree()
    test_random_forest()
    print("\n所有测试完成!") 
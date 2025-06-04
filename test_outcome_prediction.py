"""
测试结局预测模型功能
"""

import random
import numpy as np
import matplotlib.pyplot as plt
from outcome_prediction_model import perform_outcome_prediction, predict_outcome

def generate_test_data(n_samples=200):
    """生成测试数据
    
    Args:
        n_samples: 样本数量
        
    Returns:
        dict: 测试数据
    """
    # 设置随机种子以确保可重复性
    random.seed(42)
    np.random.seed(42)
    
    # 年龄特征 (20-90岁)
    age = [random.randint(20, 90) for _ in range(n_samples)]
    
    # 性别特征 (0=女性, 1=男性)
    gender = [random.randint(0, 1) for _ in range(n_samples)]
    
    # 实验室检查值 (例如: 血糖, 血压, 胆固醇)
    glucose = [random.uniform(70, 200) for _ in range(n_samples)]
    systolic_bp = [random.uniform(90, 180) for _ in range(n_samples)]
    diastolic_bp = [random.uniform(60, 110) for _ in range(n_samples)]
    cholesterol = [random.uniform(120, 300) for _ in range(n_samples)]
    
    # 吸烟状态 (0=不吸烟, 1=吸烟)
    smoking = [random.randint(0, 1) for _ in range(n_samples)]
    
    # 生成结局 (基于特征的非线性组合)
    outcome = []
    for i in range(n_samples):
        # 年龄风险因子 (年龄越大风险越高)
        age_factor = (age[i] - 20) / 70.0
        
        # 性别风险因子 (假设男性风险略高)
        gender_factor = 0.1 if gender[i] == 1 else 0
        
        # 血糖风险因子 (高血糖风险高)
        glucose_factor = max(0, (glucose[i] - 100) / 100.0)
        
        # 血压风险因子 (高血压风险高)
        bp_factor = max(0, (systolic_bp[i] - 120) / 60.0 + (diastolic_bp[i] - 80) / 30.0)
        
        # 胆固醇风险因子 (高胆固醇风险高)
        chol_factor = max(0, (cholesterol[i] - 200) / 100.0)
        
        # 吸烟风险因子
        smoking_factor = 0.2 if smoking[i] == 1 else 0
        
        # 组合所有风险因子
        risk = 0.1 + 0.3 * age_factor + 0.1 * gender_factor + \
               0.15 * glucose_factor + 0.2 * bp_factor + \
               0.15 * chol_factor + smoking_factor
        
        # 添加一些随机性
        risk += random.uniform(-0.1, 0.1)
        
        # 计算发生结局的概率 (使用Sigmoid函数将风险转换为概率)
        prob = 1.0 / (1.0 + np.exp(-5 * (risk - 0.5)))
        
        # 根据概率决定结局 (0=无事件, 1=有事件)
        outcome.append(1 if random.random() < prob else 0)
    
    # 生成观察时间 (单位: 天, 范围: 0-1000天)
    observation_time = [random.randint(30, 1000) for _ in range(n_samples)]
    
    # 返回数据集
    return {
        'age': age,
        'gender': gender,
        'glucose': glucose,
        'systolic_bp': systolic_bp,
        'diastolic_bp': diastolic_bp,
        'cholesterol': cholesterol,
        'smoking': smoking,
        'observation_time': observation_time,
        'outcome': outcome
    }

def test_basic_prediction():
    """测试基本结局预测功能"""
    print("测试基本结局预测功能...")
    
    # 生成测试数据
    data = generate_test_data(n_samples=200)
    
    # 设置预测变量
    predictor_variables = ['age', 'gender', 'glucose', 'systolic_bp', 
                          'diastolic_bp', 'cholesterol', 'smoking']
    
    # 进行结局预测分析
    result = perform_outcome_prediction(
        data=data,
        target_variable='outcome',
        predictor_variables=predictor_variables,
        model_type='random_forest',
        validation_method='split',
        validation_params={'test_size': 0.3}
    )
    
    # 打印结果
    print(f"模型类型: {result['model_type']}")
    print(f"验证方法: {result['validation_method']}")
    
    print("\n评估指标:")
    for metric, value in result['evaluation_metrics'].items():
        print(f"  {metric}: {value:.4f}")
    
    print("\n特征重要性:")
    for feature, importance in sorted(result['feature_importance'].items(), 
                                    key=lambda x: x[1], reverse=True):
        print(f"  {feature}: {importance:.4f}")
    
    # 打印风险分层信息
    if 'risk_stratification' in result:
        print("\n风险分层:")
        print(f"  Q1 (25%分位数): {result['risk_stratification']['thresholds']['q1']:.4f}")
        print(f"  Q2 (50%分位数): {result['risk_stratification']['thresholds']['q2']:.4f}")
        print(f"  Q3 (75%分位数): {result['risk_stratification']['thresholds']['q3']:.4f}")
        
        for group, stats in result['risk_stratification']['group_stats'].items():
            print(f"\n  {group}风险组:")
            print(f"    样本数: {stats['count']}")
            print(f"    事件率: {stats['event_rate']:.4f}")
            print(f"    平均概率: {stats['mean_probability']:.4f}")
            print(f"    最小概率: {stats['min_probability']:.4f}")
            print(f"    最大概率: {stats['max_probability']:.4f}")

def test_time_dependent_prediction():
    """测试时间相关结局预测功能"""
    print("\n测试时间相关结局预测功能...")
    
    # 生成测试数据
    data = generate_test_data(n_samples=200)
    
    # 设置预测变量
    predictor_variables = ['age', 'gender', 'glucose', 'systolic_bp', 
                          'diastolic_bp', 'cholesterol', 'smoking']
    
    # 进行结局预测分析 (预测180天内的结局)
    result = perform_outcome_prediction(
        data=data,
        target_variable='outcome',
        predictor_variables=predictor_variables,
        time_variable='observation_time',
        prediction_horizon=180,  # 180天内的结局
        model_type='random_forest',
        validation_method='cross_validation',
        validation_params={'cv_folds': 5}
    )
    
    # 打印结果
    print(f"模型类型: {result['model_type']}")
    print(f"验证方法: {result['validation_method']}")
    
    print("\n评估指标:")
    for metric, value in result['evaluation_metrics'].items():
        print(f"  {metric}: {value:.4f}")

def test_model_saving_and_prediction():
    """测试模型保存和单个预测功能"""
    print("\n测试模型保存和单个预测功能...")
    
    # 生成测试数据
    data = generate_test_data(n_samples=200)
    
    # 设置预测变量
    predictor_variables = ['age', 'gender', 'glucose', 'systolic_bp', 
                          'diastolic_bp', 'cholesterol', 'smoking']
    
    # 进行结局预测分析并保存模型
    result = perform_outcome_prediction(
        data=data,
        target_variable='outcome',
        predictor_variables=predictor_variables,
        model_type='gradient_boosting',
        validation_method='split',
        validation_params={'test_size': 0.3},
        save_model=True,
        model_name='test_outcome_model'
    )
    
    print(f"模型已保存到: {result.get('model_saved_path', 'unknown')}")
    
    # 使用保存的模型进行单个预测
    if 'model_saved_path' in result:
        # 构造一个新患者的数据
        new_patient = {
            'age': 65,
            'gender': 1,
            'glucose': 150,
            'systolic_bp': 145,
            'diastolic_bp': 95,
            'cholesterol': 250,
            'smoking': 1
        }
        
        # 使用保存的模型进行预测
        prediction = predict_outcome(result['model_saved_path'], new_patient)
        
        print("\n新患者预测结果:")
        print(f"  预测结局: {prediction['outcome_prediction']} (0=无事件, 1=有事件)")
        
        if 'outcome_probability' in prediction:
            print(f"  事件概率: {prediction['outcome_probability']:.4f}")
        
        if 'risk_level' in prediction:
            print(f"  风险等级: {prediction['risk_level']}")
    else:
        print("模型保存失败，无法进行预测")

def test_multiple_models():
    """测试不同类型的预测模型"""
    print("\n测试不同类型的预测模型...")
    
    # 生成测试数据
    data = generate_test_data(n_samples=200)
    
    # 设置预测变量
    predictor_variables = ['age', 'gender', 'glucose', 'systolic_bp', 
                          'diastolic_bp', 'cholesterol', 'smoking']
    
    # 测试不同类型的模型
    model_types = ['logistic', 'random_forest', 'gradient_boosting']
    
    for model_type in model_types:
        print(f"\n使用{model_type}模型:")
        
        # 进行结局预测分析
        result = perform_outcome_prediction(
            data=data,
            target_variable='outcome',
            predictor_variables=predictor_variables,
            model_type=model_type,
            validation_method='split',
            validation_params={'test_size': 0.3}
        )
        
        # 打印结果
        print("评估指标:")
        for metric, value in result['evaluation_metrics'].items():
            if metric != 'confusion_matrix':
                print(f"  {metric}: {value:.4f}")
        
        # 打印混淆矩阵（如果有）
        if 'confusion_matrix' in result:
            cm = result['confusion_matrix']
            print("\n混淆矩阵:")
            print(f"  真阴性: {cm['true_negative']}")
            print(f"  假阳性: {cm['false_positive']}")
            print(f"  假阴性: {cm['false_negative']}")
            print(f"  真阳性: {cm['true_positive']}")
            
            # 计算其他指标
            sensitivity = cm['true_positive'] / (cm['true_positive'] + cm['false_negative']) if (cm['true_positive'] + cm['false_negative']) > 0 else 0
            specificity = cm['true_negative'] / (cm['true_negative'] + cm['false_positive']) if (cm['true_negative'] + cm['false_positive']) > 0 else 0
            
            print(f"  灵敏度: {sensitivity:.4f}")
            print(f"  特异度: {specificity:.4f}")

def plot_curves(result):
    """绘制ROC曲线和PR曲线
    
    Args:
        result: 预测结果字典
    """
    if 'curve_data' not in result:
        print("结果中没有曲线数据，无法绘图")
        return
    
    curve_data = result['curve_data']
    
    # 创建图像
    plt.figure(figsize=(12, 5))
    
    # ROC曲线
    plt.subplot(1, 2, 1)
    roc_points = curve_data['roc_curve']
    plt.plot([p['fpr'] for p in roc_points], [p['tpr'] for p in roc_points], 'b-')
    plt.plot([0, 1], [0, 1], 'k--')
    plt.xlabel('假阳性率')
    plt.ylabel('真阳性率')
    plt.title(f"ROC曲线 (AUC = {result['evaluation_metrics']['roc_auc']:.4f})")
    plt.grid(True, alpha=0.3)
    
    # PR曲线
    plt.subplot(1, 2, 2)
    pr_points = curve_data['pr_curve']
    plt.plot([p['recall'] for p in pr_points], [p['precision'] for p in pr_points], 'r-')
    plt.xlabel('召回率')
    plt.ylabel('精确率')
    plt.title(f"PR曲线 (AP = {curve_data['average_precision']:.4f})")
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('outcome_prediction_curves.png')
    print("曲线图已保存到 outcome_prediction_curves.png")

def test_model_with_curves():
    """测试带曲线绘制的预测模型"""
    print("\n测试带曲线绘制的预测模型...")
    
    # 生成测试数据
    data = generate_test_data(n_samples=200)
    
    # 设置预测变量
    predictor_variables = ['age', 'gender', 'glucose', 'systolic_bp', 
                          'diastolic_bp', 'cholesterol', 'smoking']
    
    # 进行结局预测分析
    result = perform_outcome_prediction(
        data=data,
        target_variable='outcome',
        predictor_variables=predictor_variables,
        model_type='gradient_boosting',
        validation_method='split',
        validation_params={'test_size': 0.3}
    )
    
    # 绘制曲线
    plot_curves(result)

if __name__ == "__main__":
    test_basic_prediction()
    test_time_dependent_prediction()
    test_model_saving_and_prediction()
    test_multiple_models()
    test_model_with_curves()
    print("\n所有测试完成!") 
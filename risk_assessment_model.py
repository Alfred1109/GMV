"""
风险评估模型

提供用于临床风险评估的机器学习模型
"""

import math
import json
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score, 
    roc_auc_score, confusion_matrix, classification_report
)

def perform_risk_assessment(data, target_variable, predictor_variables, model_type='logistic', 
                            validation_method='cross_validation', validation_params=None):
    """执行风险评估分析
    
    Args:
        data: 包含目标变量和预测变量的数据字典
        target_variable: 目标变量名
        predictor_variables: 预测变量列表
        model_type: 模型类型，可选值: logistic, decision_tree, random_forest
        validation_method: 验证方法，可选值: cross_validation, split
        validation_params: 验证参数字典
        
    Returns:
        dict: 风险评估结果
    """
    # 初始化验证参数
    if validation_params is None:
        validation_params = {}
        
    cv_folds = validation_params.get('cv_folds', 5)
    test_size = validation_params.get('test_size', 0.3)
    
    # 提取数据
    y = np.array(data[target_variable])
    X = np.array([[data[var][i] for var in predictor_variables] for i in range(len(y))])
    
    # 数据预处理
    # 标准化数值特征
    scaler = StandardScaler()
    X = scaler.fit_transform(X)
    
    # 选择模型
    if model_type == 'logistic':
        model = LogisticRegression(max_iter=1000, random_state=42)
    elif model_type == 'decision_tree':
        model = DecisionTreeClassifier(random_state=42)
    elif model_type == 'random_forest':
        model = RandomForestClassifier(random_state=42)
    else:
        raise ValueError(f"不支持的模型类型: {model_type}")
    
    # 模型评估
    if validation_method == 'cross_validation':
        # 交叉验证
        cv_scores = {
            'accuracy': cross_val_score(model, X, y, cv=cv_folds, scoring='accuracy'),
            'precision': cross_val_score(model, X, y, cv=cv_folds, scoring='precision'),
            'recall': cross_val_score(model, X, y, cv=cv_folds, scoring='recall'),
            'f1': cross_val_score(model, X, y, cv=cv_folds, scoring='f1'),
            'roc_auc': cross_val_score(model, X, y, cv=cv_folds, scoring='roc_auc')
        }
        
        # 计算平均评估指标
        evaluation_metrics = {
            'accuracy': float(np.mean(cv_scores['accuracy'])),
            'precision': float(np.mean(cv_scores['precision'])),
            'recall': float(np.mean(cv_scores['recall'])),
            'f1': float(np.mean(cv_scores['f1'])),
            'roc_auc': float(np.mean(cv_scores['roc_auc']))
        }
        
        # 在全部数据上训练最终模型
        model.fit(X, y)
        
    elif validation_method == 'split':
        # 训练测试集分割
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=42)
        
        # 训练模型
        model.fit(X_train, y_train)
        
        # 预测
        y_pred = model.predict(X_test)
        y_pred_proba = model.predict_proba(X_test)[:, 1] if hasattr(model, 'predict_proba') else None
        
        # 计算评估指标
        evaluation_metrics = {
            'accuracy': float(accuracy_score(y_test, y_pred)),
            'precision': float(precision_score(y_test, y_pred, zero_division=0)),
            'recall': float(recall_score(y_test, y_pred, zero_division=0)),
            'f1': float(f1_score(y_test, y_pred, zero_division=0))
        }
        
        # 如果模型支持概率预测，计算ROC AUC
        if y_pred_proba is not None:
            evaluation_metrics['roc_auc'] = float(roc_auc_score(y_test, y_pred_proba))
        
        # 计算混淆矩阵
        cm = confusion_matrix(y_test, y_pred)
        evaluation_metrics['confusion_matrix'] = {
            'true_negative': int(cm[0, 0]),
            'false_positive': int(cm[0, 1]),
            'false_negative': int(cm[1, 0]),
            'true_positive': int(cm[1, 1])
        }
    else:
        raise ValueError(f"不支持的验证方法: {validation_method}")
    
    # 特征重要性
    feature_importance = {}
    
    if model_type == 'logistic':
        # 对于逻辑回归，使用系数作为特征重要性
        if hasattr(model, 'coef_'):
            for i, var in enumerate(predictor_variables):
                feature_importance[var] = float(model.coef_[0][i])
    elif model_type in ['decision_tree', 'random_forest']:
        # 对于树模型，使用特征重要性属性
        if hasattr(model, 'feature_importances_'):
            for i, var in enumerate(predictor_variables):
                feature_importance[var] = float(model.feature_importances_[i])
    
    # 风险分层（仅适用于二分类问题）
    risk_stratification = calculate_risk_stratification(model, X, y, predictor_variables)
    
    # 构建结果
    results = {
        'model_type': model_type,
        'validation_method': validation_method,
        'evaluation_metrics': evaluation_metrics,
        'feature_importance': feature_importance,
        'risk_stratification': risk_stratification,
        'variable_types': {var: get_variable_type(data[var]) for var in predictor_variables + [target_variable]}
    }
    
    return results

def calculate_risk_stratification(model, X, y, predictor_variables):
    """计算风险分层
    
    根据模型预测的概率分布，将样本分为高、中、低风险组
    
    Args:
        model: 训练好的模型
        X: 特征矩阵
        y: 目标变量
        predictor_variables: 预测变量列表
        
    Returns:
        dict: 风险分层结果
    """
    # 检查模型是否支持概率预测
    if not hasattr(model, 'predict_proba'):
        return {'message': '所选模型不支持概率预测，无法进行风险分层'}
    
    # 获取预测概率
    y_pred_proba = model.predict_proba(X)[:, 1]
    
    # 根据概率分布计算风险分层阈值
    # 低风险: < 33%分位数
    # 中风险: 33-66%分位数
    # 高风险: > 66%分位数
    low_threshold = np.percentile(y_pred_proba, 33)
    high_threshold = np.percentile(y_pred_proba, 66)
    
    # 分配风险组
    risk_groups = []
    for prob in y_pred_proba:
        if prob < low_threshold:
            risk_groups.append('low')
        elif prob <= high_threshold:
            risk_groups.append('medium')
        else:
            risk_groups.append('high')
    
    # 计算每个风险组的统计信息
    group_stats = {}
    for group in ['low', 'medium', 'high']:
        group_indices = [i for i, g in enumerate(risk_groups) if g == group]
        if group_indices:
            group_y = [y[i] for i in group_indices]
            group_stats[group] = {
                'count': len(group_indices),
                'event_rate': sum(group_y) / len(group_y) if group_y else 0,
                'threshold': low_threshold if group == 'low' else high_threshold if group == 'high' else None
            }
    
    return {
        'thresholds': {
            'low': float(low_threshold),
            'high': float(high_threshold)
        },
        'group_stats': group_stats
    }

def get_variable_type(values):
    """判断变量类型
    
    Args:
        values: 变量值列表
        
    Returns:
        str: 变量类型 (categorical, binary, continuous)
    """
    # 移除None值
    clean_values = [v for v in values if v is not None]
    
    # 如果所有值都是数字
    if all(isinstance(v, (int, float)) for v in clean_values):
        # 如果只有0和1，则为二分类
        unique_values = set(clean_values)
        if unique_values.issubset({0, 1}):
            return 'binary'
        
        # 如果不同值的数量小于等于5，则为分类变量
        elif len(unique_values) <= 5:
            return 'categorical'
            
        # 否则为连续变量
        else:
            return 'continuous'
    
    # 如果有非数字值，则为分类变量
    else:
        return 'categorical' 
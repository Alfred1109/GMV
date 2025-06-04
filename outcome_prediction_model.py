"""
结局预测模型

提供用于临床结局预测的机器学习模型
"""

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score, 
    roc_auc_score, confusion_matrix, classification_report,
    roc_curve, precision_recall_curve, average_precision_score
)
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
import joblib
import json
import math
import datetime
import os

def perform_outcome_prediction(data, target_variable, predictor_variables, time_variable=None, 
                               model_type='random_forest', prediction_horizon=None, 
                               validation_method='cross_validation', validation_params=None,
                               save_model=False, model_name=None):
    """执行结局预测分析
    
    Args:
        data: 包含目标变量和预测变量的数据字典
        target_variable: 目标变量名（结局）
        predictor_variables: 预测变量列表
        time_variable: 时间变量名，用于时间相关预测（可选）
        model_type: 模型类型，可选值: random_forest, gradient_boosting, logistic
        prediction_horizon: 预测时间范围（以天为单位），用于时间相关预测
        validation_method: 验证方法，可选值: cross_validation, split
        validation_params: 验证参数字典
        save_model: 是否保存模型
        model_name: 模型保存名称
        
    Returns:
        dict: 结局预测结果
    """
    # 初始化验证参数
    if validation_params is None:
        validation_params = {}
        
    cv_folds = validation_params.get('cv_folds', 5)
    test_size = validation_params.get('test_size', 0.3)
    
    # 数据准备
    dataset = prepare_data(data, target_variable, predictor_variables, time_variable, prediction_horizon)
    
    # 检查是否有足够的数据点
    if len(dataset['X']) < 10:
        return {
            'success': False,
            'message': '没有足够的数据点进行结局预测分析'
        }
    
    # 构建和评估模型
    model_results = build_and_evaluate_model(
        dataset, model_type, validation_method, cv_folds, test_size
    )
    
    # 风险分层
    if model_results['success'] and 'model' in model_results:
        risk_stratification = calculate_risk_stratification(
            model_results['model'], dataset['X_scaled'], dataset['y']
        )
        model_results['risk_stratification'] = risk_stratification
    
    # 保存模型（如果需要）
    if save_model and model_results['success'] and 'model' in model_results:
        if model_name is None:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            model_name = f"outcome_prediction_{model_type}_{timestamp}"
        
        save_path = save_prediction_model(
            model_results['model'], 
            dataset['scaler'], 
            dataset['imputer'],
            dataset['feature_names'],
            model_name
        )
        model_results['model_saved_path'] = save_path
    
    # 移除模型对象（不应该在API响应中返回）
    if 'model' in model_results:
        del model_results['model']
    
    return model_results

def prepare_data(data, target_variable, predictor_variables, time_variable=None, prediction_horizon=None):
    """准备预测模型数据
    
    Args:
        data: 原始数据字典
        target_variable: 目标变量名
        predictor_variables: 预测变量列表
        time_variable: 时间变量名（可选）
        prediction_horizon: 预测时间范围（天）
        
    Returns:
        dict: 处理后的数据集
    """
    # 提取数据
    y_raw = np.array(data[target_variable])
    X_raw = []
    
    for i in range(len(y_raw)):
        features = []
        for var in predictor_variables:
            if var in data:
                features.append(data[var][i])
            else:
                features.append(None)
        X_raw.append(features)
    
    X_raw = np.array(X_raw)
    
    # 处理时间相关预测
    if time_variable is not None and prediction_horizon is not None:
        # 提取时间数据
        time_data = np.array(data[time_variable])
        
        # 根据预测时间范围调整标签
        # 例如：如果预测"90天内的结局"，则根据时间数据调整标签
        y_adjusted = []
        for i, outcome in enumerate(y_raw):
            if time_data[i] > prediction_horizon:
                # 如果观察时间超过预测范围，但没有事件发生，视为负结局
                y_adjusted.append(0)
            else:
                # 否则保持原结局
                y_adjusted.append(outcome)
        
        y = np.array(y_adjusted)
    else:
        y = y_raw
    
    # 处理缺失值
    # 使用均值填充数值型缺失值
    imputer = SimpleImputer(strategy='mean')
    X = imputer.fit_transform(X_raw)
    
    # 标准化特征
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # 特征名称
    feature_names = predictor_variables
    
    return {
        'X': X,
        'X_scaled': X_scaled,
        'y': y,
        'feature_names': feature_names,
        'imputer': imputer,
        'scaler': scaler
    }

def build_and_evaluate_model(dataset, model_type, validation_method, cv_folds, test_size):
    """构建和评估预测模型
    
    Args:
        dataset: 处理后的数据集
        model_type: 模型类型
        validation_method: 验证方法
        cv_folds: 交叉验证折数
        test_size: 测试集比例
        
    Returns:
        dict: 模型评估结果
    """
    X = dataset['X_scaled']  # 使用已缩放的特征
    y = dataset['y']
    feature_names = dataset['feature_names']
    
    # 选择模型
    if model_type == 'random_forest':
        model = RandomForestClassifier(n_estimators=100, random_state=42)
    elif model_type == 'gradient_boosting':
        model = GradientBoostingClassifier(n_estimators=100, random_state=42)
    elif model_type == 'logistic':
        model = LogisticRegression(max_iter=1000, random_state=42)
    else:
        return {
            'success': False,
            'message': f'不支持的模型类型: {model_type}'
        }
    
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
        
        # 计算ROC曲线和PR曲线的数据点
        if hasattr(model, 'predict_proba'):
            y_pred_proba = model.predict_proba(X)[:, 1]
            curve_data = calculate_curve_data(y, y_pred_proba)
        else:
            curve_data = None
        
        # 暂不计算混淆矩阵（交叉验证模式下）
        confusion_mat = None
        
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
            curve_data = calculate_curve_data(y_test, y_pred_proba)
        else:
            curve_data = None
        
        # 计算混淆矩阵
        cm = confusion_matrix(y_test, y_pred)
        confusion_mat = {
            'true_negative': int(cm[0, 0]),
            'false_positive': int(cm[0, 1]),
            'false_negative': int(cm[1, 0]),
            'true_positive': int(cm[1, 1])
        }
    else:
        return {
            'success': False,
            'message': f'不支持的验证方法: {validation_method}'
        }
    
    # 特征重要性
    feature_importance = {}
    
    if model_type in ['random_forest', 'gradient_boosting']:
        # 对于树模型，使用特征重要性属性
        if hasattr(model, 'feature_importances_'):
            for i, feature in enumerate(feature_names):
                feature_importance[feature] = float(model.feature_importances_[i])
    elif model_type == 'logistic':
        # 对于逻辑回归，使用系数作为特征重要性
        if hasattr(model, 'coef_'):
            for i, feature in enumerate(feature_names):
                feature_importance[feature] = float(abs(model.coef_[0][i]))
    
    # 结果
    results = {
        'success': True,
        'model_type': model_type,
        'validation_method': validation_method,
        'evaluation_metrics': evaluation_metrics,
        'feature_importance': feature_importance,
        'model': model  # 包含模型对象，用于后续处理
    }
    
    # 添加混淆矩阵（如果有）
    if confusion_mat:
        results['confusion_matrix'] = confusion_mat
    
    # 添加曲线数据（如果有）
    if curve_data:
        results['curve_data'] = curve_data
    
    return results

def calculate_curve_data(y_true, y_pred_proba):
    """计算ROC曲线和PR曲线数据
    
    Args:
        y_true: 真实标签
        y_pred_proba: 预测概率
        
    Returns:
        dict: 曲线数据
    """
    # ROC曲线
    fpr, tpr, roc_thresholds = roc_curve(y_true, y_pred_proba)
    roc_points = []
    for i in range(len(fpr)):
        if i % max(1, len(fpr) // 100) == 0:  # 只保留约100个点，减少数据量
            roc_points.append({
                'fpr': float(fpr[i]),
                'tpr': float(tpr[i]),
                'threshold': float(roc_thresholds[i]) if i < len(roc_thresholds) else None
            })
    
    # PR曲线
    precision, recall, pr_thresholds = precision_recall_curve(y_true, y_pred_proba)
    pr_points = []
    for i in range(len(precision)):
        if i % max(1, len(precision) // 100) == 0:  # 只保留约100个点
            pr_points.append({
                'precision': float(precision[i]),
                'recall': float(recall[i]),
                'threshold': float(pr_thresholds[i]) if i < len(pr_thresholds) else None
            })
    
    # 平均精度分数
    ap_score = float(average_precision_score(y_true, y_pred_proba))
    
    return {
        'roc_curve': roc_points,
        'pr_curve': pr_points,
        'average_precision': ap_score
    }

def calculate_risk_stratification(model, X, y):
    """计算风险分层
    
    Args:
        model: 训练好的模型
        X: 特征矩阵
        y: 目标变量
        
    Returns:
        dict: 风险分层结果
    """
    # 检查模型是否支持概率预测
    if not hasattr(model, 'predict_proba'):
        return {'message': '所选模型不支持概率预测，无法进行风险分层'}
    
    # 获取预测概率
    y_pred_proba = model.predict_proba(X)[:, 1]
    
    # 根据概率分布计算风险分层阈值
    # 低风险: < 25%分位数
    # 中低风险: 25-50%分位数
    # 中高风险: 50-75%分位数
    # 高风险: > 75%分位数
    q1 = float(np.percentile(y_pred_proba, 25))
    q2 = float(np.percentile(y_pred_proba, 50))
    q3 = float(np.percentile(y_pred_proba, 75))
    
    # 分配风险组
    risk_groups = []
    for prob in y_pred_proba:
        if prob < q1:
            risk_groups.append('low')
        elif prob < q2:
            risk_groups.append('medium_low')
        elif prob < q3:
            risk_groups.append('medium_high')
        else:
            risk_groups.append('high')
    
    # 计算每个风险组的统计信息
    group_stats = {}
    for group in ['low', 'medium_low', 'medium_high', 'high']:
        group_indices = [i for i, g in enumerate(risk_groups) if g == group]
        if group_indices:
            group_y = [y[i] for i in group_indices]
            group_proba = [y_pred_proba[i] for i in group_indices]
            group_stats[group] = {
                'count': len(group_indices),
                'event_rate': float(sum(group_y) / len(group_y)) if group_y else 0,
                'mean_probability': float(np.mean(group_proba)),
                'min_probability': float(np.min(group_proba)),
                'max_probability': float(np.max(group_proba))
            }
    
    return {
        'thresholds': {
            'q1': q1,
            'q2': q2,
            'q3': q3
        },
        'group_stats': group_stats
    }

def save_prediction_model(model, scaler, imputer, feature_names, model_name):
    """保存预测模型
    
    Args:
        model: 训练好的模型
        scaler: 特征缩放器
        imputer: 缺失值填充器
        feature_names: 特征名称
        model_name: 模型名称
        
    Returns:
        str: 模型保存路径
    """
    # 创建模型目录
    model_dir = os.path.join('models', 'outcome_prediction')
    os.makedirs(model_dir, exist_ok=True)
    
    # 模型保存路径
    model_path = os.path.join(model_dir, f"{model_name}.joblib")
    
    # 创建模型包，包含模型和预处理器
    model_package = {
        'model': model,
        'scaler': scaler,
        'imputer': imputer,
        'feature_names': feature_names,
        'created_at': datetime.datetime.now().isoformat()
    }
    
    # 保存模型包
    joblib.dump(model_package, model_path)
    
    return model_path

def load_prediction_model(model_path):
    """加载预测模型
    
    Args:
        model_path: 模型路径
        
    Returns:
        dict: 加载的模型包
    """
    try:
        model_package = joblib.load(model_path)
        return model_package
    except Exception as e:
        return {'error': str(e)}

def predict_outcome(model_path, patient_data):
    """使用保存的模型预测患者结局
    
    Args:
        model_path: 模型路径
        patient_data: 患者数据，格式为{feature_name: value}
        
    Returns:
        dict: 预测结果
    """
    # 加载模型
    model_package = load_prediction_model(model_path)
    
    if 'error' in model_package:
        return {'success': False, 'message': f"加载模型失败: {model_package['error']}"}
    
    model = model_package['model']
    scaler = model_package['scaler']
    imputer = model_package['imputer']
    feature_names = model_package['feature_names']
    
    # 准备数据
    features = []
    for feature in feature_names:
        features.append(patient_data.get(feature, None))
    
    # 转换为二维数组（一个样本）
    X = np.array([features])
    
    # 填充缺失值
    X_imputed = imputer.transform(X)
    
    # 标准化
    X_scaled = scaler.transform(X_imputed)
    
    # 预测
    outcome_proba = None
    if hasattr(model, 'predict_proba'):
        outcome_proba = float(model.predict_proba(X_scaled)[0, 1])
    
    outcome = int(model.predict(X_scaled)[0])
    
    result = {
        'success': True,
        'outcome_prediction': outcome,
        'outcome_probability': outcome_proba
    }
    
    # 根据概率判断风险等级
    if outcome_proba is not None:
        if outcome_proba < 0.25:
            result['risk_level'] = 'low'
        elif outcome_proba < 0.5:
            result['risk_level'] = 'medium_low'
        elif outcome_proba < 0.75:
            result['risk_level'] = 'medium_high'
        else:
            result['risk_level'] = 'high'
    
    return result 
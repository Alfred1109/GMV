"""
风险评估API模块

提供用于临床风险评估的机器学习模型API端点
"""

def setup_risk_assessment_api(app, csrf):
    """设置风险评估API端点
    
    Args:
        app: Flask应用实例
        csrf: CSRF保护实例
    """
    from flask import jsonify, request, current_app
    from flask_login import login_required, current_user
    import json
    import numpy as np
    
    @app.route('/api/analysis/risk', methods=['POST', 'OPTIONS'])
    @csrf.exempt
    @login_required
    def risk_assessment():
        """进行风险评估分析
        
        请求体格式:
        {
            "dataset_id": 1,  // 数据集ID
            "model_type": "logistic",  // 模型类型：logistic, decision_tree, random_forest
            "target_variable": "outcome",  // 目标变量（结局）
            "predictor_variables": ["age", "gender", "bmi"],  // 预测变量列表
            "validation_method": "cross_validation", // 可选的验证方法：cross_validation, split
            "validation_params": { // 可选的验证参数
                "cv_folds": 5,  // 交叉验证折数
                "test_size": 0.3  // 测试集比例
            }
        }
        
        Returns:
            包含风险评估结果的JSON响应
        """
        if request.method == 'OPTIONS':
            response = app.make_default_options_response()
            response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
            response.headers.add('Access-Control-Allow-Methods', 'POST')
            return response
            
        try:
            # 获取请求数据
            try:
                request_data = request.get_json()
                current_app.logger.info(f"接收到风险评估请求: {request_data}")
            except Exception as e:
                current_app.logger.error(f"解析请求JSON数据失败: {str(e)}")
                return jsonify({
                    'success': False,
                    'message': f'解析请求数据失败: {str(e)}'
                }), 400
            
            if not request_data:
                current_app.logger.warning("请求数据为空")
                return jsonify({
                    'success': False,
                    'message': '请求数据为空'
                }), 400
            
            # 验证参数
            dataset_id = request_data.get('dataset_id')
            model_type = request_data.get('model_type', 'logistic')
            target_variable = request_data.get('target_variable')
            predictor_variables = request_data.get('predictor_variables', [])
            validation_method = request_data.get('validation_method', 'cross_validation')
            validation_params = request_data.get('validation_params', {})
            
            current_app.logger.info(f"解析请求参数 - 数据集ID: {dataset_id}, 模型类型: {model_type}, "
                                   f"目标变量: {target_variable}, 预测变量: {predictor_variables}")
            
            # 验证参数类型和值
            if not dataset_id:
                return jsonify({
                    'success': False,
                    'message': '未指定数据集ID'
                }), 400
                
            if not model_type:
                return jsonify({
                    'success': False,
                    'message': '未指定风险评估模型类型'
                }), 400
                
            if not target_variable:
                return jsonify({
                    'success': False,
                    'message': '未指定目标变量'
                }), 400
                
            if not predictor_variables or not isinstance(predictor_variables, list) or len(predictor_variables) < 1:
                return jsonify({
                    'success': False,
                    'message': '至少需要指定一个预测变量进行风险评估'
                }), 400
                
            # 检查数据集是否存在，并验证访问权限
            from app.models.dataset import DataSet
            from app.models.dataset_entry import DatasetEntry
            
            dataset = DataSet.query.get(dataset_id)
            if not dataset:
                return jsonify({
                    'success': False,
                    'message': f'数据集(ID={dataset_id})不存在'
                }), 404
                
            # 检查用户是否有权限访问此数据集
            if dataset.privacy_level and dataset.privacy_level != 'public':
                if dataset.created_by != current_user.id and current_user.role != 'admin':
                    if not dataset.is_shared_with(current_user.id):
                        return jsonify({
                            'success': False, 
                            'message': f'没有权限访问数据集(ID={dataset_id})'
                        }), 403
            
            # 获取数据集条目
            entries = DatasetEntry.query.filter_by(dataset_id=dataset_id).all()
            if not entries:
                return jsonify({
                    'success': False,
                    'message': f'数据集(ID={dataset_id})没有数据条目'
                }), 404
                
            # 提取数据
            data = {}
            data[target_variable] = []
            
            for var in predictor_variables:
                data[var] = []
                
            # 从所有条目中提取所需变量的值
            for entry in entries:
                try:
                    entry_data = json.loads(entry.data)
                    
                    # 提取目标变量
                    if target_variable in entry_data:
                        target_value = entry_data[target_variable]
                        # 尝试将目标变量转换为二元值(0或1)，用于二分类问题
                        if isinstance(target_value, str):
                            if target_value.lower() in ['1', 'true', 'yes', 'y', 'positive']:
                                target_value = 1
                            elif target_value.lower() in ['0', 'false', 'no', 'n', 'negative']:
                                target_value = 0
                            else:
                                try:
                                    if '.' in target_value:
                                        target_value = float(target_value)
                                    else:
                                        target_value = int(target_value)
                                except (ValueError, TypeError):
                                    pass
                        elif isinstance(target_value, bool):
                            target_value = 1 if target_value else 0
                        data[target_variable].append(target_value)
                    else:
                        data[target_variable].append(None)  # 缺失值
                    
                    # 提取预测变量
                    for var in predictor_variables:
                        if var in entry_data:
                            value = entry_data[var]
                            # 尝试将数值型字符串转换为数字
                            if isinstance(value, str):
                                try:
                                    if '.' in value:
                                        value = float(value)
                                    else:
                                        value = int(value)
                                except (ValueError, TypeError):
                                    pass
                            data[var].append(value)
                        else:
                            data[var].append(None)  # 缺失值
                except Exception as e:
                    current_app.logger.error(f"处理条目数据时出错: {str(e)}")
                    continue
                    
            # 数据预处理：移除包含缺失值的观测
            valid_indices = set(range(len(entries)))
            
            # 目标变量必须有效
            for i, value in enumerate(data[target_variable]):
                if value is None:
                    if i in valid_indices:
                        valid_indices.remove(i)
            
            # 预测变量处理
            for var in predictor_variables:
                for i, value in enumerate(data[var]):
                    if value is None:
                        if i in valid_indices:
                            valid_indices.remove(i)
            
            # 创建过滤后的数据
            filtered_data = {}
            filtered_data[target_variable] = [data[target_variable][i] for i in valid_indices]
            for var in predictor_variables:
                filtered_data[var] = [data[var][i] for i in valid_indices]
            
            # 检查是否有足够的数据点
            if len(valid_indices) < len(predictor_variables) + 10:  # 至少需要比预测变量数量多10个观测
                return jsonify({
                    'success': False,
                    'message': f'没有足够的数据点进行风险评估分析(仅有{len(valid_indices)}个有效观测)'
                }), 400
            
            # 执行风险评估分析
            try:
                # 导入必要的库
                from sklearn.model_selection import train_test_split, cross_val_score
                from sklearn.linear_model import LogisticRegression
                from sklearn.tree import DecisionTreeClassifier
                from sklearn.ensemble import RandomForestClassifier
                from sklearn.preprocessing import StandardScaler
                from sklearn.metrics import (
                    accuracy_score, precision_score, recall_score, f1_score, 
                    roc_auc_score, confusion_matrix, classification_report
                )
                
                # 提取数据
                y = np.array(filtered_data[target_variable])
                X = np.array([[filtered_data[var][i] for var in predictor_variables] for i in range(len(y))])
                
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
                    return jsonify({
                        'success': False,
                        'message': f'不支持的模型类型: {model_type}'
                    }), 400
                
                # 从验证参数中获取参数
                cv_folds = validation_params.get('cv_folds', 5)
                test_size = validation_params.get('test_size', 0.3)
                
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
                    return jsonify({
                        'success': False,
                        'message': f'不支持的验证方法: {validation_method}'
                    }), 400
                
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
                # 检查模型是否支持概率预测
                if hasattr(model, 'predict_proba'):
                    # 获取预测概率
                    y_pred_proba = model.predict_proba(X)[:, 1]
                    
                    # 根据概率分布计算风险分层阈值
                    # 低风险: < 33%分位数
                    # 中风险: 33-66%分位数
                    # 高风险: > 66%分位数
                    low_threshold = float(np.percentile(y_pred_proba, 33))
                    high_threshold = float(np.percentile(y_pred_proba, 66))
                    
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
                                'event_rate': float(sum(group_y) / len(group_y)) if group_y else 0,
                                'threshold': low_threshold if group == 'low' else high_threshold if group == 'high' else None
                            }
                    
                    risk_stratification = {
                        'thresholds': {
                            'low': low_threshold,
                            'high': high_threshold
                        },
                        'group_stats': group_stats
                    }
                else:
                    risk_stratification = {'message': '所选模型不支持概率预测，无法进行风险分层'}
                
                # 判断变量类型
                def get_variable_type(values):
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
                
                # 获取变量类型
                variable_types = {var: get_variable_type(filtered_data[var]) for var in predictor_variables + [target_variable]}
                
                # 构建结果
                result = {
                    'model_type': model_type,
                    'validation_method': validation_method,
                    'evaluation_metrics': evaluation_metrics,
                    'feature_importance': feature_importance,
                    'risk_stratification': risk_stratification,
                    'variable_types': variable_types
                }
                
                # 记录分析结果摘要
                current_app.logger.info(f"风险评估分析完成，模型类型: {model_type}, "
                                       f"验证方法: {validation_method}, "
                                       f"准确率: {evaluation_metrics.get('accuracy', 'N/A')}")
                
                # 构建响应
                response = {
                    'success': True,
                    'message': '风险评估分析完成',
                    'result': result,
                    'dataset_info': {
                        'id': dataset_id,
                        'name': dataset.name,
                        'description': dataset.description,
                        'total_entries': len(entries),
                        'valid_entries': len(valid_indices)
                    }
                }
                
                return jsonify(response), 200
                    
            except Exception as e:
                current_app.logger.error(f"执行风险评估分析时出错: {str(e)}")
                return jsonify({
                    'success': False,
                    'message': f'执行风险评估分析时出错: {str(e)}'
                }), 500
                
        except Exception as e:
            current_app.logger.error(f"风险评估分析失败: {str(e)}")
            return jsonify({
                'success': False,
                'message': f'风险评估分析失败: {str(e)}'
            }), 500 
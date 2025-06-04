"""
结局预测API模块

提供用于临床结局预测的API端点
"""

def setup_outcome_prediction_api(app, csrf):
    """设置结局预测API端点
    
    Args:
        app: Flask应用实例
        csrf: CSRF保护实例
    """
    from flask import jsonify, request, current_app
    from flask_login import login_required, current_user
    import json
    import numpy as np
    import os
    from outcome_prediction_model import perform_outcome_prediction, predict_outcome
    
    @app.route('/api/analysis/outcome_prediction', methods=['POST', 'OPTIONS'])
    @csrf.exempt
    @login_required
    def outcome_prediction():
        """进行结局预测分析
        
        请求体格式:
        {
            "dataset_id": 1,  // 数据集ID
            "model_type": "random_forest",  // 模型类型：random_forest, gradient_boosting, logistic
            "target_variable": "outcome",  // 目标变量（结局）
            "predictor_variables": ["age", "gender", "bmi"],  // 预测变量列表
            "time_variable": "follow_up_days",  // 时间变量（可选）
            "prediction_horizon": 365,  // 预测时间范围（天数）（可选）
            "validation_method": "cross_validation", // 可选的验证方法：cross_validation, split
            "validation_params": { // 可选的验证参数
                "cv_folds": 5,  // 交叉验证折数
                "test_size": 0.3  // 测试集比例
            },
            "save_model": true,  // 是否保存模型
            "model_name": "my_model"  // 模型名称（可选）
        }
        
        Returns:
            包含结局预测结果的JSON响应
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
                current_app.logger.info(f"接收到结局预测请求: {request_data}")
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
            model_type = request_data.get('model_type', 'random_forest')
            target_variable = request_data.get('target_variable')
            predictor_variables = request_data.get('predictor_variables', [])
            time_variable = request_data.get('time_variable')
            prediction_horizon = request_data.get('prediction_horizon')
            validation_method = request_data.get('validation_method', 'cross_validation')
            validation_params = request_data.get('validation_params', {})
            save_model = request_data.get('save_model', False)
            model_name = request_data.get('model_name')
            
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
                    'message': '未指定结局预测模型类型'
                }), 400
                
            if not target_variable:
                return jsonify({
                    'success': False,
                    'message': '未指定目标变量'
                }), 400
                
            if not predictor_variables or not isinstance(predictor_variables, list) or len(predictor_variables) < 1:
                return jsonify({
                    'success': False,
                    'message': '至少需要指定一个预测变量进行结局预测'
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
                
            # 如果有时间变量，也提取时间数据
            if time_variable:
                data[time_variable] = []
                
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
                    
                    # 提取时间变量（如果有）
                    if time_variable:
                        if time_variable in entry_data:
                            time_value = entry_data[time_variable]
                            # 尝试将时间值转换为数字
                            if isinstance(time_value, str):
                                try:
                                    time_value = float(time_value)
                                except (ValueError, TypeError):
                                    pass
                            data[time_variable].append(time_value)
                        else:
                            data[time_variable].append(None)  # 缺失值
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
            
            # 时间变量处理（如果有）
            if time_variable:
                for i, value in enumerate(data[time_variable]):
                    if value is None:
                        if i in valid_indices:
                            valid_indices.remove(i)
            
            # 创建过滤后的数据
            filtered_data = {}
            filtered_data[target_variable] = [data[target_variable][i] for i in valid_indices]
            
            for var in predictor_variables:
                filtered_data[var] = [data[var][i] for i in valid_indices]
                
            if time_variable:
                filtered_data[time_variable] = [data[time_variable][i] for i in valid_indices]
            
            # 检查是否有足够的数据点
            if len(valid_indices) < len(predictor_variables) + 10:  # 至少需要比预测变量数量多10个观测
                return jsonify({
                    'success': False,
                    'message': f'没有足够的数据点进行结局预测分析(仅有{len(valid_indices)}个有效观测)'
                }), 400
            
            # 执行结局预测分析
            try:
                # 如果需要保存模型且未指定模型名称，生成一个
                if save_model and not model_name:
                    import datetime
                    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                    model_name = f"outcome_model_{dataset.name}_{timestamp}"
                
                # 创建模型目录
                if save_model:
                    os.makedirs('models/outcome_prediction', exist_ok=True)
                
                # 执行结局预测
                result = perform_outcome_prediction(
                    data=filtered_data,
                    target_variable=target_variable,
                    predictor_variables=predictor_variables,
                    time_variable=time_variable,
                    prediction_horizon=prediction_horizon,
                    model_type=model_type,
                    validation_method=validation_method,
                    validation_params=validation_params,
                    save_model=save_model,
                    model_name=model_name
                )
                
                # 检查结果
                if not result.get('success', True):
                    return jsonify(result), 400
                
                # 记录分析结果摘要
                current_app.logger.info(f"结局预测分析完成，模型类型: {model_type}, "
                                       f"验证方法: {validation_method}, "
                                       f"准确率: {result.get('evaluation_metrics', {}).get('accuracy', 'N/A')}")
                
                # 构建响应
                response = {
                    'success': True,
                    'message': '结局预测分析完成',
                    'result': result,
                    'dataset_info': {
                        'id': dataset_id,
                        'name': dataset.name,
                        'description': dataset.description,
                        'total_entries': len(entries),
                        'valid_entries': len(valid_indices)
                    }
                }
                
                # 如果保存了模型，添加相关信息
                if save_model and 'model_saved_path' in result:
                    response['model_info'] = {
                        'name': model_name,
                        'path': result['model_saved_path'],
                        'created_at': datetime.datetime.now().isoformat()
                    }
                
                return jsonify(response), 200
                
            except Exception as e:
                current_app.logger.error(f"执行结局预测分析时出错: {str(e)}")
                return jsonify({
                    'success': False,
                    'message': f'执行结局预测分析时出错: {str(e)}'
                }), 500
            
        except Exception as e:
            current_app.logger.error(f"结局预测分析失败: {str(e)}")
            return jsonify({
                'success': False,
                'message': f'结局预测分析失败: {str(e)}'
            }), 500
    
    @app.route('/api/analysis/outcome_prediction/predict', methods=['POST', 'OPTIONS'])
    @csrf.exempt
    @login_required
    def predict_individual_outcome():
        """使用保存的模型预测单个患者的结局
        
        请求体格式:
        {
            "model_path": "models/outcome_prediction/my_model.joblib",  // 模型路径
            "patient_data": {  // 患者数据
                "age": 65,
                "gender": 1,
                "bmi": 28.5,
                ...
            }
        }
        
        Returns:
            包含预测结果的JSON响应
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
                current_app.logger.info(f"接收到结局预测请求: {request_data}")
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
            
            # 提取参数
            model_path = request_data.get('model_path')
            patient_data = request_data.get('patient_data', {})
            
            # 验证参数
            if not model_path:
                return jsonify({
                    'success': False,
                    'message': '未指定模型路径'
                }), 400
                
            if not patient_data or not isinstance(patient_data, dict):
                return jsonify({
                    'success': False,
                    'message': '未提供患者数据或格式不正确'
                }), 400
                
            # 检查模型文件是否存在
            if not os.path.exists(model_path):
                return jsonify({
                    'success': False,
                    'message': f'模型文件不存在: {model_path}'
                }), 404
                
            # 执行预测
            try:
                prediction_result = predict_outcome(model_path, patient_data)
                
                if not prediction_result.get('success', False):
                    return jsonify(prediction_result), 400
                
                # 记录预测结果
                current_app.logger.info(f"预测结果: 结局={prediction_result.get('outcome_prediction')}, "
                                       f"概率={prediction_result.get('outcome_probability')}")
                
                # 构建响应
                response = {
                    'success': True,
                    'message': '结局预测完成',
                    'prediction': prediction_result
                }
                
                return jsonify(response), 200
                
            except Exception as e:
                current_app.logger.error(f"执行结局预测时出错: {str(e)}")
                return jsonify({
                    'success': False,
                    'message': f'执行结局预测时出错: {str(e)}'
                }), 500
                
        except Exception as e:
            current_app.logger.error(f"结局预测失败: {str(e)}")
            return jsonify({
                'success': False,
                'message': f'结局预测失败: {str(e)}'
            }), 500
    
    @app.route('/api/analysis/outcome_prediction/models', methods=['GET'])
    @login_required
    def list_outcome_models():
        """列出所有保存的结局预测模型
        
        Returns:
            包含模型列表的JSON响应
        """
        try:
            # 检查模型目录是否存在
            model_dir = os.path.join('models', 'outcome_prediction')
            if not os.path.exists(model_dir):
                return jsonify({
                    'success': True,
                    'models': []
                }), 200
                
            # 获取所有模型文件
            model_files = [f for f in os.listdir(model_dir) if f.endswith('.joblib')]
            
            # 构建模型信息
            models = []
            for model_file in model_files:
                model_path = os.path.join(model_dir, model_file)
                model_name = os.path.splitext(model_file)[0]
                
                # 获取文件修改时间
                import datetime
                modified_time = datetime.datetime.fromtimestamp(os.path.getmtime(model_path)).isoformat()
                
                models.append({
                    'name': model_name,
                    'path': model_path,
                    'last_modified': modified_time
                })
            
            return jsonify({
                'success': True,
                'models': models
            }), 200
                
        except Exception as e:
            current_app.logger.error(f"获取模型列表失败: {str(e)}")
            return jsonify({
                'success': False,
                'message': f'获取模型列表失败: {str(e)}'
            }), 500 
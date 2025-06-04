"""
风险评估分析API处理模块
"""

import json
import pandas as pd
import numpy as np
from flask import jsonify, request, current_app
from flask_login import login_required, current_user
from app.models.dataset import DataSet
from app.models.dataset_entry import DatasetEntry
from risk_assessment_model import perform_risk_assessment

def setup_risk_assessment_routes(app, csrf):
    """设置风险评估相关路由
    
    Args:
        app: Flask应用实例
        csrf: CSRF保护实例
    """
    @app.route('/api/analysis/risk', methods=['POST', 'OPTIONS'])
    @csrf.exempt
    @login_required
    def risk_assessment_api():
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
                result = perform_risk_assessment(
                    data=filtered_data,
                    target_variable=target_variable,
                    predictor_variables=predictor_variables,
                    model_type=model_type,
                    validation_method=validation_method,
                    validation_params=validation_params
                )
                
                # 记录分析结果摘要
                current_app.logger.info(f"风险评估分析完成，模型类型: {model_type}, "
                                       f"验证方法: {validation_method}, "
                                       f"准确率: {result['evaluation_metrics'].get('accuracy', 'N/A')}")
                
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
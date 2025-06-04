"""
自定义统计模型API路由

提供创建、获取、更新和删除自定义统计模型的API
"""

from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user
from app import db, csrf
from app.models.custom_stat_model import CustomStatModel
from app.models.dataset import DataSet
import json

custom_stat_model_bp = Blueprint('custom_stat_model', __name__)

@custom_stat_model_bp.route('/api/custom_models', methods=['GET'])
@login_required
def get_custom_models():
    """获取用户的自定义统计模型列表
    
    可选参数:
    - model_type: 过滤特定类型的模型
    - dataset_id: 过滤关联特定数据集的模型
    
    Returns:
        JSON响应，包含模型列表
    """
    try:
        # 获取查询参数
        model_type = request.args.get('model_type')
        dataset_id = request.args.get('dataset_id')
        
        # 构建查询
        query = CustomStatModel.query.filter(
            (CustomStatModel.created_by == current_user.id) | 
            (CustomStatModel.is_public == True)
        )
        
        # 应用过滤条件
        if model_type:
            query = query.filter(CustomStatModel.model_type == model_type)
        
        if dataset_id:
            query = query.filter(
                (CustomStatModel.dataset_id == dataset_id) | 
                (CustomStatModel.dataset_id == None)
            )
        
        # 执行查询
        models = query.order_by(CustomStatModel.updated_at.desc()).all()
        
        # 转换为字典列表
        models_list = [model.to_dict() for model in models]
        
        return jsonify({
            'success': True,
            'models': models_list
        }), 200
    
    except Exception as e:
        current_app.logger.error(f"获取自定义模型列表失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'获取自定义模型列表失败: {str(e)}'
        }), 500

@custom_stat_model_bp.route('/api/custom_models/<int:model_id>', methods=['GET'])
@login_required
def get_custom_model(model_id):
    """获取特定的自定义统计模型
    
    Args:
        model_id: 模型ID
    
    Returns:
        JSON响应，包含模型详情
    """
    try:
        # 查询模型
        model = CustomStatModel.query.get(model_id)
        
        # 检查模型是否存在
        if not model:
            return jsonify({
                'success': False,
                'message': f'模型ID={model_id}不存在'
            }), 404
        
        # 检查访问权限
        if model.created_by != current_user.id and not model.is_public:
            return jsonify({
                'success': False,
                'message': '无权访问此模型'
            }), 403
        
        # 返回模型详情
        return jsonify({
            'success': True,
            'model': model.to_dict()
        }), 200
    
    except Exception as e:
        current_app.logger.error(f"获取自定义模型详情失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'获取自定义模型详情失败: {str(e)}'
        }), 500

@custom_stat_model_bp.route('/api/custom_models', methods=['POST'])
@csrf.exempt
@login_required
def create_custom_model():
    """创建新的自定义统计模型
    
    请求体示例:
    {
        "name": "我的回归模型",
        "description": "预测患者住院天数的模型",
        "model_type": "regression",
        "config": {
            "regression_type": "linear",
            "target_variable": "los_days",
            "include_intercept": true
        },
        "variables": ["age", "gender", "bmi", "comorbidity_count"],
        "dataset_id": 1,
        "is_public": false
    }
    
    Returns:
        JSON响应，包含创建的模型信息
    """
    try:
        # 获取请求数据
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': '请求数据为空'
            }), 400
        
        # 验证必填字段
        required_fields = ['name', 'model_type', 'config', 'variables']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({
                    'success': False,
                    'message': f'缺少必填字段: {field}'
                }), 400
        
        # 验证模型类型
        valid_model_types = ['regression', 'survival', 'risk', 'outcome']
        if data['model_type'] not in valid_model_types:
            return jsonify({
                'success': False,
                'message': f'无效的模型类型，有效值: {", ".join(valid_model_types)}'
            }), 400
        
        # 如果指定了数据集，验证数据集存在且有访问权限
        if 'dataset_id' in data and data['dataset_id']:
            dataset = DataSet.query.get(data['dataset_id'])
            
            if not dataset:
                return jsonify({
                    'success': False,
                    'message': f'数据集ID={data["dataset_id"]}不存在'
                }), 404
            
            # 检查数据集访问权限
            if dataset.privacy_level and dataset.privacy_level != 'public':
                if dataset.created_by != current_user.id and current_user.role != 'admin':
                    if not dataset.is_shared_with(current_user.id):
                        return jsonify({
                            'success': False, 
                            'message': f'没有权限访问数据集ID={data["dataset_id"]}'
                        }), 403
        
        # 创建新模型
        new_model = CustomStatModel()
        
        # 设置创建者
        data['created_by'] = current_user.id
        
        # 从请求数据更新模型属性
        new_model.from_dict(data)
        
        # 保存到数据库
        db.session.add(new_model)
        db.session.commit()
        
        # 返回创建的模型信息
        return jsonify({
            'success': True,
            'message': '自定义统计模型创建成功',
            'model': new_model.to_dict()
        }), 201
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"创建自定义模型失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'创建自定义模型失败: {str(e)}'
        }), 500

@custom_stat_model_bp.route('/api/custom_models/<int:model_id>', methods=['PUT'])
@csrf.exempt
@login_required
def update_custom_model(model_id):
    """更新现有的自定义统计模型
    
    Args:
        model_id: 模型ID
    
    Returns:
        JSON响应，包含更新后的模型信息
    """
    try:
        # 查询模型
        model = CustomStatModel.query.get(model_id)
        
        # 检查模型是否存在
        if not model:
            return jsonify({
                'success': False,
                'message': f'模型ID={model_id}不存在'
            }), 404
        
        # 检查更新权限
        if model.created_by != current_user.id and current_user.role != 'admin':
            return jsonify({
                'success': False,
                'message': '无权更新此模型'
            }), 403
        
        # 获取请求数据
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': '请求数据为空'
            }), 400
        
        # 验证模型类型（如果提供）
        if 'model_type' in data:
            valid_model_types = ['regression', 'survival', 'risk', 'outcome']
            if data['model_type'] not in valid_model_types:
                return jsonify({
                    'success': False,
                    'message': f'无效的模型类型，有效值: {", ".join(valid_model_types)}'
                }), 400
        
        # 如果指定了新的数据集，验证数据集存在且有访问权限
        if 'dataset_id' in data and data['dataset_id']:
            dataset = DataSet.query.get(data['dataset_id'])
            
            if not dataset:
                return jsonify({
                    'success': False,
                    'message': f'数据集ID={data["dataset_id"]}不存在'
                }), 404
            
            # 检查数据集访问权限
            if dataset.privacy_level and dataset.privacy_level != 'public':
                if dataset.created_by != current_user.id and current_user.role != 'admin':
                    if not dataset.is_shared_with(current_user.id):
                        return jsonify({
                            'success': False, 
                            'message': f'没有权限访问数据集ID={data["dataset_id"]}'
                        }), 403
        
        # 从请求数据更新模型属性
        model.from_dict(data)
        
        # 保存到数据库
        db.session.commit()
        
        # 返回更新后的模型信息
        return jsonify({
            'success': True,
            'message': '自定义统计模型更新成功',
            'model': model.to_dict()
        }), 200
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"更新自定义模型失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'更新自定义模型失败: {str(e)}'
        }), 500

@custom_stat_model_bp.route('/api/custom_models/<int:model_id>', methods=['DELETE'])
@csrf.exempt
@login_required
def delete_custom_model(model_id):
    """删除自定义统计模型
    
    Args:
        model_id: 模型ID
    
    Returns:
        JSON响应，包含删除结果
    """
    try:
        # 查询模型
        model = CustomStatModel.query.get(model_id)
        
        # 检查模型是否存在
        if not model:
            return jsonify({
                'success': False,
                'message': f'模型ID={model_id}不存在'
            }), 404
        
        # 检查删除权限
        if model.created_by != current_user.id and current_user.role != 'admin':
            return jsonify({
                'success': False,
                'message': '无权删除此模型'
            }), 403
        
        # 从数据库删除
        db.session.delete(model)
        db.session.commit()
        
        # 返回删除结果
        return jsonify({
            'success': True,
            'message': '自定义统计模型删除成功'
        }), 200
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"删除自定义模型失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'删除自定义模型失败: {str(e)}'
        }), 500

@custom_stat_model_bp.route('/api/custom_models/<int:model_id>/apply', methods=['POST'])
@csrf.exempt
@login_required
def apply_custom_model(model_id):
    """应用自定义统计模型到数据集
    
    Args:
        model_id: 模型ID
    
    请求体示例:
    {
        "dataset_id": 2,
        "parameters": {
            "additional_parameter1": "value1",
            "additional_parameter2": "value2"
        }
    }
    
    Returns:
        JSON响应，包含应用模型的结果
    """
    try:
        # 查询模型
        model = CustomStatModel.query.get(model_id)
        
        # 检查模型是否存在
        if not model:
            return jsonify({
                'success': False,
                'message': f'模型ID={model_id}不存在'
            }), 404
        
        # 检查访问权限
        if model.created_by != current_user.id and not model.is_public:
            return jsonify({
                'success': False,
                'message': '无权访问此模型'
            }), 403
        
        # 获取请求数据
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': '请求数据为空'
            }), 400
        
        # 验证必填字段
        if 'dataset_id' not in data:
            return jsonify({
                'success': False,
                'message': '缺少必填字段: dataset_id'
            }), 400
        
        # 验证数据集存在且有访问权限
        dataset_id = data['dataset_id']
        dataset = DataSet.query.get(dataset_id)
        
        if not dataset:
            return jsonify({
                'success': False,
                'message': f'数据集ID={dataset_id}不存在'
            }), 404
        
        # 检查数据集访问权限
        if dataset.privacy_level and dataset.privacy_level != 'public':
            if dataset.created_by != current_user.id and current_user.role != 'admin':
                if not dataset.is_shared_with(current_user.id):
                    return jsonify({
                        'success': False, 
                        'message': f'没有权限访问数据集ID={dataset_id}'
                    }), 403
        
        # 获取模型配置和变量
        model_config = json.loads(model.config)
        model_variables = json.loads(model.variables)
        
        # 获取附加参数（如果有）
        parameters = data.get('parameters', {})
        
        # 根据模型类型调用相应的分析函数
        # 这里是一个简化的示例，实际应用中需要根据模型类型调用不同的分析函数
        if model.model_type == 'regression':
            # 调用回归分析API
            # 这里需要补充实际的回归分析调用代码
            result = {
                'model_type': 'regression',
                'message': '模型应用成功，这是回归分析的结果',
                'variables': model_variables,
                'config': model_config,
                'parameters': parameters
            }
        elif model.model_type == 'survival':
            # 调用生存分析API
            # 这里需要补充实际的生存分析调用代码
            result = {
                'model_type': 'survival',
                'message': '模型应用成功，这是生存分析的结果',
                'variables': model_variables,
                'config': model_config,
                'parameters': parameters
            }
        elif model.model_type == 'risk':
            # 调用风险评估API
            # 这里需要补充实际的风险评估调用代码
            result = {
                'model_type': 'risk',
                'message': '模型应用成功，这是风险评估的结果',
                'variables': model_variables,
                'config': model_config,
                'parameters': parameters
            }
        elif model.model_type == 'outcome':
            # 调用结局预测API
            # 这里需要补充实际的结局预测调用代码
            result = {
                'model_type': 'outcome',
                'message': '模型应用成功，这是结局预测的结果',
                'variables': model_variables,
                'config': model_config,
                'parameters': parameters
            }
        else:
            return jsonify({
                'success': False,
                'message': f'不支持的模型类型: {model.model_type}'
            }), 400
        
        # 返回应用结果
        return jsonify({
            'success': True,
            'message': '自定义统计模型应用成功',
            'result': result
        }), 200
    
    except Exception as e:
        current_app.logger.error(f"应用自定义模型失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'应用自定义模型失败: {str(e)}'
        }), 500 
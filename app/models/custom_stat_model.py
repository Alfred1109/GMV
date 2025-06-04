"""
自定义统计模型数据库模型

允许用户创建和保存自定义的统计分析模型
"""

from app import db
from datetime import datetime
import json

class CustomStatModel(db.Model):
    """自定义统计模型数据库模型
    
    存储用户创建的自定义统计分析模型信息，包括模型类型、
    参数配置、变量选择等，支持跨数据集复用模型。
    """
    __tablename__ = 'custom_stat_models'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    model_type = db.Column(db.String(100), nullable=False)  # 模型类型: regression, survival, risk, outcome
    config = db.Column(db.Text, nullable=False)  # JSON格式的模型配置
    variables = db.Column(db.Text, nullable=False)  # JSON格式的变量列表
    
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关联的数据集（可选，如果模型绑定到特定数据集）
    dataset_id = db.Column(db.Integer, db.ForeignKey('data_sets.id'), nullable=True)
    
    # 是否公开分享此模型
    is_public = db.Column(db.Boolean, default=False)
    
    def to_dict(self):
        """将模型转换为字典
        
        Returns:
            dict: 模型信息字典
        """
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'model_type': self.model_type,
            'config': json.loads(self.config) if self.config else {},
            'variables': json.loads(self.variables) if self.variables else [],
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'dataset_id': self.dataset_id,
            'is_public': self.is_public
        }
    
    def from_dict(self, data):
        """从字典更新模型
        
        Args:
            data: 模型信息字典
        """
        for field in ['name', 'description', 'model_type', 'created_by', 'dataset_id', 'is_public']:
            if field in data:
                setattr(self, field, data[field])
        
        if 'config' in data:
            self.config = json.dumps(data['config'])
        
        if 'variables' in data:
            self.variables = json.dumps(data['variables'])
    
    def __repr__(self):
        return f'<CustomStatModel {self.name}>' 
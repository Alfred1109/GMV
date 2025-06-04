"""
数据库迁移脚本 - 添加自定义统计模型表

创建自定义统计模型表，支持用户保存和复用统计分析模型配置
"""

from app import app, db
from app.models.custom_stat_model import CustomStatModel
from flask_migrate import Migrate
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_custom_stat_model_table():
    """创建自定义统计模型表"""
    try:
        # 创建数据库迁移对象
        migrate = Migrate(app, db)
        
        # 检查表是否已存在
        inspector = db.inspect(db.engine)
        if 'custom_stat_models' in inspector.get_table_names():
            logger.info("自定义统计模型表已存在，无需创建")
            return
        
        # 在应用上下文中创建表
        with app.app_context():
            # 创建表
            db.create_all()
            logger.info("自定义统计模型表创建成功")
            
    except Exception as e:
        logger.error(f"创建自定义统计模型表失败: {str(e)}")
        raise

if __name__ == "__main__":
    logger.info("开始创建自定义统计模型表...")
    create_custom_stat_model_table()
    logger.info("完成数据库迁移") 
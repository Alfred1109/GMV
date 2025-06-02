from app import app, db, User, DataSet
import json
from sqlalchemy import text
import os

def init_db():
    # 创建所有表
    print("正在创建数据库表...")
    db.create_all()
    
    # 检查是否有管理员用户
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        print("创建管理员用户...")
        admin = User(username='admin', email='admin@zltech.com', role='admin')
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        
    # 添加测试数据集
    if DataSet.query.count() == 0:
        print("添加示例数据集...")
        # 测试自定义字段
        custom_fields = [
            {"name": "患者姓名", "type": "text", "description": "患者的全名", "required": True},
            {"name": "年龄", "type": "number", "description": "患者年龄", "required": True},
            {"name": "性别", "type": "select", "description": "患者性别", "options": ["男", "女"], "required": True},
            {"name": "入院日期", "type": "date", "description": "患者入院时间", "required": True},
            {"name": "主诉", "type": "text", "description": "患者主诉", "required": False},
            {"name": "既往病史", "type": "text", "description": "患者既往病史", "required": False}
        ]
        
        # 创建测试数据集
        test_dataset = DataSet(
            name="测试临床数据采集",
            description="用于测试自定义字段数据采集功能的数据集",
            created_by=admin.id,
            version="1.0",
            privacy_level="private",
            custom_fields=json.dumps(custom_fields)
        )
        
        db.session.add(test_dataset)
        db.session.commit()
        print(f"已创建测试数据集，ID: {test_dataset.id}")
    
    print("数据库初始化完成!")

def migrate_add_user_fields():
    """添加用户表的新字段: center_name, institution"""
    print("正在添加用户表新字段...")
    
    # 检查是否需要添加center_name列
    try:
        db.session.execute(text("SELECT center_name FROM user LIMIT 1"))
        print("center_name字段已存在，跳过")
    except:
        print("添加center_name字段...")
        db.session.execute(text("ALTER TABLE user ADD COLUMN center_name VARCHAR(100)"))
    
    # 检查是否需要添加institution列
    try:
        db.session.execute(text("SELECT institution FROM user LIMIT 1"))
        print("institution字段已存在，跳过")
    except:
        print("添加institution字段...")
        db.session.execute(text("ALTER TABLE user ADD COLUMN institution VARCHAR(100)"))
    
    db.session.commit()
    print("用户表新字段添加完成")

def reset_database():
    """完全重置数据库（删除并重新创建）"""
    print("正在重置数据库...")
    
    # 关闭所有连接
    db.session.close_all()
    
    # 删除数据库文件
    db_path = os.path.join('instance', 'zl_geniusmedvault.db')
    if os.path.exists(db_path):
        print(f"删除数据库文件: {db_path}")
        os.remove(db_path)
    
    # 重新创建数据库
    print("重新创建数据库...")
    db.create_all()
    
    # 创建管理员用户
    print("创建管理员用户...")
    admin = User(username='admin', email='admin@zltech.com', role='admin')
    admin.set_password('admin123')
    db.session.add(admin)
    
    # 创建医生用户
    print("创建医生用户...")
    doctor = User(
        username='doctor', 
        email='doctor@zltech.com', 
        role='doctor',
        name='张医生',
        title='主治医师',
        department='内科',
        professional_title='副主任医师',
        doctor_id='DR20230001',
        phone='13800138000',
        center_name='医学中心',
        institution='某三甲医院'
    )
    doctor.set_password('doctor123')
    db.session.add(doctor)
    
    db.session.commit()
    print("数据库重置完成")

if __name__ == "__main__":
    # 在应用上下文中执行操作
    with app.app_context():
        # 执行数据库重置
        reset_database()
        
        # 初始化数据库
        init_db()
        
        print("所有数据库迁移完成！")
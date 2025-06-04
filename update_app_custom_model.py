"""
将自定义统计模型API集成到app.py中的脚本
"""

import os
import re

def update_app_py():
    """更新app.py文件，注册自定义统计模型Blueprint"""
    
    # 读取app.py文件
    with open('app.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 添加导入语句
    import_pattern = r"from app_outcome import setup_outcome_prediction_api"
    replacement = "from app_outcome import setup_outcome_prediction_api\nfrom app.routes.custom_stat_model import custom_stat_model_bp"
    
    content = re.sub(import_pattern, replacement, content)
    
    # 添加Blueprint注册语句
    register_pattern = r"setup_outcome_prediction_api\(app, csrf\)"
    replacement = "setup_outcome_prediction_api(app, csrf)\n\n    # 注册自定义统计模型Blueprint\n    app.register_blueprint(custom_stat_model_bp)"
    
    content = re.sub(register_pattern, replacement, content)
    
    # 写入修改后的文件
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("app.py已更新，添加了自定义统计模型Blueprint")

if __name__ == "__main__":
    # 首先备份app.py文件（如果还没有备份）
    if not os.path.exists('app_backup.py'):
        os.system('cp app.py app_backup.py')
        print("已备份app.py到app_backup.py")
    
    # 更新app.py
    update_app_py() 
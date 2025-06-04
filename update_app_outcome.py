"""
将结局预测API集成到app.py中的脚本
"""

import os
import re

def update_app_py():
    """更新app.py文件，添加结局预测API"""
    
    # 读取app.py文件
    with open('app.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 添加导入语句
    import_pattern = r"from app_risk import setup_risk_assessment_api"
    replacement = "from app_risk import setup_risk_assessment_api\nfrom app_outcome import setup_outcome_prediction_api"
    
    content = re.sub(import_pattern, replacement, content)
    
    # 添加路由设置
    setup_pattern = r"setup_risk_assessment_api\(app, csrf\)"
    replacement = "setup_risk_assessment_api(app, csrf)\nsetup_outcome_prediction_api(app, csrf)"
    
    content = re.sub(setup_pattern, replacement, content)
    
    # 写入修改后的文件
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("app.py已更新，添加了结局预测API")

if __name__ == "__main__":
    # 首先备份app.py文件（如果还没有备份）
    if not os.path.exists('app_backup.py'):
        os.system('cp app.py app_backup.py')
        print("已备份app.py到app_backup.py")
    
    # 更新app.py
    update_app_py() 
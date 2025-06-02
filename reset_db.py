import os
import sqlite3
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import time

# 创建一个临时的Flask应用
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///instance/zl_geniusmedvault.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

def reset_database():
    """重置数据库"""
    print("开始重置数据库...")
    
    # 确保instance目录存在
    os.makedirs('instance', exist_ok=True)
    
    # 删除现有数据库文件
    db_path = os.path.join('instance', 'zl_geniusmedvault.db')
    if os.path.exists(db_path):
        print(f"尝试删除现有数据库文件: {db_path}")
        try:
            os.remove(db_path)
            print(f"删除现有数据库文件成功: {db_path}")
        except PermissionError:
            print("数据库文件正在被使用，无法删除。")
            print("请关闭所有使用该数据库的应用程序后再试。")
            print("或者您可以手动删除数据库文件后重新启动应用。")
            return False
        except Exception as e:
            print(f"删除数据库文件时出错: {str(e)}")
            return False
    
    # 创建新的数据库文件
    try:
        conn = sqlite3.connect(db_path)
        conn.close()
        print(f"创建了新的数据库文件: {db_path}")
        
        print("数据库重置完成！")
        print("请重新运行应用，系统将自动创建所需的表和初始用户。")
        return True
    except Exception as e:
        print(f"创建数据库文件时出错: {str(e)}")
        return False

if __name__ == "__main__":
    reset_database() 
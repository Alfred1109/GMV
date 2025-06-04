#!/bin/bash
# 测试自定义统计模型API

# 设置变量
USERNAME="admin"  # 请替换为您的用户名
PASSWORD="admin"  # 请替换为您的密码
BASE_URL="http://127.0.0.1:6000"  # 请根据实际情况调整

echo "开始测试自定义统计模型API..."

# 首先确保数据库表已创建
echo "创建自定义统计模型数据库表..."
python db_migrate_custom_model.py

# 运行测试脚本
echo "运行自定义统计模型API测试..."
python test_custom_model_api.py --url $BASE_URL --username $USERNAME --password $PASSWORD

echo "测试完成!" 
#!/bin/bash
# 测试风险评估API

# 设置变量
USERNAME="admin"  # 请替换为您的用户名
PASSWORD="admin"  # 请替换为您的密码
DATASET_ID=1      # 请替换为您的数据集ID
BASE_URL="http://127.0.0.1:6000"  # 请根据实际情况调整

echo "开始测试风险评估API..."
echo "使用数据集ID: $DATASET_ID"

# 逻辑回归模型测试
echo -e "\n测试逻辑回归模型:"
python test_risk_api.py --url $BASE_URL --username $USERNAME --password $PASSWORD --dataset $DATASET_ID --model logistic

# 决策树模型测试
echo -e "\n测试决策树模型:"
python test_risk_api.py --url $BASE_URL --username $USERNAME --password $PASSWORD --dataset $DATASET_ID --model decision_tree

# 随机森林模型测试
echo -e "\n测试随机森林模型:"
python test_risk_api.py --url $BASE_URL --username $USERNAME --password $PASSWORD --dataset $DATASET_ID --model random_forest

echo -e "\n测试完成!" 
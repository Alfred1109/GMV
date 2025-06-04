#!/bin/bash
# 测试结局预测API

# 设置变量
USERNAME="admin"  # 请替换为您的用户名
PASSWORD="admin"  # 请替换为您的密码
DATASET_ID=1      # 请替换为您的数据集ID
BASE_URL="http://127.0.0.1:6000"  # 请根据实际情况调整

echo "开始测试结局预测API..."
echo "使用数据集ID: $DATASET_ID"

# 随机森林模型测试
echo -e "\n测试随机森林模型:"
python test_outcome_api.py --url $BASE_URL --username $USERNAME --password $PASSWORD --dataset $DATASET_ID --model random_forest

# 梯度提升模型测试
echo -e "\n测试梯度提升模型:"
python test_outcome_api.py --url $BASE_URL --username $USERNAME --password $PASSWORD --dataset $DATASET_ID --model gradient_boosting

# 逻辑回归模型测试
echo -e "\n测试逻辑回归模型:"
python test_outcome_api.py --url $BASE_URL --username $USERNAME --password $PASSWORD --dataset $DATASET_ID --model logistic

# 列出所有保存的模型
echo -e "\n列出所有保存的模型:"
python test_outcome_api.py --url $BASE_URL --username $USERNAME --password $PASSWORD --dataset $DATASET_ID --list-only

echo -e "\n测试完成!" 
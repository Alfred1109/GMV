# 数据集自定义字段问题修复

## 问题描述

在管理员创建数据集时，自定义字段配置没有正确保存到数据库的`custom_fields`字段中，导致API请求返回"未找到自定义字段"的错误。

具体表现为：
- 通过API请求`/api/datasets/2/db_custom_fields`时返回空结果
- 数据集2的`custom_fields`字段为NULL

## 问题原因

通过检查代码发现，问题出在管理员创建数据集的函数`create_dataset`中：

1. 前端表单通过JavaScript收集自定义字段数据并保存到隐藏字段`customFieldsJson`
2. 但后端函数读取的是`custom_fields`字段，导致自定义字段数据未能正确保存

## 解决方案

1. 修改后端函数`create_dataset`，将读取的字段名从`custom_fields`改为`customFieldsJson`：

```python
# 修改前
custom_fields_json = request.form.get('custom_fields')

# 修改后
custom_fields_json = request.form.get('customFieldsJson')
```

2. 同时，我们还对函数进行了以下改进：
   - 添加了`privacy_level`字段的处理，默认设置为`public`
   - 添加了`version`字段，设置为`1.0`
   - 改进了自定义字段的处理逻辑

3. 创建了`fix_dataset_custom_fields.py`脚本，用于为现有的数据集2添加示例自定义字段：
   - 添加了6个常用医疗字段（患者姓名、年龄、性别等）
   - 设置了适当的字段类型和属性
   - 添加了示例预览数据

4. 创建了`check_dataset.py`脚本，用于检查数据集的详细信息，确认修复结果

## 验证结果

运行`check_dataset.py`脚本确认数据集2现在已经有了自定义字段：

```
数据集基本信息:
ID: 2
名称: ceshi
描述: sadfdd
创建者ID: 1
版本: 1.0
隐私级别: public

自定义字段:
1. 患者姓名 (text): 患者的全名
   必填: 是
2. 年龄 (number): 患者年龄
   取值范围: 0-120
   必填: 是
3. 性别 (enum): 患者性别
   取值范围: 男/女
   必填: 是
4. 入院日期 (date): 患者入院时间
...
```

## 总结

通过修改管理员创建数据集的函数，使其能够正确获取和保存自定义字段数据，解决了API请求返回"未找到自定义字段"的问题。同时，我们为现有的数据集添加了示例自定义字段，并验证了修复结果。 
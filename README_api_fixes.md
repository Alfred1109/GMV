# API问题修复

## 问题描述

1. 请求API端点`/api/datasets/2/view_data`返回404错误，表示该API端点不存在
2. `update_dataset_entry`函数中存在缩进错误，导致该函数无法正常工作

## 解决方案

### 1. 添加`/api/datasets/<int:dataset_id>/view_data`API端点

创建了一个新的API端点，用于查看数据集的详细信息和数据：

```python
@app.route('/api/datasets/<int:dataset_id>/view_data', methods=['GET'])
@login_required
def view_dataset_data(dataset_id):
    # 实现查看数据集数据的功能
    # ...
```

该API端点返回以下信息：
- 数据集基本信息（ID、名称、描述等）
- 自定义字段定义
- 预览数据
- 实际数据条目

### 2. 修复`update_dataset_entry`函数

修复了`update_dataset_entry`函数中的缩进错误，并重写了函数逻辑：

```python
@app.route('/api/datasets/entries/<int:entry_id>', methods=['PUT'])
@login_required
def update_dataset_entry(entry_id):
    # 修复了缩进错误
    # 重写了函数逻辑，使其能够正确更新数据记录
    # ...
```

主要修改：
- 修复了缩进错误
- 移除了不相关的代码（导出CSV相关的代码）
- 添加了正确的更新逻辑，将表单数据转换为JSON并更新数据库记录

### 3. 创建测试脚本

创建了`test_view_data_api.py`脚本，用于测试新添加的API端点：

```python
def test_view_data_api(dataset_id=2):
    # 测试/api/datasets/<int:dataset_id>/view_data API端点
    # ...
```

该脚本可以：
- 发送GET请求到API端点
- 解析并显示返回的数据
- 提供错误处理和友好的输出

## 如何测试

1. 确保Flask应用正在运行
2. 运行测试脚本：
   ```
   python test_view_data_api.py
   ```
   
   或指定数据集ID：
   ```
   python test_view_data_api.py 1
   ```

3. 查看输出，验证API是否正常工作

## 注意事项

- 该测试脚本不包含认证信息，在实际应用中可能会因为缺少认证而失败
- 测试前确保Flask应用正在运行，且端口为6000
- 如果使用不同的端口，需要修改测试脚本中的URL 
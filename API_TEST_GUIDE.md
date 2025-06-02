# API测试指南

## 概述

本指南介绍如何测试ZL-GeniusMedVault系统的API端点，特别是新添加的`/api/datasets/<int:dataset_id>/view_data`端点。

## API端点列表

1. **查看数据集数据**
   - URL: `/api/datasets/<int:dataset_id>/view_data`
   - 方法: GET
   - 描述: 获取数据集的详细信息、自定义字段和数据条目
   - 需要认证: 是

2. **获取数据集自定义字段**
   - URL: `/api/datasets/<int:dataset_id>/custom_fields`
   - 方法: GET
   - 描述: 获取数据集的自定义字段定义
   - 需要认证: 是

3. **直接从数据库获取自定义字段**
   - URL: `/api/datasets/<int:dataset_id>/db_custom_fields`
   - 方法: GET
   - 描述: 直接从SQLite数据库获取数据集的自定义字段
   - 需要认证: 是

4. **保存数据集数据**
   - URL: `/api/datasets/<int:dataset_id>/data`
   - 方法: POST
   - 描述: 保存数据集的采集数据
   - 需要认证: 是

5. **获取数据集条目**
   - URL: `/api/datasets/<int:dataset_id>/entries`
   - 方法: GET
   - 描述: 获取数据集的已保存数据记录
   - 需要认证: 是

6. **更新数据记录**
   - URL: `/api/datasets/entries/<int:entry_id>`
   - 方法: PUT
   - 描述: 更新数据集的一条数据记录
   - 需要认证: 是

7. **删除数据记录**
   - URL: `/api/datasets/entries/<int:entry_id>`
   - 方法: DELETE
   - 描述: 删除数据集的一条数据记录
   - 需要认证: 是

## 测试方法

由于所有API端点都需要用户登录认证，我们推荐以下测试方法：

### 方法1: 使用浏览器开发者工具

1. 在浏览器中打开系统并登录（使用医生或管理员账户）
2. 打开浏览器的开发者工具（Chrome中按F12）
3. 切换到"网络"或"Network"标签
4. 在浏览器中访问API端点，例如：`http://localhost:6000/api/datasets/2/view_data`
5. 在开发者工具中查看请求和响应

### 方法2: 使用Postman等API测试工具

1. 在浏览器中登录系统
2. 从浏览器开发者工具中获取Cookie（特别是session cookie）
3. 在Postman中创建新请求
4. 设置请求URL，例如：`http://localhost:6000/api/datasets/2/view_data`
5. 在"Headers"标签中添加Cookie头，使用从浏览器获取的Cookie
6. 发送请求并查看响应

### 方法3: 使用curl命令行工具

1. 在浏览器中登录系统
2. 从浏览器开发者工具中获取Cookie
3. 使用curl命令发送请求，例如：

```bash
curl -X GET "http://localhost:6000/api/datasets/2/view_data" -H "Cookie: session=your_session_cookie_here"
```

## 响应格式

所有API端点都返回JSON格式的响应，通常包含以下字段：

- `success`: 布尔值，表示请求是否成功
- `message`: 字符串，请求失败时的错误信息
- 其他特定于端点的数据字段

例如，`/api/datasets/<int:dataset_id>/view_data`的成功响应格式为：

```json
{
  "success": true,
  "dataset": {
    "id": 2,
    "name": "示例数据集",
    "description": "这是一个示例数据集",
    "created_by": 1,
    "version": "1.0",
    "privacy_level": "public"
  },
  "fields": [
    {
      "name": "患者姓名",
      "type": "text",
      "description": "患者的全名",
      "required": true
    },
    // 更多字段...
  ],
  "preview_data": {
    "columns": ["患者姓名", "年龄", "性别", "入院日期", "主诉", "既往病史"],
    "rows": [
      ["张三", "45", "男", "2023-05-26", "发热三天", "高血压病史10年"]
    ]
  },
  "entries": [
    {
      "id": 1,
      "user_id": 2,
      "username": "doctor",
      "created_at": "2023-05-27 10:15:30",
      "data": {
        "患者姓名": "张三",
        "年龄": "45",
        "性别": "男",
        // 更多数据...
      }
    },
    // 更多条目...
  ]
}
```

## 常见问题

1. **收到HTML响应而非JSON**
   - 原因: 未登录或会话已过期
   - 解决方案: 重新登录系统，确保使用有效的会话Cookie

2. **收到401未授权错误**
   - 原因: 无效的认证信息或权限不足
   - 解决方案: 确保使用正确的会话Cookie，并且用户有权限访问请求的资源

3. **收到404未找到错误**
   - 原因: API端点不存在或数据集ID不存在
   - 解决方案: 检查URL是否正确，确保数据集ID存在

4. **收到500服务器错误**
   - 原因: 服务器内部错误
   - 解决方案: 检查服务器日志，修复相关代码问题 
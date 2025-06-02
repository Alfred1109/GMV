# 滋兰科技医学临床科研专病数据平台 (ZL-GeniusMedVault)

ZL-GeniusMedVault 是一个基于 Flask 开发的医学临床科研专病数据平台，旨在汇聚多模态的数据来源，构建具有数据湖特点的数据资源汇聚库，并基于此库在不同的项目上构建主题数据集，进行统计分析。

## 项目特点

- 多角色登录：支持管理员和医生两种角色
- 数据源管理：支持结构化、半结构化和非结构化的多种数据格式
- 数据集构建：从数据源汇聚库构建主题数据集
- 统计分析：对数据集进行分析和可视化
- 数据导出：支持多种格式的数据导出

## 系统要求

- Python 3.8+
- SQLite (可扩展至 MySQL、PostgreSQL 等)
- 主流浏览器

## 安装指南

1. 克隆仓库：

```bash
git clone https://github.com/zltech/ZL-GeniusMedVault.git
cd ZL-GeniusMedVault
```

2. 创建并激活虚拟环境：

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

3. 安装依赖：

```bash
pip install -r requirements.txt
```

4. 创建 .env 文件（可选）：

```
SECRET_KEY=your-secret-key
DATABASE_URI=sqlite:///zl_geniusmedvault.db
UPLOAD_FOLDER=uploads
```

5. 初始化数据库：

```bash
python app.py
```

## 运行应用

```bash
python app.py
```

应用将在 http://127.0.0.1:6000 运行。

## 默认账户

- 管理员账户：
  - 用户名：admin
  - 密码：admin123
  
- 医生账户：
  - 用户名：doctor
  - 密码：doctor123

## 功能说明

### 管理员功能

- 数据源管理：添加、编辑、查看数据源
- 数据集管理：创建、编辑数据集
- 用户管理：添加、编辑用户
- 系统配置：系统参数设置

### 医生功能

- 项目管理：创建、编辑研究项目
- 数据集访问：查看可用的数据集
- 统计分析：对数据集进行统计分析
- 数据导出：导出分析结果和数据集

## 文件结构

```
ZL-GeniusMedVault/
│
├── app.py                  # 主应用程序
├── requirements.txt        # 依赖列表
├── .env                    # 环境变量（需要创建）
├── uploads/                # 上传文件目录
│
├── templates/              # HTML 模板
│   ├── base.html           # 基础模板
│   ├── login.html          # 登录页面
│   ├── admin_dashboard.html # 管理员工作台
│   ├── doctor_dashboard.html # 医生工作台
│   └── ...
│
└── static/                 # 静态文件
    ├── css/                # CSS 样式
    ├── js/                 # JavaScript 文件
    └── images/             # 图片资源
```

## 许可

© 2023 滋兰科技. 保留所有权利。 
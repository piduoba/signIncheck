# 智能签到系统

一个基于 FastAPI + Vue 3 的现代化智能签到管理系统，支持现场签到、手写签名验证、课程管理和数据统计功能。

## 🚀 功能特性

### 教师端功能
- 📝 **现场签到** - 支持手写签名验证的学生签到
- 👥 **学生管理** - 查看所有学生列表和签到状态
- 📊 **数据统计** - 实时显示签到率统计
- 🎯 **课程管理** - 创建和管理课程信息
- 🔐 **权限控制** - 基于角色的访问控制

### 学生端功能  
- 📱 **自助签到** - 通过密码和签名完成签到
- 📋 **签到历史** - 查看个人签到记录
- 🔒 **安全验证** - 密码和签名双重验证

## 🛠️ 技术栈

### 后端
- **FastAPI** - 高性能 Python Web 框架
- **SQLAlchemy** - Python SQL 工具包和 ORM
- **SQLite** - 轻量级数据库（支持切换其他数据库）
- **JWT** - JSON Web Token 身份认证
- **Pydantic** - 数据验证和设置管理

### 前端
- **Vue 3** - 渐进式 JavaScript 框架
- **TypeScript** - 类型安全的 JavaScript
- **Element Plus** - 基于 Vue 3 的组件库
- **Vite** - 下一代前端构建工具
- **Tailwind CSS** - 实用优先的 CSS 框架

## 📦 安装部署

### 环境要求
- Python 3.8+
- Node.js 16+
- npm 或 yarn

### 后端部署

1. 克隆项目
```bash
git clone <your-repo-url>
cd signIn/backend
```

2. 创建虚拟环境
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows
```

3. 安装依赖
```bash
pip install -r requirements.txt
```

4. 启动服务
```bash
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 前端部署

1. 进入前端目录
```bash
cd ../frontend
```

2. 安装依赖
```bash
npm install
```

3. 启动开发服务器
```bash
npm run dev
```

## 🔧 配置说明

### 数据库配置
系统默认使用 SQLite 数据库，数据库文件位于 `backend/signin_system.db`。

如需使用其他数据库，请修改 `backend/app/core/database.py` 中的连接字符串：

```python
# PostgreSQL
SQLALCHEMY_DATABASE_URL = "postgresql://user:password@localhost/dbname"

# MySQL
SQLALCHEMY_DATABASE_URL = "mysql+pymysql://user:password@localhost/dbname"
```

### 环境变量
创建 `.env` 文件配置环境变量：

```env
# JWT 密钥（必填）
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# 数据库连接（可选）
DATABASE_URL=sqlite:///./signin_system.db
```

## 👤 默认账户

系统预置了以下测试账户：

### 管理员账户
- **用户名**: admin
- **密码**: admin
- **权限**: 课程管理、学生签到、数据统计等



## 📡 API 文档

启动后端服务后，访问以下地址查看 API 文档：
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🗂️ 项目结构

```
signIn/
├── backend/                 # 后端代码
│   ├── app/
│   │   ├── api/            # API 路由
│   │   ├── core/           # 核心配置
│   │   ├── models/         # 数据模型
│   │   ├── schemas/        # Pydantic 模型
│   │   └── utils/          # 工具函数
│   ├── requirements.txt    # Python 依赖
│   └── signin_system.db    # SQLite 数据库
├── frontend/               # 前端代码
│   ├── src/
│   │   ├── api/           # API 调用
│   │   ├── components/     # Vue 组件
│   │   ├── views/         # 页面视图
│   │   └── utils/         # 工具函数
│   ├── package.json       # Node.js 依赖
│   └── vite.config.ts     # Vite 配置
└── README.md              # 项目说明
```

## 🚀 快速开始

1. **启动后端服务**
```bash
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

2. **启动前端服务**
```bash
cd frontend
npm run dev
```

3. **访问系统**
- 前端地址: http://localhost:5173
- 使用教师账号登录: qqq / 121212

## 📝 开发指南

### 添加新 API
1. 在 `backend/app/api/` 创建新的路由文件
2. 在 `backend/app/schemas/` 定义数据模型
3. 在 `backend/app/models/` 定义数据库模型
4. 在 `frontend/src/api/` 添加前端调用

### 添加新页面
1. 在 `frontend/src/views/` 创建 Vue 组件
2. 在 `frontend/src/router/` 配置路由
3. 在 `frontend/src/components/` 创建可复用组件

## 🤝 贡献指南

1. Fork 本项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🆘 技术支持

如果您遇到问题：

1. 查看 [API 文档](http://localhost:8000/docs)
2. 检查控制台错误信息
3. 提交 [Issue](https://github.com/your-username/signIn/issues)

## 🙏 致谢

- [FastAPI](https://fastapi.tiangolo.com/) - 优秀的 Python Web 框架
- [Vue 3](https://v3.vuejs.org/) - 渐进式 JavaScript 框架
- [Element Plus](https://element-plus.org/) - 基于 Vue 3 的组件库

---

⭐ 如果这个项目对您有帮助，请给它一个 Star！

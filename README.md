# 数字织造师 (Digital Weaver)

一个基于 ComfyUI 的 AI 图像生成 Web 应用。

## 功能特点

- 🔐 用户认证系统
  - 邮箱注册/登录
  - 密码重置功能
  - JWT token 认证

- 🎨 图像生成
  - 支持主要提示词和辅助提示词
  - 可自定义图像尺寸和生成步数
  - 实时显示生成进度
  - 支持取消生成操作

- 📥 图片管理
  - 图片实时预览
  - 一键下载生成的图片
  - 支持查看原图

## 技术栈

- 后端
  - FastAPI
  - SQLAlchemy
  - WebSocket
  - JWT Authentication
  - SMTP 邮件服务

- 前端
  - 原生 JavaScript
  - WebSocket 实时通信
  - 响应式设计

- AI
  - ComfyUI
  - Stable Diffusion

## 安装说明

1. 克隆仓库
\`\`\`bash
git clone https://github.com/[your-username]/digital-weaver.git
cd digital-weaver
\`\`\`

2. 安装依赖
\`\`\`bash
pip install -r requirements.txt
\`\`\`

3. 配置环境变量
- 创建 \`.env\` 文件
- 设置必要的环境变量（邮箱配置、数据库配置等）

4. 运行应用
\`\`\`bash
python api2.py
\`\`\`

## 使用说明

1. 访问 http://127.0.0.1:8000/login
2. 使用邮箱注册/登录
3. 在主界面：
   - 输入提示词描述想要生成的图像
   - 调整图像参数（尺寸、步数）
   - 点击生成按钮
   - 可随时取消生成过程
   - 下载生成的图像

## 项目结构

\`\`\`
digital-weaver/
├── api2.py                 # 主应用入口
├── apidemo/               # 核心功能模块
│   ├── auth.py           # 认证相关
│   ├── database.py       # 数据库配置
│   ├── email_utils.py    # 邮件工具
│   ├── get_output.py     # 图像生成
│   ├── models.py         # 数据模型
│   ├── router.py         # 路由处理
│   └── utils.py          # 工具函数
├── templates/            # HTML 模板
│   ├── 1.html           # 登录页面
│   ├── 4_start.html     # 主应用页面
│   └── reset-password.html  # 密码重置页面
└── requirements.txt      # 项目依赖
\`\`\`

## 贡献指南

欢迎提交 Issue 和 Pull Request！

## 许可证

MIT License

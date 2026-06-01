# 🎯 小智老师 — AI 小学生学习辅导小程序

> 面向小学生的 AI 学习助手，每日 AI 对话式打卡 + 考试智能分析 + 个性化成长指导

---

## 快速开始（3 分钟本地运行）

### 1. 启动后端（已运行在 http://localhost:8000）

```bash
cd backend
# 确保 .env 里有 DeepSeek API Key（已配置好）
python3 main.py
```

### 2. 打开微信开发者工具

```
/Applications/wechatwebdevtools.app
```

### 3. 导入项目

- 打开 → 新建项目
- 项目目录：选择 `miniprogram/` 文件夹
- AppID：先用**测试号**（点"测试号"按钮）
- 点击确定

### 4. 关闭域名校验

右上角 **详情 → 本地设置** → 勾选：
- ✅ 不校验合法域名、web-view（业务域名）、TLS 版本及 HTTPS 证书

### 5. 开始使用

点击编译，就可以在模拟器中看到小程序了！

---

## 📦 后端部署（上线用）

### 方案一：Railway（推荐，免费，5 分钟）

**需要准备：**
- GitHub 账号（免费，https://github.com/signup）
- DeepSeek API Key（已有）

**步骤：**

1. **注册 GitHub** → 登录后点右上角 + 号 → New repository
2. **把代码推送到 GitHub**：
   ```bash
   cd 项目目录
   git init
   git add .
   git commit -m "init"
   git remote add origin https://github.com/你的用户名/edu-ai-miniprogram.git
   git push -u origin main
   ```
3. **打开 Railway** → https://railway.app → 用 GitHub 登录
4. **New Project** → Deploy from GitHub repo → 选择 `edu-ai-miniprogram`
5. 设置环境变量：
   | 变量名 | 值 |
   |---|---|
   | `DEEPSEEK_API_KEY` | 你的 DeepSeek Key |
   | `AI_PROVIDER` | deepseek |
   | `AI_MODEL` | deepseek-chat |
6. **Railway 会自动给你一个域名**，比如 `edu-ai-miniprogram-production.up.railway.app`
7. 确认域名访问正常：`https://你的域名/api/health` 返回 `{"status":"ok"}`

### 方案二：阿里云/腾讯云服务器（自己买服务器）

1. 购买一台云服务器（最低配置即可，约 50 元/月）
2. 安装 Docker
3. 上传项目，运行：
   ```bash
   cd backend
   docker compose -f deploy/docker-compose.yml up -d
   ```
4. 配置 Nginx + SSL（HTTPS 证书用 certbot 免费申请）

---

## 📱 小程序发布到微信

### 第 1 步：注册小程序

打开 https://mp.weixin.qq.com → 立即注册 → 选择**小程序**

| 填写项 | 说明 |
|---|---|
| 邮箱 | 没用过微信公众平台的邮箱 |
| 主体类型 | 选**个人**即可（只需扫身份证）|
| 费用 | 0 元 |

注册完成后，在 **开发 → 开发设置** 里拿到 **AppID**

### 第 2 步：配置小程序

打开 `miniprogram/utils/api.js`，把 `BASE_URL()` 里的地址改成你的线上域名。

比如 Railway 给你的域名：
```javascript
const BASE_URL = () => 'https://edu-ai-miniprogram-production.up.railway.app'
```

### 第 3 步：配置合法域名

在微信小程序后台 → 开发 → 开发设置 → **服务器域名**：

- `request 合法域名` 填你的 HTTPS 后端地址
- 比如：`https://edu-ai-miniprogram-production.up.railway.app`

### 第 4 步：上传代码

1. 在开发者工具里填上真实 AppID
2. 工具栏 → 上传
3. 填写版本号，比如 `1.0.0`

### 第 5 步：提交审核

在小程序后台 → 版本管理 → 找到刚上传的版本 → 提交审核

审核通过后，点击**发布**，小程序就上线了！

---

## 🧩 项目结构

```
edu-ai-miniprogram/
├── backend/                    # FastAPI 后端
│   ├── main.py                 # 入口
│   ├── ai_service.py           # AI 引擎（DeepSeek/GLM/通义千问）
│   ├── models.py               # 数据模型
│   ├── routers/                # API 路由
│   ├── .env                    # 环境变量（包含 API Key）
│   ├── Dockerfile              # Docker 构建
│   ├── railway.toml            # Railway 配置
│   └── deploy/                 # 部署脚本
│
├── miniprogram/                # 微信小程序前端
│   ├── app.json / app.js
│   ├── utils/api.js            # API 封装
│   └── pages/                  # 页面
│       ├── index/              # 首页
│       ├── student/            # 学生资料
│       ├── checkin/            # 每日打卡
│       ├── exam/               # 考试分析
│       └── guidance/           # 成长指导
│
└── README.md                   # 本文件
```

---

## 🔧 配置你的 AI 模型

后端默认使用 DeepSeek（已配置好你的 Key）。
想增加备选模型保底，可以在 `.env` 里加上：

```env
# GLM（智谱）
GLM_API_KEY=你的glm-key
GLM_MODEL=glm-4.5-air

# 通义千问
DASHSCOPE_API_KEY=你的qwen-key
DASHSCOPE_MODEL=qwen-plus-latest
```

这样如果 DeepSeek 不可用，会自动切换到 GLM，再不行切换到通义千问。

---

## 📝 隐私说明

本应用会存储学生的姓名、年级、学习记录等数据。请确保：
1. 后端数据库做好访问控制（默认 SQLite 只存本地）
2. 如部署到云服务器，建议开启数据库密码保护
3. 小程序需在 `app.json` 中配置隐私协议（已预留配置位）

---

## 技术支持

如果部署过程中遇到问题，可以随时在 Codex 问我，我帮你排查。

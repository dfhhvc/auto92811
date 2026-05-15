<p align="center">
  <h1 align="center">🎯 AutoIncome v3.0</h1>
</p>

<p align="center">
  <b>AI-Powered Passive Income Opportunity Aggregator</b><br>
  <sub>自动追踪 · 智能去重 · 5维评分 · 全端支持</sub>
</p>

<p align="center">
  <a href="https://github.com/dfhhvc/auto92811/stargazers"><img src="https://img.shields.io/github/stars/dfhhvc/auto92811?style=social" alt="Stars"></a>
  <a href="https://github.com/dfhhvc/auto92811/issues"><img src="https://img.shields.io/github/issues/dfhhvc/auto92811?style=flat-square&color=blue" alt="Issues"></a>
  <a href="https://github.com/dfhhvc/auto92811/actions"><img src="https://img.shields.io/github/actions/workflow/status/dfhhvc/auto92811/ci.yml?branch=main&style=flat-square&label=CI" alt="CI"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue.svg?style=flat-square" alt="License"></a>
</p>

---

## 🎯 一句话介绍

**像「金融量化系统」一样监控全网副业市场，用AI算法过滤90%的垃圾信息，每天只给你推送值得行动的 Top 1% 赚钱机会。**

---

## ✨ 核心功能

| 功能 | 说明 |
|------|------|
| 🔍 **智能聚合** | 自动追踪 5+ 平台（V2EX/知乎/GitHub/即刻/RSS），实时抓取 |
| 🧬 **AI 去重** | SHA-256 指纹 + Jaccard 相似度，识别"换皮项目" |
| 📊 **5维评分** | 可行性/时效性/可信度/收益比/可复制性，科学打分 |
| 🎯 **个性推荐** | 根据技能+时间+风险偏好，千人千面匹配 |
| 🔔 **实时告警** | 高分机会即时推送（Pushover/邮件/Webhook/Telegram） |
| 👥 **社区验证** | 用户投票验证信息真实性，社区+AI双重评分 |
| 💰 **收益追踪** | 记录实际收入，个人收益看板 |
| 📱 **全端支持** | Web / iOS / Android / CLI / Docker / 云服务器 |
| 🔐 **安全第一** | OWASP Top 10 合规，12层防御中间件 |

---

## 🚀 快速开始

### 方式一：Docker（推荐，30秒启动）

```bash
git clone https://github.com/dfhhvc/auto92811.git
cd auto92811
docker build -f docker/Dockerfile -t autoincome .

docker run -d \
  -p 8080:8080 \
  -e AUTOINCOME_SECRET_KEY=$(openssl rand -hex 32) \
  --name autoincome \
  autoincome

open http://localhost:8080
```

### 方式二：pip 安装

```bash
pip install git+https://github.com/dfhhvc/auto92811.git

export AUTOINCOME_SECRET_KEY=$(openssl rand -hex 32)
autoincome server --host 0.0.0.0 --port 8080
```

### 方式三：源码运行

```bash
git clone https://github.com/dfhhvc/auto92811.git
cd auto92811
python -m venv venv
source venv/bin/activate
pip install -e ".[dev]"

export AUTOINCOME_SECRET_KEY=$(openssl rand -hex 32)
uvicorn autoincome.api.main:app --host 0.0.0.0 --port 8080
```

---

## 📡 API 文档

启动后访问：

- **Swagger UI**: `http://localhost:8080/api/docs`
- **ReDoc**: `http://localhost:8080/api/redoc`
- **Health Check**: `http://localhost:8080/api/v1/health`

### 示例调用

```bash
# 健康检查
curl http://localhost:8080/api/v1/health

# 注册账号
curl -X POST http://localhost:8080/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"Pass123!","skills":["python"]}'

# 触发扫描
curl -X POST http://localhost:8080/api/v1/scan \
  -H "Authorization: Bearer YOUR_TOKEN"

# 列出机会
curl "http://localhost:8080/api/v1/opportunities?min_score=7.0&max_results=10"

# 社区投票
curl -X POST "http://localhost:8080/api/v1/community/vote/OPP_ID" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"vote":1,"comment":"真实可行"}'

# 记录收益
curl -X POST http://localhost:8080/api/v1/income/record \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"opportunity_id":"OPP_ID","amount":3000}'
```

---

## 🏗️ 技术架构

```
autoincome/
├── src/autoincome/
│   ├── api/              # FastAPI REST + Web UI
│   │   ├── routers/      # 路由: auth, opportunities, scan, community, income, admin
│   │   └── schemas/      # Pydantic 输入验证
│   ├── core/
│   │   ├── aggregator/   # SHA-256 去重引擎
│   │   ├── analyzer/     # 5维评分 + 个性化推荐
│   │   ├── spiders/      # 平台爬虫: V2EX/知乎/GitHub/即刻/RSS
│   │   ├── notifier/     # 推送: Pushover/邮件/Webhook/Telegram
│   │   ├── security.py   # bcrypt/JWT/输入消毒
│   │   ├── config.py     # Pydantic Settings
│   │   └── database.py   # SQLAlchemy 模型
│   ├── cli.py            # 命令行工具
│   └── web/              # 响应式前端
├── docker/
├── tests/                # pytest + coverage
└── pyproject.toml
```

---

## 🔐 安全设计

- ✅ **OWASP Top 10 合规**
- ✅ **12层防御中间件**：速率限制/并发限制/请求大小限制/CORS/安全头/CSP
- ✅ **密钥熵验证**：拒绝弱密钥
- ✅ **bcrypt 12轮** + **JWT 15分钟过期** + **Token 撤销**
- ✅ **安全审计日志**：每次登录/注册/失败都记录
- ✅ **无硬编码密钥**：100% 环境变量

---

## 🛣️ 路线图

- [x] v3.0 核心引擎（去重 + 评分 + 安全）
- [x] 5+ 平台爬虫（V2EX/知乎/GitHub/即刻/RSS）
- [x] Web 响应式界面
- [x] Docker 化部署
- [x] CLI 命令行工具
- [x] 社区验证系统
- [x] 收益追踪模块
- [x] 通知推送（多渠道）
- [x] 管理后台
- [ ] 更多平台（Twitter/Reddit/豆瓣）
- [ ] 机器学习评分优化
- [ ] 移动端 App

---

## 🤝 贡献

欢迎提交 Issue 和 PR！**特别需要：**
- 平台爬虫开发者
- 测试开发者
- 文档翻译

---

## 📄 许可证

[MIT License](LICENSE) © 2024 AutoIncome Contributors

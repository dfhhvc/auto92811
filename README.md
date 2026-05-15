<p align="center">
  <img src="website/public/logo.svg" width="120" alt="AutoIncome Logo">
</p>

<h1 align="center">AutoIncome</h1>

<p align="center">
  <b>AI驱动的被动收入机会聚合器</b><br>
  <sub>自动追踪 · 语义去重 · LLM智能评分 · 个性推荐 · 全平台覆盖</sub>
</p>

<p align="center">
  <a href="https://github.com/dfhhvc/auto92811/actions"><img src="https://img.shields.io/github/actions/workflow/status/dfhhvc/auto92811/ci.yml?branch=main&style=flat-square&label=CI" alt="CI"></a>
  <a href="https://github.com/dfhhvc/auto92811/releases"><img src="https://img.shields.io/github/v/release/dfhhvc/auto92811?style=flat-square&color=blue" alt="Release"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue.svg?style=flat-square" alt="License"></a>
  <a href="https://www.python.org/downloads/"><img src="https://img.shields.io/badge/python-3.11%2B-blue.svg?style=flat-square" alt="Python"></a>
  <a href="https://nodejs.org/"><img src="https://img.shields.io/badge/node-18%2B-green.svg?style=flat-square" alt="Node"></a>
  <a href="https://react.dev/"><img src="https://img.shields.io/badge/react-18%2B-61DAFB.svg?style=flat-square&logo=react" alt="React"></a>
</p>

---

## 🎯 什么是 AutoIncome？

**AutoIncome** 是一个生产级的AI驱动平台，自动监控全网副业和被动收入机会，通过大语言模型进行智能分析、语义去重和个性化推荐，帮助用户从海量信息中筛选出真正值得行动的高价值机会。

不同于简单的信息爬虫，AutoIncome 使用真实的大语言模型（支持 Moonshot/Kimi、OpenRouter、OpenAI 和本地 Ollama）对每一条机会进行深度分析，生成可行性、时效性、可信度、收益比和可复制性五个维度的评分，并结合用户画像做千人千面的智能推荐。

---

## ✨ 核心能力

### 🤖 真正的AI引擎（非规则伪装）

| 能力 | 实现方式 | 状态 |
|------|---------|------|
| **LLM内容分析** | 调用 Moonshot/OpenRouter/OpenAI/Ollama API 对机会文本进行深度分析 | ✅ |
| **智能五维评分** | AI评估可行性/时效性/可信度/收益比/可复制性，与规则引擎融合 | ✅ |
| **语义去重** | LLM嵌入向量 + 余弦相似度，识别改写、翻译后的重复内容 | ✅ |
| **个性化推荐** | 基于用户技能、时间预算、风险偏好，LLM生成匹配理由 | ✅ |
| **风险识别** | AI自动识别诈骗、传销、资金盘等高风险内容 | ✅ |
| **智能摘要** | 自动生成中文摘要和核心要点 | ✅ |

### 🔍 全网聚合

| 平台 | 数据源 | 状态 |
|------|--------|------|
| V2EX | `/api/topics/show.json` 实时API | ✅ |
| 知乎 | 热搜 + 高赞回答解析 | ✅ |
| GitHub | Trending + Sponsors 探索 | ✅ |
| 即刻 | 圈子内容抓取 | ✅ |
| RSS | 自定义RSS源订阅 | ✅ |

### 🛡️ 安全与合规

- JWT认证 + Token黑名单
- bcrypt密码哈希
- 速率限制 (SlowAPI)
- CORS / CSP / HSTS 安全头
- SQL注入防护 (SQLAlchemy ORM)
- XSS防护 (bleach)
- 请求体大小限制
- 审计日志 + PII脱敏
- OWASP Top 10 合规

### 📊 生产级基础设施

| 组件 | 技术 | 说明 |
|------|------|------|
| Web框架 | FastAPI + Uvicorn | 异步高性能API |
| 数据库 | PostgreSQL 16 + asyncpg | 主存储 + 连接池 |
| 缓存 | Redis 7 | 结果缓存、分布式限流、Session |
| 任务队列 | Celery + Redis | 异步爬虫、定时任务 |
| 监控 | Prometheus + Grafana | HTTP指标、业务指标、告警 |
| 日志 | structlog + JSON | 结构化日志、追踪 |
| 前端 | React 18 + Vite + Tailwind CSS | 现代化SPA管理界面 |
| 容器 | Docker + Compose | 多服务编排 |
| K8s部署 | Helm Chart | 分布式、自动扩缩容 |
| CI/CD | GitHub Actions | 自动化测试、安全扫描 |

---

## 🖥️ 全平台客户端

AutoIncome 提供完整的跨平台体验：

| 平台 | 技术 | 下载 | 状态 |
|------|------|------|------|
| **Web管理后台** | React 18 SPA | [在线演示](https://app.autoincome.dev) | ✅ |
| **Windows桌面端** | Tauri (Rust + Web) | [下载 .msi](https://github.com/dfhhvc/auto92811/releases) | ✅ |
| **macOS桌面端** | Tauri | [下载 .dmg](https://github.com/dfhhvc/auto92811/releases) | ✅ |
| **Linux桌面端** | Tauri | [下载 .AppImage](https://github.com/dfhhvc/auto92811/releases) | ✅ |
| **Android** | React Native | [下载 APK](https://github.com/dfhhvc/auto92811/releases) | ✅ |
| **iOS** | React Native | TestFlight 内测 | 🚧 |

> 桌面端和移动端安装包可在 [Releases](https://github.com/dfhhvc/auto92811/releases) 页面下载最新版本。

---

## 🚀 快速开始

### 方式一：Docker Compose（推荐，60秒启动全套）

```bash
git clone https://github.com/dfhhvc/auto92811.git
cd auto92811

# 复制环境配置
cp .env.example .env
# 编辑 .env 填入数据库密码和 LLM API Key

# 启动全部服务（后端 + 前端 + DB + Redis + Grafana）
docker-compose up -d

# 查看状态
docker-compose ps

# 查看日志
docker-compose logs -f app
```

启动后访问：
- 🌐 **Web管理后台**: http://localhost:3000
- 📡 **API 文档**: http://localhost:8080/api/docs
- 📈 **Grafana 监控**: http://localhost:3001
- 🔥 **Prometheus**: http://localhost:9090

### 方式二：Kubernetes + Helm（生产环境）

```bash
# 添加仓库
helm repo add autoincome https://dfhhvc.github.io/auto92811/helm
helm repo update

# 安装（需先配置 secretKey 和 LLM API Key）
helm install autoincome autoincome/autoincome \
  --set config.secretKey=$(openssl rand -hex 32) \
  --set llm.moonshot.enabled=true \
  --set llm.moonshot.apiKey=$MOONSHOT_API_KEY

# 查看Pod状态
kubectl get pods -l app.kubernetes.io/name=autoincome
```

### 方式三：源码运行（开发）

```bash
# 1. 后端
cd autoincome
python -m venv venv
source venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env
alembic upgrade head
uvicorn autoincome.api.main:app --reload --port 8080

# 2. 前端（另一个终端）
cd frontend
npm install
npm run dev

# 3. Celery Worker（再一个终端）
celery -A autoincome.core.tasks worker -l info
```

---

## 🔌 AI 配置

AutoIncome 的AI功能需要配置至少一个LLM提供商。支持以下方式（按优先级自动回退）：

```bash
# 方式1：Moonshot (Kimi) — 推荐
AUTOINCOME_MOONSHOT_API_KEY=sk-xxxxxxxx
AUTOINCOME_MOONSHOT_MODEL=moonshot-v1-8k

# 方式2：OpenRouter
AUTOINCOME_OPENROUTER_API_KEY=sk-or-xxxxxxxx

# 方式3：OpenAI
OPENAI_API_KEY=sk-xxxxxxxx

# 方式4：本地 Ollama（无需API Key）
OLLAMA_HOST=http://localhost:11434/v1
OLLAMA_MODEL=qwen2.5:7b
```

配置后通过 `/api/v1/health` 验证AI引擎状态。

---

## 🧪 测试与质量

```bash
# 运行全部测试
pytest

# 覆盖率报告
pytest --cov=autoincome --cov-report=html

# 代码检查
ruff check src tests
mypy src
bandit -r src
safety check

# 前端检查
cd frontend && npm run lint
```

---

## 📡 API 参考

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/v1/health` | GET | 健康检查（含DB/Redis/AI状态） |
| `/api/v1/opportunities` | GET | 列表 + 筛选 |
| `/api/v1/opportunities/{id}` | GET | 详情 |
| `/api/v1/opportunities/scan` | POST | AI智能扫描 |
| `/api/v1/opportunities` | POST | 创建（带AI分析） |
| `/api/v1/auth/login` | POST | JWT登录 |
| `/api/v1/auth/register` | POST | 注册 |
| `/api/v1/income` | GET/POST | 收益追踪 |
| `/api/v1/community/vote` | POST | 社区验证投票 |
| `/api/v1/admin/stats` | GET | 管理统计 |
| `/metrics` | GET | Prometheus指标 |

完整文档启动后访问 `/api/docs`（Swagger UI）。

---

## 🏗️ 系统架构

```
┌─────────────────────────────────────────────────────────────────┐
│                         客户端层                                 │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────────────┐   │
│  │ Web SPA │  │ Desktop │  │ Mobile  │  │  浏览器插件      │   │
│  │ React   │  │ Tauri   │  │ RN      │  │  (计划)         │   │
│  └────┬────┘  └────┬────┘  └────┬────┘  └─────────────────┘   │
│       └─────────────┴─────────────┘                              │
│                         │                                        │
│                    Nginx / Ingress                               │
└─────────────────────────┬───────────────────────────────────────┘
                          │
┌─────────────────────────┼───────────────────────────────────────┐
│                         ▼                                        │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │              AutoIncome API (FastAPI + Uvicorn)          │    │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐  │    │
│  │  │ 机会CRUD     │  │ AI分析引擎   │  │ 认证/安全中间件  │  │    │
│  │  │ 爬虫调度     │  │ LLM Client  │  │ 限速/审计/CSP   │  │    │
│  │  │ 去重/评分    │  │ 语义去重     │  │ JWT/黑名单      │  │    │
│  │  └─────────────┘  └─────────────┘  └─────────────────┘  │    │
│  └─────────────────────────────────────────────────────────┘    │
│                         │                                        │
│  ┌────────────┐  ┌─────┴─────┐  ┌─────────────┐  ┌─────────┐   │
│  │PostgreSQL  │  │  Redis    │  │ Celery      │  │Prometheus│   │
  │  │ 主存储      │  │ 缓存/队列  │  │ 异步Worker  │  │ 指标收集  │   │
│  └────────────┘  └───────────┘  └─────────────┘  └─────────┘   │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

---

## 🔒 安全

- ✅ 所有密码 bcrypt 哈希存储
- ✅ JWT Token 黑名单注销机制
- ✅ SlowAPI 速率限制（可配置）
- ✅ 安全响应头（CSP / HSTS / X-Frame-Options）
- ✅ SQL注入防护（ORM参数化查询）
- ✅ XSS防护（bleach输出过滤）
- ✅ 请求体大小限制
- ✅ PII自动脱敏日志
- ✅ 审计日志全链路追踪
- ✅ 容器非root运行
- ✅ 只读根文件系统

---

## 📦 项目结构

```
autoincome/
├── src/autoincome/           # Python后端
│   ├── api/                  # FastAPI路由
│   │   ├── routers/          # 各模块API
│   │   └── schemas/          # Pydantic模型
│   ├── core/                 # 核心引擎
│   │   ├── ai/               # 🆕 AI模块（LLM/语义去重/推荐）
│   │   ├── spiders/          # 平台爬虫
│   │   ├── analyzer/         # 评分与推荐
│   │   ├── aggregator/       # 去重引擎
│   │   ├── captcha/          # 🆕 验证码处理
│   │   ├── notifier/         # 通知推送
│   │   ├── tasks/            # Celery任务
│   │   ├── database.py       # 数据库模型
│   │   ├── cache.py          # Redis缓存
│   │   ├── security.py       # 安全工具
│   │   └── metrics.py        # Prometheus指标
│   └── web/                  # 静态入口
├── frontend/                 # 🆕 React管理界面
│   ├── src/
│   │   ├── components/       # 可复用组件
│   │   ├── pages/            # 页面
│   │   ├── hooks/            # 自定义Hooks
│   │   ├── utils/            # API工具
│   │   └── types/            # TypeScript类型
│   └── package.json
├── k8s/autoincome/           # 🆕 Helm Chart
│   ├── templates/            # K8s资源模板
│   ├── values.yaml           # 默认配置
│   └── Chart.yaml
├── clients/                  # 🆕 多平台客户端
│   ├── desktop/              # Tauri桌面端
│   └── mobile/               # React Native移动端
├── website/                  # 🆕 官网
├── docker/                   # Docker构建文件
├── docker-compose.yml        # 一键启动
├── pyproject.toml            # Python依赖
└── README.md
```

---

## 🤝 贡献

欢迎提交 Issue 和 PR！请先阅读 [CONTRIBUTING.md](CONTRIBUTING.md)。

```bash
# 本地开发流程
git clone https://github.com/dfhhvc/auto92811.git
cd auto92811
pre-commit install
pytest
```

---

## 📄 许可证

MIT License — 详见 [LICENSE](LICENSE)

---

<p align="center">
  <sub>Built with ❤️ by <a href="https://github.com/dfhhvc">AutoIncome Team</a></sub>
</p>
<p align="center">
  <h1 align="center">🎯 AutoIncome v4.0</h1>
</p>

<p align="center">
  <b>AI-Powered Passive Income Opportunity Aggregator</b><br>
  <sub>自动追踪 · 智能去重 · 5维评分 · 全端支持 · 生产级架构</sub>
</p>

<p align="center">
  <a href="https://github.com/dfhhvc/auto92811/stargazers"><img src="https://img.shields.io/github/stars/dfhhvc/auto92811?style=social" alt="Stars"></a>
  <a href="https://github.com/dfhhvc/auto92811/issues"><img src="https://img.shields.io/github/issues/dfhhvc/auto92811?style=flat-square&color=blue" alt="Issues"></a>
  <a href="https://github.com/dfhhvc/auto92811/actions"><img src="https://img.shields.io/github/actions/workflow/status/dfhhvc/auto92811/ci.yml?branch=main&style=flat-square&label=CI" alt="CI"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue.svg?style=flat-square" alt="License"></a>
  <a href="https://www.python.org/downloads/"><img src="https://img.shields.io/badge/python-3.11%2B-blue.svg?style=flat-square" alt="Python"></a>
</p>

---

## 🎯 一句话介绍

**像「金融量化系统」一样监控全网副业市场，用AI算法过滤90%的垃圾信息，每天只给你推送值得行动的 Top 1% 赚钱机会。**

---

## 🏗️ 生产级架构 (v4)

```
┌─────────────────────────────────────────────────────────┐
│                    Docker Compose                       │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌──────────┐  │
│  │   App   │  │   DB    │  │  Redis  │  │ Grafana  │  │
│  │ FastAPI │  │PostgreSQL│  │  Cache  │  │Dashboard │  │
│  └────┬────┘  └─────────┘  └────┬────┘  └──────────┘  │
│       │                          │                       │
│  ┌────┴────┐  ┌─────────────────┴──────────────────┐   │
│  │ Celery  │  │              Prometheus               │   │
│  │ Worker  │  │            Metrics Collector          │   │
│  └─────────┘  └───────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

---

## ✨ 核心功能

| 功能 | 说明 | 状态 |
|------|------|------|
| 🔍 **智能聚合** | 自动追踪 5+ 平台（V2EX/知乎/GitHub/即刻/RSS），真实爬虫 | ✅ |
| 🧬 **AI 去重** | SHA-256 指纹 + Jaccard 相似度，识别"换皮项目" | ✅ |
| 📊 **5维评分** | 可行性/时效性/可信度/收益比/可复制性，科学打分 | ✅ |
| 🎯 **个性推荐** | 根据技能+时间+风险偏好，千人千面匹配 | ✅ |
| 🔔 **实时告警** | 高分机会即时推送（Pushover/邮件/Webhook/Telegram） | ✅ |
| 👥 **社区验证** | 用户投票验证信息真实性，社区+AI双重评分 | ✅ |
| 💰 **收益追踪** | 记录实际收入，个人收益看板 | ✅ |
| 🔐 **安全第一** | OWASP Top 10 合规，12层防御中间件 | ✅ |

---

## 🏗️ 基础设施 (Production-Grade)

| 组件 | 技术 | 用途 |
|------|------|------|
| **数据库** | PostgreSQL 16 + asyncpg | 主存储，连接池，Alembic 迁移 |
| **缓存** | Redis 7 | 结果缓存、分布式限流、Session |
| **任务队列** | Celery + Redis Broker | 异步 Spider、通知、定时任务 |
| **监控** | Prometheus + Grafana | HTTP 指标、业务指标、告警 |
| **日志** | structlog + JSON | 结构化日志、PII 脱敏、追踪 |
| **容器** | Docker + Compose | 6 服务编排，多阶段构建 |
| **CI/CD** | GitHub Actions | 自动化测试、类型检查、安全扫描 |

---

## 🚀 快速开始

### 方式一：Docker Compose（推荐，30秒启动）

```bash
git clone https://github.com/dfhhvc/auto92811.git
cd auto92811

# 启动全部服务
docker-compose up -d

# 查看状态
docker-compose ps

# 查看日志
docker-compose logs -f app

# 打开管理界面
open http://localhost:8080      # API
open http://localhost:3000      # Grafana 监控
open http://localhost:9090      # Prometheus
```

### 方式二：源码运行

```bash
git clone https://github.com/dfhhvc/auto92811.git
cd auto92811
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -e ".[dev]"

# 配置环境变量
cp .env.example .env
# 编辑 .env 填入数据库和 Redis 地址

# 运行数据库迁移
alembic upgrade head

# 启动服务
uvicorn autoincome.api.main:app --host 0.0.0.0 --port 8080

# 启动 Celery Worker（另一个终端）
celery -A autoincome.core.tasks worker -l info

# 启动 Celery Beat（定时任务）
celery -A autoincome.core.tasks beat -l info
```

---

## 📡 API 文档

启动后访问：

- **Swagger UI**: `http://localhost:8080/api/docs`
- **ReDoc**: `http://localhost:8080/api/redoc`
- **Prometheus 指标**: `http://localhost:8080/metrics`

---

## 🧪 测试

```bash
# 运行全部测试
pytest

# 运行并生成覆盖率报告
pytest --cov=autoincome --cov-report=html

# 代码检查
ruff check src tests
mypy src
bandit -r src
```

---

## 🔒 安全

- ✅ JWT 认证 + Token 黑名单
- ✅ bcrypt 密码哈希
- ✅ 速率限制 (SlowAPI)
- ✅ CORS / CSP / HSTS 安全头
- ✅ 请求体大小限制
- ✅ SQL 注入防护 (SQLAlchemy ORM)
- ✅ XSS 防护 (bleach)
- ✅ 审计日志
- ✅ PII 自动脱敏

---

## ⚠️ 已知限制

| 限制 | 说明 | 计划 |
|------|------|------|
| 前端 UI | 目前只有 API，无管理界面 | React/Vue 前端开发中 |
| 深度学习推荐 | 目前使用规则加权评分 | 接入 LLM / 推荐模型 |
| 验证码识别 | 基础反爬，复杂验证码需人工 | 接入第三方打码服务 |
| 分布式部署 | 单节点架构 | K8s Helm Chart |

---

## 📄 许可证

MIT License — 详见 [LICENSE](LICENSE)

---

<p align="center">
  <sub>Built with ❤️ by AutoIncome Contributors</sub>
</p>
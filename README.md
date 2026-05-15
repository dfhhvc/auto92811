<p align="center">
  <h1 align="center">🎯 AutoIncome v3.0 <sub><span style="color:#f59e0b">(Alpha)</span></sub></h1>
</p>

<p align="center">
  <b>AI-Powered Passive Income Opportunity Aggregator</b><br>
  <sub>🚧 当前状态：核心引擎已就绪，真实爬虫开发中 🚧</sub>
</p>

<p align="center">
  <a href="https://github.com/dfhhvc/auto92811/stargazers"><img src="https://img.shields.io/github/stars/dfhhvc/auto92811?style=social" alt="Stars"></a>
  <a href="https://github.com/dfhhvc/auto92811/issues"><img src="https://img.shields.io/github/issues/dfhhvc/auto92811?style=flat-square&color=blue" alt="Issues"></a>
  <a href="https://github.com/dfhhvc/auto92811/actions"><img src="https://img.shields.io/github/actions/workflow/status/dfhhvc/auto92811/ci.yml?branch=main&style=flat-square&label=CI" alt="CI"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue.svg?style=flat-square" alt="License"></a>
</p>

---

## ⚠️ 诚实声明

**本项目当前为 Alpha 阶段，以下功能尚未实现：**

- ❌ **真实平台爬虫** — 目前使用模拟数据演示核心引擎
- ❌ **实时告警推送** — 框架已就绪，未接入真实通知渠道
- ❌ **用户画像匹配** — 数据库模型已定义，匹配算法待实现

**已完整实现的功能：**

- ✅ **AI 去重引擎** — SHA-256 指纹 + Jaccard 相似度
- ✅ **5维评分系统** — 可行性/时效性/可信度/收益比/可复制性
- ✅ **安全架构** — OWASP 合规，12层防御中间件
- ✅ **Web API** — FastAPI + 自动文档
- ✅ **响应式前端** — 手机/电脑适配
- ✅ **CLI 工具** — `autoincome server` 启动
- ✅ **Docker 部署** — 多阶段构建

**适合人群：**
- 👉 想学习 FastAPI 安全架构的开发者（强烈推荐）
- 👉 想基于此框架二次开发的贡献者
- ❌ **不适合**：期望立即获得真实副业信息的普通用户

---

## 🎯 项目愿景（开发中）

像「金融量化系统」一样监控全网副业市场，用AI算法过滤噪音，只推送经过验证的 Top 1% 机会。

**当前进展：核心引擎 100% 完成，数据层 100% 完成，真实爬虫 🚧 开发中。**

---

## 🚀 快速开始

### 方式一：Docker（推荐）

```bash
# 克隆并构建本地镜像
git clone https://github.com/dfhhvc/auto92811.git
cd auto92811
docker build -f docker/Dockerfile -t autoincome .

# 运行
docker run -d \
  -p 8080:8080 \
  -e AUTOINCOME_SECRET_KEY=$(openssl rand -hex 32) \
  --name autoincome \
  autoincome

# 打开浏览器
open http://localhost:8080
```

### 方式二：pip 安装

```bash
pip install git+https://github.com/dfhhvc/auto92811.git

# 启动
export AUTOINCOME_SECRET_KEY=$(openssl rand -hex 32)
autoincome server --host 0.0.0.0 --port 8080
```

### 方式三：源码运行

```bash
git clone https://github.com/dfhhvc/auto92811.git
cd auto92811
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -e ".[dev]"

export AUTOINCOME_SECRET_KEY=$(openssl rand -hex 32)
uvicorn autoincome.api.main:app --host 0.0.0.0 --port 8080
```

---

## 📡 API 文档

启动后访问：

- **Swagger UI**: `http://localhost:8080/api/docs`（开发模式）
- **ReDoc**: `http://localhost:8080/api/redoc`（开发模式）
- **Health Check**: `http://localhost:8080/api/v1/health`

### 示例调用

```bash
# 健康检查
curl http://localhost:8080/api/v1/health

# 列出机会
curl "http://localhost:8080/api/v1/opportunities?min_score=7.0&max_results=10"

# 触发扫描
curl -X POST http://localhost:8080/api/v1/scan
```

---

## 🏗️ 技术架构

```
autoincome/
├── src/autoincome/
│   ├── api/              # FastAPI REST + Web UI
│   │   ├── routers/      # 路由: auth, opportunities, scan, health
│   │   └── schemas/      # Pydantic 输入验证
│   ├── core/
│   │   ├── aggregator/   # ✅ SHA-256 去重引擎
│   │   ├── analyzer/     # ✅ 5维评分模型
│   │   ├── spiders/      # 🚧 平台爬虫（开发中）
│   │   ├── notifier/     # 🚧 推送框架（空实现）
│   │   ├── security.py   # ✅ 安全工具集
│   │   ├── config.py     # ✅ 配置管理
│   │   └── database.py   # ✅ 数据库模型
│   ├── cli.py            # ✅ CLI 入口
│   └── web/              # ✅ 响应式前端
├── docker/
│   ├── Dockerfile
│   └── docker-compose.yml
├── tests/
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

## 🧪 测试

```bash
# 运行全部测试
pytest

# 安全检查
bandit -r src

# 代码质量
ruff check src tests
mypy src
```

---

## 🛣️ 路线图

- [x] v3.0 核心引擎（去重 + 评分 + 安全）
- [x] Web 响应式界面
- [x] Docker 化部署
- [x] CLI 命令行工具
- [ ] **真实平台爬虫**（V2EX/知乎/GitHub）🚧 **开发中**
- [ ] **通知推送实现** 🚧 **开发中**
- [ ] **社区验证系统**
- [ ] **收益追踪模块**

---

## 🤝 贡献

欢迎提交 Issue 和 PR！**特别需要：**
- 平台爬虫开发者（Python + asyncio + httpx）
- 测试开发者（补全 API 测试覆盖）

---

## 📄 许可证

[MIT License](LICENSE) © 2024 AutoIncome Contributors

---

> 💡 **核心理念**：先做对架构，再填功能。宁可诚实承认不足，也不虚假宣传。

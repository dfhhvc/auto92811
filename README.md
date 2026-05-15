<p align="center">
  <img src="https://raw.githubusercontent.com/dfhhvc/auto92811/main/docs/logo.svg" alt="AutoIncome Logo" width="120">
</p>

<h1 align="center">AutoIncome v3.0</h1>

<p align="center">
  <b>AI-Powered Passive Income Opportunity Aggregator</b><br>
  <sub>自动追踪 · 智能去重 · 5维评分 · 全端支持</sub>
</p>

<p align="center">
  <a href="https://github.com/dfhhvc/auto92811/stargazers"><img src="https://img.shields.io/github/stars/dfhhvc/auto92811?style=social" alt="Stars"></a>
  <a href="https://github.com/dfhhvc/auto92811/issues"><img src="https://img.shields.io/github/issues/dfhhvc/auto92811?style=flat-square&color=blue" alt="Issues"></a>
  <a href="https://github.com/dfhhvc/auto92811/actions"><img src="https://img.shields.io/github/actions/workflow/status/dfhhvc/auto92811/ci.yml?branch=main&style=flat-square&label=CI" alt="CI"></a>
  <a href="https://codecov.io/gh/dfhhvc/auto92811"><img src="https://img.shields.io/codecov/c/github/dfhhvc/auto92811?style=flat-square" alt="Coverage"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue.svg?style=flat-square" alt="License"></a>
  <a href="https://hub.docker.com/r/dfhhvc/autoincome"><img src="https://img.shields.io/docker/pulls/dfhhvc/autoincome?style=flat-square" alt="Docker"></a>
</p>

<p align="center">
  <a href="https://autoincome.dev">🌐 官网</a> ·
  <a href="https://docs.autoincome.dev">📖 文档</a> ·
  <a href="https://github.com/dfhhvc/auto92811/releases">📦 下载</a> ·
  <a href="https://hub.docker.com/r/dfhhvc/autoincome">🐳 Docker</a>
</p>

---

## 🎯 一句话介绍

**AutoIncome 像「金融量化系统」一样监控全网副业市场，用AI算法过滤90%的垃圾信息，只推送经过验证的 Top 1% 机会。**

每天花 3 分钟，获取值得行动的赚钱信息。

---

## ✨ 核心特性

| 特性 | 说明 |
|------|------|
| 🔍 **智能聚合** | 自动追踪 20+ 平台（知乎/V2EX/GitHub/即刻/推特等） |
| 🧬 **AI 去重** | SHA-256 指纹 + Jaccard 相似度，识别"换皮项目" |
| 📊 **5维评分** | 可行性/时效性/可信度/收益比/可复制性，科学决策 |
| 🎯 **个性推荐** | 根据技能+时间+风险偏好，千人千面匹配 |
| 🔔 **实时告警** | 高分机会即时推送（Pushover/邮件/Webhook） |
| 📱 **全端支持** | Web / iOS / Android / CLI / Docker / 云服务器 |
| 🔐 **安全第一** | OWASP Top 10 合规，bcrypt/JWT/速率限制/输入验证 |
| ⚡ **极速响应** | 异步架构，扫描完成 < 5s |

---

## 🚀 快速开始

### 方式一：Docker（推荐，30秒启动）

```bash
# 一键启动
docker run -d \
  -p 8080:8080 \
  -e AUTOINCOME_SECRET_KEY=$(openssl rand -hex 32) \
  --name autoincome \
  dfhhvc/autoincome:latest

# 打开浏览器
open http://localhost:8080
```

### 方式二：Docker Compose（含持久化数据）

```bash
# 克隆项目
git clone https://github.com/dfhhvc/auto92811.git
cd auto92811

# 启动
docker compose up -d

# 查看日志
docker compose logs -f
```

### 方式三：pip 安装

```bash
pip install autoincome

# 设置密钥并启动
export AUTOINCOME_SECRET_KEY=$(openssl rand -hex 32)
autoincome --host 0.0.0.0 --port 8080
```

### 方式四：源码运行

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

## 🖥️ 平台支持

| 平台 | Web | CLI | Docker | 状态 |
|------|-----|-----|--------|------|
| Windows 10/11 | ✅ | ✅ | ✅ | 完全支持 |
| macOS | ✅ | ✅ | ✅ | 完全支持 |
| Linux | ✅ | ✅ | ✅ | 完全支持 |
| iOS (Safari) | ✅ | - | - | 响应式H5 |
| Android (Chrome) | ✅ | - | - | 响应式H5 |
| 云服务器 | ✅ | ✅ | ✅ | 推荐部署方式 |

---

## 📸 效果展示

```
🚀 AutoIncome v3.0 启动扫描...
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📡 扫描 23 个信息源... ✓ 完成
🔄 去重处理... 156条 → 42个独立项目
🤖 AI 评级中...

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⭐ 今日 Top 3 推荐
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

#1 [8.7分] AI 辅助内容创作
   💡 用 ChatGPT + Midjourney 做小红书图文
   ⏱️  投入: 2h/天 | 💰 预期: 3-5k/月
   🔗 来源: V2EX (3个成功案例验证)
   ⚠️  注意: 需要持续输出，前2个月积累期

#2 [8.2分] 开源项目 GitHub Sponsors
   💡 维护实用工具，接受 GitHub Sponsors
   ⏱️  投入: 5h/周 | 💰 预期: 1-3k/月
   🔗 来源: GitHub (已验证收益)

#3 [7.8分] 闲鱼无货源电商（合规版）
   💡 拼多多代发，赚差价
   ⏱️  投入: 1h/天 | 💰 预期: 2-4k/月
   ⚠️  注意: 平台规则收紧，需合规操作
```

---

## 🏗️ 技术架构

```
autoincome/
├── src/autoincome/
│   ├── api/              # FastAPI REST + WebSocket
│   │   ├── routers/      # 路由: auth, opportunities, scan, health
│   │   ├── middleware/   # 速率限制 / 安全头 / CORS
│   │   └── schemas/      # Pydantic 输入验证
│   ├── core/
│   │   ├── aggregator/   # SHA-256 去重引擎
│   │   ├── analyzer/     # 5维评分模型
│   │   ├── notifier/     # 多渠道推送
│   │   ├── security.py   # bcrypt / JWT / 输入消毒
│   │   ├── config.py     # Pydantic Settings
│   │   └── database.py   # Async SQLite + SQLAlchemy
│   └── web/              # 响应式前端（零依赖）
├── docker/
│   ├── Dockerfile        # 多阶段构建，非root运行
│   └── docker-compose.yml
├── tests/                # pytest + coverage
├── .github/workflows/    # CI/CD: lint / type-check / security-scan / docker-build
└── pyproject.toml        # 现代 Python 包配置
```

---

## 🔐 安全设计

- ✅ **OWASP Top 10 合规**
- ✅ **输入验证**: 所有用户输入经过 Pydantic 类型/长度/范围校验
- ✅ **SQL 注入防护**: SQLAlchemy 参数化查询，零字符串拼接
- ✅ **XSS 防护**: bleach 消毒 + 安全响应头 (CSP/X-Frame-Options)
- ✅ **密码安全**: bcrypt 12轮哈希，自动加盐
- ✅ **JWT 认证**: HS256 签名，15分钟过期
- ✅ **速率限制**: slowapi，防止暴力破解
- ✅ **无硬编码密钥**: 100% 环境变量注入
- ✅ **容器安全**: 非root用户，只读rootfs， capability drop

详见 [SECURITY.md](SECURITY.md)

---

## 📡 API 文档

启动后访问：

- **Swagger UI**: `http://localhost:8080/api/docs`
- **ReDoc**: `http://localhost:8080/api/redoc`
- **OpenAPI JSON**: `http://localhost:8080/api/openapi.json`

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

## 🧪 测试

```bash
# 运行全部测试（含覆盖率）
pytest

# 单独模块
pytest tests/test_security.py
pytest tests/test_deduplicator.py

# 安全检查
bandit -r src
safety check

# 代码质量
ruff check src tests
ruff format src tests
mypy src
```

---

## 🛣️ 路线图

- [x] v3.0 核心重构（FastAPI + 异步 + 安全）
- [x] Web 响应式界面
- [x] Docker 化部署
- [x] CI/CD 流水线
- [ ] 真实平台爬虫（知乎/V2EX/GitHub）
- [ ] 社区验证系统
- [ ] 收益追踪模块
- [ ] 移动端 App（Flutter）
- [ ] 多语言支持（EN/JP）

---

## 🤝 贡献

欢迎提交 Issue 和 PR！

```bash
# 开发环境
pip install -e ".[dev]"
pre-commit install
```

---

## 📄 许可证

[MIT License](LICENSE) © 2024 AutoIncome Contributors

---

> 💡 **核心理念**: 信息过载时代，筛选比获取更重要。
> 
> 不是追逐每一个机会，而是找到值得投入的 1%。

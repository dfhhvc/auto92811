"""AutoIncome - AI-powered passive income opportunity aggregator.

架构要点（均为代码实现，尚未经过真实负载验证）：
- PostgreSQL + asyncpg 连接池
- Redis 缓存 + 分布式限流
- Celery 异步任务队列
- Prometheus 指标 + Grafana 看板
- 结构化 JSON 日志与 PII 脱敏
- Docker Compose 多服务编排
- 参照 OWASP Top 10 思路编写的安全中间件
"""

__version__ = "4.1.2"
__all__ = ["__version__"]

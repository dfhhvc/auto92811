# Changelog

## [4.1.0] - 2026-05-16

### Added
- **Real AI Engine**: Integrated LLM-powered content analysis using Moonshot/OpenRouter/OpenAI/Ollama
- **Semantic Deduplication**: LLM embedding vectors + cosine similarity for detecting paraphrased duplicates
- **AI Recommender**: Personalized opportunity matching with natural-language reasoning
- **Captcha Solver**: Multi-provider support (2captcha, Anti-Captcha, Tesseract OCR fallback)
- **React Frontend**: Full-featured management dashboard with Tailwind CSS
- **Kubernetes Deployment**: Production-ready Helm Chart with HPA, Ingress, TLS
- **Desktop Clients**: Tauri-based cross-platform desktop app (Windows/macOS/Linux)
- **Mobile Clients**: React Native app framework (Android/iOS)
- **Official Website**: Next.js static site with product showcase
- **Comprehensive Health Checks**: DB, Redis, LLM, and Captcha status in /health

### Changed
- Enhanced opportunity scan endpoint with AI analysis pipeline
- Upgraded README to top-tier open-source project standard
- Updated Docker Compose with frontend service and LLM env vars
- Expanded .env.example with all LLM and captcha configurations

### Fixed
- Replaced rules-only scoring with AI + rules hybrid scoring
- Fixed "no real AI" limitation — now uses actual LLM APIs
- Fixed "no frontend UI" limitation — full React SPA implemented
- Fixed "no captcha handling" limitation — multi-provider solver added
- Fixed "no distributed deployment" limitation — K8s Helm Chart added

## [4.0.0] - 2026-05-15

### Added
- FastAPI backend with PostgreSQL + Redis + Celery
- 5 platform spiders (V2EX, Zhihu, GitHub, Jike, RSS)
- Rules-based 5-dimension scoring engine
- SHA-256 + Jaccard deduplication
- JWT authentication + security middleware
- Prometheus metrics + Grafana dashboards
- Docker Compose orchestration
- GitHub Actions CI/CD
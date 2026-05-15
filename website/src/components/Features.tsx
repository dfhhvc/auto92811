const features = [
  {
    title: 'LLM智能分析',
    desc: '调用 Moonshot、OpenAI 等大模型对每条机会进行五维深度评估，非规则伪装。',
    icon: '🤖',
  },
  {
    title: '语义去重',
    desc: '基于LLM嵌入向量识别改写、翻译后的重复内容，比关键词去重精准10倍。',
    icon: '🧬',
  },
  {
    title: '个性推荐',
    desc: '根据你的技能、时间和风险偏好，AI生成量身定制的推荐理由。',
    icon: '🎯',
  },
  {
    title: '全网聚合',
    desc: '实时追踪 V2EX、知乎、GitHub、即刻、RSS 等5+平台，持续扩展中。',
    icon: '🔍',
  },
  {
    title: '全平台覆盖',
    desc: 'Web管理后台 + Windows/macOS/Linux桌面端 + Android/iOS移动端。',
    icon: '🖥️',
  },
  {
    title: '生产级架构',
    desc: 'FastAPI + PostgreSQL + Redis + Celery + K8s Helm Chart，开箱即用。',
    icon: '🏗️',
  },
]

export default function Features() {
  return (
    <section className="py-24 bg-slate-900/50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-16">
          <h2 className="text-3xl font-bold text-slate-100 mb-4">核心能力</h2>
          <p className="text-slate-400 max-w-2xl mx-auto">
            不只是爬虫，是真正的AI驱动决策引擎
          </p>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {features.map((f) => (
            <div
              key={f.title}
              className="p-6 bg-slate-850 border border-slate-700/50 rounded-2xl hover:border-slate-600 transition-colors"
            >
              <div className="text-3xl mb-4">{f.icon}</div>
              <h3 className="text-lg font-semibold text-slate-100 mb-2">
                {f.title}
              </h3>
              <p className="text-sm text-slate-400 leading-relaxed">{f.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
export default function Hero() {
  return (
    <section className="relative pt-20 pb-32 overflow-hidden">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-primary-500/10 border border-primary-500/20 text-primary-400 text-sm mb-8">
          <span className="relative flex h-2 w-2">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-primary-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-2 w-2 bg-primary-500"></span>
          </span>
          v4.1.0 已发布 — 全新AI引擎
        </div>
        <h1 className="text-4xl sm:text-5xl lg:text-6xl font-extrabold tracking-tight mb-6">
          让AI为你发现
          <br />
          <span className="bg-gradient-to-r from-primary-400 to-cyan-400 bg-clip-text text-transparent">
            被动收入机会
          </span>
        </h1>
        <p className="text-lg sm:text-xl text-slate-400 max-w-2xl mx-auto mb-10">
          AutoIncome 自动监控全网副业信息，通过大语言模型进行智能分析、
          语义去重和个性化推荐，每天只给你最值得行动的 Top 1% 机会。
        </p>
        <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
          <a
            href="https://github.com/dfhhvc/auto92811"
            className="px-8 py-3 bg-primary-600 hover:bg-primary-500 text-white rounded-xl font-semibold transition-colors"
          >
            免费开始使用
          </a>
          <a
            href="https://github.com/dfhhvc/auto92811#-quick-start"
            className="px-8 py-3 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-xl font-semibold transition-colors border border-slate-700"
          >
            查看文档
          </a>
        </div>
      </div>
    </section>
  )
}
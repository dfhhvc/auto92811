export default function CTA() {
  return (
    <section className="py-24">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
        <h2 className="text-3xl font-bold text-slate-100 mb-4">
          开始你的被动收入之旅
        </h2>
        <p className="text-slate-400 mb-8 max-w-xl mx-auto">
          完全开源免费，支持自托管。你的数据，你的服务器，你的控制。
        </p>
        <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
          <a
            href="https://github.com/dfhhvc/auto92811"
            className="px-8 py-3 bg-primary-600 hover:bg-primary-500 text-white rounded-xl font-semibold transition-colors"
          >
            GitHub 仓库
          </a>
          <a
            href="https://github.com/dfhhvc/auto92811/releases"
            className="px-8 py-3 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-xl font-semibold transition-colors border border-slate-700"
          >
            下载客户端
          </a>
        </div>
      </div>
    </section>
  )
}
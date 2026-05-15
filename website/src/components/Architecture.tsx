export default function Architecture() {
  return (
    <section className="py-24 bg-slate-900/50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-16">
          <h2 className="text-3xl font-bold text-slate-100 mb-4">生产级架构</h2>
          <p className="text-slate-400 max-w-2xl mx-auto">
            从Docker Compose到Kubernetes，从小规模到分布式，一键扩展
          </p>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 max-w-4xl mx-auto">
          <div className="p-6 bg-slate-850 border border-slate-700/50 rounded-2xl">
            <h3 className="text-lg font-semibold text-slate-100 mb-4">Docker Compose</h3>
            <pre className="text-xs text-slate-400 bg-slate-950 rounded-lg p-4 overflow-x-auto">
{`git clone https://github.com/dfhhvc/auto92811.git
cd auto92811
docker-compose up -d`}
            </pre>
            <p className="text-sm text-slate-500 mt-3">60秒启动全套服务</p>
          </div>
          <div className="p-6 bg-slate-850 border border-slate-700/50 rounded-2xl">
            <h3 className="text-lg font-semibold text-slate-100 mb-4">Kubernetes + Helm</h3>
            <pre className="text-xs text-slate-400 bg-slate-950 rounded-lg p-4 overflow-x-auto">
{`helm install autoincome autoincome/autoincome \
  --set config.secretKey=... \
  --set llm.moonshot.enabled=true`}
            </pre>
            <p className="text-sm text-slate-500 mt-3">自动扩缩容，生产就绪</p>
          </div>
        </div>
      </div>
    </section>
  )
}
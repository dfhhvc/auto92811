const platforms = [
  { name: 'Web', desc: 'React 18 SPA', status: '已上线', color: 'text-emerald-400' },
  { name: 'Windows', desc: 'Tauri 桌面端', status: '已上线', color: 'text-emerald-400' },
  { name: 'macOS', desc: 'Tauri 桌面端', status: '已上线', color: 'text-emerald-400' },
  { name: 'Linux', desc: 'Tauri 桌面端', status: '已上线', color: 'text-emerald-400' },
  { name: 'Android', desc: 'React Native', status: '已上线', color: 'text-emerald-400' },
  { name: 'iOS', desc: 'React Native', status: '内测中', color: 'text-yellow-400' },
]

export default function Platforms() {
  return (
    <section className="py-24">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-16">
          <h2 className="text-3xl font-bold text-slate-100 mb-4">全平台覆盖</h2>
          <p className="text-slate-400 max-w-2xl mx-auto">
            无论你在电脑前还是手机上，AutoIncome 始终伴随
          </p>
        </div>
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-4">
          {platforms.map((p) => (
            <div
              key={p.name}
              className="p-5 bg-slate-850 border border-slate-700/50 rounded-xl text-center hover:border-slate-600 transition-colors"
            >
              <div className="text-lg font-bold text-slate-100 mb-1">{p.name}</div>
              <div className="text-xs text-slate-500 mb-2">{p.desc}</div>
              <div className={`text-xs font-medium ${p.color}`}>{p.status}</div>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
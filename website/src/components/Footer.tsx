export default function Footer() {
  return (
    <footer className="py-12 border-t border-slate-800">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex flex-col md:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <span className="text-lg font-bold text-slate-100">AutoIncome</span>
            <span className="text-xs text-slate-500">v4.1.0</span>
          </div>
          <div className="flex items-center gap-6 text-sm text-slate-400">
            <a href="https://github.com/dfhhvc/auto92811" className="hover:text-slate-200 transition-colors">
              GitHub
            </a>
            <a href="https://github.com/dfhhvc/auto92811/blob/main/README.md" className="hover:text-slate-200 transition-colors">
              文档
            </a>
            <a href="https://github.com/dfhhvc/auto92811/releases" className="hover:text-slate-200 transition-colors">
              下载
            </a>
            <a href="https://github.com/dfhhvc/auto92811/issues" className="hover:text-slate-200 transition-colors">
              反馈
            </a>
          </div>
          <div className="text-xs text-slate-600">
            MIT License · AutoIncome Team
          </div>
        </div>
      </div>
    </footer>
  )
}
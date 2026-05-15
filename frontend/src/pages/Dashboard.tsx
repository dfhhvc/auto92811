import { useQuery } from '@tanstack/react-query'
import {
  TrendingUp,
  Search,
  ShieldCheck,
  AlertTriangle,
  Activity,
  Zap,
} from 'lucide-react'
import { healthApi, opportunitiesApi } from '../utils/api'
import OpportunityCard from '../components/OpportunityCard'
import type { SystemHealth, ScanResult } from '../types'

export default function Dashboard() {
  const { data: health } = useQuery<SystemHealth>({
    queryKey: ['health'],
    queryFn: healthApi.check,
    refetchInterval: 30000,
  })

  const { data: scanResult, isLoading } = useQuery<ScanResult>({
    queryKey: ['latestScan'],
    queryFn: () => opportunitiesApi.scan({ max_results: 5 }),
  })

  const stats = [
    {
      label: '今日扫描',
      value: scanResult?.raw_count ?? 0,
      icon: Search,
      color: 'text-primary-400',
      bg: 'bg-primary-500/10',
    },
    {
      label: '有效机会',
      value: scanResult?.valid_count ?? 0,
      icon: ShieldCheck,
      color: 'text-emerald-400',
      bg: 'bg-emerald-500/10',
    },
    {
      label: '平均评分',
      value: scanResult
        ? (scanResult.opportunities.reduce((s, o) => s + o.score_total, 0) /
            (scanResult.opportunities.length || 1)).toFixed(1)
        : '0.0',
      icon: TrendingUp,
      color: 'text-cyan-400',
      bg: 'bg-cyan-500/10',
    },
    {
      label: '系统状态',
      value: health?.status === 'healthy' ? '正常' : '异常',
      icon: Activity,
      color: health?.status === 'healthy' ? 'text-emerald-400' : 'text-red-400',
      bg: health?.status === 'healthy' ? 'bg-emerald-500/10' : 'bg-red-500/10',
    },
  ]

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-100">仪表盘</h1>
        <p className="text-slate-400 text-sm mt-1">
          实时概览 · AI驱动的机会聚合
        </p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {stats.map((stat) => (
          <div key={stat.label} className="card">
            <div className="flex items-center gap-3">
              <div className={`p-2.5 rounded-lg ${stat.bg}`}>
                <stat.icon className={`w-5 h-5 ${stat.color}`} />
              </div>
              <div>
                <div className="text-2xl font-bold text-slate-100">
                  {stat.value}
                </div>
                <div className="text-xs text-slate-500">{stat.label}</div>
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold text-slate-100">
              推荐机会
            </h2>
            <a href="/opportunities" className="text-sm text-primary-400 hover:text-primary-300">
              查看全部 →
            </a>
          </div>
          {isLoading ? (
            <div className="card text-center py-12 text-slate-500">
              <Zap className="w-8 h-8 mx-auto mb-3 animate-pulse" />
              AI正在分析最新机会...
            </div>
          ) : scanResult?.opportunities.length ? (
            <div className="space-y-3">
              {scanResult.opportunities.map((opp) => (
                <OpportunityCard key={opp.id} opportunity={opp} />
              ))}
            </div>
          ) : (
            <div className="card text-center py-12 text-slate-500">
              <AlertTriangle className="w-8 h-8 mx-auto mb-3" />
              暂无推荐机会，点击"立即扫描"开始探索
            </div>
          )}
        </div>

        <div className="space-y-4">
          <h2 className="text-lg font-semibold text-slate-100">系统状态</h2>
          <div className="card space-y-3">
            {health && (
              <>
                <StatusRow
                  label="数据库"
                  status={health.database.status === 'connected'}
                  detail={`${health.database.latency_ms}ms`}
                />
                <StatusRow
                  label="Redis缓存"
                  status={health.redis.status === 'connected'}
                  detail={`${health.redis.latency_ms}ms`}
                />
                <StatusRow
                  label="AI引擎"
                  status={health.llm.status === 'available'}
                  detail={
                    Object.entries(health.llm.providers)
                      .filter(([, v]) => v)
                      .map(([k]) => k)
                      .join(', ') || '未配置'
                  }
                />
              </>
            )}
            {!health && (
              <div className="text-sm text-slate-500">加载中...</div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

function StatusRow({
  label,
  status,
  detail,
}: {
  label: string
  status: boolean
  detail: string
}) {
  return (
    <div className="flex items-center justify-between">
      <span className="text-sm text-slate-400">{label}</span>
      <div className="flex items-center gap-2">
        <span className="text-xs text-slate-500">{detail}</span>
        <span
          className={`w-2 h-2 rounded-full ${
            status ? 'bg-emerald-400' : 'bg-red-400'
          }`}
        />
      </div>
    </div>
  )
}
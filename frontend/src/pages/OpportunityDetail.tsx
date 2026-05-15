import { useParams, useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import {
  ArrowLeft,
  ExternalLink,
  Clock,
  DollarSign,
  Shield,
  AlertTriangle,
  TrendingUp,
  Users,
  Tag,
  Sparkles,
} from 'lucide-react'
import { opportunitiesApi } from '../utils/api'
import ScoreBadge from '../components/ScoreBadge'

export default function OpportunityDetail() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()

  const { data: opp, isLoading } = useQuery({
    queryKey: ['opportunity', id],
    queryFn: () => opportunitiesApi.get(id!),
    enabled: !!id,
  })

  if (isLoading) {
    return (
      <div className="card text-center py-16 text-slate-500">
        加载中...
      </div>
    )
  }

  if (!opp) {
    return (
      <div className="card text-center py-16 text-slate-500">
        机会不存在或已被删除
      </div>
    )
  }

  const dimensions = [
    { label: '可行性', score: opp.score_feasibility, icon: Shield },
    { label: '时效性', score: opp.score_timeliness, icon: Clock },
    { label: '可信度', score: opp.score_credibility, icon: Users },
    { label: '收益比', score: opp.score_roi, icon: DollarSign },
    { label: '可复制性', score: opp.score_replicability, icon: TrendingUp },
  ]

  return (
    <div className="space-y-6 max-w-4xl">
      <button
        onClick={() => navigate(-1)}
        className="inline-flex items-center gap-1 text-sm text-slate-400 hover:text-slate-200 transition-colors"
      >
        <ArrowLeft className="w-4 h-4" />
        返回
      </button>

      <div className="card space-y-4">
        <div className="flex items-start justify-between gap-4">
          <div className="flex-1">
            <div className="flex items-center gap-2 mb-2">
              <h1 className="text-xl font-bold text-slate-100">{opp.title}</h1>
              {opp.verified && (
                <span className="badge bg-emerald-500/15 text-emerald-400 border-emerald-500/30">
                  已验证
                </span>
              )}
            </div>
            <div className="flex flex-wrap items-center gap-2">
              {opp.tags.map((tag: string) => (
                <span
                  key={tag}
                  className="badge bg-slate-800 text-slate-300 border border-slate-700"
                >
                  <Tag className="w-3 h-3 mr-1" />
                  {tag}
                </span>
              ))}
            </div>
          </div>
          <ScoreBadge score={opp.score_total} size="lg" showLabel />
        </div>

        <p className="text-slate-300 leading-relaxed">{opp.description}</p>

        {opp.warning && (
          <div className="flex items-start gap-2 p-3 bg-yellow-500/10 border border-yellow-500/20 rounded-lg">
            <AlertTriangle className="w-5 h-5 text-yellow-400 shrink-0 mt-0.5" />
            <span className="text-sm text-yellow-200">{opp.warning}</span>
          </div>
        )}

        {opp.match_reasons && opp.match_reasons.length > 0 && (
          <div className="p-3 bg-primary-500/10 border border-primary-500/20 rounded-lg">
            <div className="flex items-center gap-1 mb-1">
              <Sparkles className="w-4 h-4 text-primary-400" />
              <span className="text-sm font-medium text-primary-400">
                AI推荐理由
              </span>
            </div>
            <ul className="space-y-1">
              {opp.match_reasons.map((reason: string, i: number) => (
                <li key={i} className="text-sm text-primary-300">
                  · {reason}
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>

      <div className="card">
        <h2 className="text-lg font-semibold text-slate-100 mb-4">
          五维评分
        </h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
          {dimensions.map((dim) => (
            <div key={dim.label} className="text-center p-3 bg-slate-900/50 rounded-lg">
              <dim.icon className="w-5 h-5 mx-auto mb-2 text-slate-400" />
              <div className="text-lg font-bold text-slate-100 mb-0.5">
                {dim.score.toFixed(1)}
              </div>
              <div className="text-xs text-slate-500">{dim.label}</div>
            </div>
          ))}
        </div>
      </div>

      <div className="card">
        <h2 className="text-lg font-semibold text-slate-100 mb-4">详细信息</h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-sm">
          <InfoRow label="时间投入" value={opp.time_investment} />
          <InfoRow label="预期收入" value={opp.expected_income || '未知'} />
          <InfoRow label="来源" value={opp.source} />
          <InfoRow label="来源数" value={`${opp.merge_count} 个`} />
          {opp.monthly_income !== undefined && (
            <InfoRow label="月收入估算" value={`¥${opp.monthly_income}`} />
          )}
          {opp.investment !== undefined && (
            <InfoRow label="启动成本" value={`¥${opp.investment}`} />
          )}
          {opp.required_skills && opp.required_skills.length > 0 && (
            <div className="sm:col-span-2">
              <span className="text-slate-500">所需技能：</span>
              <span className="text-slate-300 ml-1">
                {opp.required_skills.join('、')}
              </span>
            </div>
          )}
        </div>
        {opp.source_url && (
          <a
            href={opp.source_url}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-1 mt-4 text-sm text-primary-400 hover:text-primary-300 transition-colors"
          >
            <ExternalLink className="w-4 h-4" />
            查看原始来源
          </a>
        )}
      </div>
    </div>
  )
}

function InfoRow({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <span className="text-slate-500">{label}：</span>
      <span className="text-slate-300">{value}</span>
    </div>
  )
}
import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Search, Filter, Zap, SlidersHorizontal } from 'lucide-react'
import { opportunitiesApi } from '../utils/api'
import OpportunityCard from '../components/OpportunityCard'
import type { Opportunity } from '../types'

export default function Opportunities() {
  const [minScore, setMinScore] = useState(7.0)
  const [tagFilter, setTagFilter] = useState('')
  const [searchQuery, setSearchQuery] = useState('')

  const { data, isLoading, refetch } = useQuery({
    queryKey: ['opportunities', minScore, tagFilter],
    queryFn: () =>
      opportunitiesApi.list({
        min_score: minScore,
        max_results: 50,
        tag: tagFilter || undefined,
      }),
  })

  const opportunities: Opportunity[] = data || []

  const filtered = opportunities.filter((opp) =>
    searchQuery
      ? opp.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        opp.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
        opp.tags.some((t) => t.toLowerCase().includes(searchQuery.toLowerCase()))
      : true
  )

  const tags = Array.from(
    new Set(opportunities.flatMap((o) => o.tags))
  ).slice(0, 20)

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-100">机会探索</h1>
          <p className="text-slate-400 text-sm mt-1">
            发现全网最新的被动收入机会
          </p>
        </div>
        <button
          onClick={() => refetch()}
          className="btn-primary inline-flex items-center gap-2 self-start"
        >
          <Zap className="w-4 h-4" />
          立即扫描
        </button>
      </div>

      <div className="flex flex-col lg:flex-row gap-4">
        <div className="flex-1 relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="搜索标题、描述或标签..."
            className="input pl-10"
          />
        </div>
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2">
            <SlidersHorizontal className="w-4 h-4 text-slate-400" />
            <span className="text-sm text-slate-400">最低评分</span>
            <select
              value={minScore}
              onChange={(e) => setMinScore(Number(e.target.value))}
              className="input py-1.5 w-24"
            >
              <option value={5.0}>5.0</option>
              <option value={6.0}>6.0</option>
              <option value={7.0}>7.0</option>
              <option value={8.0}>8.0</option>
              <option value={8.5}>8.5</option>
            </select>
          </div>
        </div>
      </div>

      {tags.length > 0 && (
        <div className="flex flex-wrap items-center gap-2">
          <Filter className="w-4 h-4 text-slate-500" />
          <button
            onClick={() => setTagFilter('')}
            className={`badge ${
              !tagFilter
                ? 'bg-primary-500/20 text-primary-400 border-primary-500/40'
                : 'bg-slate-800 text-slate-400 border-slate-700 hover:border-slate-600'
            }`}
          >
            全部
          </button>
          {tags.map((tag) => (
            <button
              key={tag}
              onClick={() => setTagFilter(tag === tagFilter ? '' : tag)}
              className={`badge transition-colors ${
                tagFilter === tag
                  ? 'bg-primary-500/20 text-primary-400 border-primary-500/40'
                  : 'bg-slate-800 text-slate-400 border-slate-700 hover:border-slate-600'
              }`}
            >
              {tag}
            </button>
          ))}
        </div>
      )}

      {isLoading ? (
        <div className="card text-center py-16 text-slate-500">
          <Zap className="w-10 h-10 mx-auto mb-4 animate-pulse" />
          AI正在全网扫描并分析机会...
        </div>
      ) : filtered.length > 0 ? (
        <div className="space-y-3">
          {filtered.map((opp) => (
            <OpportunityCard key={opp.id} opportunity={opp} />
          ))}
        </div>
      ) : (
        <div className="card text-center py-16 text-slate-500">
          <Search className="w-10 h-10 mx-auto mb-4" />
          未找到匹配的机会，尝试调整筛选条件
        </div>
      )}
    </div>
  )
}
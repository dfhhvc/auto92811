import { ExternalLink, Clock, DollarSign, Shield, Users } from 'lucide-react'
import { Link } from 'react-router-dom'
import ScoreBadge from './ScoreBadge'
import type { Opportunity } from '../types'

interface OpportunityCardProps {
  opportunity: Opportunity
}

export default function OpportunityCard({ opportunity }: OpportunityCardProps) {
  return (
    <div className="card-hover group">
      <div className="flex items-start justify-between gap-3">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1.5">
            <Link
              to={`/opportunities/${opportunity.id}`}
              className="text-base font-semibold text-slate-100 hover:text-primary-400 transition-colors truncate"
            >
              {opportunity.title}
            </Link>
            {opportunity.verified && (
              <Shield className="w-4 h-4 text-emerald-400 shrink-0" />
            )}
          </div>
          <p className="text-sm text-slate-400 line-clamp-2 mb-3">
            {opportunity.description}
          </p>
          <div className="flex flex-wrap items-center gap-2 mb-3">
            {opportunity.tags.map((tag) => (
              <span
                key={tag}
                className="badge bg-slate-800 text-slate-300 border border-slate-700"
              >
                {tag}
              </span>
            ))}
          </div>
          <div className="flex flex-wrap items-center gap-4 text-xs text-slate-500">
            <span className="flex items-center gap-1">
              <Clock className="w-3.5 h-3.5" />
              {opportunity.time_investment}
            </span>
            <span className="flex items-center gap-1">
              <DollarSign className="w-3.5 h-3.5" />
              {opportunity.expected_income || '未知'}
            </span>
            <span className="flex items-center gap-1">
              <Users className="w-3.5 h-3.5" />
              {opportunity.source}
            </span>
            {opportunity.merge_count > 1 && (
              <span className="text-primary-400">
                +{opportunity.merge_count - 1} 个来源
              </span>
            )}
          </div>
        </div>
        <div className="flex flex-col items-end gap-2 shrink-0">
          <ScoreBadge score={opportunity.score_total} size="md" showLabel />
          {opportunity.match_score !== undefined && (
            <span className="text-xs text-primary-400 font-medium">
              匹配度 {opportunity.match_score.toFixed(1)}
            </span>
          )}
        </div>
      </div>
      {opportunity.source_url && (
        <a
          href={opportunity.source_url}
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex items-center gap-1 mt-3 text-xs text-primary-400 hover:text-primary-300 transition-colors"
        >
          <ExternalLink className="w-3.5 h-3.5" />
          查看来源
        </a>
      )}
    </div>
  )
}
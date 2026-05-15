export interface Opportunity {
  id: string
  title: string
  description: string
  source: string
  source_url?: string
  verified: boolean
  warning?: string
  tags: string[]
  score_total: number
  score_feasibility: number
  score_timeliness: number
  score_credibility: number
  score_roi: number
  score_replicability: number
  match_score?: number
  match_reasons?: string[]
  risk_note?: string
  time_investment: string
  expected_income: string
  monthly_income?: number
  investment?: number
  required_skills?: string[]
  merge_count: number
  created_at: string
}

export interface UserProfile {
  id: string
  skills: string[]
  time_budget: string
  risk_level: 'conservative' | 'moderate' | 'aggressive'
  languages: string[]
  notifications_enabled: boolean
}

export interface IncomeRecord {
  id: string
  opportunity_id: string
  opportunity_title: string
  amount: number
  currency: string
  date: string
  note?: string
}

export interface ScanResult {
  status: string
  raw_count: number
  unique_count: number
  merged_count: number
  valid_count: number
  recommended_count: number
  elapsed_seconds: number
  opportunities: Opportunity[]
  error_message?: string
}

export interface SystemHealth {
  status: string
  version: string
  uptime: number
  database: { status: string; latency_ms: number }
  redis: { status: string; latency_ms: number }
  llm: { status: string; providers: Record<string, boolean> }
}
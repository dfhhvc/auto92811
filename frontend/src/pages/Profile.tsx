import { useState } from 'react'
import { UserCircle, Save, Check } from 'lucide-react'

export default function Profile() {
  const [saved, setSaved] = useState(false)
  const [profile, setProfile] = useState({
    skills: '写作, 编程, 设计',
    time_budget: '2h',
    risk_level: 'moderate' as const,
    languages: 'zh',
  })

  const handleSave = () => {
    setSaved(true)
    setTimeout(() => setSaved(false), 2000)
  }

  return (
    <div className="space-y-6 max-w-2xl">
      <div>
        <h1 className="text-2xl font-bold text-slate-100">个人档案</h1>
        <p className="text-slate-400 text-sm mt-1">
          配置您的技能和偏好，让AI为您精准推荐
        </p>
      </div>

      <div className="card space-y-5">
        <div className="flex items-center gap-3 mb-4">
          <div className="w-14 h-14 rounded-full bg-primary-600 flex items-center justify-center">
            <UserCircle className="w-8 h-8 text-white" />
          </div>
          <div>
            <div className="font-semibold text-slate-100">用户</div>
            <div className="text-sm text-slate-500">基础版用户</div>
          </div>
        </div>

        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-slate-300 mb-1.5">
              技能标签（用逗号分隔）
            </label>
            <input
              type="text"
              value={profile.skills}
              onChange={(e) =>
                setProfile({ ...profile, skills: e.target.value })
              }
              className="input"
              placeholder="例如：写作, 编程, 设计"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-300 mb-1.5">
              每日可投入时间
            </label>
            <select
              value={profile.time_budget}
              onChange={(e) =>
                setProfile({ ...profile, time_budget: e.target.value as any })
              }
              className="input"
            >
              <option value="1h">1 小时</option>
              <option value="2h">2 小时</option>
              <option value="4h">4 小时</option>
              <option value="8h">8 小时</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-300 mb-1.5">
              风险偏好
            </label>
            <select
              value={profile.risk_level}
              onChange={(e) =>
                setProfile({ ...profile, risk_level: e.target.value as any })
              }
              className="input"
            >
              <option value="conservative">保守型 — 稳健收益，低风险</option>
              <option value="moderate">平衡型 — 适中风险与收益</option>
              <option value="aggressive">激进型 — 高风险高回报</option>
            </select>
          </div>
        </div>

        <button
          onClick={handleSave}
          className="btn-primary inline-flex items-center gap-2"
        >
          {saved ? (
            <>
              <Check className="w-4 h-4" />
              已保存
            </>
          ) : (
            <>
              <Save className="w-4 h-4" />
              保存配置
            </>
          )}
        </button>
      </div>
    </div>
  )
}
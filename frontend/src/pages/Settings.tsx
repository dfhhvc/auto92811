import { useState } from 'react'
import { Bell, Shield, Globe, Server, Check } from 'lucide-react'

export default function Settings() {
  const [saved, setSaved] = useState(false)
  const [settings, setSettings] = useState({
    notifications: true,
    emailAlerts: false,
    pushAlerts: true,
    darkMode: true,
    language: 'zh',
    apiEndpoint: '',
  })

  const handleSave = () => {
    setSaved(true)
    setTimeout(() => setSaved(false), 2000)
  }

  return (
    <div className="space-y-6 max-w-2xl">
      <div>
        <h1 className="text-2xl font-bold text-slate-100">设置</h1>
        <p className="text-slate-400 text-sm mt-1">
          管理通知、安全和其他偏好
        </p>
      </div>

      <div className="card space-y-6">
        <div className="flex items-center gap-3 pb-4 border-b border-slate-800">
          <Bell className="w-5 h-5 text-primary-400" />
          <h2 className="text-lg font-semibold text-slate-100">通知</h2>
        </div>

        <ToggleRow
          label="启用通知"
          description="接收高分机会推送"
          enabled={settings.notifications}
          onChange={(v) => setSettings({ ...settings, notifications: v })}
        />
        <ToggleRow
          label="邮件提醒"
          description="每日摘要邮件"
          enabled={settings.emailAlerts}
          onChange={(v) => setSettings({ ...settings, emailAlerts: v })}
        />
        <ToggleRow
          label="推送通知"
          description="浏览器/APP推送"
          enabled={settings.pushAlerts}
          onChange={(v) => setSettings({ ...settings, pushAlerts: v })}
        />
      </div>

      <div className="card space-y-6">
        <div className="flex items-center gap-3 pb-4 border-b border-slate-800">
          <Globe className="w-5 h-5 text-primary-400" />
          <h2 className="text-lg font-semibold text-slate-100">通用</h2>
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-300 mb-1.5">
            语言
          </label>
          <select
            value={settings.language}
            onChange={(e) =>
              setSettings({ ...settings, language: e.target.value })
            }
            className="input"
          >
            <option value="zh">简体中文</option>
            <option value="en">English</option>
          </select>
        </div>

        <ToggleRow
          label="深色模式"
          description="强制深色主题"
          enabled={settings.darkMode}
          onChange={(v) => setSettings({ ...settings, darkMode: v })}
        />
      </div>

      <div className="card space-y-6">
        <div className="flex items-center gap-3 pb-4 border-b border-slate-800">
          <Server className="w-5 h-5 text-primary-400" />
          <h2 className="text-lg font-semibold text-slate-100">高级</h2>
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-300 mb-1.5">
            API 端点
          </label>
          <input
            type="text"
            value={settings.apiEndpoint}
            onChange={(e) =>
              setSettings({ ...settings, apiEndpoint: e.target.value })
            }
            placeholder="https://api.autoincome.dev"
            className="input"
          />
          <p className="text-xs text-slate-500 mt-1">
            留空使用默认端点
          </p>
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
            <Shield className="w-4 h-4" />
            保存设置
          </>
        )}
      </button>
    </div>
  )
}

function ToggleRow({
  label,
  description,
  enabled,
  onChange,
}: {
  label: string
  description: string
  enabled: boolean
  onChange: (v: boolean) => void
}) {
  return (
    <div className="flex items-center justify-between">
      <div>
        <div className="text-sm font-medium text-slate-200">{label}</div>
        <div className="text-xs text-slate-500">{description}</div>
      </div>
      <button
        onClick={() => onChange(!enabled)}
        className={`relative w-11 h-6 rounded-full transition-colors ${
          enabled ? 'bg-primary-600' : 'bg-slate-700'
        }`}
      >
        <span
          className={`absolute top-0.5 left-0.5 w-5 h-5 bg-white rounded-full transition-transform ${
            enabled ? 'translate-x-5' : 'translate-x-0'
          }`}
        />
      </button>
    </div>
  )
}
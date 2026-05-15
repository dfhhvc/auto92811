import { useState } from 'react'
import {
  TrendingUp,
  Plus,
  Wallet,
  Calendar,
  DollarSign,
} from 'lucide-react'
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts'

const mockData = [
  { month: '1月', amount: 1200 },
  { month: '2月', amount: 1800 },
  { month: '3月', amount: 1500 },
  { month: '4月', amount: 2400 },
  { month: '5月', amount: 3200 },
  { month: '6月', amount: 2800 },
]

const mockRecords = [
  {
    id: '1',
    title: 'AI写作助手代运营',
    amount: 3200,
    date: '2024-06-15',
    note: '小红书账号代运营收入',
  },
  {
    id: '2',
    title: '开源项目赞助',
    amount: 800,
    date: '2024-06-10',
    note: 'GitHub Sponsors',
  },
  {
    id: '3',
    title: '技术咨询',
    amount: 1500,
    date: '2024-06-05',
    note: '周末技术顾问',
  },
]

export default function Income() {
  const [showAdd, setShowAdd] = useState(false)
  const total = mockData.reduce((s, d) => s + d.amount, 0)

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-100">收益追踪</h1>
          <p className="text-slate-400 text-sm mt-1">
            记录并可视化您的被动收入
          </p>
        </div>
        <button
          onClick={() => setShowAdd(!showAdd)}
          className="btn-primary inline-flex items-center gap-2"
        >
          <Plus className="w-4 h-4" />
          记一笔
        </button>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="card">
          <div className="flex items-center gap-3">
            <div className="p-2.5 bg-emerald-500/10 rounded-lg">
              <Wallet className="w-5 h-5 text-emerald-400" />
            </div>
            <div>
              <div className="text-2xl font-bold text-slate-100">
                ¥{total.toLocaleString()}
              </div>
              <div className="text-xs text-slate-500">累计收益</div>
            </div>
          </div>
        </div>
        <div className="card">
          <div className="flex items-center gap-3">
            <div className="p-2.5 bg-primary-500/10 rounded-lg">
              <TrendingUp className="w-5 h-5 text-primary-400" />
            </div>
            <div>
              <div className="text-2xl font-bold text-slate-100">
                ¥{Math.round(total / mockData.length).toLocaleString()}
              </div>
              <div className="text-xs text-slate-500">月均收益</div>
            </div>
          </div>
        </div>
        <div className="card">
          <div className="flex items-center gap-3">
            <div className="p-2.5 bg-cyan-500/10 rounded-lg">
              <Calendar className="w-5 h-5 text-cyan-400" />
            </div>
            <div>
              <div className="text-2xl font-bold text-slate-100">
                {mockRecords.length}
              </div>
              <div className="text-xs text-slate-500">收入笔数</div>
            </div>
          </div>
        </div>
      </div>

      <div className="card">
        <h2 className="text-lg font-semibold text-slate-100 mb-4">
          收益趋势
        </h2>
        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={mockData}>
              <defs>
                <linearGradient id="colorAmount" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3} />
                  <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
              <XAxis dataKey="month" stroke="#64748b" fontSize={12} />
              <YAxis stroke="#64748b" fontSize={12} />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#1e293b',
                  border: '1px solid #334155',
                  borderRadius: '8px',
                  color: '#e2e8f0',
                }}
              />
              <Area
                type="monotone"
                dataKey="amount"
                stroke="#3b82f6"
                fillOpacity={1}
                fill="url(#colorAmount)"
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="card">
        <h2 className="text-lg font-semibold text-slate-100 mb-4">
          收入明细
        </h2>
        <div className="space-y-3">
          {mockRecords.map((record) => (
            <div
              key={record.id}
              className="flex items-center justify-between p-3 bg-slate-900/50 rounded-lg"
            >
              <div>
                <div className="font-medium text-slate-200">{record.title}</div>
                <div className="text-xs text-slate-500 mt-0.5">
                  {record.date} · {record.note}
                </div>
              </div>
              <div className="flex items-center gap-1 text-emerald-400 font-semibold">
                <DollarSign className="w-4 h-4" />
                +{record.amount}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
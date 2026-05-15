import { useEffect, useState } from 'react'
import { invoke } from '@tauri-apps/api/core'

function App() {
  const [apiUrl, setApiUrl] = useState('http://localhost:8080')
  const [health, setHealth] = useState<any>(null)

  useEffect(() => {
    checkHealth()
  }, [apiUrl])

  const checkHealth = async () => {
    try {
      const res = await fetch(`${apiUrl}/api/v1/health`)
      const data = await res.json()
      setHealth(data)
    } catch (e) {
      setHealth({ status: 'offline' })
    }
  }

  return (
    <div style={{
      width: '100vw',
      height: '100vh',
      display: 'flex',
      flexDirection: 'column',
      background: '#0f172a',
      color: '#e2e8f0',
      fontFamily: 'system-ui, sans-serif'
    }}>
      <div style={{
        padding: '12px 20px',
        borderBottom: '1px solid #334155',
        display: 'flex',
        alignItems: 'center',
        gap: 12
      }}>
        <span style={{ fontSize: 18, fontWeight: 'bold' }}>AutoIncome Desktop</span>
        <span style={{ fontSize: 12, color: '#64748b' }}>v4.1.0</span>
        <div style={{ flex: 1 }} />
        <input
          value={apiUrl}
          onChange={(e) => setApiUrl(e.target.value)}
          placeholder="API地址"
          style={{
            padding: '6px 12px',
            borderRadius: 6,
            border: '1px solid #334155',
            background: '#1e293b',
            color: '#e2e8f0',
            fontSize: 13,
            width: 240
          }}
        />
        <span style={{
          width: 8,
          height: 8,
          borderRadius: '50%',
          background: health?.status === 'healthy' ? '#10b981' : '#ef4444'
        }} />
      </div>
      <iframe
        src={apiUrl === 'http://localhost:8080' ? 'http://localhost:3000' : `${apiUrl}/app`}
        style={{ flex: 1, border: 'none' }}
        title="AutoIncome"
      />
    </div>
  )
}

export default App
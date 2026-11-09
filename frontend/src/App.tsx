import { lazy, Suspense, useCallback, useEffect, useMemo, useRef, useState } from 'react'
import {
  Activity, AlertTriangle, ArrowRight, BarChart3, Bot, Boxes,
  CheckCircle2, ChevronRight, CircleGauge, Clock3, Cog, Database,
  Gauge, HeartPulse, History, Layers3, Menu, Moon, Network, Pause,
  Play, Radar, RefreshCcw, Route, Satellite, Settings2, ShieldAlert,
  SlidersHorizontal, Sparkles, Thermometer, Video, Wrench, X, Zap,
} from 'lucide-react'
import {
  Area, AreaChart, Bar, BarChart, CartesianGrid, Cell, Line,
  LineChart, Pie, PieChart, ResponsiveContainer, Tooltip, XAxis, YAxis,
} from 'recharts'
import { VideoCarousel } from './VideoCarousel'

const DigitalTwin3DPanel = lazy(() => import('./twin3d/DigitalTwin3DPanel')
  .then(module => ({ default: module.DigitalTwin3DPanel })))

type Twin = Record<string, any>

const API_BASE = (import.meta as any).env?.DEV ? '' : (import.meta as any).env?.VITE_API_URL || ''
const api = (path: string) => `${API_BASE}${path}`

const navigation = [
  ['Dashboard', '/dashboard', CircleGauge],
  ['Digital Twin', '/digital-twin', Boxes],
  ['Telemetry', '/telemetry', Activity],
  ['Health', '/health', HeartPulse],
  ['Fault Prediction', '/prediction', Bot],
  ['Mission Reliability', '/mission', Route],
  ['Maintenance', '/maintenance', Wrench],
  ['History', '/history', History],
  ['Simulation', '/simulation', SlidersHorizontal],
  ['Project Video', '/video', Video],
  ['Architecture', '/architecture', Network],
  ['About', '/about', Sparkles],
] as const

const faultOptions = [
  ['normal', 'Normal operation', 'Healthy synthetic baseline'],
  ['overheating', 'Overheating', 'Thermal signal escalation'],
  ['low_oil_pressure', 'Low oil pressure', 'Lubrication risk trend'],
  ['excessive_vibration', 'Excessive vibration', 'Mechanical condition signal'],
  ['abnormal_fuel_flow', 'Fuel abnormality', 'Fuel-flow / pressure deviation'],
  ['cooling_degradation', 'Cooling degradation', 'Progressive thermal‑management loss'],
  ['sensor_anomaly', 'Sensor anomaly', 'Telemetry consistency deviation'],
  ['progressive_degradation', 'Progressive degradation', 'Multi‑system health decline'],
]

function useTwin() {
  const [twin, setTwin] = useState<Twin | null>(null)
  const [history, setHistory] = useState<Twin[]>([])
  const [connected, setConnected] = useState(false)
  const [error, setError] = useState('')

  const hydrate = useCallback(async () => {
    try {
      const [engine, health, telemetry, prediction, mission, maintenance, alerts, snapshots] =
        await Promise.all(
          ['/api/engine', '/api/health', '/api/telemetry/latest',
           '/api/prediction', '/api/mission', '/api/maintenance',
           '/api/alerts', '/api/history?limit=180']
            .map(p => fetch(api(p)).then(r => r.ok ? r.json() : Promise.reject(new Error(`${r.status}`))))
        )
      setTwin({ ...engine, health, telemetry, prediction, mission, maintenance, alerts: alerts.live || [] })
      setHistory(Array.isArray(snapshots) ? snapshots.slice(-180) : [])
      setError('')
    } catch {
      setError('Backend unavailable. Start the local FastAPI service to enable the live twin.')
    }
  }, [])

  useEffect(() => {
    hydrate()
    let socket: WebSocket | undefined
    let retry: number | undefined
    const connect = () => {
      const base = API_BASE ? API_BASE.replace(/^http/, 'ws')
               : `${location.protocol === 'https:' ? 'wss' : 'ws'}://${location.host}`
      socket = new WebSocket(`${base}/ws/telemetry`)
      socket.onopen = () => { setConnected(true); setError('') }
      socket.onmessage = ev => {
        const incoming = JSON.parse(ev.data)
        setTwin(incoming)
        setHistory(prev => [...prev, incoming].slice(-180))
      }
      socket.onerror = () => socket?.close()
      socket.onclose = () => { setConnected(false); retry = window.setTimeout(connect, 2500) }
    }
    connect()
    return () => { if (retry) clearTimeout(retry); socket?.close() }
  }, [hydrate])

  const command = useCallback(async (path: string, body?: unknown) => {
    const response = await fetch(api(path), {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: body ? JSON.stringify(body) : undefined
    })
    if (!response.ok) throw new Error(`Command failed (${response.status})`)
    const result = await response.json()
    setTwin(result)
    setHistory(prev => {
      const latest = prev[prev.length - 1]
      return latest?.updated_at === result.updated_at ? prev : [...prev, result].slice(-180)
    })
    return result
  }, [])

  return { twin, history, connected, error, hydrate, command }
}

/* ... rest of the component (navigation bar, panels, rendering, etc.) ... */

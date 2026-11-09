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

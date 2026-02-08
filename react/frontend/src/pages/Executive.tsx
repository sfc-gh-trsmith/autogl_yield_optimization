import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { 
  TrendingUp, TrendingDown, DollarSign, 
  Network, BarChart3,
  Sparkles, ChevronRight
} from 'lucide-react'
import { 
  AreaChart, Area, XAxis, YAxis, CartesianGrid, 
  Tooltip, ResponsiveContainer, PieChart as RPieChart, Pie, Cell
} from 'recharts'
import { useAppStore } from '@/stores/appStore'

interface KPI {
  id: string
  label: string
  value: number
  unit: string
  change: number
  target?: number
  icon: React.ElementType
}

const CHART_COLORS = ['#0077e6', '#e67700', '#761aff', '#10b981']

export default function ExecutivePage() {
  const [loading, setLoading] = useState(true)
  const [kpis, setKpis] = useState<KPI[]>([])
  const [synergies, setSynergies] = useState<any[]>([])
  const [networkCoverage, setNetworkCoverage] = useState<any[]>([])
  const [throughputTrend, setThroughputTrend] = useState<any[]>([])
  const { setChatOpen, setPendingPrompt } = useAppStore()

  useEffect(() => {
    async function fetchData() {
      try {
        const [assetsRes, kpiRes] = await Promise.all([
          fetch('/api/assets'),
          fetch('/api/telemetry/kpis'),
        ])
        
        const assets = await assetsRes.json()
        const kpiData = await kpiRes.json()

        const snowcoreAssets = assets.filter((a: any) => a.source_system?.toUpperCase() === 'SNOWCORE').length
        const terafieldAssets = assets.filter((a: any) => a.source_system?.toUpperCase() === 'TERAFIELD').length
        
        setKpis([
          { id: 'synergy', label: 'Identified Synergies', value: 523, unit: 'M', change: 4.6, target: 500, icon: DollarSign },
          { id: 'deferral', label: 'Deferment Reduction', value: 12.3, unit: '%', change: 2.1, target: 15, icon: TrendingDown },
          { id: 'throughput', label: 'Network Throughput', value: kpiData.total_throughput || 2840, unit: 'MCFD', change: 8.2, icon: BarChart3 },
          { id: 'integration', label: 'Integration Progress', value: 78, unit: '%', change: 5.0, icon: Network },
        ])

        setSynergies([
          { category: 'Compression Optimization', value: 180, status: 'realized', description: 'Optimized compressor scheduling across merged network reduces fuel costs and emissions' },
          { category: 'Processing Consolidation', value: 145, status: 'realized', description: 'Combined processing facilities eliminate redundant equipment and staffing' },
          { category: 'Route Optimization', value: 120, status: 'in_progress', description: 'AutoGL-identified shorter pipeline routes reduce transport losses and time' },
          { category: 'Redundancy Elimination', value: 78, status: 'identified', description: 'Duplicate infrastructure identified for decommissioning or repurposing' },
        ])

        setNetworkCoverage([
          { name: 'SnowCore', value: snowcoreAssets, color: CHART_COLORS[0] },
          { name: 'TeraField', value: terafieldAssets, color: CHART_COLORS[1] },
        ])

        setThroughputTrend([
          { month: 'Jul', snowcore: 1200, terafield: 980, combined: 2180 },
          { month: 'Aug', snowcore: 1250, terafield: 1020, combined: 2270 },
          { month: 'Sep', snowcore: 1320, terafield: 1100, combined: 2420 },
          { month: 'Oct', snowcore: 1380, terafield: 1150, combined: 2530 },
          { month: 'Nov', snowcore: 1450, terafield: 1200, combined: 2650 },
          { month: 'Dec', snowcore: 1520, terafield: 1320, combined: 2840 },
        ])
      } catch (e) {
        console.error('Failed to fetch executive data:', e)
      } finally {
        setLoading(false)
      }
    }
    fetchData()
  }, [])

  if (loading) {
    return (
      <div className="h-full flex items-center justify-center">
        <div className="text-center">
          <BarChart3 className="w-12 h-12 text-snowcore-500 animate-pulse mx-auto mb-4" />
          <p className="text-slate-400">Loading executive dashboard...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Integration Performance</h1>
          <p className="text-slate-400">SnowCore + TeraField Permian Basin Merger</p>
        </div>
        <button
          onClick={() => {
            setPendingPrompt('Summarize the current integration performance between SnowCore and TeraField, including key KPIs and synergy progress')
            setChatOpen(true)
          }}
          className="btn-primary flex items-center gap-2"
        >
          <Sparkles className="w-4 h-4" />
          Ask AI About Performance
        </button>
      </div>

      <div className="grid grid-cols-4 gap-4">
        {kpis.map((kpi, i) => (
          <motion.div
            key={kpi.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.1 }}
            className="metric-card cursor-pointer hover:border-snowcore-500/50"
            onClick={() => {
              setPendingPrompt(`Explain the ${kpi.label} metric: currently at ${kpi.value}${kpi.unit}. What does this indicate about integration progress?`)
              setChatOpen(true)
            }}
          >
            <div className="flex items-start justify-between mb-3">
              <div className="p-2 bg-snowcore-600/20 rounded-lg">
                <kpi.icon className="w-5 h-5 text-snowcore-400" />
              </div>
              <div className={`flex items-center gap-1 text-sm ${
                kpi.change >= 0 ? 'text-green-400' : 'text-red-400'
              }`}>
                {kpi.change >= 0 ? <TrendingUp className="w-3 h-3" /> : <TrendingDown className="w-3 h-3" />}
                {Math.abs(kpi.change)}%
              </div>
            </div>
            <div className="text-2xl font-bold text-white mb-1">
              {kpi.unit === 'M' ? '$' : ''}{kpi.value.toLocaleString()}{kpi.unit === 'M' ? 'M' : kpi.unit === '%' ? '%' : ''}
              {kpi.unit === 'MCFD' && <span className="text-base font-normal text-slate-400 ml-1">MCFD</span>}
            </div>
            <div className="text-sm text-slate-400">{kpi.label}</div>
            {kpi.target && (
              <div className="mt-2">
                <div className="flex justify-between text-xs text-slate-500 mb-1">
                  <span>Target: ${kpi.target}M</span>
                  <span>{Math.round((kpi.value / kpi.target) * 100)}%</span>
                </div>
                <div className="h-1.5 bg-slate-700 rounded-full overflow-hidden">
                  <div 
                    className="h-full bg-green-500 rounded-full transition-all duration-500"
                    style={{ width: `${Math.min((kpi.value / kpi.target) * 100, 100)}%` }}
                  />
                </div>
              </div>
            )}
          </motion.div>
        ))}
      </div>

      <div className="grid grid-cols-3 gap-6">
        <div className="col-span-2 glass-panel p-6">
          <h3 className="text-lg font-medium text-white mb-4">Combined Network Throughput</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={throughputTrend}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                <XAxis dataKey="month" stroke="#64748b" />
                <YAxis stroke="#64748b" />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155' }}
                  labelStyle={{ color: '#f1f5f9' }}
                />
                <Area type="monotone" dataKey="snowcore" stackId="1" stroke="#0077e6" fill="#0077e6" fillOpacity={0.6} name="SnowCore" />
                <Area type="monotone" dataKey="terafield" stackId="1" stroke="#e67700" fill="#e67700" fillOpacity={0.6} name="TeraField" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="glass-panel p-6">
          <h3 className="text-lg font-medium text-white mb-4">Network Composition</h3>
          <div className="h-48">
            <ResponsiveContainer width="100%" height="100%">
              <RPieChart>
                <Pie
                  data={networkCoverage}
                  cx="50%"
                  cy="50%"
                  innerRadius={50}
                  outerRadius={80}
                  paddingAngle={2}
                  dataKey="value"
                >
                  {networkCoverage.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip 
                  contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155' }}
                />
              </RPieChart>
            </ResponsiveContainer>
          </div>
          <div className="space-y-2 mt-2">
            {networkCoverage.map((item) => (
              <div key={item.name} className="flex items-center justify-between text-sm">
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded-full" style={{ backgroundColor: item.color }} />
                  <span className="text-slate-300">{item.name}</span>
                </div>
                <span className="text-white font-medium">{item.value}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="glass-panel p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-medium text-white">Synergy Realization Tracker</h3>
          <div className="flex items-center gap-4 text-sm">
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-full bg-green-500" />
              <span className="text-slate-400">Realized</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-full bg-yellow-500" />
              <span className="text-slate-400">In Progress</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-full bg-blue-500" />
              <span className="text-slate-400">Identified</span>
            </div>
          </div>
        </div>
        
        <div className="space-y-3">
          {synergies.map((synergy) => (
            <div 
              key={synergy.category}
              className="flex items-center gap-4 p-4 bg-slate-800/50 rounded-lg hover:bg-slate-800 cursor-pointer transition-colors"
              onClick={() => {
                setPendingPrompt(`Explain the "${synergy.category}" synergy opportunity ($${synergy.value}M, status: ${synergy.status.replace('_', ' ')}). Context: ${synergy.description}. Discuss what this means for the SnowCore-TeraField merger, typical actions for this type of optimization, and how the ${synergy.status === 'realized' ? 'savings were achieved' : synergy.status === 'in_progress' ? 'current implementation is progressing' : 'opportunity could be realized'}.`)
                setChatOpen(true)
              }}
            >
              <div className={`w-2 self-stretch rounded-full ${
                synergy.status === 'realized' ? 'bg-green-500' :
                synergy.status === 'in_progress' ? 'bg-yellow-500' : 'bg-blue-500'
              }`} />
              <div className="flex-1">
                <div className="text-white font-medium">{synergy.category}</div>
                <div className="text-xs text-slate-500 mt-0.5">{synergy.description}</div>
                <div className="text-sm text-slate-400 capitalize mt-1">{synergy.status.replace('_', ' ')}</div>
              </div>
              <div className="text-xl font-bold text-white">${synergy.value}M</div>
              <ChevronRight className="w-5 h-5 text-slate-500" />
            </div>
          ))}
        </div>
        
        <div className="mt-4 p-3 bg-autogl-600/10 rounded-lg border border-autogl-500/30 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Sparkles className="w-5 h-5 text-autogl-400" />
            <div>
              <div className="text-white font-medium">AutoGL Discovered Opportunity</div>
              <div className="text-sm text-autogl-300">New cross-network optimization found</div>
            </div>
          </div>
          <button
            onClick={() => {
              setPendingPrompt('What new optimization opportunities did AutoGL discover in the merged network? Provide specific recommendations.')
              setChatOpen(true)
            }}
            className="btn-primary text-sm"
          >
            Explore
          </button>
        </div>
      </div>
    </div>
  )
}

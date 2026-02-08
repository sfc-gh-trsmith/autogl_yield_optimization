import { useState, useEffect, useMemo, useCallback } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import MapGL from 'react-map-gl/maplibre'
import DeckGL from '@deck.gl/react'
import { ScatterplotLayer } from '@deck.gl/layers'
import { 
  Radio, AlertTriangle, CheckCircle, Clock, 
  Activity, Bell, ChevronRight, Sparkles
} from 'lucide-react'
import { useAppStore } from '@/stores/appStore'
import type { Asset } from '@/types'
import 'maplibre-gl/dist/maplibre-gl.css'

const PERMIAN_CENTER = { latitude: 31.85, longitude: -103.5, zoom: 8 }

interface Alert {
  id: string
  asset_id: string
  asset_name: string
  type: 'pressure' | 'flow' | 'anomaly' | 'maintenance'
  severity: 'low' | 'medium' | 'high' | 'critical'
  message: string
  timestamp: Date
  acknowledged: boolean
}

export default function OperationsPage() {
  const [assets, setAssets] = useState<Asset[]>([])
  const [alerts, setAlerts] = useState<Alert[]>([])
  const [loading, setLoading] = useState(true)
  const [selectedAlert, setSelectedAlert] = useState<Alert | null>(null)
  const [filterSeverity, setFilterSeverity] = useState<string | null>(null)
  const [viewState, setViewState] = useState(PERMIAN_CENTER)
  const { setChatOpen, setChatContext, setSelectedAsset } = useAppStore()

  const handleAlertSelect = useCallback((alert: Alert) => {
    setSelectedAlert(alert)
    const asset = assets.find(a => a.asset_id === alert.asset_id)
    if (asset) {
      setViewState({
        latitude: asset.latitude,
        longitude: asset.longitude,
        zoom: 11,
        transitionDuration: 500,
      } as any)
      setSelectedAsset(asset)
    }
  }, [assets, setSelectedAsset])

  useEffect(() => {
    async function fetchData() {
      try {
        const [assetsRes, anomaliesRes] = await Promise.all([
          fetch('/api/assets'),
          fetch('/api/predictions/anomalies?min_risk=0.5'),
        ])
        
        const assetsData = await assetsRes.json()
        const anomalies = await anomaliesRes.json()
        
        setAssets(assetsData)
        
        const generatedAlerts: Alert[] = anomalies.slice(0, 12).map((a: any, i: number) => ({
          id: `alert-${i}`,
          asset_id: a.asset_id,
          asset_name: a.asset_name,
          type: a.risk_score > 0.8 ? 'anomaly' : a.risk_score > 0.7 ? 'pressure' : 'flow',
          severity: a.risk_score > 0.85 ? 'critical' : a.risk_score > 0.75 ? 'high' : a.risk_score > 0.6 ? 'medium' : 'low',
          message: a.explanation || `Anomaly detected: risk score ${(a.risk_score * 100).toFixed(0)}%`,
          timestamp: new Date(Date.now() - Math.random() * 3600000),
          acknowledged: Math.random() > 0.7,
        }))
        
        setAlerts(generatedAlerts.sort((a, b) => {
          const severityOrder = { critical: 0, high: 1, medium: 2, low: 3 }
          return severityOrder[a.severity] - severityOrder[b.severity]
        }))
      } catch (e) {
        console.error('Failed to fetch operations data:', e)
      } finally {
        setLoading(false)
      }
    }
    fetchData()
  }, [])

  const filteredAlerts = useMemo(() => {
    if (!filterSeverity) return alerts
    return alerts.filter(a => a.severity === filterSeverity)
  }, [alerts, filterSeverity])

  const alertCounts = useMemo(() => ({
    critical: alerts.filter(a => a.severity === 'critical').length,
    high: alerts.filter(a => a.severity === 'high').length,
    medium: alerts.filter(a => a.severity === 'medium').length,
    low: alerts.filter(a => a.severity === 'low').length,
    unacknowledged: alerts.filter(a => !a.acknowledged).length,
  }), [alerts])

  const getAlertAsset = (alertItem: Alert) => assets.find(a => a.asset_id === alertItem.asset_id)

  const layers = useMemo(() => [
    new ScatterplotLayer({
      id: 'assets',
      data: assets,
      getPosition: (d: Asset) => [d.longitude, d.latitude],
      getFillColor: (d: Asset) => {
        const alert = alerts.find(a => a.asset_id === d.asset_id)
        if (alert?.severity === 'critical') return [220, 38, 38, 255]
        if (alert?.severity === 'high') return [239, 68, 68, 200]
        if (alert?.severity === 'medium') return [245, 158, 11, 180]
        if (alert) return [16, 185, 129, 150]
        return [100, 116, 139, 100]
      },
      getRadius: (d: Asset) => {
        const alert = alerts.find(a => a.asset_id === d.asset_id)
        if (alert?.severity === 'critical') return 800
        if (alert) return 600
        return 400
      },
      radiusMinPixels: 5,
      radiusMaxPixels: 20,
      pickable: true,
      onClick: ({ object }) => {
        if (object) {
          const alert = alerts.find(a => a.asset_id === (object as Asset).asset_id)
          if (alert) setSelectedAlert(alert)
          setSelectedAsset(object as Asset)
        }
      },
      updateTriggers: {
        getFillColor: [alerts],
        getRadius: [alerts],
      },
    }),
  ], [assets, alerts, setSelectedAsset])

  const acknowledgeAlert = (alertId: string) => {
    setAlerts(alerts.map(a => 
      a.id === alertId ? { ...a, acknowledged: true } : a
    ))
  }

  if (loading) {
    return (
      <div className="h-full flex items-center justify-center">
        <div className="text-center">
          <Radio className="w-12 h-12 text-snowcore-500 animate-pulse mx-auto mb-4" />
          <p className="text-slate-400">Loading operations center...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="h-full flex">
      <div className="flex-1 relative">
        <DeckGL
          viewState={viewState}
          onViewStateChange={({ viewState: vs }) => setViewState(vs as any)}
          controller={true}
          layers={layers}
          style={{ position: 'absolute', inset: '0' }}
        >
          <MapGL
            mapStyle="https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json"
            attributionControl={false}
          />
        </DeckGL>

        <div className="absolute top-4 left-4 z-10">
          <div className="glass-panel p-4">
            <h3 className="text-sm font-medium text-white mb-3 flex items-center gap-2">
              <Activity className="w-4 h-4" />
              Network Health
            </h3>
            <div className="grid grid-cols-2 gap-2">
              <button
                onClick={() => setFilterSeverity(filterSeverity === 'critical' ? null : 'critical')}
                className={`p-2 rounded-lg text-sm flex items-center gap-2 transition-colors ${
                  filterSeverity === 'critical' ? 'bg-red-600/30 border border-red-500' : 'bg-red-600/10 hover:bg-red-600/20'
                }`}
              >
                <div className="w-3 h-3 rounded-full bg-red-600 animate-pulse" />
                <span className="text-red-300">Critical</span>
                <span className="text-red-200 font-bold ml-auto">{alertCounts.critical}</span>
              </button>
              <button
                onClick={() => setFilterSeverity(filterSeverity === 'high' ? null : 'high')}
                className={`p-2 rounded-lg text-sm flex items-center gap-2 transition-colors ${
                  filterSeverity === 'high' ? 'bg-red-500/30 border border-red-400' : 'bg-red-500/10 hover:bg-red-500/20'
                }`}
              >
                <div className="w-3 h-3 rounded-full bg-red-500" />
                <span className="text-red-200">High</span>
                <span className="text-red-100 font-bold ml-auto">{alertCounts.high}</span>
              </button>
              <button
                onClick={() => setFilterSeverity(filterSeverity === 'medium' ? null : 'medium')}
                className={`p-2 rounded-lg text-sm flex items-center gap-2 transition-colors ${
                  filterSeverity === 'medium' ? 'bg-yellow-500/30 border border-yellow-400' : 'bg-yellow-500/10 hover:bg-yellow-500/20'
                }`}
              >
                <div className="w-3 h-3 rounded-full bg-yellow-500" />
                <span className="text-yellow-300">Medium</span>
                <span className="text-yellow-200 font-bold ml-auto">{alertCounts.medium}</span>
              </button>
              <button
                onClick={() => setFilterSeverity(filterSeverity === 'low' ? null : 'low')}
                className={`p-2 rounded-lg text-sm flex items-center gap-2 transition-colors ${
                  filterSeverity === 'low' ? 'bg-green-500/30 border border-green-400' : 'bg-green-500/10 hover:bg-green-500/20'
                }`}
              >
                <div className="w-3 h-3 rounded-full bg-green-500" />
                <span className="text-green-300">Low</span>
                <span className="text-green-200 font-bold ml-auto">{alertCounts.low}</span>
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="w-96 bg-slate-900 border-l border-slate-800 flex flex-col">
        <div className="p-4 border-b border-slate-800">
          <div className="flex items-center justify-between mb-2">
            <h3 className="font-semibold text-white flex items-center gap-2">
              <Bell className="w-5 h-5" />
              Active Alerts
            </h3>
            <span className="px-2 py-1 bg-red-500/20 text-red-300 rounded-full text-xs">
              {alertCounts.unacknowledged} new
            </span>
          </div>
          <button
            onClick={() => {
              setChatContext(`Operations center showing ${alertCounts.critical} critical and ${alertCounts.high} high priority alerts`)
              setChatOpen(true)
            }}
            className="w-full btn-secondary text-sm flex items-center justify-center gap-2"
          >
            <Sparkles className="w-4 h-4" />
            AI Triage Assistance
          </button>
        </div>

        <div className="flex-1 overflow-y-auto">
          <AnimatePresence>
            {filteredAlerts.map((alert, i) => (
              <motion.div
                key={alert.id}
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -20 }}
                transition={{ delay: i * 0.05 }}
                onClick={() => handleAlertSelect(alert)}
                className={`p-4 border-b border-slate-800 cursor-pointer transition-colors ${
                  selectedAlert?.id === alert.id ? 'bg-slate-800' : 'hover:bg-slate-800/50'
                } ${!alert.acknowledged ? 'border-l-2' : ''} ${
                  alert.severity === 'critical' ? 'border-l-red-600' :
                  alert.severity === 'high' ? 'border-l-red-500' :
                  alert.severity === 'medium' ? 'border-l-yellow-500' : 'border-l-green-500'
                }`}
              >
                <div className="flex items-start gap-3">
                  <div className={`p-2 rounded-lg ${
                    alert.severity === 'critical' ? 'bg-red-600/20' :
                    alert.severity === 'high' ? 'bg-red-500/20' :
                    alert.severity === 'medium' ? 'bg-yellow-500/20' : 'bg-green-500/20'
                  }`}>
                    <AlertTriangle className={`w-4 h-4 ${
                      alert.severity === 'critical' ? 'text-red-400' :
                      alert.severity === 'high' ? 'text-red-300' :
                      alert.severity === 'medium' ? 'text-yellow-400' : 'text-green-400'
                    }`} />
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <span className="text-white font-medium truncate">{alert.asset_name}</span>
                      {!alert.acknowledged && (
                        <span className="w-2 h-2 rounded-full bg-blue-500" />
                      )}
                    </div>
                    <p className="text-sm text-slate-400 line-clamp-2">{alert.message}</p>
                    <div className="flex items-center gap-2 mt-1 text-xs text-slate-500">
                      <Clock className="w-3 h-3" />
                      {alert.timestamp.toLocaleTimeString()}
                    </div>
                  </div>
                  <ChevronRight className="w-4 h-4 text-slate-500" />
                </div>
              </motion.div>
            ))}
          </AnimatePresence>
        </div>

        <AnimatePresence>
          {selectedAlert && (
            <motion.div
              initial={{ y: '100%' }}
              animate={{ y: 0 }}
              exit={{ y: '100%' }}
              className="border-t border-slate-700 p-4 bg-slate-850"
            >
              <div className="flex items-center justify-between mb-3">
                <h4 className="font-medium text-white">{selectedAlert.asset_name}</h4>
                <button 
                  onClick={() => setSelectedAlert(null)}
                  className="text-slate-400 hover:text-white"
                >
                  ×
                </button>
              </div>
              <p className="text-sm text-slate-300 mb-4">{selectedAlert.message}</p>
              <div className="flex gap-2">
                {!selectedAlert.acknowledged && (
                  <button
                    onClick={() => acknowledgeAlert(selectedAlert.id)}
                    className="btn-secondary flex-1 flex items-center justify-center gap-2 text-sm"
                  >
                    <CheckCircle className="w-4 h-4" />
                    Acknowledge
                  </button>
                )}
                <button
                  onClick={() => {
                    const asset = getAlertAsset(selectedAlert)
                    setChatContext(`Alert on ${selectedAlert.asset_name}: ${selectedAlert.message}. What actions should I take?`)
                    setChatOpen(true)
                    if (asset) setSelectedAsset(asset)
                  }}
                  className="btn-primary flex-1 flex items-center justify-center gap-2 text-sm"
                >
                  <Sparkles className="w-4 h-4" />
                  Ask AI
                </button>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  )
}

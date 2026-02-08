import { useState, useEffect, useMemo, useCallback } from 'react'
import MapGL from 'react-map-gl/maplibre'
import DeckGL from '@deck.gl/react'
import { ScatterplotLayer, ArcLayer } from '@deck.gl/layers'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  Play, RotateCcw, AlertTriangle, CheckCircle, 
  Gauge, Clock, ChevronRight, Zap
} from 'lucide-react'
import { useAppStore } from '@/stores/appStore'
import type { Asset, SimulationResult, NetworkEdge } from '@/types'
import 'maplibre-gl/dist/maplibre-gl.css'

const getInitialViewState = (assets: {latitude: number, longitude: number}[]) => {
  if (assets.length === 0) return { latitude: 31.9, longitude: -102.2, zoom: 9, pitch: 40, bearing: 0 }
  const lats = assets.map(a => a.latitude).filter(Boolean)
  const lons = assets.map(a => a.longitude).filter(Boolean)
  const minLat = Math.min(...lats), maxLat = Math.max(...lats)
  const minLon = Math.min(...lons), maxLon = Math.max(...lons)
  const centerLat = (minLat + maxLat) / 2
  const centerLon = (minLon + maxLon) / 2
  const latRange = maxLat - minLat
  const lonRange = maxLon - minLon
  const maxRange = Math.max(latRange, lonRange)
  const zoom = maxRange < 0.5 ? 11 : maxRange < 1 ? 10 : maxRange < 2 ? 9 : 8
  return { latitude: centerLat, longitude: centerLon, zoom, pitch: 40, bearing: 0 }
}

const COLORS = {
  source: [239, 68, 68],
  target: [59, 130, 246],
  cascade: [245, 158, 11],
  safe: [16, 185, 129],
}

type SimStep = 'select-source' | 'select-targets' | 'configure' | 'running' | 'results'

export default function SimulationPage() {
  const [assets, setAssets] = useState<Asset[]>([])
  const [edges, setEdges] = useState<NetworkEdge[]>([])
  const [loading, setLoading] = useState(true)
  const [step, setStep] = useState<SimStep>('select-source')
  const [sourceAsset, setSourceAsset] = useState<Asset | null>(null)
  const [targetAssets, setTargetAssets] = useState<Asset[]>([])
  const [pressureChange, setPressureChange] = useState(-50)
  const [simulation, setSimulation] = useState<SimulationResult | null>(null)
  const [animationProgress, setAnimationProgress] = useState(0)
  const [isAnimating, setIsAnimating] = useState(false)
  const [viewState, setViewState] = useState<ReturnType<typeof getInitialViewState> | null>(null)
  const { setChatOpen, setPendingPrompt } = useAppStore()

  useEffect(() => {
    Promise.all([
      fetch('/api/assets').then(r => r.json()),
      fetch('/api/assets/edges/all').then(r => r.json())
    ]).then(([assetsData, edgesData]) => {
      setAssets(assetsData)
      setEdges(edgesData)
      setViewState(getInitialViewState(assetsData))
    }).finally(() => setLoading(false))
  }, [])

  useEffect(() => {
    if (!isAnimating || !simulation) return
    const duration = simulation.pressure_cascade.length * 1000
    const startTime = Date.now()
    const animate = () => {
      const elapsed = Date.now() - startTime
      const progress = Math.min(elapsed / duration, 1)
      setAnimationProgress(progress)
      if (progress < 1) requestAnimationFrame(animate)
      else setIsAnimating(false)
    }
    requestAnimationFrame(animate)
  }, [isAnimating, simulation])

  const handleAssetClick = useCallback((asset: Asset) => {
    if (step === 'select-source') {
      setSourceAsset(asset)
      setStep('select-targets')
    } else if (step === 'select-targets') {
      if (asset.asset_id === sourceAsset?.asset_id) return
      if (targetAssets.find(t => t.asset_id === asset.asset_id)) {
        setTargetAssets(targetAssets.filter(t => t.asset_id !== asset.asset_id))
      } else if (targetAssets.length < 5) {
        setTargetAssets([...targetAssets, asset])
      }
    }
  }, [step, sourceAsset, targetAssets])

  const runSimulation = async () => {
    if (!sourceAsset || targetAssets.length === 0) return
    setStep('running')
    setSimulation(null)
    
    try {
      const response = await fetch('/api/simulation/pressure-cascade', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          source_asset_id: sourceAsset.asset_id,
          target_asset_ids: targetAssets.map(t => t.asset_id),
          pressure_change_psi: pressureChange,
        }),
      })
      
      if (!response.ok) {
        throw new Error(`Simulation request failed: HTTP ${response.status}`)
      }
      
      const result = await response.json()
      
      if (!result.pressure_cascade || result.pressure_cascade.length === 0) {
        console.warn('Simulation returned empty pressure cascade')
      }
      
      setSimulation(result)
      setStep('results')
      setAnimationProgress(0)
      setIsAnimating(true)
    } catch (e) {
      console.error('Simulation failed:', e)
      setStep('configure')
    }
  }

  const resetSimulation = () => {
    setSourceAsset(null)
    setTargetAssets([])
    setSimulation(null)
    setAnimationProgress(0)
    setIsAnimating(false)
    setStep('select-source')
  }

  const getAssetColor = (asset: Asset): [number, number, number, number] => {
    if (sourceAsset?.asset_id === asset.asset_id) return [...COLORS.source, 255] as [number, number, number, number]
    if (targetAssets.find(t => t.asset_id === asset.asset_id)) return [...COLORS.target, 255] as [number, number, number, number]
    
    if (simulation && step === 'results') {
      const cascadeItem = simulation.pressure_cascade.find(p => p.asset_id === asset.asset_id)
      if (cascadeItem) {
        const idx = simulation.pressure_cascade.indexOf(cascadeItem)
        const threshold = (idx + 1) / simulation.pressure_cascade.length
        if (animationProgress >= threshold) {
          if (cascadeItem.risk_level === 'critical') return [220, 38, 38, 255]
          if (cascadeItem.risk_level === 'high') return [239, 68, 68, 255]
          if (cascadeItem.risk_level === 'medium') return [245, 158, 11, 255]
          return [...COLORS.safe, 255] as [number, number, number, number]
        }
      }
    }
    return [100, 116, 139, 150]
  }

  const assetLookup = useMemo(() => {
    const lookup = new Map<string, Asset>()
    assets.forEach(a => lookup.set(a.asset_id, a))
    return lookup
  }, [assets])

  const layers = useMemo(() => {
    const layerList = []

    layerList.push(
      new ArcLayer({
        id: 'pipeline-edges',
        data: edges.filter(e => e.source_system !== 'autogl'),
        getSourcePosition: (d: NetworkEdge) => {
          const src = assetLookup.get(d.source_asset_id)
          return src ? [src.longitude, src.latitude] : [0, 0]
        },
        getTargetPosition: (d: NetworkEdge) => {
          const tgt = assetLookup.get(d.target_asset_id)
          return tgt ? [tgt.longitude, tgt.latitude] : [0, 0]
        },
        getSourceColor: [100, 116, 139, 120] as [number, number, number, number],
        getTargetColor: [100, 116, 139, 120] as [number, number, number, number],
        getWidth: 2,
        pickable: false,
      })
    )

    if (simulation && step === 'results') {
      const cascadeArcs = simulation.pressure_cascade.slice(0, -1).map((item, i) => ({
        source: item,
        target: simulation.pressure_cascade[i + 1],
        progress: animationProgress,
      }))

      layerList.push(
        new ArcLayer({
          id: 'cascade-flow',
          data: cascadeArcs.filter((_, i) => animationProgress > (i + 1) / simulation.pressure_cascade.length),
          getSourcePosition: (d: any) => [d.source.longitude, d.source.latitude],
          getTargetPosition: (d: any) => [d.target.longitude, d.target.latitude],
          getSourceColor: [245, 158, 11, 200],
          getTargetColor: [239, 68, 68, 200],
          getWidth: 4,
          getTilt: 10,
        })
      )
    }

    layerList.push(
      new ScatterplotLayer({
        id: 'assets',
        data: assets,
        getPosition: (d: Asset) => [d.longitude, d.latitude],
        getFillColor: (d: Asset) => getAssetColor(d),
        getRadius: (d: Asset) => {
          if (sourceAsset?.asset_id === d.asset_id) return 1000
          if (targetAssets.find(t => t.asset_id === d.asset_id)) return 800
          return 500
        },
        radiusMinPixels: 8,
        radiusMaxPixels: 25,
        pickable: step === 'select-source' || step === 'select-targets',
        onClick: ({ object }) => object && handleAssetClick(object as Asset),
        updateTriggers: {
          getFillColor: [sourceAsset, targetAssets, simulation, animationProgress],
          getRadius: [sourceAsset, targetAssets],
        },
      })
    )

    if (sourceAsset) {
      layerList.push(
        new ScatterplotLayer({
          id: 'source-highlight',
          data: [sourceAsset],
          getPosition: (d: Asset) => [d.longitude, d.latitude],
          getFillColor: [0, 0, 0, 0] as [number, number, number, number],
          getLineColor: [...COLORS.source, 255] as [number, number, number, number],
          getRadius: 1500,
          radiusMinPixels: 30,
          radiusMaxPixels: 50,
          stroked: true,
          lineWidthMinPixels: 3,
        })
      )
    }

    return layerList
  }, [assets, edges, assetLookup, sourceAsset, targetAssets, simulation, animationProgress, step, handleAssetClick])

  if (loading) {
    return (
      <div className="h-full flex items-center justify-center">
        <div className="text-center">
          <Gauge className="w-12 h-12 text-snowcore-500 animate-pulse mx-auto mb-4" />
          <p className="text-slate-400">Loading simulation environment...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="h-full flex">
      <div className="flex-1 relative">
        <DeckGL
          initialViewState={viewState || { latitude: 31.9, longitude: -102.2, zoom: 9, pitch: 40, bearing: 0 }}
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
            <div className="flex items-center gap-3 mb-4">
              <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${
                step === 'results' ? 'bg-green-600/20' : 'bg-snowcore-600/20'
              }`}>
                {step === 'results' ? (
                  <CheckCircle className="w-5 h-5 text-green-400" />
                ) : (
                  <Zap className="w-5 h-5 text-snowcore-400" />
                )}
              </div>
              <div>
                <h3 className="font-medium text-white">Pressure Cascade Simulation</h3>
                <p className="text-sm text-slate-400">
                  {step === 'select-source' && 'Click an asset to select as pressure change source'}
                  {step === 'select-targets' && `Select up to 5 downstream targets (${targetAssets.length}/5)`}
                  {step === 'configure' && 'Configure simulation parameters'}
                  {step === 'running' && 'Running simulation...'}
                  {step === 'results' && 'Simulation complete'}
                </p>
              </div>
            </div>

            <div className="flex gap-2 mb-4">
              {['select-source', 'select-targets', 'configure', 'results'].map((s, i) => (
                <div 
                  key={s}
                  className={`h-1 flex-1 rounded-full transition-all ${
                    ['select-source', 'select-targets', 'configure', 'running', 'results'].indexOf(step) >= i
                      ? 'bg-snowcore-500'
                      : 'bg-slate-700'
                  }`}
                />
              ))}
            </div>

            {step === 'select-source' && (
              <div className="text-xs text-slate-400 space-y-2 mb-4 p-3 bg-slate-800/30 rounded-lg">
                <p className="font-medium text-slate-300">What is Pressure Cascade Simulation?</p>
                <p>Model how a pressure drop at one asset propagates through the connected pipeline network.</p>
                <p className="font-medium text-slate-300 mt-2">Steps:</p>
                <ol className="list-decimal list-inside space-y-1">
                  <li>Select a source asset (pressure change origin)</li>
                  <li>Select 1-5 downstream target assets</li>
                  <li>Configure pressure change magnitude</li>
                  <li>Run simulation to see cascade effects</li>
                </ol>
              </div>
            )}

            {sourceAsset && (
              <div className="mb-3 p-2 bg-red-500/10 rounded-lg border border-red-500/30">
                <div className="flex items-center gap-2 text-sm">
                  <div className="w-3 h-3 rounded-full bg-red-500" />
                  <span className="text-red-300">Source:</span>
                  <span className="text-white">{sourceAsset.asset_name}</span>
                </div>
              </div>
            )}

            {targetAssets.length > 0 && (
              <div className="mb-3 p-2 bg-blue-500/10 rounded-lg border border-blue-500/30">
                <div className="text-sm text-blue-300 mb-1">Targets:</div>
                {targetAssets.map(t => (
                  <div key={t.asset_id} className="flex items-center gap-2 text-xs text-white">
                    <div className="w-2 h-2 rounded-full bg-blue-500" />
                    {t.asset_name}
                  </div>
                ))}
              </div>
            )}

            {(step === 'select-targets' || step === 'configure') && targetAssets.length > 0 && (
              <div className="space-y-3">
                <div>
                  <label className="text-xs text-slate-400 block mb-1">Pressure Change (PSI)</label>
                  <input
                    type="range"
                    min="-200"
                    max="0"
                    value={pressureChange}
                    onChange={(e) => setPressureChange(Number(e.target.value))}
                    className="w-full"
                  />
                  <div className="text-center text-sm text-white font-medium">{pressureChange} PSI</div>
                </div>

                <button
                  onClick={runSimulation}
                  className="btn-primary w-full flex items-center justify-center gap-2"
                >
                  <Play className="w-4 h-4" />
                  Run Simulation
                </button>
              </div>
            )}

            {step === 'results' && (
              <button
                onClick={resetSimulation}
                className="btn-secondary w-full flex items-center justify-center gap-2"
              >
                <RotateCcw className="w-4 h-4" />
                Reset
              </button>
            )}
          </div>
        </div>
      </div>

      <AnimatePresence>
        {simulation && step === 'results' && (
          <motion.div
            initial={{ x: 400, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            exit={{ x: 400, opacity: 0 }}
            className="w-96 bg-slate-900 border-l border-slate-800 overflow-y-auto"
          >
            <div className="p-4 border-b border-slate-800">
              <h3 className="font-semibold text-white mb-1">Simulation Results</h3>
              <p className="text-sm text-slate-400">
                Impact: {simulation.estimated_impact_mcfd.toLocaleString()} MCFD
              </p>
            </div>

            <div className="p-4 space-y-4">
              <div>
                <h4 className="text-sm font-medium text-white mb-2 flex items-center gap-2">
                  <Clock className="w-4 h-4 text-slate-400" />
                  Pressure Cascade Timeline
                </h4>
                <div className="space-y-2">
                  {simulation.pressure_cascade.map((item, i) => (
                    <motion.div
                      key={item.asset_id}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ 
                        opacity: animationProgress > (i + 1) / simulation.pressure_cascade.length ? 1 : 0.3,
                        x: 0 
                      }}
                      transition={{ delay: i * 0.1 }}
                      className="flex items-center gap-3 p-2 rounded-lg bg-slate-800/50"
                    >
                      <div className={`w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold ${
                        item.risk_level === 'critical' ? 'bg-red-600' :
                        item.risk_level === 'high' ? 'bg-red-500' :
                        item.risk_level === 'medium' ? 'bg-yellow-500' : 'bg-green-500'
                      }`}>
                        {i + 1}
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="text-sm text-white truncate">{item.asset_name}</div>
                        <div className="text-xs text-slate-400">
                          +{item.time_offset_min}min · {item.pressure_delta.toFixed(0)} PSI
                        </div>
                      </div>
                      <div className={`text-xs px-2 py-1 rounded ${
                        item.risk_level === 'critical' ? 'bg-red-500/20 text-red-300' :
                        item.risk_level === 'high' ? 'bg-red-500/20 text-red-300' :
                        item.risk_level === 'medium' ? 'bg-yellow-500/20 text-yellow-300' :
                        'bg-green-500/20 text-green-300'
                      }`}>
                        {item.new_pressure.toFixed(0)} PSI
                      </div>
                    </motion.div>
                  ))}
                </div>
              </div>

              <div>
                <h4 className="text-sm font-medium text-white mb-2 flex items-center gap-2">
                  <AlertTriangle className="w-4 h-4 text-yellow-400" />
                  Recommended Actions
                </h4>
                <div className="space-y-2">
                  {simulation.recommended_actions.map((action, i) => (
                    <div 
                      key={i}
                      className={`p-2 rounded-lg text-sm ${
                        action.includes('CRITICAL') 
                          ? 'bg-red-500/20 text-red-200 border border-red-500/30'
                          : 'bg-slate-800/50 text-slate-300'
                      }`}
                    >
                      {action}
                    </div>
                  ))}
                </div>
              </div>

              <button
                onClick={() => {
                  setPendingPrompt(`Simulation shows ${simulation.pressure_cascade.filter(p => p.risk_level === 'critical' || p.risk_level === 'high').length} high-risk pressure events. What mitigation actions should I take?`)
                  setChatOpen(true)
                }}
                className="btn-primary w-full flex items-center justify-center gap-2"
              >
                Ask AI for Guidance
                <ChevronRight className="w-4 h-4" />
              </button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}

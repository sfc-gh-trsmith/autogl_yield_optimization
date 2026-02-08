import { useState, useEffect, useMemo, useCallback } from 'react'
import MapGL, { NavigationControl } from 'react-map-gl/maplibre'
import DeckGL from '@deck.gl/react'
import { ScatterplotLayer, ArcLayer } from '@deck.gl/layers'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  Sparkles, AlertTriangle, Network, 
  Info, ToggleLeft, ToggleRight, Loader2, ChevronDown, ChevronUp, Lightbulb
} from 'lucide-react'
import { useAppStore } from '@/stores/appStore'
import type { Asset, NetworkEdge, GraphPrediction } from '@/types'
import 'maplibre-gl/dist/maplibre-gl.css'

interface AutoGLInterpretation {
  total_discoveries: number
  cross_network_count: number
  same_network_count: number
  interpretation: string
}

const getInitialViewState = (assets: Asset[]) => {
  if (assets.length === 0) return { latitude: 31.9, longitude: -102.2, zoom: 8 }
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
  return { latitude: centerLat, longitude: centerLon, zoom }
}

const COLORS = {
  snowcore: [0, 119, 230],
  terafield: [230, 119, 0],
  autogl: [118, 26, 255],
  riskLow: [16, 185, 129],
  riskMedium: [245, 158, 11],
  riskHigh: [239, 68, 68],
  riskCritical: [220, 38, 38],
}

export default function NetworkDiscoveryPage() {
  const [assets, setAssets] = useState<Asset[]>([])
  const [edges, setEdges] = useState<NetworkEdge[]>([])
  const [predictions, setPredictions] = useState<GraphPrediction[]>([])
  const [loading, setLoading] = useState(true)
  const [hoveredAsset, setHoveredAsset] = useState<Asset | null>(null)
  const [viewState, setViewState] = useState<{latitude: number, longitude: number, zoom: number} | null>(null)
  const [autoGLInterpretation, setAutoGLInterpretation] = useState<AutoGLInterpretation | null>(null)
  const [interpretationLoading, setInterpretationLoading] = useState(false)
  const [showAutoGLInfo, setShowAutoGLInfo] = useState(false)
  const { showAutoGLLinks, toggleAutoGLLinks, setSelectedAsset, setChatOpen, setChatContext } = useAppStore()

  useEffect(() => {
    async function fetchData() {
      try {
        const [assetsRes, edgesRes, predsRes] = await Promise.all([
          fetch('/api/assets'),
          fetch('/api/assets/edges/all'),
          fetch('/api/predictions/link-discoveries'),
        ])
        const assetsData = await assetsRes.json()
        setAssets(assetsData)
        setEdges(await edgesRes.json())
        setPredictions(await predsRes.json())
        setViewState(getInitialViewState(assetsData))
      } catch (e) {
        console.error('Failed to fetch data:', e)
      } finally {
        setLoading(false)
      }
    }
    fetchData()
  }, [])

  useEffect(() => {
    if (showAutoGLLinks && !autoGLInterpretation && !interpretationLoading) {
      setInterpretationLoading(true)
      fetch('/api/predictions/autogl-interpretation')
        .then(res => res.json())
        .then(data => setAutoGLInterpretation(data))
        .catch(console.error)
        .finally(() => setInterpretationLoading(false))
    }
  }, [showAutoGLLinks, autoGLInterpretation, interpretationLoading])

  const assetLookup = useMemo(() => {
    const lookup = new globalThis.Map<string, Asset>()
    assets.forEach(a => lookup.set(a.asset_id, a))
    return lookup
  }, [assets])

  const handleAssetClick = useCallback((asset: Asset) => {
    setSelectedAsset(asset)
    setChatContext(`Viewing ${asset.asset_name} (${asset.asset_type}) - ${asset.source_system} asset in ${asset.field}`)
    setChatOpen(true)
  }, [setSelectedAsset, setChatContext, setChatOpen])

  const getAssetColor = (asset: Asset): [number, number, number] => {
    if (asset.risk_score && asset.risk_score > 0.8) return COLORS.riskCritical as [number, number, number]
    if (asset.risk_score && asset.risk_score > 0.6) return COLORS.riskHigh as [number, number, number]
    if (asset.source_system?.toUpperCase() === 'SNOWCORE') return COLORS.snowcore as [number, number, number]
    if (asset.source_system?.toUpperCase() === 'TERAFIELD') return COLORS.terafield as [number, number, number]
    return [100, 116, 139]
  }

  const layers = useMemo(() => {
    const layerList = []

    const existingEdges = edges.filter(e => e.source_system !== 'autogl')
    layerList.push(
      new ArcLayer({
        id: 'existing-edges',
        data: existingEdges,
        getSourcePosition: (d: NetworkEdge) => {
          const src = assetLookup.get(d.source_asset_id)
          return src ? [src.longitude, src.latitude] : [0, 0]
        },
        getTargetPosition: (d: NetworkEdge) => {
          const tgt = assetLookup.get(d.target_asset_id)
          return tgt ? [tgt.longitude, tgt.latitude] : [0, 0]
        },
        getSourceColor: (d: NetworkEdge) => {
          const src = assetLookup.get(d.source_asset_id)
          return (src?.source_system?.toUpperCase() === 'SNOWCORE' ? [...COLORS.snowcore, 150] : [...COLORS.terafield, 150]) as [number, number, number, number]
        },
        getTargetColor: (d: NetworkEdge) => {
          const tgt = assetLookup.get(d.target_asset_id)
          return (tgt?.source_system?.toUpperCase() === 'SNOWCORE' ? [...COLORS.snowcore, 150] : [...COLORS.terafield, 150]) as [number, number, number, number]
        },
        getWidth: 2,
        pickable: false,
      })
    )

    if (showAutoGLLinks) {
      layerList.push(
        new ArcLayer({
          id: 'predicted-edges',
          data: predictions,
          getSourcePosition: (d: GraphPrediction) => [d.source_lon!, d.source_lat!],
          getTargetPosition: (d: GraphPrediction) => [d.target_lon!, d.target_lat!],
          getSourceColor: [...COLORS.autogl, 255] as [number, number, number, number],
          getTargetColor: [...COLORS.autogl, 255] as [number, number, number, number],
          getWidth: (d: GraphPrediction) => 2 + d.confidence * 3,
          getTilt: 15,
          pickable: true,
          onHover: () => {},
        })
      )
    }

    layerList.push(
      new ScatterplotLayer({
        id: 'assets',
        data: assets,
        getPosition: (d: Asset) => [d.longitude, d.latitude],
        getFillColor: (d: Asset) => [...getAssetColor(d), 200],
        getRadius: (d: Asset) => {
          if (d.asset_type === 'processing_plant') return 800
          if (d.asset_type === 'compressor_station') return 600
          return 400
        },
        radiusMinPixels: 6,
        radiusMaxPixels: 20,
        pickable: true,
        onHover: ({ object }) => setHoveredAsset(object as Asset | null),
        onClick: ({ object }) => object && handleAssetClick(object as Asset),
      })
    )

    const highRiskAssets = assets.filter(a => a.risk_score && a.risk_score > 0.7)
    if (highRiskAssets.length > 0) {
      layerList.push(
        new ScatterplotLayer({
          id: 'risk-indicators',
          data: highRiskAssets,
          getPosition: (d: Asset) => [d.longitude, d.latitude],
          getFillColor: [0, 0, 0, 0],
          getLineColor: COLORS.riskHigh as [number, number, number, number],
          getRadius: 1000,
          radiusMinPixels: 20,
          radiusMaxPixels: 40,
          stroked: true,
          lineWidthMinPixels: 2,
          pickable: false,
        })
      )
    }

    return layerList
  }, [assets, edges, predictions, showAutoGLLinks, assetLookup, handleAssetClick])

  const stats = useMemo(() => ({
    snowcore: assets.filter(a => a.source_system?.toUpperCase() === 'SNOWCORE').length,
    terafield: assets.filter(a => a.source_system?.toUpperCase() === 'TERAFIELD').length,
    discovered: predictions.length,
    highRisk: assets.filter(a => a.risk_score && a.risk_score > 0.7).length,
  }), [assets, predictions])

  if (loading) {
    return (
      <div className="h-full flex items-center justify-center">
        <div className="text-center">
          <Network className="w-12 h-12 text-snowcore-500 animate-pulse mx-auto mb-4" />
          <p className="text-slate-400">Loading network topology...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="h-full relative">
      <DeckGL
        initialViewState={viewState || { latitude: 31.9, longitude: -102.2, zoom: 8 }}
        controller={true}
        layers={layers}
        style={{ position: 'absolute', inset: '0' }}
      >
        <MapGL
          mapStyle="https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json"
          attributionControl={false}
        >
          <NavigationControl position="bottom-right" />
        </MapGL>
      </DeckGL>

      <div className="absolute top-4 left-4 z-10 space-y-3 max-h-[calc(100vh-120px)] overflow-y-auto scrollbar-thin scrollbar-thumb-slate-700">
        <div className="glass-panel p-4 space-y-3">
          <h3 className="text-sm font-medium text-white flex items-center gap-2">
            <Network className="w-4 h-4" />
            Network Status
          </h3>
          
          <div className="grid grid-cols-2 gap-3 text-sm">
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-full" style={{ backgroundColor: `rgb(${COLORS.snowcore.join(',')})` }} />
              <span className="text-slate-300">SnowCore</span>
              <span className="text-white font-medium ml-auto">{stats.snowcore}</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-full" style={{ backgroundColor: `rgb(${COLORS.terafield.join(',')})` }} />
              <span className="text-slate-300">TeraField</span>
              <span className="text-white font-medium ml-auto">{stats.terafield}</span>
            </div>
          </div>

          <div className="pt-2 border-t border-slate-700">
            <button
              onClick={toggleAutoGLLinks}
              className={`w-full flex items-center justify-between p-2 rounded-lg transition-all ${
                showAutoGLLinks 
                  ? 'bg-autogl-600/20 border border-autogl-500/50' 
                  : 'bg-slate-800/50 hover:bg-slate-800'
              }`}
            >
              <div className="flex items-center gap-2">
                <Sparkles className={`w-4 h-4 ${showAutoGLLinks ? 'text-autogl-400' : 'text-slate-400'}`} />
                <span className={`text-sm ${showAutoGLLinks ? 'text-autogl-300' : 'text-slate-300'}`}>
                  AutoGL Discoveries
                </span>
                <div className="relative group">
                  <Info className="w-3.5 h-3.5 text-slate-500 cursor-help" />
                  <div className="absolute left-0 bottom-full mb-2 w-80 p-3 bg-slate-800 rounded-lg 
                                  border border-slate-700 opacity-0 invisible group-hover:opacity-100 
                                  group-hover:visible transition-all z-50 text-left shadow-xl"
                       onClick={(e) => e.stopPropagation()}>
                    <p className="font-medium text-autogl-300 mb-2 text-xs">AutoGL Graph Neural Network Analysis</p>
                    <p className="text-slate-400 mb-2 text-xs leading-relaxed">
                      Identifies hidden connections between SnowCore and TeraField networks using 
                      graph-based machine learning on asset topology, flow patterns, and sensor correlations.
                    </p>
                    <p className="text-slate-500 text-xs mb-2">
                      Purple arcs represent discovered links with line thickness indicating confidence level.
                    </p>
                    {interpretationLoading ? (
                      <div className="flex items-center gap-2 text-slate-500 text-xs border-t border-slate-700 pt-2 mt-2">
                        <Loader2 className="w-3 h-3 animate-spin" />
                        <span>Generating AI interpretation...</span>
                      </div>
                    ) : autoGLInterpretation ? (
                      <div className="border-t border-slate-700 pt-2 mt-2">
                        <p className="text-autogl-200 font-medium mb-1 text-xs">AI Insight:</p>
                        <p className="text-slate-300 text-xs leading-relaxed">{autoGLInterpretation.interpretation}</p>
                        <div className="flex gap-3 mt-2 text-xs text-slate-500">
                          <span>{autoGLInterpretation.cross_network_count} cross-network</span>
                          <span>{autoGLInterpretation.same_network_count} same-network</span>
                        </div>
                      </div>
                    ) : null}
                  </div>
                </div>
              </div>
              {showAutoGLLinks ? (
                <ToggleRight className="w-5 h-5 text-autogl-400" />
              ) : (
                <ToggleLeft className="w-5 h-5 text-slate-500" />
              )}
            </button>
            
            <AnimatePresence>
              {showAutoGLLinks && (
                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: 'auto' }}
                  exit={{ opacity: 0, height: 0 }}
                  className="mt-2 p-2 bg-autogl-900/30 rounded-lg border border-autogl-500/20"
                >
                  <div className="flex items-center gap-2 text-sm">
                    <div className="w-3 h-3 rounded-full" style={{ backgroundColor: `rgb(${COLORS.autogl.join(',')})` }} />
                    <span className="text-autogl-300">New Links Found</span>
                    <span className="text-autogl-200 font-bold ml-auto">{stats.discovered}</span>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </div>

          {stats.highRisk > 0 && (
            <div className="pt-2 border-t border-slate-700">
              <div className="flex items-center gap-2 text-sm text-risk-high">
                <AlertTriangle className="w-4 h-4" />
                <span>{stats.highRisk} High Risk Assets</span>
              </div>
            </div>
          )}
        </div>

<div className="glass-panel p-3">
          <button
            onClick={() => setShowAutoGLInfo(!showAutoGLInfo)}
            className="w-full flex items-center justify-between text-left"
          >
            <div className="flex items-center gap-2">
              <Lightbulb className="w-4 h-4 text-autogl-400" />
              <span className="text-sm font-medium text-white">Why This Matters</span>
            </div>
            {showAutoGLInfo ? (
              <ChevronUp className="w-4 h-4 text-slate-400" />
            ) : (
              <ChevronDown className="w-4 h-4 text-slate-400" />
            )}
          </button>
          
          <AnimatePresence>
            {showAutoGLInfo && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                exit={{ opacity: 0, height: 0 }}
                className="overflow-hidden"
              >
                <div className="pt-3 space-y-3 text-xs">
                  <div className="bg-autogl-900/30 border border-autogl-500/20 rounded-lg p-3">
                    <p className="text-autogl-200 leading-relaxed">
                      Cross-network discoveries reveal <span className="text-white font-medium">integration opportunities</span> — 
                      where SnowCore and TeraField infrastructure can be connected to reduce redundancy, 
                      optimize flow routing, and unlock merger synergies worth <span className="text-white font-medium">millions in operational savings</span>.
                    </p>
                  </div>
                  
                  <div className="border-t border-slate-700 pt-3">
                    <p className="text-slate-300 font-medium mb-2">Reading the map:</p>
                    <div className="space-y-1.5">
                      <div className="flex items-center gap-2">
                        <div className="w-2 h-2 rounded-full flex-shrink-0" style={{ backgroundColor: `rgb(${COLORS.snowcore.join(',')})` }} />
                        <span className="text-snowcore-300">Blue</span>
                        <span className="text-slate-500">—</span>
                        <span className="text-slate-400">SnowCore assets</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <div className="w-2 h-2 rounded-full flex-shrink-0" style={{ backgroundColor: `rgb(${COLORS.terafield.join(',')})` }} />
                        <span className="text-terafield-300">Green</span>
                        <span className="text-slate-500">—</span>
                        <span className="text-slate-400">TeraField assets</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <div className="w-2 h-2 rounded-full flex-shrink-0" style={{ backgroundColor: `rgb(${COLORS.autogl.join(',')})` }} />
                        <span className="text-autogl-300">Purple arcs</span>
                        <span className="text-slate-500">—</span>
                        <span className="text-slate-400">Discovered connections</span>
                      </div>
                    </div>
                  </div>
                  
                  <p className="text-slate-500 pt-2 border-t border-slate-700">
                    <span className="text-slate-400">Thicker arcs</span> = higher confidence. Click any asset for details.
                  </p>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>

      <AnimatePresence>
        {hoveredAsset && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 10 }}
            className="absolute bottom-4 left-4 z-10 glass-panel p-4 min-w-64"
          >
            <div className="flex items-start gap-3">
              <div 
                className="w-10 h-10 rounded-lg flex items-center justify-center"
                style={{ backgroundColor: `rgba(${getAssetColor(hoveredAsset).join(',')}, 0.3)` }}
              >
                <Network 
                  className="w-5 h-5" 
                  style={{ color: `rgb(${getAssetColor(hoveredAsset).join(',')})` }} 
                />
              </div>
              <div className="flex-1">
                <h4 className="font-medium text-white">{hoveredAsset.asset_name}</h4>
                <p className="text-sm text-slate-400">{hoveredAsset.asset_type}</p>
                <div className="flex items-center gap-3 mt-2 text-xs">
                  <span className={`px-2 py-0.5 rounded-full ${
                    hoveredAsset.source_system === 'snowcore' 
                      ? 'bg-snowcore-600/20 text-snowcore-300' 
                      : 'bg-terafield-600/20 text-terafield-300'
                  }`}>
                    {hoveredAsset.source_system}
                  </span>
                  {hoveredAsset.risk_score && hoveredAsset.risk_score > 0.5 && (
                    <span className={`risk-indicator ${
                      hoveredAsset.risk_score > 0.8 ? 'risk-critical' :
                      hoveredAsset.risk_score > 0.6 ? 'risk-high' : 'risk-medium'
                    }`}>
                      Risk: {(hoveredAsset.risk_score * 100).toFixed(0)}%
                    </span>
                  )}
                </div>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      <div className="absolute top-4 right-4 z-10">
        <div className="glass-panel p-2">
          <div className="text-xs text-slate-400 space-y-1">
            <div className="flex items-center gap-2">
              <div className="w-4 h-1 rounded" style={{ backgroundColor: `rgb(${COLORS.snowcore.join(',')})` }} />
              <span>SnowCore Network</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-4 h-1 rounded" style={{ backgroundColor: `rgb(${COLORS.terafield.join(',')})` }} />
              <span>TeraField Network</span>
            </div>
            {showAutoGLLinks && (
              <div className="flex items-center gap-2">
                <div className="w-4 h-1 rounded" style={{ backgroundColor: `rgb(${COLORS.autogl.join(',')})` }} />
                <span>AutoGL Discovery</span>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { 
  FileSearch, FileText, Image, AlertTriangle, 
  Search, Filter, ChevronRight, Sparkles, Network,
  ExternalLink, Clock
} from 'lucide-react'
import { useAppStore } from '@/stores/appStore'
import type { Asset } from '@/types'

interface Document {
  id: string
  title: string
  doc_type: 'p_and_id' | 'maintenance_log' | 'inspection_report' | 'safety_protocol'
  asset_ids: string[]
  relevance_score: number
  last_updated: Date
  summary: string
  thumbnail?: string
}

export default function EngineerPage() {
  const [assets, setAssets] = useState<Asset[]>([])
  const [documents, setDocuments] = useState<Document[]>([])
  const [loading, setLoading] = useState(true)
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedDoc, setSelectedDoc] = useState<Document | null>(null)
  const [selectedAssetFilter, setSelectedAssetFilter] = useState<Asset | null>(null)
  const [docTypeFilter, setDocTypeFilter] = useState<string | null>(null)
  const { setChatOpen, setPendingPrompt, setSelectedAsset } = useAppStore()

  useEffect(() => {
    async function fetchData() {
      try {
        const assetsRes = await fetch('/api/assets')
        const assetsData = await assetsRes.json()
        setAssets(assetsData)

        const mockDocs: Document[] = [
          { id: 'd1', title: 'Delaware Basin Main Line P&ID', doc_type: 'p_and_id', asset_ids: ['WELL_001', 'COMP_001'], relevance_score: 0.95, last_updated: new Date('2024-11-15'), summary: 'Primary flow diagram showing the Delaware Basin main line configuration with valve positions and instrument locations.' },
          { id: 'd2', title: 'Compressor Station Alpha Maintenance Log', doc_type: 'maintenance_log', asset_ids: ['COMP_001'], relevance_score: 0.88, last_updated: new Date('2024-12-01'), summary: 'Weekly maintenance records including vibration analysis and bearing inspections.' },
          { id: 'd3', title: 'Processing Plant Bravo Safety Inspection', doc_type: 'inspection_report', asset_ids: ['PROC_001'], relevance_score: 0.82, last_updated: new Date('2024-10-20'), summary: 'Quarterly safety inspection covering emergency shutdown systems and relief valve testing.' },
          { id: 'd4', title: 'TeraField Integration Safety Protocol', doc_type: 'safety_protocol', asset_ids: [], relevance_score: 0.91, last_updated: new Date('2024-11-01'), summary: 'Standard operating procedures for safely integrating TeraField SCADA systems with SnowCore infrastructure.' },
          { id: 'd5', title: 'Gathering System Junction 7 P&ID', doc_type: 'p_and_id', asset_ids: ['JCT_007'], relevance_score: 0.78, last_updated: new Date('2024-09-15'), summary: 'Detailed piping diagram for junction point connecting three major gathering lines.' },
          { id: 'd6', title: 'High Pressure Well Cluster Inspection', doc_type: 'inspection_report', asset_ids: ['WELL_015', 'WELL_016', 'WELL_017'], relevance_score: 0.85, last_updated: new Date('2024-11-28'), summary: 'Annual inspection of high-pressure wells including casing integrity and BOP certification.' },
          { id: 'd7', title: 'Emergency Response Procedure - Permian', doc_type: 'safety_protocol', asset_ids: [], relevance_score: 0.94, last_updated: new Date('2024-08-01'), summary: 'Comprehensive emergency response procedures for all Permian Basin facilities.' },
          { id: 'd8', title: 'Compressor Station Beta Overhaul Log', doc_type: 'maintenance_log', asset_ids: ['COMP_002'], relevance_score: 0.79, last_updated: new Date('2024-11-10'), summary: 'Major overhaul documentation including parts replacement and performance testing.' },
        ]
        setDocuments(mockDocs)
      } catch (e) {
        console.error('Failed to fetch engineer data:', e)
      } finally {
        setLoading(false)
      }
    }
    fetchData()
  }, [])

  const filteredDocuments = documents.filter(doc => {
    const matchesSearch = !searchQuery || 
      doc.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      doc.summary.toLowerCase().includes(searchQuery.toLowerCase())
    const matchesType = !docTypeFilter || doc.doc_type === docTypeFilter
    const matchesAsset = !selectedAssetFilter || 
      doc.asset_ids.includes(selectedAssetFilter.asset_id)
    return matchesSearch && matchesType && matchesAsset
  })

  const getDocIcon = (type: string) => {
    switch (type) {
      case 'p_and_id': return Image
      case 'maintenance_log': return FileText
      case 'inspection_report': return AlertTriangle
      case 'safety_protocol': return FileSearch
      default: return FileText
    }
  }

  const getDocTypeLabel = (type: string) => {
    switch (type) {
      case 'p_and_id': return 'P&ID'
      case 'maintenance_log': return 'Maintenance'
      case 'inspection_report': return 'Inspection'
      case 'safety_protocol': return 'Safety'
      default: return type
    }
  }

  const getDocTypeColor = (type: string) => {
    switch (type) {
      case 'p_and_id': return 'bg-blue-500/20 text-blue-300'
      case 'maintenance_log': return 'bg-green-500/20 text-green-300'
      case 'inspection_report': return 'bg-yellow-500/20 text-yellow-300'
      case 'safety_protocol': return 'bg-red-500/20 text-red-300'
      default: return 'bg-slate-500/20 text-slate-300'
    }
  }

  if (loading) {
    return (
      <div className="h-full flex items-center justify-center">
        <div className="text-center">
          <FileSearch className="w-12 h-12 text-snowcore-500 animate-pulse mx-auto mb-4" />
          <p className="text-slate-400">Loading document intelligence...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="h-full flex">
      <div className="w-80 bg-slate-900/50 border-r border-slate-800 flex flex-col">
        <div className="p-4 border-b border-slate-800">
          <h3 className="font-medium text-white mb-3 flex items-center gap-2">
            <Filter className="w-4 h-4" />
            Document Filters
          </h3>
          
          <div className="relative mb-3">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search documents..."
              className="input-field pl-10"
            />
          </div>

          <div className="space-y-2">
            <p className="text-xs text-slate-400 uppercase tracking-wider">Document Type</p>
            <div className="flex flex-wrap gap-1">
              {['p_and_id', 'maintenance_log', 'inspection_report', 'safety_protocol'].map(type => (
                <button
                  key={type}
                  onClick={() => setDocTypeFilter(docTypeFilter === type ? null : type)}
                  className={`px-2 py-1 rounded text-xs transition-colors ${
                    docTypeFilter === type
                      ? getDocTypeColor(type) + ' border border-current'
                      : 'bg-slate-800 text-slate-400 hover:bg-slate-700'
                  }`}
                >
                  {getDocTypeLabel(type)}
                </button>
              ))}
            </div>
          </div>
        </div>

        <div className="p-4 border-b border-slate-800">
          <p className="text-xs text-slate-400 uppercase tracking-wider mb-2">Filter by Asset</p>
          <div className="max-h-48 overflow-y-auto space-y-1">
            {selectedAssetFilter && (
              <div className="flex items-center justify-between p-2 bg-snowcore-600/20 rounded-lg mb-2">
                <span className="text-sm text-snowcore-300 truncate">{selectedAssetFilter.asset_name}</span>
                <button 
                  onClick={() => setSelectedAssetFilter(null)}
                  className="text-slate-400 hover:text-white"
                >
                  ×
                </button>
              </div>
            )}
            {!selectedAssetFilter && assets.slice(0, 10).map(asset => (
              <button
                key={asset.asset_id}
                onClick={() => setSelectedAssetFilter(asset)}
                className="w-full text-left p-2 text-sm text-slate-300 hover:bg-slate-800 rounded-lg transition-colors flex items-center gap-2"
              >
                <Network className="w-3 h-3 text-slate-500" />
                <span className="truncate">{asset.asset_name}</span>
              </button>
            ))}
          </div>
        </div>

        <div className="flex-1 overflow-y-auto p-4">
          <div className="flex items-center justify-between mb-3">
            <p className="text-sm text-slate-400">{filteredDocuments.length} documents</p>
            <button
              onClick={() => {
                setPendingPrompt('Help me search technical documents for the Permian network')
                setChatOpen(true)
              }}
              className="text-xs text-autogl-400 hover:text-autogl-300 flex items-center gap-1"
            >
              <Sparkles className="w-3 h-3" />
              AI Search
            </button>
          </div>
          
          <div className="space-y-2">
            {filteredDocuments.map((doc) => {
              const DocIcon = getDocIcon(doc.doc_type)
              return (
                <motion.div
                  key={doc.id}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  onClick={() => setSelectedDoc(doc)}
                  className={`p-3 rounded-lg cursor-pointer transition-colors ${
                    selectedDoc?.id === doc.id
                      ? 'bg-slate-800 border border-slate-600'
                      : 'bg-slate-800/50 hover:bg-slate-800'
                  }`}
                >
                  <div className="flex items-start gap-3">
                    <div className={`p-2 rounded-lg ${getDocTypeColor(doc.doc_type)}`}>
                      <DocIcon className="w-4 h-4" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <h4 className="text-sm font-medium text-white truncate">{doc.title}</h4>
                      <div className="flex items-center gap-2 mt-1 text-xs text-slate-500">
                        <Clock className="w-3 h-3" />
                        {doc.last_updated.toLocaleDateString()}
                      </div>
                    </div>
                  </div>
                </motion.div>
              )
            })}
          </div>
        </div>
      </div>

      <div className="flex-1 flex flex-col">
        {selectedDoc ? (
          <>
            <div className="p-6 border-b border-slate-800">
              <div className="flex items-start justify-between">
                <div>
                  <div className="flex items-center gap-2 mb-2">
                    <span className={`px-2 py-0.5 rounded text-xs ${getDocTypeColor(selectedDoc.doc_type)}`}>
                      {getDocTypeLabel(selectedDoc.doc_type)}
                    </span>
                    <span className="text-xs text-slate-500">
                      Relevance: {(selectedDoc.relevance_score * 100).toFixed(0)}%
                    </span>
                  </div>
                  <h2 className="text-xl font-semibold text-white">{selectedDoc.title}</h2>
                  <p className="text-sm text-slate-400 mt-1">
                    Last updated: {selectedDoc.last_updated.toLocaleDateString()}
                  </p>
                </div>
                <div className="flex gap-2">
                  <button className="btn-secondary text-sm flex items-center gap-2">
                    <ExternalLink className="w-4 h-4" />
                    Open
                  </button>
                  <button
                    onClick={() => {
                      setPendingPrompt(`Analyze this document: "${selectedDoc.title}". Summary: ${selectedDoc.summary}`)
                      setChatOpen(true)
                    }}
                    className="btn-primary text-sm flex items-center gap-2"
                  >
                    <Sparkles className="w-4 h-4" />
                    Ask AI
                  </button>
                </div>
              </div>
            </div>

            <div className="flex-1 p-6 overflow-y-auto">
              <div className="max-w-3xl">
                <div className="glass-panel p-6 mb-6">
                  <h3 className="text-sm font-medium text-slate-400 uppercase tracking-wider mb-3">Summary</h3>
                  <p className="text-slate-200 leading-relaxed">{selectedDoc.summary}</p>
                </div>

                {selectedDoc.asset_ids.length > 0 && (
                  <div className="glass-panel p-6 mb-6">
                    <h3 className="text-sm font-medium text-slate-400 uppercase tracking-wider mb-3">Related Assets</h3>
                    <div className="flex flex-wrap gap-2">
                      {selectedDoc.asset_ids.map(assetId => {
                        const asset = assets.find(a => a.asset_id === assetId)
                        return (
                          <button
                            key={assetId}
                            onClick={() => asset && setSelectedAsset(asset)}
                            className="flex items-center gap-2 px-3 py-1.5 bg-slate-800 hover:bg-slate-700 rounded-lg transition-colors"
                          >
                            <Network className="w-4 h-4 text-snowcore-400" />
                            <span className="text-sm text-slate-200">{asset?.asset_name || assetId}</span>
                          </button>
                        )
                      })}
                    </div>
                  </div>
                )}

                <div className="glass-panel p-6">
                  <h3 className="text-sm font-medium text-slate-400 uppercase tracking-wider mb-3">AI Document Analysis</h3>
                  <div className="space-y-3">
                    <button
                      onClick={() => {
                        setPendingPrompt(`What are the key safety considerations from "${selectedDoc.title}"?`)
                        setChatOpen(true)
                      }}
                      className="w-full text-left p-3 bg-slate-800/50 hover:bg-slate-800 rounded-lg transition-colors flex items-center justify-between"
                    >
                      <span className="text-slate-300">What are the key safety considerations?</span>
                      <ChevronRight className="w-4 h-4 text-slate-500" />
                    </button>
                    <button
                      onClick={() => {
                        setPendingPrompt(`What maintenance actions are recommended in "${selectedDoc.title}"?`)
                        setChatOpen(true)
                      }}
                      className="w-full text-left p-3 bg-slate-800/50 hover:bg-slate-800 rounded-lg transition-colors flex items-center justify-between"
                    >
                      <span className="text-slate-300">What maintenance is recommended?</span>
                      <ChevronRight className="w-4 h-4 text-slate-500" />
                    </button>
                    <button
                      onClick={() => {
                        setPendingPrompt(`Are there any compliance issues mentioned in "${selectedDoc.title}"?`)
                        setChatOpen(true)
                      }}
                      className="w-full text-left p-3 bg-slate-800/50 hover:bg-slate-800 rounded-lg transition-colors flex items-center justify-between"
                    >
                      <span className="text-slate-300">Any compliance considerations?</span>
                      <ChevronRight className="w-4 h-4 text-slate-500" />
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </>
        ) : (
          <div className="flex-1 flex items-center justify-center">
            <div className="text-center">
              <FileSearch className="w-16 h-16 text-slate-600 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-slate-400 mb-2">Select a document</h3>
              <p className="text-sm text-slate-500 max-w-md">
                Choose a document from the list to view details, or use AI search to find specific information
              </p>
              <button
                onClick={() => {
                  setPendingPrompt('Help me find technical documentation for the Permian network integration')
                  setChatOpen(true)
                }}
                className="mt-4 btn-primary flex items-center gap-2 mx-auto"
              >
                <Sparkles className="w-4 h-4" />
                Search with AI
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

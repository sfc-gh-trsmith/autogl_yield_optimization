export type RiskLevel = 'low' | 'medium' | 'high' | 'critical'
export type NetworkSource = 'snowcore' | 'terafield' | 'autogl'
export type PersonaType = 'executive' | 'operations' | 'engineer'

export interface Asset {
  asset_id: string
  asset_name: string
  asset_type: string
  source_system: string
  latitude: number
  longitude: number
  basin: string
  field: string
  risk_score?: number
  anomaly_score?: number
  current_pressure?: number
  design_pressure?: number
  throughput?: number
}

export interface NetworkEdge {
  edge_id: string
  source_asset_id: string
  target_asset_id: string
  edge_type: string
  source_system: string
  confidence?: number
  discovery_method?: string
}

export interface GraphPrediction {
  source_node: string
  target_node: string
  prediction_type?: string
  confidence: number
  risk_score: number
  explanation: string
  source_lat?: number
  source_lon?: number
  target_lat?: number
  target_lon?: number
  source_asset?: Asset
  target_asset?: Asset
}

export interface TelemetryReading {
  asset_id: string
  timestamp: string
  pressure_psi: number
  flow_rate_mcfd: number
  temperature_f: number
  gas_composition_c1: number
}

export interface SimulationResult {
  scenario_id: string
  source_asset: Asset
  affected_assets: Asset[]
  pressure_cascade: {
    asset_id: string
    asset_name: string
    time_offset_min: number
    pressure_delta: number
    new_pressure: number
    original_pressure: number
    risk_level: RiskLevel
    latitude: number
    longitude: number
  }[]
  recommended_actions: string[]
  estimated_impact_mcfd: number
}

export interface CortexMessage {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
  toolCalls?: CortexToolCall[]
  reasoning?: string
}

export interface CortexToolCall {
  id: string
  name: string
  status: 'running' | 'completed' | 'error'
  input?: string
  output?: string
}

export interface DocumentResult {
  doc_id: string
  title: string
  doc_type: string
  content_preview: string
  relevance_score: number
  asset_ids: string[]
}

export interface KPIMetric {
  id: string
  label: string
  value: number
  unit: string
  change: number
  trend: 'up' | 'down' | 'stable'
  target?: number
}

import { create } from 'zustand'
import type { Asset, PersonaType, GraphPrediction, CortexMessage } from '@/types'

interface AppState {
  persona: PersonaType
  setPersona: (persona: PersonaType) => void
  
  selectedAsset: Asset | null
  setSelectedAsset: (asset: Asset | null) => void
  
  showAutoGLLinks: boolean
  toggleAutoGLLinks: () => void
  
  chatOpen: boolean
  setChatOpen: (open: boolean) => void
  toggleChat: () => void
  
  chatContext: string
  setChatContext: (context: string) => void
  
  pendingPrompt: string | null
  setPendingPrompt: (prompt: string | null) => void
  
  predictions: GraphPrediction[]
  setPredictions: (predictions: GraphPrediction[]) => void
  
  messages: CortexMessage[]
  addMessage: (message: CortexMessage) => void
  updateMessage: (id: string, updates: Partial<CortexMessage>) => void
  clearMessages: () => void
  
  simulationMode: boolean
  setSimulationMode: (mode: boolean) => void
  
  simulationAssets: Asset[]
  addSimulationAsset: (asset: Asset) => void
  removeSimulationAsset: (assetId: string) => void
  clearSimulationAssets: () => void
}

export const useAppStore = create<AppState>((set) => ({
  persona: 'operations',
  setPersona: (persona) => set({ persona }),
  
  selectedAsset: null,
  setSelectedAsset: (asset) => set({ selectedAsset: asset }),
  
  showAutoGLLinks: false,
  toggleAutoGLLinks: () => set((state) => ({ showAutoGLLinks: !state.showAutoGLLinks })),
  
  chatOpen: false,
  setChatOpen: (open) => set({ chatOpen: open }),
  toggleChat: () => set((state) => ({ chatOpen: !state.chatOpen })),
  
  chatContext: '',
  setChatContext: (context) => set({ chatContext: context }),
  
  pendingPrompt: null,
  setPendingPrompt: (prompt) => set({ pendingPrompt: prompt }),
  
  predictions: [],
  setPredictions: (predictions) => set({ predictions }),
  
  messages: [],
  addMessage: (message) => set((state) => ({ messages: [...state.messages, message] })),
  updateMessage: (id, updates) => set((state) => ({
    messages: state.messages.map((m) => m.id === id ? { ...m, ...updates } : m)
  })),
  clearMessages: () => set({ messages: [] }),
  
  simulationMode: false,
  setSimulationMode: (mode) => set({ simulationMode: mode }),
  
  simulationAssets: [],
  addSimulationAsset: (asset) => set((state) => {
    if (state.simulationAssets.find(a => a.asset_id === asset.asset_id)) return state
    return { simulationAssets: [...state.simulationAssets, asset] }
  }),
  removeSimulationAsset: (assetId) => set((state) => ({
    simulationAssets: state.simulationAssets.filter(a => a.asset_id !== assetId)
  })),
  clearSimulationAssets: () => set({ simulationAssets: [] }),
}))

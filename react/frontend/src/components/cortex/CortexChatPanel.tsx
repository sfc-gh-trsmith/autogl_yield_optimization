import { useState, useRef, useEffect } from 'react'
import { Send, Loader2, Sparkles, X, Trash2 } from 'lucide-react'
import { useAppStore } from '@/stores/appStore'
import { useCortexAgent } from '@/hooks/useCortexAgent'
import CortexMessage from './CortexMessage'

export default function CortexChatPanel() {
  const [input, setInput] = useState('')
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const processingPromptRef = useRef<string | null>(null)
  const { messages, chatContext, selectedAsset, pendingPrompt, setPendingPrompt, toggleChat, clearMessages } = useAppStore()
  const { sendMessage, status, reasoningStage } = useCortexAgent()

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  useEffect(() => {
    if (pendingPrompt && status !== 'streaming' && processingPromptRef.current !== pendingPrompt) {
      processingPromptRef.current = pendingPrompt
      setPendingPrompt(null)
      sendMessage(pendingPrompt)
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [pendingPrompt, status])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!input.trim() || status === 'streaming') return

    let contextualPrompt = input
    if (selectedAsset) {
      contextualPrompt = `[Context: User is viewing asset "${selectedAsset.asset_name}" (${selectedAsset.asset_type}) in ${selectedAsset.field}]\n\n${input}`
    } else if (chatContext) {
      contextualPrompt = `[Context: ${chatContext}]\n\n${input}`
    }

    await sendMessage(contextualPrompt)
    setInput('')
  }

  const handleSamplePromptClick = async (query: string) => {
    if (status === 'streaming') return
    let contextualPrompt = query
    if (selectedAsset) {
      contextualPrompt = `[Context: User is viewing asset "${selectedAsset.asset_name}" (${selectedAsset.asset_type}) in ${selectedAsset.field}]\n\n${query}`
    } else if (chatContext) {
      contextualPrompt = `[Context: ${chatContext}]\n\n${query}`
    }
    await sendMessage(contextualPrompt)
  }

  const suggestedQueries = selectedAsset
    ? [
        `What is the risk assessment for ${selectedAsset.asset_name}?`,
        `Show maintenance history and operational data for this asset`,
        `How does this asset connect to the broader network?`,
      ]
    : [
        'Show me high-risk assets and explain the contributing factors',
        'Find cross-network synergies discovered by AutoGL and their operational impact',
        'Analyze pressure trends across SnowCore assets and flag anomalies',
        'What TeraField assets should be prioritized for integration based on AutoGL predictions?',
      ]

  return (
    <div className="h-full flex flex-col">
      <div 
        className="p-3 border-b border-slate-800 cursor-pointer hover:bg-slate-800/50 transition-colors"
        onClick={toggleChat}
      >
        <div className="flex items-center gap-2">
          <Sparkles className="w-4 h-4 text-autogl-400" />
          <h3 className="text-xs font-medium text-white flex-1">Cortex AI Assistant</h3>
          {messages.length > 0 && (
            <button
              onClick={(e) => { e.stopPropagation(); clearMessages(); }}
              className="p-1 hover:bg-slate-700 rounded transition-colors"
              title="Clear chat history"
            >
              <Trash2 className="w-3.5 h-3.5 text-slate-400 hover:text-white" />
            </button>
          )}
          <X className="w-4 h-4 text-slate-400 hover:text-white" />
        </div>
        {selectedAsset && (
          <p className="text-xs text-slate-400 mt-1">
            Context: {selectedAsset.asset_name}
          </p>
        )}
      </div>

      <div className="flex-1 overflow-y-auto p-3 space-y-3">
        {messages.length === 0 ? (
          <div className="space-y-3">
            <p className="text-xs text-slate-400 text-center">
              Ask me anything about the Permian network integration
            </p>
            <div className="space-y-1.5">
              {suggestedQueries.map((query, i) => (
                <button
                  key={i}
                  onClick={() => handleSamplePromptClick(query)}
                  disabled={status === 'streaming'}
                  className="w-full text-left p-2 text-[11px] text-slate-300 bg-slate-800/50 
                           rounded-lg hover:bg-slate-800 transition-colors border border-slate-700/50
                           disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {query}
                </button>
              ))}
            </div>
          </div>
        ) : (
          messages.map((message) => (
            <CortexMessage key={message.id} message={message} />
          ))
        )}

        {status === 'streaming' && reasoningStage && (
          <div className="flex items-center gap-2 text-xs text-autogl-400">
            <Loader2 className="w-3.5 h-3.5 animate-spin" />
            <span>{reasoningStage}</span>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      <form onSubmit={handleSubmit} className="p-3 border-t border-slate-800">
        <div className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask about assets, risks, or documents..."
            className="input-field flex-1 text-xs"
            disabled={status === 'streaming'}
          />
          <button
            type="submit"
            disabled={!input.trim() || status === 'streaming'}
            className="btn-primary"
          >
            {status === 'streaming' ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <Send className="w-4 h-4" />
            )}
          </button>
        </div>
      </form>
    </div>
  )
}

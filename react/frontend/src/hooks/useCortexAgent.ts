import { useCallback, useState } from 'react'
import { useAppStore } from '@/stores/appStore'
import type { CortexMessage, CortexToolCall } from '@/types'

type AgentStatus = 'idle' | 'streaming' | 'error'

export function useCortexAgent() {
  const [status, setStatus] = useState<AgentStatus>('idle')
  const [reasoningStage, setReasoningStage] = useState<string | null>(null)
  const { addMessage, updateMessage, selectedAsset } = useAppStore()

  const sendMessage = useCallback(async (content: string) => {
    const userMessage: CortexMessage = {
      id: crypto.randomUUID(),
      role: 'user',
      content,
      timestamp: new Date(),
    }
    addMessage(userMessage)

    const assistantId = crypto.randomUUID()
    const assistantMessage: CortexMessage = {
      id: assistantId,
      role: 'assistant',
      content: '',
      timestamp: new Date(),
      toolCalls: [],
    }
    addMessage(assistantMessage)

    setStatus('streaming')
    setReasoningStage('Connecting to Cortex Agent...')

    try {
      const response = await fetch('/api/agent/run', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          message: content,
          context: selectedAsset?.asset_id || null
        }),
      })

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`)
      }

      const reader = response.body?.getReader()
      if (!reader) throw new Error('No response body')

      const decoder = new TextDecoder()
      let buffer = ''
      let fullContent = ''
      const toolCalls: CortexToolCall[] = []
      let reasoning = ''

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split('\n')
        buffer = lines.pop() || ''

        for (const line of lines) {
          if (!line.startsWith('data: ')) continue
          const data = line.slice(6).trim()
          if (data === '[DONE]') continue

          try {
            const event = JSON.parse(data)

            switch (event.type) {
              case 'text_delta':
                fullContent += event.text
                updateMessage(assistantId, { content: fullContent })
                break

              case 'tool_start':
                setReasoningStage(`Using ${event.tool_name}...`)
                toolCalls.push({
                  id: event.tool_call_id || crypto.randomUUID(),
                  name: event.tool_name,
                  status: 'running',
                  input: event.input,
                })
                updateMessage(assistantId, { toolCalls: [...toolCalls] })
                break

              case 'tool_end':
                const toolIndex = toolCalls.findIndex(t => t.name === event.tool_name && t.status === 'running')
                if (toolIndex >= 0) {
                  toolCalls[toolIndex] = { ...toolCalls[toolIndex], status: 'completed', output: event.output }
                  updateMessage(assistantId, { toolCalls: [...toolCalls] })
                }
                setReasoningStage('Processing results...')
                break

              case 'reasoning':
                reasoning += event.text
                updateMessage(assistantId, { reasoning })
                setReasoningStage(event.text.slice(0, 50) + '...')
                break

              case 'error':
                throw new Error(event.message || 'Agent error')
            }
          } catch (e) {
            if (e instanceof SyntaxError) continue
            throw e
          }
        }
      }

      setStatus('idle')
      setReasoningStage(null)
    } catch (error) {
      console.error('Agent error:', error)
      setStatus('error')
      setReasoningStage(null)
      updateMessage(assistantId, {
        content: 'Sorry, I encountered an error. Please try again.',
      })
    }
  }, [addMessage, updateMessage, selectedAsset])

  return { sendMessage, status, reasoningStage }
}

import { motion } from 'framer-motion'
import { User, Sparkles, Database, FileSearch, ChevronDown, ChevronUp } from 'lucide-react'
import { useState } from 'react'
import ReactMarkdown from 'react-markdown'
import type { CortexMessage as MessageType } from '@/types'

interface Props {
  message: MessageType
}

export default function CortexMessage({ message }: Props) {
  const [showReasoning, setShowReasoning] = useState(false)
  const isUser = message.role === 'user'

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className={`flex gap-3 ${isUser ? 'flex-row-reverse' : ''}`}
    >
      <div
        className={`w-6 h-6 rounded-full flex items-center justify-center flex-shrink-0 ${
          isUser ? 'bg-snowcore-600' : 'bg-autogl-600'
        }`}
      >
        {isUser ? (
          <User className="w-3 h-3 text-white" />
        ) : (
          <Sparkles className="w-3 h-3 text-white" />
        )}
      </div>

      <div className={`flex-1 ${isUser ? 'text-right' : ''}`}>
        <div
          className={`inline-block max-w-full p-2.5 rounded-lg text-xs ${
            isUser
              ? 'bg-snowcore-600/20 text-white'
              : 'bg-slate-800/50 text-slate-100'
          }`}
        >
          <div className="prose prose-xs prose-invert max-w-none prose-p:my-1 prose-ul:my-1 prose-ol:my-1 prose-li:my-0.5 prose-headings:my-1.5 prose-pre:my-1 prose-code:text-[10px] prose-code:bg-slate-700/50 prose-code:px-1 prose-code:py-0.5 prose-code:rounded [&_p]:text-xs [&_li]:text-xs [&_code]:text-[10px]">
            <ReactMarkdown>{message.content}</ReactMarkdown>
          </div>
        </div>

        {message.toolCalls && message.toolCalls.length > 0 && (
          <div className="mt-2 space-y-1">
            {message.toolCalls.map((tool) => (
              <div
                key={tool.id}
                className="flex items-center gap-2 text-xs text-slate-400"
              >
                {tool.name.includes('analyst') ? (
                  <Database className="w-3 h-3" />
                ) : (
                  <FileSearch className="w-3 h-3" />
                )}
                <span>
                  {tool.name} · {tool.status}
                </span>
              </div>
            ))}
          </div>
        )}

        {message.reasoning && (
          <button
            onClick={() => setShowReasoning(!showReasoning)}
            className="mt-2 flex items-center gap-1 text-xs text-autogl-400 hover:text-autogl-300"
          >
            {showReasoning ? (
              <ChevronUp className="w-3 h-3" />
            ) : (
              <ChevronDown className="w-3 h-3" />
            )}
            <span>Reasoning</span>
          </button>
        )}

        {showReasoning && message.reasoning && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            className="mt-2 p-2 text-xs text-slate-400 bg-slate-800/30 rounded-lg border border-slate-700/30"
          >
            {message.reasoning}
          </motion.div>
        )}
      </div>
    </motion.div>
  )
}

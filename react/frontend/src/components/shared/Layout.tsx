import { Outlet, NavLink, useLocation } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  Network, 
  Play, 
  LayoutDashboard, 
  Radio, 
  FileSearch,
  MessageSquare,
  X
} from 'lucide-react'
import { useAppStore } from '@/stores/appStore'
import CortexChatPanel from '@/components/cortex/CortexChatPanel'

const navItems = [
  { path: '/executive', label: 'Executive', icon: LayoutDashboard },
  { path: '/network', label: 'Network Discovery', icon: Network },
  { path: '/simulation', label: 'Simulation', icon: Play },
  { path: '/operations', label: 'Operations', icon: Radio },
  { path: '/engineer', label: 'Engineer', icon: FileSearch },
]

export default function Layout() {
  const location = useLocation()
  const { chatOpen, toggleChat } = useAppStore()

  return (
    <div className="min-h-screen flex">
      <aside className="w-64 bg-slate-900 border-r border-slate-800 flex flex-col">
        <div className="p-6 border-b border-slate-800">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-snowcore-500 to-autogl-500 flex items-center justify-center">
              <Network className="w-5 h-5 text-white" />
            </div>
            <div>
              <h1 className="font-semibold text-white">SnowCore</h1>
              <p className="text-xs text-slate-400">Permian Integration</p>
            </div>
          </div>
        </div>

        <nav className="flex-1 p-4 space-y-1">
          {navItems.map(({ path, label, icon: Icon }) => (
            <NavLink
              key={path}
              to={path}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all duration-200 ${
                  isActive
                    ? 'bg-snowcore-600/20 text-snowcore-400 border border-snowcore-500/30'
                    : 'text-slate-400 hover:bg-slate-800 hover:text-white'
                }`
              }
            >
              <Icon className="w-5 h-5" />
              <span className="text-sm font-medium">{label}</span>
            </NavLink>
          ))}
        </nav>

        <div className="p-4 border-t border-slate-800">
          <div className="glass-panel p-3">
            <div className="flex items-center gap-2 mb-2">
              <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
              <span className="text-xs text-slate-400">Cortex Agent Active</span>
            </div>
            <div className="text-xs text-slate-500">
              claude-3-5-sonnet · Analyst + Search
            </div>
          </div>
        </div>
      </aside>

      <main className="flex-1 flex flex-col">
        <header className="h-14 bg-slate-900/50 border-b border-slate-800 flex items-center justify-between px-6">
          <div className="flex items-center gap-4">
            <h2 className="text-lg font-medium text-white">
              {navItems.find(n => n.path === location.pathname)?.label || 'Dashboard'}
            </h2>
          </div>
          
          <button
            onClick={toggleChat}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-all duration-200 ${
              chatOpen 
                ? 'bg-snowcore-600 text-white' 
                : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
            }`}
          >
            {chatOpen ? <X className="w-4 h-4" /> : <MessageSquare className="w-4 h-4" />}
            <span className="text-sm font-medium">AI Assistant</span>
          </button>
        </header>

        <div className="flex-1 flex overflow-hidden">
          <div className={`flex-1 overflow-auto transition-all duration-300 ${chatOpen ? 'mr-[480px]' : ''}`}>
            <Outlet />
          </div>

          <AnimatePresence>
            {chatOpen && (
              <motion.div
                initial={{ x: 480, opacity: 0 }}
                animate={{ x: 0, opacity: 1 }}
                exit={{ x: 480, opacity: 0 }}
                transition={{ type: 'spring', damping: 25, stiffness: 200 }}
                className="fixed right-0 top-14 bottom-0 w-[480px] bg-slate-900 border-l border-slate-800 z-50"
              >
                <CortexChatPanel />
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </main>
    </div>
  )
}

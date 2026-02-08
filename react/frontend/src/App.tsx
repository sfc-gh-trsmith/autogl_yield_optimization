import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import Layout from '@/components/shared/Layout'
import NetworkDiscoveryPage from '@/pages/NetworkDiscovery'
import SimulationPage from '@/pages/Simulation'
import ExecutivePage from '@/pages/Executive'
import OperationsPage from '@/pages/Operations'
import EngineerPage from '@/pages/Engineer'

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Navigate to="/network" replace />} />
          <Route path="network" element={<NetworkDiscoveryPage />} />
          <Route path="simulation" element={<SimulationPage />} />
          <Route path="executive" element={<ExecutivePage />} />
          <Route path="operations" element={<OperationsPage />} />
          <Route path="engineer" element={<EngineerPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}

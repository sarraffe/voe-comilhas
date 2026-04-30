import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import Dashboard from './pages/Dashboard'
import CotacaoDetalhe from './pages/CotacaoDetalhe'
import PropostaPublica from './pages/PropostaPublica'

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/cotacoes/:id" element={<CotacaoDetalhe />} />
        <Route path="/proposta/:codigo" element={<PropostaPublica />} />
      </Routes>
    </BrowserRouter>
  )
}

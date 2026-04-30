import { useState, useEffect, useCallback } from 'react'
import axios from 'axios'
import Layout from '../components/Layout'
import CotacaoCard from '../components/CotacaoCard'
import StatusBadge, { STATUS_CONFIG } from '../components/StatusBadge'

const API_URL = import.meta.env.VITE_API_URL || 'https://voe-comilhas-production.up.railway.app'

export default function Dashboard() {
  const [cotacoes, setCotacoes] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [search, setSearch] = useState('')
  const [filterStatus, setFilterStatus] = useState('')

  const fetchCotacoes = useCallback(async () => {
    try {
      setLoading(true)
      const params = {}
      if (filterStatus) params.status = filterStatus
      const res = await axios.get(`${API_URL}/cotacoes`, { params })
      setCotacoes(res.data.data || [])
    } catch (err) {
      setError('Erro ao carregar cotações. Verifique se o backend está rodando.')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }, [filterStatus])

  const handleDelete = useCallback(async (id) => {
    try {
      await axios.delete(`${API_URL}/cotacoes/${id}`)
      setCotacoes(prev => prev.filter(c => c.id !== id))
    } catch (err) {
      console.error('Erro ao excluir cotação:', err)
      alert('Não foi possível excluir a cotação. Tente novamente.')
    }
  }, [])

  const handleStatusChange = useCallback(async (id, newStatus) => {
    // Otimista: atualiza imediatamente na UI
    setCotacoes(prev => prev.map(c => c.id === id ? { ...c, status: newStatus } : c))
    try {
      await axios.patch(`${API_URL}/cotacoes/${id}/status`, { status: newStatus })
    } catch (err) {
      console.error('Erro ao atualizar status:', err)
      // Reverter em caso de erro
      fetchCotacoes()
    }
  }, [fetchCotacoes])

  useEffect(() => {
    fetchCotacoes()
    // Auto-refresh a cada 30 segundos
    const interval = setInterval(fetchCotacoes, 30000)
    return () => clearInterval(interval)
  }, [fetchCotacoes])

  // Filtro local por busca de texto
  const filtered = cotacoes.filter(c => {
    if (!search) return true
    const cliente = c.clientes || {}
    const searchLower = search.toLowerCase()
    return (
      (cliente.nome || '').toLowerCase().includes(searchLower) ||
      (cliente.whatsapp || '').includes(search) ||
      (c.origem || '').toLowerCase().includes(searchLower) ||
      (c.destino || '').toLowerCase().includes(searchLower)
    )
  })

  // Contagem por status
  const counts = cotacoes.reduce((acc, c) => {
    acc[c.status] = (acc[c.status] || 0) + 1
    return acc
  }, {})

  return (
    <Layout>
      {/* Stats rápidas */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-8">
        {['novo', 'em_cotacao', 'proposta_enviada', 'vendido'].map(status => (
          <button
            key={status}
            onClick={() => setFilterStatus(filterStatus === status ? '' : status)}
            className={`card text-center cursor-pointer hover:shadow-md transition-all ${
              filterStatus === status ? 'ring-2 ring-primary' : ''
            }`}
          >
            <p className="text-3xl font-bold text-primary mb-1">{counts[status] || 0}</p>
            <StatusBadge status={status} />
          </button>
        ))}
      </div>

      {/* Filtros */}
      <div className="flex flex-col sm:flex-row gap-3 mb-6">
        <div className="flex-1 relative">
          <svg className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
          <input
            type="text"
            placeholder="Buscar por nome, telefone, origem ou destino..."
            value={search}
            onChange={e => setSearch(e.target.value)}
            className="input pl-9"
          />
        </div>
        <select
          value={filterStatus}
          onChange={e => setFilterStatus(e.target.value)}
          className="select w-full sm:w-48"
        >
          <option value="">Todos os status</option>
          {Object.entries(STATUS_CONFIG).map(([key, { label }]) => (
            <option key={key} value={key}>{label}</option>
          ))}
        </select>
        <button
          onClick={fetchCotacoes}
          className="btn-secondary flex items-center gap-2 whitespace-nowrap"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
          Atualizar
        </button>
      </div>

      {/* Título + contagem */}
      <div className="flex items-center justify-between mb-4">
        <h1 className="text-xl font-bold text-gray-900">
          Cotações
          {filterStatus && <span className="ml-2 text-primary text-sm font-normal">· {STATUS_CONFIG[filterStatus]?.label}</span>}
        </h1>
        <span className="text-sm text-gray-400">{filtered.length} resultado{filtered.length !== 1 ? 's' : ''}</span>
      </div>

      {/* Conteúdo */}
      {loading ? (
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
        </div>
      ) : error ? (
        <div className="card text-center py-12">
          <p className="text-danger font-medium mb-2">{error}</p>
          <button onClick={fetchCotacoes} className="btn-primary mt-2">Tentar novamente</button>
        </div>
      ) : filtered.length === 0 ? (
        <div className="card text-center py-16">
          <svg className="w-12 h-12 text-gray-300 mx-auto mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          <p className="text-gray-400 font-medium">Nenhuma cotação encontrada</p>
          {search && <p className="text-sm text-gray-300 mt-1">Tente outro termo de busca</p>}
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filtered.map(cotacao => (
            <CotacaoCard
              key={cotacao.id}
              cotacao={cotacao}
              onDelete={handleDelete}
              onStatusChange={handleStatusChange}
            />
          ))}
        </div>
      )}
    </Layout>
  )
}

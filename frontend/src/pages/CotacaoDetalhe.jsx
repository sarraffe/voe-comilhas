import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import axios from 'axios'
import Layout from '../components/Layout'
import StatusBadge, { STATUS_CONFIG } from '../components/StatusBadge'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

function InfoField({ label, value }) {
  return (
    <div>
      <label className="label">{label}</label>
      <p className="text-sm font-medium text-gray-900">{value || '—'}</p>
    </div>
  )
}

function formatDate(d) {
  if (!d) return '—'
  const [y, m, dd] = d.split('-')
  return `${dd}/${m}/${y}`
}

const EMPTY_OPCAO = {
  companhia: '', origem: '', destino: '', data_voo: '', horario_saida: '',
  horario_chegada: '', paradas: '', bagagem: '', regras: '',
  valor_total: '', destaque: '', validade: ''
}

export default function CotacaoDetalhe() {
  const { id } = useParams()
  const navigate = useNavigate()

  const [cotacao, setCotacao] = useState(null)
  const [mensagens, setMensagens] = useState([])
  const [opcoes, setOpcoes] = useState([])
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [novaOpcao, setNovaOpcao] = useState(EMPTY_OPCAO)
  const [showNovaOpcao, setShowNovaOpcao] = useState(false)
  const [proposta, setProposta] = useState(null)
  const [gerandoProposta, setGerandoProposta] = useState(false)
  const [error, setError] = useState(null)

  const fetchAll = async () => {
    try {
      setLoading(true)
      const [cotRes, msgRes, opcRes] = await Promise.all([
        axios.get(`${API_URL}/cotacoes/${id}`),
        axios.get(`${API_URL}/cotacoes/${id}/mensagens`),
        axios.get(`${API_URL}/cotacoes/${id}/opcoes`),
      ])
      setCotacao(cotRes.data)
      setMensagens(msgRes.data.data || [])
      setOpcoes(opcRes.data.data || [])
      if (cotRes.data.codigo_proposta) {
        setProposta(cotRes.data.codigo_proposta)
      }
    } catch (err) {
      setError('Cotação não encontrada.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { fetchAll() }, [id])

  const handleStatusChange = async (newStatus) => {
    try {
      setSaving(true)
      await axios.patch(`${API_URL}/cotacoes/${id}/status`, { status: newStatus })
      setCotacao(prev => ({ ...prev, status: newStatus }))
    } catch (err) {
      alert('Erro ao atualizar status.')
    } finally {
      setSaving(false)
    }
  }

  // Converte DD/MM/AAAA → AAAA-MM-DD para o backend
  function parseDateBR(str) {
    if (!str) return ''
    if (str.includes('/')) {
      const [d, m, y] = str.split('/')
      return `${y}-${m}-${d}`
    }
    return str
  }

  const handleSaveOpcao = async () => {
    try {
      setSaving(true)
      const payload = { ...novaOpcao }
      if (payload.valor_total) payload.valor_total = parseFloat(payload.valor_total)
      if (payload.data_voo) payload.data_voo = parseDateBR(payload.data_voo)
      await axios.post(`${API_URL}/cotacoes/${id}/opcoes`, payload)
      setNovaOpcao(EMPTY_OPCAO)
      setShowNovaOpcao(false)
      await fetchAll()
    } catch (err) {
      alert(err.response?.data?.detail || 'Erro ao salvar opção.')
    } finally {
      setSaving(false)
    }
  }

  const handleGerarProposta = async () => {
    try {
      setGerandoProposta(true)
      const res = await axios.post(`${API_URL}/cotacoes/${id}/gerar-proposta`)
      setProposta(res.data.codigo)
      await fetchAll()
    } catch (err) {
      alert(err.response?.data?.detail || 'Erro ao gerar proposta.')
    } finally {
      setGerandoProposta(false)
    }
  }

  const propostaLink = proposta ? `${window.location.origin}/proposta/${proposta}` : null

  if (loading) return (
    <Layout>
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
      </div>
    </Layout>
  )

  if (error || !cotacao) return (
    <Layout>
      <div className="card text-center py-16">
        <p className="text-danger font-medium">{error || 'Cotação não encontrada.'}</p>
        <button onClick={() => navigate('/dashboard')} className="btn-primary mt-4">Voltar ao Dashboard</button>
      </div>
    </Layout>
  )

  const cliente = cotacao.clientes || {}

  return (
    <Layout>
      {/* Breadcrumb */}
      <button onClick={() => navigate('/dashboard')} className="flex items-center gap-1 text-sm text-gray-400 hover:text-primary mb-6 transition-colors">
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
        </svg>
        Dashboard
      </button>

      <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">

        {/* Coluna Principal */}
        <div className="xl:col-span-2 space-y-6">

          {/* Dados do Cliente */}
          <div className="card">
            <div className="flex items-center justify-between mb-4">
              <h2 className="font-bold text-gray-900">Cliente</h2>
              <StatusBadge status={cotacao.status} />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <InfoField label="Nome" value={cliente.nome} />
              <InfoField label="WhatsApp" value={cliente.whatsapp} />
            </div>
          </div>

          {/* Dados da Viagem */}
          <div className="card">
            <h2 className="font-bold text-gray-900 mb-4">Dados da Viagem</h2>
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-4">
              <InfoField label="Tipo" value={cotacao.tipo_viagem === 'ida_volta' ? 'Ida e Volta' : cotacao.tipo_viagem === 'somente_ida' ? 'Somente Ida' : null} />
              <InfoField label="Origem" value={cotacao.origem} />
              <InfoField label="Destino" value={cotacao.destino} />
              <InfoField label="Data de Ida" value={formatDate(cotacao.data_ida)} />
              <InfoField label="Data de Volta" value={formatDate(cotacao.data_volta)} />
              <InfoField label="Adultos" value={cotacao.adultos} />
              <InfoField label="Crianças" value={cotacao.criancas} />
              <InfoField label="Bebês" value={cotacao.bebes} />
              <InfoField label="Bagagem 23kg" value={cotacao.bagagem_23kg === true ? `Sim (${cotacao.quantidade_malas || 1} mala${cotacao.quantidade_malas > 1 ? 's' : ''})` : cotacao.bagagem_23kg === false ? 'Não' : null} />
              <InfoField label="Forma de Pagamento" value={cotacao.forma_pagamento} />
              <div className="col-span-2">
                <InfoField label="Observações" value={cotacao.observacoes} />
              </div>
            </div>
          </div>

          {/* Status */}
          <div className="card">
            <h2 className="font-bold text-gray-900 mb-4">Alterar Status</h2>
            <div className="flex flex-wrap gap-2">
              {Object.entries(STATUS_CONFIG).map(([key, { label }]) => (
                <button
                  key={key}
                  onClick={() => handleStatusChange(key)}
                  disabled={saving || cotacao.status === key}
                  className={`px-3 py-1.5 rounded-lg text-sm font-medium border transition-all ${
                    cotacao.status === key
                      ? 'bg-primary text-white border-primary'
                      : 'bg-white text-gray-600 border-gray-200 hover:border-primary hover:text-primary'
                  } disabled:opacity-50`}
                >
                  {label}
                </button>
              ))}
            </div>
          </div>

          {/* Opções de Voo */}
          <div className="card">
            <div className="flex items-center justify-between mb-4">
              <h2 className="font-bold text-gray-900">Opções de Voo ({opcoes.length}/3)</h2>
              {opcoes.length < 3 && (
                <button
                  onClick={() => setShowNovaOpcao(!showNovaOpcao)}
                  className="btn-primary text-sm"
                >
                  {showNovaOpcao ? 'Cancelar' : '+ Adicionar'}
                </button>
              )}
            </div>

            {/* Lista de opções existentes */}
            {opcoes.length === 0 && !showNovaOpcao && (
              <p className="text-sm text-gray-400 text-center py-6">Nenhuma opção cadastrada ainda.</p>
            )}
            {opcoes.map((op, i) => (
              <div key={op.id} className="border border-gray-100 rounded-xl p-4 mb-3 bg-gray-50">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-xs font-bold text-gray-400 uppercase">Opção {i + 1}</span>
                  {op.destaque && <span className="text-xs bg-primary/10 text-primary px-2 py-0.5 rounded-full font-medium">{op.destaque}</span>}
                </div>
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                  <InfoField label="Companhia" value={op.companhia} />
                  <InfoField label="Trecho" value={`${op.origem || '?'} → ${op.destino || '?'}`} />
                  <InfoField label="Data" value={formatDate(op.data_voo)} />
                  <InfoField label="Valor Total" value={op.valor_total ? `R$ ${Number(op.valor_total).toFixed(2)}` : null} />
                  <InfoField label="Saída" value={op.horario_saida} />
                  <InfoField label="Chegada" value={op.horario_chegada} />
                  <InfoField label="Paradas" value={op.paradas} />
                  <InfoField label="Bagagem" value={op.bagagem} />
                </div>
                {op.regras && <div className="mt-2 text-xs text-gray-500"><strong>Regras:</strong> {op.regras}</div>}
              </div>
            ))}

            {/* Formulário nova opção */}
            {showNovaOpcao && (
              <div className="border border-primary/20 bg-primary-50/30 rounded-xl p-4 mt-2">
                <h3 className="font-semibold text-primary mb-4">Nova Opção de Voo</h3>
                <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
                  {[
                    { key: 'companhia', label: 'Companhia Aérea', type: 'text' },
                    { key: 'origem', label: 'Origem (sigla)', type: 'text' },
                    { key: 'destino', label: 'Destino (sigla)', type: 'text' },
                    { key: 'data_voo', label: 'Data do Voo', type: 'text', placeholder: 'DD/MM/AAAA' },
                    { key: 'horario_saida', label: 'Horário de Saída', type: 'text', placeholder: 'ex: 08:30' },
                    { key: 'horario_chegada', label: 'Horário de Chegada', type: 'text', placeholder: 'ex: 11:45' },
                    { key: 'paradas', label: 'Paradas/Conexões', type: 'text', placeholder: 'ex: 1 escala em BSB' },
                    { key: 'bagagem', label: 'Bagagem Incluída', type: 'text', placeholder: 'ex: 23kg despachada' },
                    { key: 'valor_total', label: 'Valor Total (R$)', type: 'number' },
                    { key: 'validade', label: 'Válido até', type: 'datetime-local' },
                  ].map(({ key, label, type, placeholder }) => (
                    <div key={key}>
                      <label className="label">{label}</label>
                      <input
                        type={type}
                        placeholder={placeholder}
                        value={novaOpcao[key]}
                        onChange={e => setNovaOpcao(prev => ({ ...prev, [key]: e.target.value }))}
                        className="input"
                      />
                    </div>
                  ))}
                  <div>
                    <label className="label">Destaque</label>
                    <select
                      value={novaOpcao.destaque}
                      onChange={e => setNovaOpcao(prev => ({ ...prev, destaque: e.target.value }))}
                      className="select"
                    >
                      <option value="">Sem destaque</option>
                      <option>Mais barata</option>
                      <option>Mais rápida</option>
                      <option>Melhor custo-benefício</option>
                    </select>
                  </div>
                  <div className="col-span-2 sm:col-span-3">
                    <label className="label">Regras e Restrições</label>
                    <textarea
                      rows={2}
                      placeholder="ex: Tarifa não reembolsável, permite alteração com taxa..."
                      value={novaOpcao.regras}
                      onChange={e => setNovaOpcao(prev => ({ ...prev, regras: e.target.value }))}
                      className="input resize-none"
                    />
                  </div>
                </div>
                <div className="flex gap-2 mt-4">
                  <button onClick={handleSaveOpcao} disabled={saving} className="btn-primary">
                    {saving ? 'Salvando...' : 'Salvar Opção'}
                  </button>
                  <button onClick={() => { setShowNovaOpcao(false); setNovaOpcao(EMPTY_OPCAO) }} className="btn-secondary">
                    Cancelar
                  </button>
                </div>
              </div>
            )}

            {/* Gerar Proposta */}
            {opcoes.length > 0 && (
              <div className="mt-4 pt-4 border-t border-gray-100">
                {proposta ? (
                  <div className="bg-green-50 border border-green-200 rounded-xl p-4">
                    <p className="text-sm font-semibold text-green-800 mb-2">✓ Proposta gerada!</p>
                    <div className="flex items-center gap-2">
                      <input readOnly value={propostaLink} className="input text-xs bg-white" />
                      <button
                        onClick={() => { navigator.clipboard.writeText(propostaLink); alert('Link copiado!') }}
                        className="btn-primary text-sm whitespace-nowrap"
                      >
                        Copiar
                      </button>
                      <a href={propostaLink} target="_blank" rel="noreferrer" className="btn-secondary text-sm whitespace-nowrap">
                        Abrir
                      </a>
                    </div>
                  </div>
                ) : (
                  <button
                    onClick={handleGerarProposta}
                    disabled={gerandoProposta}
                    className="btn-primary w-full flex items-center justify-center gap-2"
                  >
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
                    </svg>
                    {gerandoProposta ? 'Gerando...' : 'Gerar Link da Proposta'}
                  </button>
                )}
              </div>
            )}
          </div>
        </div>

        {/* Coluna: Mensagens */}
        <div className="xl:col-span-1">
          <div className="card h-full flex flex-col" style={{ maxHeight: '80vh' }}>
            <h2 className="font-bold text-gray-900 mb-4">Conversa WhatsApp</h2>
            <div className="flex-1 overflow-y-auto space-y-2 pr-1">
              {mensagens.length === 0 ? (
                <p className="text-sm text-gray-400 text-center py-8">Nenhuma mensagem ainda.</p>
              ) : (
                mensagens.map(msg => (
                  <div key={msg.id} className={`flex ${msg.origem_mensagem === 'cliente' ? 'justify-start' : 'justify-end'}`}>
                    <div className={`max-w-[85%] rounded-2xl px-4 py-2.5 text-sm ${
                      msg.origem_mensagem === 'cliente'
                        ? 'bg-gray-100 text-gray-800 rounded-tl-sm'
                        : 'bg-primary text-white rounded-tr-sm'
                    }`}>
                      <p className="whitespace-pre-wrap">{msg.conteudo}</p>
                      <p className={`text-xs mt-1 ${msg.origem_mensagem === 'cliente' ? 'text-gray-400' : 'text-white/60'}`}>
                        {msg.origem_mensagem === 'cliente' ? 'Cliente' : 'Agente'} · {new Date(msg.created_at).toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' })}
                      </p>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>

      </div>
    </Layout>
  )
}

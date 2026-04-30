import { useState, useRef, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import StatusBadge from './StatusBadge'

const STATUS_OPTIONS = [
  { value: 'novo',               label: 'Novo' },
  { value: 'em_cotacao',         label: 'Em Cotação' },
  { value: 'proposta_enviada',   label: 'Proposta Enviada' },
  { value: 'aguardando_cliente', label: 'Aguardando Cliente' },
  { value: 'vendido',            label: 'Vendido' },
  { value: 'perdido',            label: 'Perdido' },
]

function formatDate(dateStr) {
  if (!dateStr) return '—'
  const [y, m, d] = dateStr.split('-')
  return `${d}/${m}/${y}`
}

export default function CotacaoCard({ cotacao, onDelete, onStatusChange }) {
  const navigate = useNavigate()
  const [showStatusMenu, setShowStatusMenu] = useState(false)
  const [confirmDelete, setConfirmDelete] = useState(false)
  const menuRef = useRef(null)
  const cliente = cotacao.clientes || {}

  // Fechar dropdown ao clicar fora
  useEffect(() => {
    function handleClickOutside(e) {
      if (menuRef.current && !menuRef.current.contains(e.target)) {
        setShowStatusMenu(false)
      }
    }
    if (showStatusMenu) document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [showStatusMenu])

  function handleStatusClick(e) {
    e.stopPropagation()
    setShowStatusMenu(v => !v)
  }

  function handleStatusSelect(e, newStatus) {
    e.stopPropagation()
    setShowStatusMenu(false)
    if (newStatus !== cotacao.status && onStatusChange) {
      onStatusChange(cotacao.id, newStatus)
    }
  }

  function handleDeleteClick(e) {
    e.stopPropagation()
    setConfirmDelete(true)
  }

  function handleDeleteConfirm(e) {
    e.stopPropagation()
    setConfirmDelete(false)
    if (onDelete) onDelete(cotacao.id)
  }

  function handleDeleteCancel(e) {
    e.stopPropagation()
    setConfirmDelete(false)
  }

  return (
    <div
      onClick={() => navigate(`/cotacoes/${cotacao.id}`)}
      className="card hover:shadow-md hover:border-primary/20 cursor-pointer transition-all duration-200 group relative"
    >
      {/* Overlay de confirmação de exclusão */}
      {confirmDelete && (
        <div
          onClick={e => e.stopPropagation()}
          className="absolute inset-0 bg-white/96 rounded-xl flex flex-col items-center justify-center gap-3 z-20"
        >
          <p className="text-sm font-semibold text-gray-800">Excluir esta cotação?</p>
          <p className="text-xs text-gray-400 text-center px-4">Esta ação não pode ser desfeita.</p>
          <div className="flex gap-2 mt-1">
            <button
              onClick={handleDeleteConfirm}
              className="px-4 py-1.5 rounded-lg bg-red-500 hover:bg-red-600 text-white text-xs font-medium transition-colors"
            >
              Excluir
            </button>
            <button
              onClick={handleDeleteCancel}
              className="px-4 py-1.5 rounded-lg bg-gray-100 hover:bg-gray-200 text-gray-700 text-xs font-medium transition-colors"
            >
              Cancelar
            </button>
          </div>
        </div>
      )}

      <div className="flex items-start justify-between mb-3">
        <div className="flex-1 min-w-0 pr-2">
          <p className="font-semibold text-gray-900 truncate group-hover:text-primary transition-colors">
            {cliente.nome || 'Cliente sem nome'}
          </p>
          <p className="text-sm text-gray-500 flex items-center gap-1 mt-0.5">
            <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
            </svg>
            {cliente.whatsapp || '—'}
          </p>
        </div>

        {/* Badge de status — clicável para mudar */}
        <div className="relative flex-shrink-0" ref={menuRef}>
          <button
            onClick={handleStatusClick}
            title="Clique para alterar o status"
            className="focus:outline-none hover:opacity-80 transition-opacity"
          >
            <StatusBadge status={cotacao.status} />
          </button>
          {showStatusMenu && (
            <div className="absolute right-0 top-full mt-1 z-30 bg-white border border-gray-200 rounded-lg shadow-xl py-1 min-w-[180px]">
              <p className="text-xs text-gray-400 px-3 py-1 border-b border-gray-100 mb-1">Alterar status</p>
              {STATUS_OPTIONS.map(opt => (
                <button
                  key={opt.value}
                  onClick={(e) => handleStatusSelect(e, opt.value)}
                  className={`w-full text-left px-3 py-2 text-sm hover:bg-gray-50 transition-colors flex items-center gap-2 ${
                    opt.value === cotacao.status
                      ? 'font-semibold text-primary'
                      : 'text-gray-700'
                  }`}
                >
                  {opt.value === cotacao.status && (
                    <svg className="w-3.5 h-3.5 text-primary flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                    </svg>
                  )}
                  {opt.value !== cotacao.status && <span className="w-3.5 flex-shrink-0" />}
                  {opt.label}
                </button>
              ))}
            </div>
          )}
        </div>
      </div>

      <div className="flex items-center gap-2 text-sm text-gray-700 mb-3">
        <span className="font-medium">{cotacao.origem || '?'}</span>
        <svg className="w-4 h-4 text-primary flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 8l4 4m0 0l-4 4m4-4H3" />
        </svg>
        <span className="font-medium">{cotacao.destino || '?'}</span>
        {cotacao.tipo_viagem === 'ida_volta' && (
          <svg className="w-4 h-4 text-gray-400 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16l-4-4m0 0l4-4m-4 4h18" />
          </svg>
        )}
      </div>

      <div className="flex items-center justify-between text-xs text-gray-400">
        <span>
          {cotacao.data_ida ? `Ida: ${formatDate(cotacao.data_ida)}` : 'Data não informada'}
          {cotacao.data_volta ? ` · Volta: ${formatDate(cotacao.data_volta)}` : ''}
        </span>
        <div className="flex items-center gap-2">
          <span className="flex items-center gap-1">
            <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
            {(cotacao.adultos || 1)} adulto{(cotacao.adultos || 1) > 1 ? 's' : ''}
            {cotacao.criancas > 0 ? ` · ${cotacao.criancas} criança${cotacao.criancas > 1 ? 's' : ''}` : ''}
          </span>
          {/* Botão excluir — aparece no hover */}
          <button
            onClick={handleDeleteClick}
            title="Excluir cotação"
            className="opacity-0 group-hover:opacity-100 transition-opacity p-1 rounded hover:bg-red-50 text-gray-300 hover:text-red-500"
          >
            <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
            </svg>
          </button>
        </div>
      </div>
    </div>
  )
}

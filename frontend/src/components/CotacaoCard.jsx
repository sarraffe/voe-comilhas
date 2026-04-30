import { useNavigate } from 'react-router-dom'
import StatusBadge from './StatusBadge'

function formatDate(dateStr) {
  if (!dateStr) return '—'
  const [y, m, d] = dateStr.split('-')
  return `${d}/${m}/${y}`
}

export default function CotacaoCard({ cotacao }) {
  const navigate = useNavigate()
  const cliente = cotacao.clientes || {}

  return (
    <div
      onClick={() => navigate(`/cotacoes/${cotacao.id}`)}
      className="card hover:shadow-md hover:border-primary/20 cursor-pointer transition-all duration-200 group"
    >
      <div className="flex items-start justify-between mb-3">
        <div className="flex-1 min-w-0">
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
        <StatusBadge status={cotacao.status} />
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
        <span className="flex items-center gap-1">
          <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
              d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z" />
          </svg>
          {(cotacao.adultos || 1)} adulto{(cotacao.adultos || 1) > 1 ? 's' : ''}
          {cotacao.criancas > 0 ? ` · ${cotacao.criancas} criança${cotacao.criancas > 1 ? 's' : ''}` : ''}
        </span>
      </div>
    </div>
  )
}

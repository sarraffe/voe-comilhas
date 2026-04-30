const STATUS_CONFIG = {
  dados_incompletos: { label: 'Dados Incompletos', color: 'bg-gray-100 text-gray-600' },
  novo:              { label: 'Novo',              color: 'bg-blue-100 text-blue-700' },
  em_cotacao:        { label: 'Em Cotação',        color: 'bg-yellow-100 text-yellow-700' },
  proposta_enviada:  { label: 'Proposta Enviada',  color: 'bg-purple-100 text-purple-700' },
  aguardando_cliente:{ label: 'Aguardando Cliente',color: 'bg-orange-100 text-orange-700' },
  vendido:           { label: 'Vendido ✓',         color: 'bg-green-100 text-green-700' },
  perdido:           { label: 'Perdido',            color: 'bg-red-100 text-red-700' },
}

export default function StatusBadge({ status }) {
  const config = STATUS_CONFIG[status] || { label: status, color: 'bg-gray-100 text-gray-600' }
  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${config.color}`}>
      {config.label}
    </span>
  )
}

export { STATUS_CONFIG }

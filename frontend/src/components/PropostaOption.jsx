function formatDate(dateStr) {
  if (!dateStr) return '—'
  const [y, m, d] = dateStr.split('-')
  return `${d}/${m}/${y}`
}

function formatCurrency(value) {
  if (!value) return '—'
  return new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(value)
}

function formatDatetime(dateStr) {
  if (!dateStr) return '—'
  return new Date(dateStr).toLocaleDateString('pt-BR', {
    day: '2-digit', month: '2-digit', year: 'numeric',
    hour: '2-digit', minute: '2-digit'
  })
}

export default function PropostaOption({ opcao, index, whatsapp }) {
  const destaqueColors = {
    'Mais barata': 'bg-green-50 border-green-200',
    'Mais rápida': 'bg-blue-50 border-blue-200',
    'Melhor custo-benefício': 'bg-purple-50 border-purple-200',
  }

  const borderClass = destaqueColors[opcao.destaque] || 'bg-white border-gray-200'

  const handleWhatsApp = () => {
    const phone = '55' + (whatsapp || '').replace(/\D/g, '')
    const msg = encodeURIComponent(`Olá! Quero confirmar a opção ${index + 1} da proposta: ${opcao.companhia} - ${opcao.origem} → ${opcao.destino} - ${formatDate(opcao.data_voo)} - ${formatCurrency(opcao.valor_total)}`)
    window.open(`https://wa.me/${phone}?text=${msg}`, '_blank')
  }

  return (
    <div className={`rounded-2xl border-2 p-6 ${borderClass} transition-all hover:shadow-md`}>
      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="text-xs font-bold text-gray-400 uppercase tracking-wider">Opção {index + 1}</span>
            {opcao.destaque && (
              <span className="bg-primary text-white text-xs font-semibold px-2 py-0.5 rounded-full">
                {opcao.destaque}
              </span>
            )}
          </div>
          <h3 className="text-xl font-bold text-gray-900">{opcao.companhia || 'Companhia não informada'}</h3>
        </div>
        <div className="text-right">
          <p className="text-xs text-gray-400">Total</p>
          <p className="text-2xl font-bold text-primary">{formatCurrency(opcao.valor_total)}</p>
        </div>
      </div>

      {/* Trecho */}
      <div className="bg-gray-50 rounded-xl p-4 mb-4">
        <div className="flex items-center justify-between">
          <div className="text-center">
            <p className="text-2xl font-bold text-gray-900">{opcao.origem || '—'}</p>
            <p className="text-sm text-gray-500">{opcao.horario_saida || '—'}</p>
          </div>
          <div className="flex-1 mx-4 flex flex-col items-center">
            <div className="flex items-center gap-1 w-full">
              <div className="h-0.5 flex-1 bg-gray-300"></div>
              <svg className="w-4 h-4 text-primary flex-shrink-0" fill="currentColor" viewBox="0 0 24 24">
                <path d="M21 16v-2l-8-5V3.5c0-.83-.67-1.5-1.5-1.5S10 2.67 10 3.5V9l-8 5v2l8-2.5V19l-2 1.5V22l3.5-1 3.5 1v-1.5L13 19v-5.5l8 2.5z"/>
              </svg>
              <div className="h-0.5 flex-1 bg-gray-300"></div>
            </div>
            <p className="text-xs text-gray-400 mt-1">{formatDate(opcao.data_voo)}</p>
            {opcao.paradas && <p className="text-xs text-orange-500 font-medium">{opcao.paradas}</p>}
          </div>
          <div className="text-center">
            <p className="text-2xl font-bold text-gray-900">{opcao.destino || '—'}</p>
            <p className="text-sm text-gray-500">{opcao.horario_chegada || '—'}</p>
          </div>
        </div>
      </div>

      {/* Detalhes */}
      <div className="grid grid-cols-2 gap-3 mb-4 text-sm">
        {opcao.bagagem && (
          <div className="flex items-center gap-2 text-gray-600">
            <svg className="w-4 h-4 text-gray-400 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
            </svg>
            <span>{opcao.bagagem}</span>
          </div>
        )}
        {opcao.validade && (
          <div className="flex items-center gap-2 text-gray-600">
            <svg className="w-4 h-4 text-gray-400 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <span>Válido até: {formatDatetime(opcao.validade)}</span>
          </div>
        )}
      </div>

      {opcao.regras && (
        <div className="bg-yellow-50 border border-yellow-100 rounded-lg p-3 mb-4 text-xs text-yellow-800">
          <strong>Regras:</strong> {opcao.regras}
        </div>
      )}

      {/* Botões */}
      <div className="flex gap-2 mt-4">
        <button
          onClick={handleWhatsApp}
          className="flex-1 bg-[#25D366] hover:bg-[#20b858] text-white font-semibold py-2.5 px-4 rounded-xl transition-colors flex items-center justify-center gap-2"
        >
          <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
            <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z"/>
          </svg>
          Escolher esta opção
        </button>
      </div>
    </div>
  )
}

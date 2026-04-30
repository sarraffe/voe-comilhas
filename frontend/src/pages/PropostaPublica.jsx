import { useState, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import axios from 'axios'
import PropostaOption from '../components/PropostaOption'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

function formatDate(d) {
  if (!d) return '—'
  const [y, m, dd] = d.split('-')
  return `${dd}/${m}/${y}`
}

export default function PropostaPublica() {
  const { codigo } = useParams()
  const [proposta, setProposta] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    axios.get(`${API_URL}/propostas/${codigo}`)
      .then(res => setProposta(res.data))
      .catch(() => setError('Proposta não encontrada ou código inválido.'))
      .finally(() => setLoading(false))
  }, [codigo])

  if (loading) return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center">
      <div className="text-center">
        <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-[#1A3A8F] mx-auto mb-3"></div>
        <p className="text-gray-500 text-sm">Carregando proposta...</p>
      </div>
    </div>
  )

  if (error || !proposta) return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow p-8 text-center max-w-sm w-full">
        <svg className="w-12 h-12 text-red-300 mx-auto mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
        </svg>
        <p className="text-gray-600 font-medium">{error || 'Proposta não encontrada.'}</p>
        <p className="text-sm text-gray-400 mt-1">Verifique o link recebido ou entre em contato com nossa equipe.</p>
      </div>
    </div>
  )

  const cliente = proposta.clientes || {}
  const opcoes = proposta.opcoes_voo || []
  const whatsapp = cliente.whatsapp || ''

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#EEF2FF] to-gray-50">

      {/* Header */}
      <header className="bg-[#1A3A8F] shadow-lg">
        <div className="max-w-3xl mx-auto px-4 py-5 flex items-center gap-3">
          <div className="bg-white/10 rounded-xl p-2.5">
            <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
            </svg>
          </div>
          <div>
            <h1 className="text-white font-bold text-lg leading-tight">Voe Comilhas</h1>
            <p className="text-white/60 text-xs">Proposta de Passagem Aérea</p>
          </div>
        </div>
      </header>

      <main className="max-w-3xl mx-auto px-4 py-8 space-y-6">

        {/* Boas-vindas */}
        <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
          <h2 className="text-xl font-bold text-gray-900 mb-1">
            Olá{cliente.nome ? `, ${cliente.nome.split(' ')[0]}` : ''}! 👋
          </h2>
          <p className="text-gray-500 text-sm">Preparamos as melhores opções de voo para a sua viagem.</p>
        </div>

        {/* Resumo da Viagem */}
        <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
          <h3 className="font-bold text-gray-900 mb-4">Resumo da Viagem</h3>
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-4">
            <div>
              <p className="text-xs text-gray-400 uppercase font-medium mb-0.5">Tipo</p>
              <p className="font-semibold text-gray-900">
                {proposta.tipo_viagem === 'ida_volta' ? 'Ida e Volta' : 'Somente Ida'}
              </p>
            </div>
            <div>
              <p className="text-xs text-gray-400 uppercase font-medium mb-0.5">Origem</p>
              <p className="font-semibold text-gray-900">{proposta.origem || '—'}</p>
            </div>
            <div>
              <p className="text-xs text-gray-400 uppercase font-medium mb-0.5">Destino</p>
              <p className="font-semibold text-gray-900">{proposta.destino || '—'}</p>
            </div>
            <div>
              <p className="text-xs text-gray-400 uppercase font-medium mb-0.5">Data de Ida</p>
              <p className="font-semibold text-gray-900">{formatDate(proposta.data_ida)}</p>
            </div>
            {proposta.data_volta && (
              <div>
                <p className="text-xs text-gray-400 uppercase font-medium mb-0.5">Data de Volta</p>
                <p className="font-semibold text-gray-900">{formatDate(proposta.data_volta)}</p>
              </div>
            )}
            <div>
              <p className="text-xs text-gray-400 uppercase font-medium mb-0.5">Passageiros</p>
              <p className="font-semibold text-gray-900">
                {proposta.adultos || 1} adulto{(proposta.adultos || 1) > 1 ? 's' : ''}
                {proposta.criancas > 0 ? ` · ${proposta.criancas} criança${proposta.criancas > 1 ? 's' : ''}` : ''}
                {proposta.bebes > 0 ? ` · ${proposta.bebes} bebê${proposta.bebes > 1 ? 's' : ''}` : ''}
              </p>
            </div>
            {proposta.forma_pagamento && (
              <div>
                <p className="text-xs text-gray-400 uppercase font-medium mb-0.5">Pagamento</p>
                <p className="font-semibold text-gray-900">{proposta.forma_pagamento}</p>
              </div>
            )}
          </div>
        </div>

        {/* Opções de Voo */}
        <div>
          <h3 className="font-bold text-gray-900 mb-4 text-lg">
            {opcoes.length === 1 ? 'Opção de Voo' : `${opcoes.length} Opções de Voo`}
          </h3>
          {opcoes.length === 0 ? (
            <div className="bg-white rounded-2xl shadow-sm p-8 text-center">
              <p className="text-gray-400">As opções de voo estão sendo preparadas. Em breve você receberá uma atualização!</p>
            </div>
          ) : (
            <div className="space-y-4">
              {opcoes.map((opcao, index) => (
                <PropostaOption key={opcao.id} opcao={opcao} index={index} whatsapp={whatsapp} />
              ))}
            </div>
          )}
        </div>

        {/* CTA WhatsApp */}
        <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6 text-center">
          <p className="text-gray-600 mb-4 text-sm">Tem dúvidas ou quer confirmar uma opção? Fale com nossa equipe!</p>
          <a
            href={`https://wa.me/${('55' + whatsapp.replace(/\D/g, '')).replace(/^55+/, '55')}?text=Ol%C3%A1%2C+quero+saber+mais+sobre+minha+proposta+${proposta.codigo_proposta}`}
            target="_blank"
            rel="noreferrer"
            className="inline-flex items-center gap-2 bg-[#25D366] hover:bg-[#20b858] text-white font-semibold py-3 px-6 rounded-xl transition-colors"
          >
            <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
              <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z"/>
            </svg>
            Falar no WhatsApp
          </a>
        </div>

        {/* Rodapé */}
        <div className="text-center pb-4">
          <p className="text-xs text-gray-400">
            Proposta gerada pela Voe Comilhas · Código: {proposta.codigo_proposta}
          </p>
          <p className="text-xs text-gray-300 mt-1">
            Valores e disponibilidade sujeitos a alteração. Entre em contato para confirmar.
          </p>
        </div>

      </main>
    </div>
  )
}

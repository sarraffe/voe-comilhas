"""
Serviço de Inteligência Artificial - OpenAI.
Conduz a conversa com o cliente para coletar dados de cotação.
"""
import json
import logging
from typing import Optional
from openai import OpenAI
from config import settings

logger = logging.getLogger(__name__)

# ── Cliente OpenAI (singleton) ────────────────────────────────────────────────
_openai_client: Optional[OpenAI] = None

def get_openai_client() -> OpenAI:
    global _openai_client
    if _openai_client is None:
        if not settings.openai_api_key:
            raise ValueError("OPENAI_API_KEY não configurada.")
        _openai_client = OpenAI(api_key=settings.openai_api_key)
    return _openai_client


# ── PROMPT DO SISTEMA ─────────────────────────────────────────────────────────
SYSTEM_PROMPT = """
Você é a assistente virtual da Voe Comilhas, uma agência de viagens especializada em passagens aéreas, economia com milhas e atendimento personalizado.

Sua função é atender clientes pelo WhatsApp e coletar os dados necessários para uma cotação de passagem aérea.

Você deve conversar de forma natural, simpática, objetiva e profissional.

Você nunca deve dizer que é uma inteligência artificial.

Você nunca deve inventar preços, horários, voos ou disponibilidade.

Você não realiza a cotação final. Sua função é coletar os dados e encaminhar para a equipe.

DADOS QUE DEVEM SER COLETADOS:

1. tipo_viagem: "ida_volta" ou "somente_ida"
2. origem: cidade/aeroporto de origem
3. destino: cidade/aeroporto de destino
4. data_ida: data de ida no formato YYYY-MM-DD
5. data_volta: data de volta no formato YYYY-MM-DD (somente se tipo_viagem = "ida_volta")
6. adultos: número de adultos (default 1)
7. criancas: número de crianças (default 0)
8. bebes: número de bebês (default 0)
9. bagagem_23kg: true ou false
10. quantidade_malas: número de malas (somente se bagagem_23kg = true)
11. forma_pagamento: forma de pagamento desejada
12. nome_cliente: nome do cliente
13. whatsapp_cliente: número de WhatsApp do cliente
14. observacoes: observações adicionais (opcional)

REGRAS DE CONVERSA:

- Faça uma pergunta por vez sempre que possível.
- Se o cliente enviar várias informações juntas, extraia todas.
- Se faltar informação, pergunte apenas o que falta.
- Se o cliente perguntar preço antes de informar os dados, diga que para buscar a melhor opção precisa concluir os dados da viagem.
- Se o cliente disser que quer passagem barata, pergunte se ele tem flexibilidade nas datas.
- Se o cliente informar Manaus, considerar MAO.
- Se informar São Gabriel da Cachoeira, considerar SJL.
- Se informar São Paulo, perguntar se pode considerar todos os aeroportos: GRU, CGH e VCP.
- Se for ida e volta, data_volta é obrigatória.
- Se for somente ida, data_volta pode ser null.
- Se não informar crianças ou bebês, considerar 0.
- Se não informar bagagem, perguntar se precisa incluir bagagem despachada de 23kg.
- Se bagagem_23kg for false, quantidade_malas deve ser 0.
- Quando todos os dados estiverem completos, status_cotacao deve ser "novo".
- Enquanto faltar dado, status_cotacao deve ser "dados_incompletos".

DADOS OBRIGATÓRIOS PARA CONSIDERAR COMPLETO:
- tipo_viagem ✓
- origem ✓
- destino ✓
- data_ida ✓
- data_volta ✓ (somente se ida e volta)
- adultos ✓ (ao menos 1)
- bagagem_23kg ✓ (precisa ser confirmado explicitamente)
- forma_pagamento ✓
- nome_cliente ✓

MENSAGEM INICIAL:
Quando for a primeira mensagem do cliente, responda com:
"Olá! Seja bem-vindo à Voe Comilhas. Vou te ajudar a encontrar a melhor opção de passagem. Sua viagem será ida e volta ou somente ida?"

RESUMO FINAL:
Quando os dados estiverem completos, responda com este formato exato:

Perfeito, já tenho todos os dados da sua cotação:

Cliente: {nome_cliente}
WhatsApp: {whatsapp_cliente}
Tipo de viagem: {tipo_viagem}
Origem: {origem}
Destino: {destino}
Data de ida: {data_ida}
Data de volta: {data_volta}
Adultos: {adultos}
Crianças: {criancas}
Bebês: {bebes}
Bagagem: {sim/não + quantidade de malas}
Forma de pagamento: {forma_pagamento}
Observações: {observacoes}

Nossa equipe vai buscar as melhores opções disponíveis e te retornar em breve.

FORMATO DE RESPOSTA:
Você DEVE sempre responder APENAS em JSON válido com esta estrutura exata.
Não escreva NADA fora do JSON. Não use markdown. Não use ```json. Apenas o JSON puro.

{
  "resposta_cliente": "texto que será enviado ao cliente",
  "dados_extraidos": {
    "tipo_viagem": null,
    "origem": null,
    "destino": null,
    "data_ida": null,
    "data_volta": null,
    "adultos": null,
    "criancas": null,
    "bebes": null,
    "bagagem_23kg": null,
    "quantidade_malas": null,
    "forma_pagamento": null,
    "nome_cliente": null,
    "whatsapp_cliente": null,
    "observacoes": null
  },
  "status_cotacao": "dados_incompletos",
  "dados_completos": false
}

Preencha dados_extraidos apenas com os campos que foram informados pelo cliente.
Mantenha null para campos ainda não informados.
"""


# ── FUNÇÃO PRINCIPAL ──────────────────────────────────────────────────────────

def processar_mensagem_cliente(
    mensagem_cliente: str,
    cotacao_atual: dict,
    historico: list
) -> dict:
    """
    Processa a mensagem do cliente usando a OpenAI.

    Args:
        mensagem_cliente: Texto da mensagem recebida
        cotacao_atual: Dados atuais da cotação (campos já preenchidos)
        historico: Lista de mensagens recentes [{origem_mensagem, conteudo}]

    Returns:
        dict com: resposta_cliente, dados_extraidos, status_cotacao, dados_completos
    """
    client = get_openai_client()

    # Montar contexto da cotação atual para o modelo
    cotacao_context = _format_cotacao_context(cotacao_atual)

    # Montar histórico de mensagens para a API
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
    ]

    # Adicionar contexto da cotação atual (como mensagem de sistema adicional)
    if cotacao_context:
        messages.append({
            "role": "system",
            "content": f"DADOS ATUAIS DA COTAÇÃO:\n{cotacao_context}"
        })

    # Adicionar histórico de conversas
    for msg in historico:
        role = "user" if msg.get("origem_mensagem") == "cliente" else "assistant"
        messages.append({"role": role, "content": msg.get("conteudo", "")})

    # Adicionar mensagem atual do cliente
    messages.append({"role": "user", "content": mensagem_cliente})

    logger.info(f"[OpenAI] Enviando {len(messages)} mensagens para o modelo {settings.openai_model}")

    try:
        response = client.chat.completions.create(
            model=settings.openai_model,
            messages=messages,
            temperature=0.7,
            max_tokens=1000,
            response_format={"type": "json_object"},
        )

        content = response.choices[0].message.content.strip()
        logger.debug(f"[OpenAI] Resposta bruta: {content[:200]}...")

        # Parse do JSON retornado
        result = json.loads(content)
        logger.info(f"[OpenAI] Resposta processada. Status: {result.get('status_cotacao')} | Completo: {result.get('dados_completos')}")
        return result

    except json.JSONDecodeError as e:
        logger.error(f"[OpenAI] Erro ao parsear JSON da resposta: {e}")
        return _fallback_response("Desculpe, tive um problema técnico. Pode repetir sua mensagem?")

    except Exception as e:
        logger.error(f"[OpenAI] Erro inesperado: {e}")
        return _fallback_response("Desculpe, ocorreu um erro. Nossa equipe foi notificada. Tente novamente em instantes.")


# ── FUNÇÕES AUXILIARES ────────────────────────────────────────────────────────

def _format_cotacao_context(cotacao: dict) -> str:
    """Formata os dados atuais da cotação para contexto do prompt."""
    if not cotacao:
        return ""

    campos = [
        ("tipo_viagem", "Tipo de viagem"),
        ("origem", "Origem"),
        ("destino", "Destino"),
        ("data_ida", "Data de ida"),
        ("data_volta", "Data de volta"),
        ("adultos", "Adultos"),
        ("criancas", "Crianças"),
        ("bebes", "Bebês"),
        ("bagagem_23kg", "Bagagem 23kg"),
        ("quantidade_malas", "Quantidade de malas"),
        ("forma_pagamento", "Forma de pagamento"),
        ("observacoes", "Observações"),
    ]

    linhas = []
    for campo, label in campos:
        valor = cotacao.get(campo)
        if valor is not None and valor != "" and valor != 0:
            linhas.append(f"- {label}: {valor}")

    return "\n".join(linhas) if linhas else "Nenhum dado coletado ainda."


def _fallback_response(mensagem: str) -> dict:
    """Resposta de fallback em caso de erro."""
    return {
        "resposta_cliente": mensagem,
        "dados_extraidos": {
            "tipo_viagem": None,
            "origem": None,
            "destino": None,
            "data_ida": None,
            "data_volta": None,
            "adultos": None,
            "criancas": None,
            "bebes": None,
            "bagagem_23kg": None,
            "quantidade_malas": None,
            "forma_pagamento": None,
            "nome_cliente": None,
            "whatsapp_cliente": None,
            "observacoes": None,
        },
        "status_cotacao": "dados_incompletos",
        "dados_completos": False,
    }

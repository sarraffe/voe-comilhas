"""
Serviço de Inteligência Artificial - OpenAI.
Conduz a conversa com o cliente para coletar dados de cotação.
"""
import json
import logging
from datetime import date
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
def _get_system_prompt() -> str:
    hoje = date.today().strftime("%d/%m/%Y")
    return f"""
Você é a Camila, assistente virtual da Voe Comilhas — agência especializada em passagens aéreas e atendimento personalizado pelo WhatsApp.

Converse de forma calorosa, simpática e profissional. Use linguagem natural e objetiva. Use emojis APENAS na saudação inicial e no resumo final. No restante da conversa, NÃO use emojis.

Você NUNCA deve dizer que é uma inteligência artificial.
Você NUNCA inventa preços, horários, voos ou disponibilidade.
Sua função é coletar os dados e encaminhar para a equipe humana cotar.

DATA DE HOJE: {hoje}
REGRA ABSOLUTA DE DATAS: NUNCA aceite datas no passado. Todas as datas de viagem devem ser a partir de hoje ({hoje}). Se o cliente informar uma data que já passou, explique gentilmente que não é possível cotar viagens para datas passadas e peça uma nova data.

FORMATO DE DATA: Sempre peça e exiba datas no formato brasileiro DD/MM/AAAA. NUNCA peça no formato americano (mês/dia/ano ou ano/mês/dia). Internamente converta para YYYY-MM-DD antes de salvar em data_ida e data_volta.

FORMAS DE PAGAMENTO: As únicas formas aceitas são PIX ou cartão de crédito. Se o cliente perguntar sobre outra forma (boleto, dinheiro, milhas, etc.), informe que trabalhamos apenas com PIX ou cartão de crédito. Ao mencionar cartão de crédito, informe que há um pequeno acréscimo de 2% por parcela.

DADOS QUE DEVEM SER COLETADOS:

1. tipo_viagem: "ida_volta" ou "somente_ida"
2. origem: cidade/aeroporto de origem
3. destino: cidade/aeroporto de destino
4. data_ida: data de ida — pergunte em DD/MM/AAAA, salve internamente em YYYY-MM-DD
5. data_volta: data de volta — apenas se ida e volta, mesma regra de formato
6. adultos: número de adultos (default 1)
7. criancas: número de crianças entre 2 e 11 anos (default 0)
8. bebes: número de bebês até 2 anos (default 0)
9. bagagem_23kg: true ou false
10. quantidade_malas: número de malas (somente se bagagem_23kg = true)
11. forma_pagamento: "pix" ou "cartao_credito" — NUNCA aceitar outra opção
12. nome_cliente: nome do cliente
13. observacoes: observações adicionais (opcional)

REGRAS DE CONVERSA:

- Faça uma pergunta por vez sempre que possível.
- Se o cliente enviar várias informações juntas, extraia todas de uma vez.
- Se faltar informação, pergunte apenas o que falta.
- Se o cliente perguntar preço antes de completar os dados, diga que precisa finalizar o cadastro para buscar a melhor opção.
- Se o cliente quiser passagem barata, pergunte se tem flexibilidade de datas.
- Se o cliente informar Manaus, considere o aeroporto MAO.
- Se informar São Gabriel da Cachoeira, considere SJL.
- Se informar São Paulo, pergunte se pode considerar todos os aeroportos: GRU, CGH e VCP.
- Se for ida e volta, data_volta é obrigatória.
- Se for somente ida, data_volta pode ser null.
- Se não informar crianças ou bebês, assuma 0.
- Sempre perguntar sobre bagagem despachada de 23kg se não informado.
- Se bagagem_23kg for false, quantidade_malas deve ser 0.
- Quando todos os dados estiverem completos, status_cotacao deve ser "novo".
- Enquanto faltar dado, status_cotacao deve ser "dados_incompletos".

DADOS OBRIGATÓRIOS PARA CONSIDERAR COMPLETO:
- tipo_viagem ✓
- origem ✓
- destino ✓
- data_ida ✓ (futura, formato YYYY-MM-DD internamente)
- data_volta ✓ (somente se ida e volta, futura)
- adultos ✓ (ao menos 1)
- bagagem_23kg ✓ (confirmado explicitamente)
- forma_pagamento ✓
- nome_cliente ✓

MENSAGEM INICIAL:
Quando for a primeira mensagem do cliente, responda com:
"Olá! ✈️ Seja bem-vindo à Voe Comilhas! Sou a Camila e vou te ajudar a encontrar a melhor opção de passagem aérea. Sua viagem será ida e volta ou somente ida?"

RESUMO FINAL:
Quando os dados estiverem completos, envie este resumo (use apenas estes emojis no resumo):

✅ Perfeito! Já tenho todos os dados da sua cotação:

Cliente: {{nome_cliente}}
Trecho: {{origem}} → {{destino}}
Tipo: {{ida e volta / somente ida}}
Data de ida: {{data_ida em DD/MM/AAAA}}
Data de volta: {{data_volta em DD/MM/AAAA ou "Somente ida"}}
Passageiros: {{adultos}} adulto(s){{, criancas criança(s) se > 0}}{{, bebes bebê(s) se > 0}}
Bagagem: {{Sim — X mala(s) / Não}}
Pagamento: {{PIX / Cartão de crédito (acréscimo de 2% por parcela)}}
Observações: {{observacoes ou "Nenhuma"}}

Nossa equipe já vai buscar as melhores opções e retorna em breve! 🚀

FORMATO DE RESPOSTA:
Você DEVE sempre responder APENAS em JSON válido com esta estrutura exata.
Não escreva NADA fora do JSON. Não use markdown. Não use ```json. Apenas o JSON puro.

{{
  "resposta_cliente": "texto que será enviado ao cliente",
  "dados_extraidos": {{
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
    "observacoes": null
  }},
  "status_cotacao": "dados_incompletos",
  "dados_completos": false
}}

Preencha dados_extraidos apenas com os campos que foram informados pelo cliente.
Mantenha null para campos ainda não informados.
data_ida e data_volta devem ser salvas SEMPRE no formato YYYY-MM-DD (para o banco de dados), mesmo que o cliente informe em DD/MM/AAAA.
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
        {"role": "system", "content": _get_system_prompt()},
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

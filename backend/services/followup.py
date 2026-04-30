"""
Serviço de Follow-up Automático.
Envia mensagens a cada 30 minutos para clientes com proposta enviada,
até que o cliente responda ou o limite de follow-ups seja atingido.
"""
import logging
from datetime import datetime, timezone, timedelta

from services import supabase_service as db
from services.uazapi import send_text_message

logger = logging.getLogger(__name__)

# ── Configurações ──────────────────────────────────────────────────────────────
MAX_FOLLOWUPS = 5                  # máximo de follow-ups (5 × 30min = 2h30)
INTERVALO_MINUTOS = 30             # intervalo entre follow-ups

# Sequência de mensagens de follow-up
MENSAGENS_FOLLOWUP = [
    "Olá! Passando para ver se conseguiu verificar a proposta de passagem que enviamos. Alguma dúvida?",
    "Oi! Só lembrando que as tarifas aéreas podem mudar a qualquer momento. Se quiser garantir sua passagem, é só falar!",
    "Olá! Nossa equipe está à disposição para esclarecer qualquer dúvida sobre a proposta ou ajustar alguma informação.",
    "Oi! Gostaríamos de saber se a proposta atendeu suas expectativas. Pode nos dar um retorno?",
    "Olá! Esta é nossa última mensagem automática. Caso queira continuar, é só chamar. Estamos aqui para ajudar!",
]


# ── Função principal ───────────────────────────────────────────────────────────

def executar_followups():
    """
    Verifica todas as cotações com proposta enviada e envia follow-up
    se necessário. Executado pelo scheduler a cada 30 minutos.
    """
    logger.info("[Follow-up] Iniciando verificação de follow-ups...")

    cotacoes = db.get_cotacoes_proposta_enviada()
    if not cotacoes:
        logger.info("[Follow-up] Nenhuma cotação com proposta enviada.")
        return

    agora = datetime.now(timezone.utc)
    enviados = 0

    for cotacao in cotacoes:
        try:
            cotacao_id = cotacao["id"]
            cliente = cotacao.get("clientes") or {}
            phone = cliente.get("whatsapp")
            nome = cliente.get("nome") or "cliente"

            if not phone:
                logger.warning(f"[Follow-up] Cotação {cotacao_id} sem WhatsApp, pulando.")
                continue

            # Verificar se cliente já respondeu (última mensagem é do cliente)
            ultima_msg = db.get_last_message(cotacao_id)
            if ultima_msg and ultima_msg.get("origem_mensagem") == "cliente":
                logger.info(f"[Follow-up] Cotação {cotacao_id}: cliente respondeu, sem follow-up.")
                continue

            # Verificar limite de follow-ups
            count = db.get_followup_count(cotacao_id)
            if count >= MAX_FOLLOWUPS:
                logger.info(f"[Follow-up] Cotação {cotacao_id}: limite atingido ({count}/{MAX_FOLLOWUPS}).")
                continue

            # Verificar se já passou o intervalo desde o último follow-up
            ultimo_followup = db.get_last_followup_time(cotacao_id)
            if ultimo_followup:
                # Converter para datetime com timezone
                if ultimo_followup.endswith("Z"):
                    ultimo_followup = ultimo_followup.replace("Z", "+00:00")
                dt_ultimo = datetime.fromisoformat(ultimo_followup)
                if dt_ultimo.tzinfo is None:
                    dt_ultimo = dt_ultimo.replace(tzinfo=timezone.utc)
                if agora - dt_ultimo < timedelta(minutes=INTERVALO_MINUTOS):
                    logger.debug(f"[Follow-up] Cotação {cotacao_id}: aguardando intervalo.")
                    continue

            # Selecionar mensagem da sequência
            mensagem = MENSAGENS_FOLLOWUP[count]

            # Enviar via WhatsApp
            sucesso = send_text_message(phone, mensagem)
            if sucesso:
                # Salvar follow-up no histórico de mensagens
                db.save_message(cotacao_id=cotacao_id, cliente_id=cliente["id"],
                                origem_mensagem="followup", conteudo=mensagem)
                enviados += 1
                logger.info(f"[Follow-up] #{count + 1} enviado para {phone} (cotação {cotacao_id})")
            else:
                logger.error(f"[Follow-up] Falha ao enviar para {phone}")

        except Exception as e:
            logger.error(f"[Follow-up] Erro ao processar cotação {cotacao.get('id')}: {e}")

    logger.info(f"[Follow-up] Verificação concluída. Follow-ups enviados: {enviados}")

"""
Rota do Webhook - recebe mensagens da Uazapi (WhatsApp).
Este é o coração do agente inteligente.
"""
import logging
from fastapi import APIRouter, Request, BackgroundTasks
from fastapi.responses import JSONResponse

from services import supabase_service as db
from services import uazapi
from services import agente_openai

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/webhook/uazapi")
async def webhook_uazapi(request: Request, background_tasks: BackgroundTasks):
    """
    Recebe payload bruto da Uazapi e processa a mensagem.
    Sempre retorna 200 para a Uazapi não reenviar.
    """
    try:
        payload = await request.json()
    except Exception:
        logger.warning("[Webhook] Payload inválido recebido.")
        return JSONResponse(status_code=200, content={"ok": True})

    # Processar em background para responder rápido à Uazapi
    background_tasks.add_task(_processar_mensagem, payload)
    return JSONResponse(status_code=200, content={"ok": True})


async def _processar_mensagem(payload: dict):
    """
    Pipeline completo de processamento de mensagem.
    Executa de forma assíncrona para não bloquear o webhook.
    """
    # 1. Salvar payload bruto para debug
    try:
        db.save_webhook_log("uazapi", payload)
    except Exception as e:
        logger.error(f"[Webhook] Erro ao salvar log: {e}")

    # 2. Extrair informações da mensagem
    parsed = uazapi.parse_incoming_message(payload)
    if not parsed:
        logger.debug("[Webhook] Mensagem ignorada (não processável).")
        return

    phone = parsed["phone"]
    name = parsed.get("name")
    text = parsed["text"]

    logger.info(f"[Webhook] Nova mensagem de {phone}: {text[:80]}...")

    # 3. Identificar ou criar cliente
    try:
        cliente = db.get_or_create_cliente(phone, name)
        cliente_id = cliente["id"]
    except Exception as e:
        logger.error(f"[Webhook] Erro ao obter/criar cliente {phone}: {e}")
        return

    # 4. Buscar cotação aberta do cliente
    try:
        cotacao = db.get_cotacao_aberta(cliente_id)
        if not cotacao:
            cotacao = db.create_cotacao(cliente_id)
        cotacao_id = cotacao["id"]
    except Exception as e:
        logger.error(f"[Webhook] Erro ao obter/criar cotação para {cliente_id}: {e}")
        return

    # 5. Salvar mensagem recebida
    try:
        db.save_message(cliente_id, cotacao_id, "cliente", text)
    except Exception as e:
        logger.error(f"[Webhook] Erro ao salvar mensagem: {e}")

    # 6. Buscar histórico recente de mensagens (excluindo a que acabamos de salvar)
    try:
        historico = db.get_recent_messages(cliente_id, cotacao_id, limit=12)
        # Remover a última mensagem (a que acabamos de salvar) para evitar duplicação
        if historico and historico[-1].get("origem_mensagem") == "cliente":
            historico = historico[:-1]
    except Exception as e:
        logger.warning(f"[Webhook] Erro ao buscar histórico: {e}")
        historico = []

    # 7. Processar com OpenAI
    try:
        resultado = agente_openai.processar_mensagem_cliente(
            mensagem_cliente=text,
            cotacao_atual=cotacao,
            historico=historico,
        )
    except Exception as e:
        logger.error(f"[Webhook] Erro ao processar com OpenAI: {e}")
        # Enviar mensagem de erro genérica
        uazapi.send_text_message(phone, "Desculpe, ocorreu um erro interno. Tente novamente em instantes.")
        return

    # 8. Atualizar cotação com dados extraídos
    try:
        dados_extraidos = resultado.get("dados_extraidos", {})
        novo_status = resultado.get("status_cotacao", "dados_incompletos")

        # Montar update apenas com campos não-nulos
        update_data = {k: v for k, v in dados_extraidos.items() if v is not None}
        update_data["status"] = novo_status

        if update_data:
            db.update_cotacao(cotacao_id, update_data)

        # Se dados completos, garantir status "novo"
        if resultado.get("dados_completos") and novo_status == "dados_incompletos":
            db.update_status(cotacao_id, "novo")

    except Exception as e:
        logger.error(f"[Webhook] Erro ao atualizar cotação {cotacao_id}: {e}")

    # 9. Obter resposta do agente
    resposta_agente = resultado.get("resposta_cliente", "")
    if not resposta_agente:
        logger.warning("[Webhook] Agente não retornou resposta para o cliente.")
        return

    # 10. Salvar resposta do agente
    try:
        db.save_message(cliente_id, cotacao_id, "agente", resposta_agente)
    except Exception as e:
        logger.error(f"[Webhook] Erro ao salvar resposta do agente: {e}")

    # 11. Enviar resposta para o cliente via Uazapi
    sucesso = uazapi.send_text_message(phone, resposta_agente)
    if sucesso:
        logger.info(f"[Webhook] Resposta enviada para {phone} ✓")
    else:
        logger.error(f"[Webhook] Falha ao enviar resposta para {phone}")

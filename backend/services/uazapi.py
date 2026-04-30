"""
Serviço de integração com a Uazapi (WhatsApp).
Responsável por envio de mensagens e configuração do webhook.
"""
import re
import logging
from typing import Optional
import requests
from config import settings

logger = logging.getLogger(__name__)


# ── NORMALIZAÇÃO DE TELEFONE ───────────────────────────────────────────────────

def normalize_phone(phone: str) -> str:
    """
    Normaliza número de telefone:
    - Remove caracteres especiais (espaços, parênteses, traços, +)
    - Garante DDI 55 para números brasileiros
    """
    # Remover tudo que não é dígito
    digits = re.sub(r"\D", "", phone)

    # Se começa com 55 e tem 12 ou 13 dígitos → já está correto
    if digits.startswith("55") and len(digits) in (12, 13):
        return digits

    # Se tem 10 ou 11 dígitos → adiciona DDI 55
    if len(digits) in (10, 11):
        return "55" + digits

    # Caso já venha com 55 mas sem comprimento correto, retorna como está
    return digits


# ── ENVIO DE MENSAGEM ─────────────────────────────────────────────────────────

def send_text_message(phone: str, message: str) -> bool:
    """
    Envia mensagem de texto via Uazapi.
    Retorna True se sucesso, False se falha.
    """
    if not settings.uazapi_base_url or not settings.uazapi_token:
        logger.error("[Uazapi] UAZAPI_BASE_URL ou UAZAPI_TOKEN não configurados.")
        return False

    normalized = normalize_phone(phone)
    url = f"{settings.uazapi_base_url}/message/text"

    headers = {
        "token": settings.uazapi_token,
        "Content-Type": "application/json",
    }

    payload = {
        "to": normalized,
        "text": message,
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=15)
        response.raise_for_status()
        logger.info(f"[Uazapi] Mensagem enviada para {normalized} ✓")
        return True
    except requests.exceptions.Timeout:
        logger.error(f"[Uazapi] Timeout ao enviar mensagem para {normalized}")
        return False
    except requests.exceptions.HTTPError as e:
        logger.error(f"[Uazapi] Erro HTTP ao enviar mensagem: {e.response.status_code} - {e.response.text}")
        return False
    except Exception as e:
        logger.error(f"[Uazapi] Erro inesperado ao enviar mensagem: {e}")
        return False


# ── CONFIGURAÇÃO DO WEBHOOK ────────────────────────────────────────────────────

def configure_webhook() -> bool:
    """
    Configura o webhook na Uazapi apontando para o endpoint da aplicação.
    Endpoint destino: {WEBHOOK_PUBLIC_URL}/webhook/uazapi
    """
    if not settings.uazapi_base_url or not settings.uazapi_admin_token:
        logger.error("[Uazapi] UAZAPI_BASE_URL ou UAZAPI_ADMIN_TOKEN não configurados.")
        return False

    webhook_url = f"{settings.webhook_public_url}/webhook/uazapi"
    url = f"{settings.uazapi_base_url}/instance/webhook"

    headers = {
        "token": settings.uazapi_admin_token,
        "Content-Type": "application/json",
    }

    payload = {
        "instanceId": settings.uazapi_instance_id,
        "webhook": webhook_url,
        "webhookEnabled": True,
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=15)
        response.raise_for_status()
        logger.info(f"[Uazapi] Webhook configurado: {webhook_url} ✓")
        return True
    except requests.exceptions.HTTPError as e:
        logger.error(f"[Uazapi] Erro ao configurar webhook: {e.response.status_code} - {e.response.text}")
        return False
    except Exception as e:
        logger.error(f"[Uazapi] Erro inesperado ao configurar webhook: {e}")
        return False


# ── PARSE DE MENSAGEM RECEBIDA ─────────────────────────────────────────────────

def parse_incoming_message(payload: dict) -> Optional[dict]:
    """
    Extrai informações relevantes do payload bruto da Uazapi.

    Retorna dict com:
    - phone: número do remetente
    - name: nome do contato (se disponível)
    - text: texto da mensagem
    - message_id: ID da mensagem
    - timestamp: timestamp da mensagem
    - message_type: tipo da mensagem
    - from_me: se foi enviada pelo próprio número
    - is_group: se é mensagem de grupo

    Retorna None se a mensagem não deve ser processada.
    """
    try:
        # Estrutura típica da Uazapi
        # O payload pode variar dependendo da versão da Uazapi
        event = payload.get("event") or payload.get("type") or ""
        data = payload.get("data") or payload

        # Ignorar eventos que não sejam de mensagem
        if event and "message" not in event.lower():
            logger.debug(f"[Uazapi] Evento ignorado: {event}")
            return None

        # Suporte a diferentes estruturas de payload da Uazapi
        message = data.get("message") or data

        # Verificar se é mensagem própria
        from_me = (
            message.get("fromMe")
            or message.get("from_me")
            or data.get("fromMe")
            or False
        )
        if from_me:
            logger.debug("[Uazapi] Mensagem própria ignorada.")
            return None

        # Verificar se é grupo
        remote_jid = (
            message.get("remoteJid")
            or message.get("remote_jid")
            or data.get("remoteJid")
            or data.get("chatId")
            or ""
        )
        is_group = "@g.us" in str(remote_jid)
        if is_group:
            logger.debug("[Uazapi] Mensagem de grupo ignorada.")
            return None

        # Extrair número do remetente
        phone = (
            message.get("from")
            or message.get("sender")
            or data.get("from")
            or data.get("sender")
            or remote_jid
            or ""
        )
        # Remover sufixos do WhatsApp (@s.whatsapp.net, @c.us)
        phone = re.sub(r"@.*", "", str(phone))
        phone = re.sub(r"\D", "", phone)

        if not phone:
            logger.warning("[Uazapi] Número do remetente não encontrado no payload.")
            return None

        # Extrair nome do contato
        name = (
            data.get("pushName")
            or data.get("notifyName")
            or message.get("pushName")
            or message.get("notifyName")
            or None
        )

        # Extrair texto da mensagem
        text = (
            message.get("text")
            or message.get("body")
            or message.get("conversation")
            or (message.get("extendedTextMessage") or {}).get("text")
            or data.get("text")
            or data.get("body")
            or ""
        )

        if not text:
            logger.debug("[Uazapi] Mensagem sem texto (mídia ou outro tipo) ignorada.")
            return None

        # Extrair metadados
        message_id = (
            message.get("id")
            or data.get("id")
            or ""
        )
        timestamp = (
            message.get("timestamp")
            or message.get("messageTimestamp")
            or data.get("timestamp")
            or None
        )
        message_type = (
            message.get("type")
            or data.get("type")
            or "text"
        )

        return {
            "phone": phone,
            "name": name,
            "text": str(text).strip(),
            "message_id": message_id,
            "timestamp": timestamp,
            "message_type": message_type,
            "from_me": from_me,
            "is_group": is_group,
        }

    except Exception as e:
        logger.error(f"[Uazapi] Erro ao fazer parse da mensagem: {e}")
        return None

"""
Serviço de integração com o Supabase.
Todas as operações de banco de dados passam por aqui.
"""
import logging
import uuid
from typing import Optional, List
from supabase import create_client, Client
from config import settings

logger = logging.getLogger(__name__)

# ── Cliente Supabase (singleton) ──────────────────────────────────────────────
def get_supabase() -> Client:
    if not settings.supabase_url or not settings.supabase_service_role_key:
        raise ValueError("SUPABASE_URL e SUPABASE_SERVICE_ROLE_KEY são obrigatórios.")
    return create_client(settings.supabase_url, settings.supabase_service_role_key)


# ── CLIENTES ──────────────────────────────────────────────────────────────────

def get_or_create_cliente(whatsapp: str, nome: Optional[str] = None) -> dict:
    """Busca cliente pelo WhatsApp ou cria um novo."""
    supabase = get_supabase()
    try:
        res = supabase.table("clientes").select("*").eq("whatsapp", whatsapp).single().execute()
        cliente = res.data
        # Atualiza nome se não tinha e agora chegou
        if cliente and nome and not cliente.get("nome"):
            supabase.table("clientes").update({"nome": nome}).eq("id", cliente["id"]).execute()
            cliente["nome"] = nome
        logger.info(f"[Supabase] Cliente encontrado: {whatsapp}")
        return cliente
    except Exception:
        # Cliente não existe → criar
        data = {"whatsapp": whatsapp}
        if nome:
            data["nome"] = nome
        res = supabase.table("clientes").insert(data).execute()
        cliente = res.data[0]
        logger.info(f"[Supabase] Cliente criado: {whatsapp}")
        return cliente


# ── COTAÇÕES ──────────────────────────────────────────────────────────────────

def get_cotacao_aberta(cliente_id: str) -> Optional[dict]:
    """Retorna a cotação aberta mais recente do cliente (status != vendido/perdido)."""
    supabase = get_supabase()
    try:
        res = (
            supabase.table("cotacoes")
            .select("*")
            .eq("cliente_id", cliente_id)
            .not_.in_("status", ["vendido", "perdido"])
            .order("created_at", desc=True)
            .limit(1)
            .execute()
        )
        if res.data:
            logger.info(f"[Supabase] Cotação aberta encontrada para cliente {cliente_id}")
            return res.data[0]
        return None
    except Exception as e:
        logger.error(f"[Supabase] Erro ao buscar cotação aberta: {e}")
        return None


def create_cotacao(cliente_id: str) -> dict:
    """Cria nova cotação com status dados_incompletos."""
    supabase = get_supabase()
    data = {
        "cliente_id": cliente_id,
        "status": "dados_incompletos",
        "adultos": 1,
        "criancas": 0,
        "bebes": 0,
        "bagagem_23kg": False,
        "quantidade_malas": 0,
    }
    res = supabase.table("cotacoes").insert(data).execute()
    logger.info(f"[Supabase] Cotação criada para cliente {cliente_id}")
    return res.data[0]


def update_cotacao(cotacao_id: str, data: dict) -> dict:
    """Atualiza campos de uma cotação."""
    supabase = get_supabase()
    # Remover campos None para não sobrescrever valores existentes
    clean_data = {k: v for k, v in data.items() if v is not None}
    if not clean_data:
        return get_cotacao_by_id(cotacao_id)
    res = supabase.table("cotacoes").update(clean_data).eq("id", cotacao_id).execute()
    logger.info(f"[Supabase] Cotação {cotacao_id} atualizada: {list(clean_data.keys())}")
    return res.data[0] if res.data else {}


def update_status(cotacao_id: str, status: str) -> dict:
    """Atualiza apenas o status de uma cotação."""
    supabase = get_supabase()
    res = supabase.table("cotacoes").update({"status": status}).eq("id", cotacao_id).execute()
    logger.info(f"[Supabase] Status da cotação {cotacao_id} → {status}")
    return res.data[0] if res.data else {}


def list_cotacoes(status: Optional[str] = None, search: Optional[str] = None) -> List[dict]:
    """Lista cotações com dados do cliente via join."""
    supabase = get_supabase()
    query = supabase.table("cotacoes").select(
        "*, clientes(id, nome, whatsapp)"
    ).order("created_at", desc=True)
    if status:
        query = query.eq("status", status)
    res = query.execute()
    return res.data or []


def get_cotacao_by_id(cotacao_id: str) -> Optional[dict]:
    """Retorna cotação pelo ID com dados do cliente."""
    supabase = get_supabase()
    try:
        res = supabase.table("cotacoes").select(
            "*, clientes(id, nome, whatsapp)"
        ).eq("id", cotacao_id).single().execute()
        return res.data
    except Exception as e:
        logger.error(f"[Supabase] Cotação {cotacao_id} não encontrada: {e}")
        return None


# ── MENSAGENS ─────────────────────────────────────────────────────────────────

def save_message(
    cliente_id: str,
    cotacao_id: Optional[str],
    origem_mensagem: str,
    conteudo: str
) -> dict:
    """Salva mensagem de cliente ou agente."""
    supabase = get_supabase()
    data = {
        "cliente_id": cliente_id,
        "cotacao_id": cotacao_id,
        "origem_mensagem": origem_mensagem,
        "conteudo": conteudo,
    }
    res = supabase.table("mensagens").insert(data).execute()
    return res.data[0] if res.data else {}


def get_recent_messages(
    cliente_id: str,
    cotacao_id: Optional[str] = None,
    limit: int = 10
) -> List[dict]:
    """Retorna mensagens recentes ordenadas do mais antigo para o mais novo."""
    supabase = get_supabase()
    query = supabase.table("mensagens").select("*").eq("cliente_id", cliente_id)
    if cotacao_id:
        query = query.eq("cotacao_id", cotacao_id)
    res = query.order("created_at", desc=True).limit(limit).execute()
    # Reverter para ordem cronológica (mais antigo primeiro)
    return list(reversed(res.data or []))


# ── OPÇÕES DE VOO ─────────────────────────────────────────────────────────────

def create_opcao_voo(cotacao_id: str, data: dict) -> dict:
    """Cria uma opção de voo para uma cotação."""
    supabase = get_supabase()
    data["cotacao_id"] = cotacao_id
    res = supabase.table("opcoes_voo").insert(data).execute()
    logger.info(f"[Supabase] Opção de voo criada para cotação {cotacao_id}")
    return res.data[0] if res.data else {}


def list_opcoes_voo(cotacao_id: str) -> List[dict]:
    """Lista opções de voo de uma cotação."""
    supabase = get_supabase()
    res = (
        supabase.table("opcoes_voo")
        .select("*")
        .eq("cotacao_id", cotacao_id)
        .order("created_at")
        .execute()
    )
    return res.data or []


# ── PROPOSTA ──────────────────────────────────────────────────────────────────

def generate_codigo_proposta(cotacao_id: str) -> str:
    """Gera código único para a proposta e salva na cotação."""
    supabase = get_supabase()
    # Gera código curto único: VC + 8 chars do UUID
    codigo = "VC" + str(uuid.uuid4()).replace("-", "").upper()[:8]
    supabase.table("cotacoes").update({"codigo_proposta": codigo, "status": "proposta_enviada"}).eq("id", cotacao_id).execute()
    logger.info(f"[Supabase] Proposta gerada para cotação {cotacao_id}: {codigo}")
    return codigo


def get_proposta_by_codigo(codigo: str) -> Optional[dict]:
    """Retorna proposta completa com opções de voo pelo código."""
    supabase = get_supabase()
    try:
        res = supabase.table("cotacoes").select(
            "*, clientes(id, nome, whatsapp), opcoes_voo(*)"
        ).eq("codigo_proposta", codigo).single().execute()
        return res.data
    except Exception as e:
        logger.error(f"[Supabase] Proposta {codigo} não encontrada: {e}")
        return None


# ── WEBHOOK LOGS ──────────────────────────────────────────────────────────────

def save_webhook_log(origem: str, payload: dict) -> dict:
    """Salva payload bruto do webhook para debug."""
    supabase = get_supabase()
    try:
        res = supabase.table("webhook_logs").insert({
            "origem": origem,
            "payload": payload
        }).execute()
        return res.data[0] if res.data else {}
    except Exception as e:
        logger.error(f"[Supabase] Erro ao salvar webhook log: {e}")
        return {}

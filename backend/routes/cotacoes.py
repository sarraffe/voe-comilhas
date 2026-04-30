"""
Rotas de gerenciamento de cotações.
Usadas pelo painel administrativo.
"""
import logging
from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List

from services import supabase_service as db
from schemas.cotacao_schema import CotacaoUpdate, CotacaoStatusUpdate
from schemas.proposta_schema import OpcaoVooCreate

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/cotacoes", tags=["Cotações"])


@router.get("")
def list_cotacoes(
    status: Optional[str] = Query(None, description="Filtrar por status"),
    search: Optional[str] = Query(None, description="Buscar por nome ou telefone"),
):
    """Lista todas as cotações com dados do cliente."""
    try:
        cotacoes = db.list_cotacoes(status=status, search=search)
        return {"data": cotacoes, "total": len(cotacoes)}
    except Exception as e:
        logger.error(f"[Cotações] Erro ao listar: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{cotacao_id}")
def get_cotacao(cotacao_id: str):
    """Retorna detalhes de uma cotação pelo ID."""
    cotacao = db.get_cotacao_by_id(cotacao_id)
    if not cotacao:
        raise HTTPException(status_code=404, detail="Cotação não encontrada.")
    return cotacao


@router.patch("/{cotacao_id}")
def update_cotacao(cotacao_id: str, data: CotacaoUpdate):
    """Atualiza dados de uma cotação."""
    cotacao = db.get_cotacao_by_id(cotacao_id)
    if not cotacao:
        raise HTTPException(status_code=404, detail="Cotação não encontrada.")
    try:
        updated = db.update_cotacao(cotacao_id, data.model_dump(exclude_none=True))
        return updated
    except Exception as e:
        logger.error(f"[Cotações] Erro ao atualizar {cotacao_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/{cotacao_id}/status")
def update_status(cotacao_id: str, data: CotacaoStatusUpdate):
    """Atualiza apenas o status de uma cotação."""
    cotacao = db.get_cotacao_by_id(cotacao_id)
    if not cotacao:
        raise HTTPException(status_code=404, detail="Cotação não encontrada.")
    try:
        updated = db.update_status(cotacao_id, data.status)
        return updated
    except Exception as e:
        logger.error(f"[Cotações] Erro ao atualizar status {cotacao_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{cotacao_id}/opcoes")
def create_opcao_voo(cotacao_id: str, data: OpcaoVooCreate):
    """Cadastra uma opção de voo para a cotação (máximo 3)."""
    cotacao = db.get_cotacao_by_id(cotacao_id)
    if not cotacao:
        raise HTTPException(status_code=404, detail="Cotação não encontrada.")

    # Verificar limite de 3 opções
    opcoes = db.list_opcoes_voo(cotacao_id)
    if len(opcoes) >= 3:
        raise HTTPException(
            status_code=400,
            detail="Limite de 3 opções de voo por cotação atingido."
        )

    try:
        opcao = db.create_opcao_voo(cotacao_id, data.model_dump(exclude_none=True))
        return opcao
    except Exception as e:
        logger.error(f"[Cotações] Erro ao criar opção de voo: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{cotacao_id}/opcoes")
def list_opcoes_voo(cotacao_id: str):
    """Lista as opções de voo de uma cotação."""
    cotacao = db.get_cotacao_by_id(cotacao_id)
    if not cotacao:
        raise HTTPException(status_code=404, detail="Cotação não encontrada.")
    opcoes = db.list_opcoes_voo(cotacao_id)
    return {"data": opcoes, "total": len(opcoes)}


@router.post("/{cotacao_id}/gerar-proposta")
def gerar_proposta(cotacao_id: str):
    """Gera código único de proposta e altera status para proposta_enviada."""
    cotacao = db.get_cotacao_by_id(cotacao_id)
    if not cotacao:
        raise HTTPException(status_code=404, detail="Cotação não encontrada.")

    # Verificar se tem ao menos 1 opção de voo
    opcoes = db.list_opcoes_voo(cotacao_id)
    if not opcoes:
        raise HTTPException(
            status_code=400,
            detail="É necessário cadastrar ao menos 1 opção de voo antes de gerar a proposta."
        )

    try:
        codigo = db.generate_codigo_proposta(cotacao_id)
        from config import settings
        link = f"{settings.frontend_url}/proposta/{codigo}"
        return {
            "codigo": codigo,
            "link": link,
            "message": "Proposta gerada com sucesso! Compartilhe o link com o cliente."
        }
    except Exception as e:
        logger.error(f"[Cotações] Erro ao gerar proposta {cotacao_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{cotacao_id}")
def delete_cotacao(cotacao_id: str):
    """Exclui uma cotação e seus registros relacionados."""
    cotacao = db.get_cotacao_by_id(cotacao_id)
    if not cotacao:
        raise HTTPException(status_code=404, detail="Cotação não encontrada.")
    success = db.delete_cotacao(cotacao_id)
    if not success:
        raise HTTPException(status_code=500, detail="Erro ao excluir cotação.")
    return {"ok": True, "message": "Cotação excluída com sucesso."}


@router.get("/{cotacao_id}/mensagens")
def get_mensagens(
    cotacao_id: str,
    limit: int = Query(50, ge=1, le=200),
):
    """Retorna mensagens de uma cotação para o painel admin."""
    cotacao = db.get_cotacao_by_id(cotacao_id)
    if not cotacao:
        raise HTTPException(status_code=404, detail="Cotação não encontrada.")
    mensagens = db.get_recent_messages(
        cotacao["cliente_id"], cotacao_id, limit=limit
    )
    return {"data": mensagens, "total": len(mensagens)}

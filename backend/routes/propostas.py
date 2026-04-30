"""
Rota pública de propostas.
Acessível sem autenticação pelo cliente final.
"""
import logging
from fastapi import APIRouter, HTTPException
from services import supabase_service as db

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/propostas", tags=["Propostas"])


@router.get("/{codigo}")
def get_proposta(codigo: str):
    """
    Retorna proposta completa pelo código.
    Endpoint público — acessado pela página de proposta do cliente.
    """
    proposta = db.get_proposta_by_codigo(codigo)
    if not proposta:
        raise HTTPException(
            status_code=404,
            detail="Proposta não encontrada ou código inválido."
        )
    return proposta

"""
Rotas de clientes.
"""
import logging
from fastapi import APIRouter, HTTPException
from services import supabase_service as db

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/clientes", tags=["Clientes"])


@router.get("")
def list_clientes():
    """Lista todos os clientes."""
    try:
        supabase = db.get_supabase()
        res = supabase.table("clientes").select("*").order("created_at", desc=True).execute()
        return {"data": res.data or [], "total": len(res.data or [])}
    except Exception as e:
        logger.error(f"[Clientes] Erro ao listar: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{cliente_id}")
def get_cliente(cliente_id: str):
    """Retorna dados de um cliente pelo ID."""
    try:
        supabase = db.get_supabase()
        res = supabase.table("clientes").select("*").eq("id", cliente_id).single().execute()
        return res.data
    except Exception as e:
        raise HTTPException(status_code=404, detail="Cliente não encontrado.")


@router.get("/{cliente_id}/cotacoes")
def get_cotacoes_cliente(cliente_id: str):
    """Retorna cotações de um cliente."""
    try:
        supabase = db.get_supabase()
        res = (
            supabase.table("cotacoes")
            .select("*")
            .eq("cliente_id", cliente_id)
            .order("created_at", desc=True)
            .execute()
        )
        return {"data": res.data or [], "total": len(res.data or [])}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

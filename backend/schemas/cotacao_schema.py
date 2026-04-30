from pydantic import BaseModel
from typing import Optional, Literal
from datetime import datetime, date


StatusCotacao = Literal[
    "dados_incompletos",
    "novo",
    "em_cotacao",
    "proposta_enviada",
    "aguardando_cliente",
    "vendido",
    "perdido",
]


class CotacaoUpdate(BaseModel):
    tipo_viagem: Optional[str] = None
    origem: Optional[str] = None
    destino: Optional[str] = None
    data_ida: Optional[date] = None
    data_volta: Optional[date] = None
    adultos: Optional[int] = None
    criancas: Optional[int] = None
    bebes: Optional[int] = None
    bagagem_23kg: Optional[bool] = None
    quantidade_malas: Optional[int] = None
    forma_pagamento: Optional[str] = None
    observacoes: Optional[str] = None


class CotacaoStatusUpdate(BaseModel):
    status: StatusCotacao


class CotacaoResponse(BaseModel):
    id: str
    cliente_id: Optional[str] = None
    tipo_viagem: Optional[str] = None
    origem: Optional[str] = None
    destino: Optional[str] = None
    data_ida: Optional[date] = None
    data_volta: Optional[date] = None
    adultos: Optional[int] = None
    criancas: Optional[int] = None
    bebes: Optional[int] = None
    bagagem_23kg: Optional[bool] = None
    quantidade_malas: Optional[int] = None
    forma_pagamento: Optional[str] = None
    observacoes: Optional[str] = None
    status: Optional[str] = None
    codigo_proposta: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    clientes: Optional[dict] = None

    class Config:
        from_attributes = True

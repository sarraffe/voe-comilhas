from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date


class OpcaoVooCreate(BaseModel):
    companhia: Optional[str] = None
    origem: Optional[str] = None
    destino: Optional[str] = None
    data_voo: Optional[date] = None
    horario_saida: Optional[str] = None
    horario_chegada: Optional[str] = None
    paradas: Optional[str] = None
    bagagem: Optional[str] = None
    regras: Optional[str] = None
    valor_total: Optional[float] = None
    destaque: Optional[str] = None
    validade: Optional[datetime] = None


class OpcaoVooResponse(OpcaoVooCreate):
    id: str
    cotacao_id: str
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class PropostaPublicaResponse(BaseModel):
    id: str
    codigo_proposta: str
    tipo_viagem: Optional[str] = None
    origem: Optional[str] = None
    destino: Optional[str] = None
    data_ida: Optional[date] = None
    data_volta: Optional[date] = None
    adultos: Optional[int] = None
    criancas: Optional[int] = None
    bebes: Optional[int] = None
    bagagem_23kg: Optional[bool] = None
    forma_pagamento: Optional[str] = None
    clientes: Optional[dict] = None
    opcoes_voo: Optional[list] = None

    class Config:
        from_attributes = True

from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ClienteBase(BaseModel):
    whatsapp: str
    nome: Optional[str] = None


class ClienteCreate(ClienteBase):
    pass


class ClienteResponse(ClienteBase):
    id: str
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

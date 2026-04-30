"""
Configurações centralizadas da aplicação.
Lê variáveis do .env automaticamente.
"""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Supabase
    supabase_url: str = ""
    supabase_service_role_key: str = ""

    # OpenAI
    openai_api_key: str = ""
    openai_model: str = "gpt-4.1-mini"

    # Uazapi
    uazapi_base_url: str = ""
    uazapi_token: str = ""
    uazapi_admin_token: str = ""
    uazapi_instance_id: str = ""
    webhook_public_url: str = ""

    # Aplicação
    app_env: str = "development"
    backend_port: int = 8000
    frontend_url: str = "http://localhost:5173"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()

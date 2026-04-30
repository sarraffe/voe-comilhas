"""
Voe Comilhas - Agente Inteligente de Cotação
Backend FastAPI - Ponto de entrada da aplicação
"""
import logging
import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from config import settings
from routes import webhook_uazapi, cotacoes, clientes, propostas

# ── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.DEBUG if settings.app_env == "development" else logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    stream=sys.stdout,
)
logger = logging.getLogger(__name__)


# ── Lifespan ──────────────────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Executado na inicialização e desligamento da aplicação."""
    logger.info("=" * 60)
    logger.info("🛫 Voe Comilhas - Agente Inteligente de Cotação")
    logger.info(f"   Ambiente : {settings.app_env}")
    logger.info(f"   Porta    : {settings.backend_port}")
    logger.info(f"   Frontend : {settings.frontend_url}")
    logger.info(f"   Webhook  : {settings.webhook_public_url}/webhook/uazapi")
    logger.info("=" * 60)

    # Configurar webhook na Uazapi ao iniciar
    if settings.uazapi_base_url and settings.uazapi_token and settings.webhook_public_url:
        from services.uazapi import configure_webhook
        logger.info("🔗 Configurando webhook na Uazapi...")
        configure_webhook()
    else:
        logger.warning("⚠️  Variáveis Uazapi não configuradas — webhook não configurado.")

    yield

    logger.info("🛬 Aplicação encerrada.")


# ── App ────────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="Voe Comilhas - API",
    description="Agente Inteligente de Cotação de Passagens Aéreas",
    version="1.0.0",
    lifespan=lifespan,
)

# ── CORS ──────────────────────────────────────────────────────────────────────
# Origens sempre permitidas (dev + produção Netlify)
allowed_origins = [
    "http://localhost:5173",
    "http://localhost:3000",
    "https://voe-comilhas.netlify.app",
]
# Adiciona FRONTEND_URL do env se vier diferente das acima
if settings.frontend_url and settings.frontend_url not in allowed_origins:
    allowed_origins.append(settings.frontend_url)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Rotas ──────────────────────────────────────────────────────────────────────
app.include_router(webhook_uazapi.router)
app.include_router(cotacoes.router)
app.include_router(clientes.router)
app.include_router(propostas.router)


# ── Health Check ──────────────────────────────────────────────────────────────
@app.get("/health", tags=["Sistema"])
def health_check():
    """Verifica se o serviço está no ar."""
    return {
        "status": "ok",
        "service": "Voe Comilhas API",
        "version": "1.0.0",
        "environment": settings.app_env,
    }


@app.get("/", tags=["Sistema"])
def root():
    return {
        "message": "Voe Comilhas - Agente Inteligente de Cotação",
        "docs": "/docs",
        "health": "/health",
    }


# ── Handler de erros genérico ─────────────────────────────────────────────────
@app.exception_handler(Exception)
async def generic_exception_handler(request, exc):
    logger.error(f"Erro não tratado: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Erro interno do servidor. Verifique os logs."},
    )


# ── Entrada direta ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.backend_port,
        reload=settings.app_env == "development",
        log_level="debug" if settings.app_env == "development" else "info",
    )

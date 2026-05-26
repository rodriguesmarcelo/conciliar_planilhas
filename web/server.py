# -*- coding: utf-8 -*-
"""Aplicação FastAPI da plataforma barelli.automacao."""
import asyncio
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from web.auth import get_current_user
from web.config import get_settings
from web.modules.conciliador import storage
from web.modules.registry import ALL_MODULES, ModuleManifest, get_manifests

settings = get_settings()

# Build do frontend (gerado por `npm run build`). Pode não existir em dev.
DIST = Path(__file__).resolve().parent / "frontend" / "dist"

# Intervalo da limpeza periódica de temporários (uploads/resultados).
_CLEANUP_INTERVAL_SECONDS = 2 * 60 * 60


@asynccontextmanager
async def lifespan(app: FastAPI):
    storage.cleanup_old()

    async def _periodic_cleanup() -> None:
        while True:
            await asyncio.sleep(_CLEANUP_INTERVAL_SECONDS)
            storage.cleanup_old()

    task = asyncio.create_task(_periodic_cleanup())
    try:
        yield
    finally:
        task.cancel()


app = FastAPI(title=settings.app_name, version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclui os routers de cada módulo sob /api, já com o ponto de injeção do auth.
for module in ALL_MODULES:
    app.include_router(
        module.router,
        prefix="/api",
        dependencies=[Depends(get_current_user)],
    )


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/api/modules", response_model=list[ModuleManifest])
def modules() -> list[ModuleManifest]:
    return get_manifests()


# --- SPA (build do frontend) ----------------------------------------------
# Registrado por último para não ofuscar as rotas /api acima. Só ativa quando o
# build existe (em dev, o Vite serve o front na 5173 e a API fica só aqui).
if DIST.is_dir():
    app.mount("/assets", StaticFiles(directory=DIST / "assets"), name="assets")

    @app.get("/{full_path:path}")
    def serve_spa(full_path: str) -> FileResponse:
        if full_path.startswith("api"):
            raise HTTPException(status_code=404)
        candidate = DIST / full_path
        if full_path and candidate.is_file():
            return FileResponse(candidate)
        return FileResponse(DIST / "index.html")

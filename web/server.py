# -*- coding: utf-8 -*-
"""Aplicação FastAPI da plataforma barelli.automacao."""
from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from web.auth import get_current_user
from web.config import get_settings
from web.modules.registry import ALL_MODULES, ModuleManifest, get_manifests

settings = get_settings()

app = FastAPI(title=settings.app_name, version="0.1.0")

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

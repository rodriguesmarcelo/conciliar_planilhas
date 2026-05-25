# -*- coding: utf-8 -*-
"""Configuração tipada da plataforma barelli.automacao.

Lê de variáveis de ambiente (prefixo BARELLI_) e de um arquivo .env opcional.
"""
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="BARELLI_",
        extra="ignore",
    )

    app_name: str = "barelli.automacao"
    port: int = 8000

    # Autenticação desativada nesta fase (estrutura pronta em web/auth.py).
    auth_enabled: bool = False

    # Origens liberadas no CORS (Vite dev server por padrão).
    cors_origins: list[str] = ["http://localhost:5173"]

    # Override opcional do diretório de dados/perfis. Quando None, usa o padrão
    # de core/utils.py (raiz do projeto), compartilhado com o app desktop.
    data_dir: str | None = None


@lru_cache
def get_settings() -> Settings:
    return Settings()

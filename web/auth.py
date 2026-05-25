# -*- coding: utf-8 -*-
"""Stub de autenticação.

Enquanto AUTH_ENABLED for False, todas as requisições passam como usuário
anônimo. A dependency get_current_user já é declarada pelos routers, então o
ponto de injeção para ativar login no futuro já existe.
"""
from fastapi import Depends
from pydantic import BaseModel

from web.config import Settings, get_settings


class User(BaseModel):
    id: str
    name: str


ANONYMOUS = User(id="anon", name="Anônimo")


def get_current_user(settings: Settings = Depends(get_settings)) -> User:
    if not settings.auth_enabled:
        return ANONYMOUS
    # TODO: validar credenciais (sessão/token) quando AUTH_ENABLED=True.
    return ANONYMOUS

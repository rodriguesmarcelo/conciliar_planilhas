# -*- coding: utf-8 -*-
"""Inicializa o servidor web da plataforma barelli.automacao.

Execute SEMPRE a partir da raiz do projeto para que `core` e `web` resolvam
nos imports:

    python run_web.py

A porta vem de BARELLI_PORT (ou .env), padrão 8000. Fica acessível na intranet
em http://<ip-do-servidor>:<porta>.
"""
import uvicorn

from web.config import get_settings

if __name__ == "__main__":
    settings = get_settings()
    uvicorn.run("web.server:app", host="0.0.0.0", port=settings.port)

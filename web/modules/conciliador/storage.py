# -*- coding: utf-8 -*-
"""Armazenamento temporário de uploads e resultados da conciliação.

Arquivos ficam em <tempdir>/barelli_automacao/. Resultados são identificados
por token e o nome sugerido para download é mantido em memória (vive enquanto o
servidor estiver no ar). cleanup_old() remove arquivos antigos.
"""
import os
import tempfile
import time
import uuid

BASE_DIR = os.path.join(tempfile.gettempdir(), "barelli_automacao")

# token -> nome de arquivo sugerido para o download
_RESULT_NAMES: dict[str, str] = {}


def _ensure_dir() -> None:
    os.makedirs(BASE_DIR, exist_ok=True)


def cleanup_old(ttl_minutes: int = 60) -> None:
    """Remove arquivos temporários mais antigos que ttl_minutes."""
    _ensure_dir()
    cutoff = time.time() - ttl_minutes * 60
    for name in os.listdir(BASE_DIR):
        path = os.path.join(BASE_DIR, name)
        try:
            if os.path.isfile(path) and os.path.getmtime(path) < cutoff:
                os.remove(path)
        except OSError:
            pass
    # Limpa nomes de resultados cujo arquivo não existe mais.
    for token in list(_RESULT_NAMES):
        if not os.path.isfile(os.path.join(BASE_DIR, f"result_{token}.xlsx")):
            _RESULT_NAMES.pop(token, None)


def save_upload(upload) -> str:
    """Grava um UploadFile (FastAPI) num arquivo temporário, preservando a extensão."""
    _ensure_dir()
    ext = os.path.splitext(upload.filename or "")[1].lower()
    path = os.path.join(BASE_DIR, f"upload_{uuid.uuid4().hex}{ext}")
    with open(path, "wb") as f:
        f.write(upload.file.read())
    return path


def new_result_path(suggested_name: str | None = None) -> tuple[str, str]:
    """Cria um token e o caminho do .xlsx de resultado."""
    _ensure_dir()
    token = uuid.uuid4().hex
    path = os.path.join(BASE_DIR, f"result_{token}.xlsx")
    if suggested_name:
        _RESULT_NAMES[token] = suggested_name
    return token, path


def result_path(token: str) -> str | None:
    path = os.path.join(BASE_DIR, f"result_{token}.xlsx")
    return path if os.path.isfile(path) else None


def result_name(token: str) -> str:
    return _RESULT_NAMES.get(token, f"Resultado_{token}.xlsx")


# Limpeza ao carregar o módulo.
cleanup_old()

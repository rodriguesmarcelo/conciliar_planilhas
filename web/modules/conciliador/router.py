# -*- coding: utf-8 -*-
"""Endpoints do módulo Conciliador. Reaproveita integralmente o core/."""
import uuid
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import FileResponse

from core.engine import run as engine_run
from core.exporter import export_result
from core.profile_builder import build_comparison, build_default_output, validate_profile
from core.profile_manager import (
    delete_profile,
    duplicate_profile,
    load_all_profiles,
    load_profile,
    save_profile,
)
from core.reader import (
    ColumnNotFoundError,
    InvalidFileError,
    preview_sheet,
    read_sheet,
    validate_columns,
)
from web.modules.conciliador import storage
from web.modules.conciliador.schemas import (
    PreviewResponse,
    ProfileInput,
    RunResponse,
)

XLSX_MEDIA_TYPE = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

XLS_MESSAGE = (
    "O arquivo selecionado está no formato antigo '.xls'.\n\n"
    "Por favor:\n"
    "  1. Abra o arquivo no Excel\n"
    "  2. Clique em Arquivo → Salvar Como\n"
    "  3. Escolha o formato 'Pasta de Trabalho do Excel (*.xlsx)'\n"
    "  4. Salve e selecione o novo arquivo aqui.\n\n"
    "O sistema aceita apenas arquivos .xlsx ou .csv."
)

router = APIRouter(prefix="/conciliador", tags=["conciliador"])


def _is_xls(upload: Optional[UploadFile]) -> bool:
    return bool(upload and (upload.filename or "").lower().endswith(".xls"))


def _safe_len(df) -> int:
    if df is None:
        return 0
    try:
        return len(df)
    except Exception:
        return 0


# ── Perfis ────────────────────────────────────────────────────────────────────

@router.get("/profiles")
def list_profiles() -> list:
    return list(load_all_profiles().values())


@router.get("/profiles/{profile_id}")
def get_profile(profile_id: str) -> dict:
    profile = load_profile(profile_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Perfil não encontrado.")
    return profile


@router.post("/profiles")
def save(profile_in: ProfileInput) -> dict:
    data = profile_in.model_dump()
    mode = data.get("mode", "dual")
    sheets = data.get("sheets", [])

    comp_in = data.get("comparison") or {}
    comparison = build_comparison(
        mode, comp_in.get("match_fields"), comp_in.get("one_to_one", False)
    )

    # Preserva o output ao editar um perfil existente; senão gera o default.
    existing = load_profile(data["id"]) if data.get("id") else None
    if existing and existing.get("output"):
        output = existing["output"]
    else:
        output = build_default_output(mode, sheets)

    profile = {
        "id": data.get("id") or str(uuid.uuid4()),
        "name": (data.get("name") or "").strip(),
        "mode": mode,
        "date_format": data.get("date_format", "dd/mm/yyyy"),
        "sheets": sheets,
        "comparison": comparison,
        "output": output,
    }

    err = validate_profile(profile)
    if err:
        raise HTTPException(status_code=400, detail=err)

    save_profile(profile)
    return profile


@router.post("/profiles/{profile_id}/duplicate")
def duplicate(profile_id: str) -> dict:
    novo = duplicate_profile(profile_id)
    if not novo:
        raise HTTPException(status_code=404, detail="Perfil não encontrado.")
    return novo


@router.delete("/profiles/{profile_id}")
def remove(profile_id: str) -> dict:
    if not delete_profile(profile_id):
        raise HTTPException(status_code=404, detail="Perfil não encontrado.")
    return {"deleted": True}


# ── Pré-visualização ────────────────────────────────────────────────────────────

@router.post("/preview", response_model=PreviewResponse)
def preview(file: UploadFile = File(...)) -> PreviewResponse:
    if _is_xls(file):
        raise HTTPException(status_code=400, detail=XLS_MESSAGE)
    path = storage.save_upload(file)
    try:
        rows = preview_sheet(path, max_rows=20)
    except InvalidFileError as e:
        raise HTTPException(status_code=400, detail=str(e))

    if not rows:
        return PreviewResponse(header=[], rows=[])
    header = [str(h) for h in rows[0]]
    data_rows = [["" if v is None else str(v) for v in r] for r in rows[1:]]
    return PreviewResponse(header=header, rows=data_rows)


# ── Execução ──────────────────────────────────────────────────────────────────

@router.post("/run/{profile_id}", response_model=RunResponse)
def run_reconciliation(
    profile_id: str,
    file_a: UploadFile = File(...),
    file_b: Optional[UploadFile] = File(None),
) -> RunResponse:
    profile = load_profile(profile_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Perfil não encontrado.")

    storage.cleanup_old()

    if _is_xls(file_a) or _is_xls(file_b):
        raise HTTPException(status_code=400, detail=XLS_MESSAGE)

    mode = profile.get("mode", "dual")
    sheets = profile.get("sheets", [])
    date_fmt = profile.get("date_format", "dd/mm/yyyy")

    if mode == "dual" and file_b is None:
        raise HTTPException(
            status_code=400,
            detail="Modo dual requer duas planilhas (file_a e file_b).",
        )

    path_a = storage.save_upload(file_a)
    path_b = storage.save_upload(file_b) if file_b else None

    try:
        validate_columns(path_a, sheets[0])
        if mode == "dual" and len(sheets) > 1:
            validate_columns(path_b, sheets[1])

        df_a = read_sheet(path_a, sheets[0], date_fmt)
        df_b = read_sheet(path_b, sheets[1], date_fmt) if (mode == "dual" and path_b) else None
        result = engine_run(profile, df_a, df_b)
    except (ColumnNotFoundError, InvalidFileError) as e:
        raise HTTPException(status_code=400, detail=str(e))

    nome = (profile.get("name") or "resultado").replace(" ", "_")
    suggested = f"Resultado_{nome}_{datetime.now().strftime('%d-%m-%Y')}.xlsx"
    token, out_path = storage.new_result_path(suggested)
    export_result(result, profile, out_path, file_a=path_a, file_b=path_b)

    if mode == "single":
        counts = {"normalizados": _safe_len(result.get("normalizados"))}
    else:
        counts = {
            "conciliados": _safe_len(result.get("conciliados")),
            "nao_conciliados_a": _safe_len(result.get("nao_conciliados_a")),
            "nao_conciliados_b": _safe_len(result.get("nao_conciliados_b")),
        }

    return RunResponse(
        mode=mode,
        counts=counts,
        download_token=token,
        suggested_filename=suggested,
    )


@router.get("/run/result/{token}")
def download_result(token: str) -> FileResponse:
    path = storage.result_path(token)
    if not path:
        raise HTTPException(status_code=404, detail="Resultado não encontrado ou expirado.")
    return FileResponse(path, media_type=XLSX_MEDIA_TYPE, filename=storage.result_name(token))

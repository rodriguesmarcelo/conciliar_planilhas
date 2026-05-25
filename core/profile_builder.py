# -*- coding: utf-8 -*-
"""Lógica de montagem e validação de perfis, compartilhada entre desktop e web.

Sem dependência de UI. Portado de ui/screen_profile.py para reuso pelo backend
web (web/modules/conciliador/router.py) e pelo app desktop.
"""
from __future__ import annotations

from typing import Optional

# Caracteres proibidos no Windows para nomes de arquivo (perfis viram .json).
INVALID_FILENAME_CHARS = set('/\\|:*?"<>')


def validate_profile(profile: dict) -> Optional[str]:
    """Valida um perfil montado. Retorna mensagem de erro ou None se válido."""
    name = (profile.get("name") or "").strip()
    if not name:
        return "O nome do perfil não pode estar vazio."

    found = [c for c in name if c in INVALID_FILENAME_CHARS]
    if found:
        chars_str = "  ".join(f"'{c}'" for c in sorted(set(found)))
        return (
            f"O nome do perfil contém caracteres inválidos: {chars_str}\n\n"
            f"Esses caracteres não são permitidos em nomes de arquivo no Windows.\n"
            f"Por favor, remova-os e tente novamente."
        )

    for i, sheet in enumerate(profile.get("sheets", [])):
        cols = sheet.get("columns", [])
        if not cols:
            lbl = sheet.get("label") or f"Planilha {'A' if i == 0 else 'B'}"
            return f"A planilha '{lbl}' deve ter ao menos 1 campo configurado."
        for col in cols:
            try:
                if int(col["col_index"]) < 1:
                    raise ValueError
            except (ValueError, TypeError, KeyError):
                return f"Índice de coluna inválido no campo '{col.get('field')}'."
    return None


def build_comparison(mode: str, match_fields=None, one_to_one: bool = False) -> dict:
    """Monta o bloco de comparação. No modo single, fica desabilitado."""
    if mode == "single":
        return {"enabled": False, "match_fields": [], "one_to_one": False}
    return {
        "enabled": True,
        "match_fields": list(match_fields or []),
        "one_to_one": bool(one_to_one),
    }


def build_default_output(mode: str, sheets: list) -> dict:
    """Gera o bloco `output` default a partir do modo e das planilhas."""
    if mode == "single":
        cols = [{"header": c["field"].replace("_", " ").title(),
                 "field": c["field"], "fixed_value": None}
                for c in (sheets[0].get("columns", []) if sheets else [])]
        return {"tabs": [{"name": "Dados Normalizados", "source": "normalizados", "columns": cols}]}

    la = sheets[0].get("label", "A") if sheets else "A"
    lb = sheets[1].get("label", "B") if len(sheets) > 1 else "B"

    def _cols(sh):
        return [{"header": c["field"].replace("_", " ").title(),
                 "field": c["field"], "fixed_value": None}
                for c in sh.get("columns", [])]

    cc = _cols(sheets[0]) + [
        {"header": f"Linha {la}", "field": "__linha___a", "fixed_value": None},
        {"header": f"Linha {lb}", "field": "__linha___b", "fixed_value": None}]

    return {"tabs": [
        {"name": "Dados Conciliados",          "source": "conciliados",       "columns": cc},
        {"name": f"Não Conciliados - {la}",    "source": "nao_conciliados_a",
         "columns": _cols(sheets[0]) + [{"header": f"Linha {la}", "field": "__linha__", "fixed_value": None}]},
        {"name": f"Não Conciliados - {lb}",    "source": "nao_conciliados_b",
         "columns": _cols(sheets[1] if len(sheets) > 1 else {}) + [{"header": f"Linha {lb}", "field": "__linha__", "fixed_value": None}]},
    ]}

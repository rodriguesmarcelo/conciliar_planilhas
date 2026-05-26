# -*- coding: utf-8 -*-
"""Interoperabilidade de perfis web ↔ desktop (Task 09).

A web (web/modules/conciliador/router.save) e o desktop
(ui/screen_profile) usam os MESMOS core/profile_builder + core/profile_manager.
Aqui um perfil é criado pelo caminho web, recarregado do disco (como o desktop
faria) e comparado ao que os builders compartilhados produzem.

    python tests/test_interop.py      (ou: pytest tests/test_interop.py)
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from _helpers import run_suite
from core.profile_builder import build_comparison, build_default_output, validate_profile
from core.profile_manager import delete_profile, load_profile
from web.modules.conciliador.router import save
from web.modules.conciliador.schemas import ColumnInput, ComparisonInput, ProfileInput, SheetInput


def test_web_profile_opens_on_desktop():
    profile_in = ProfileInput(
        id=None,
        name="__TESTE_INTEROP__",
        mode="dual",
        date_format="dd/mm/yyyy",
        sheets=[
            SheetInput(label="Razão", start_row=10, columns=[
                ColumnInput(field="data", col_index=1, skip_if_invalid_date=True),
                ColumnInput(field="valor", col_index=4),
            ]),
            SheetInput(label="Extrato", start_row=11, columns=[
                ColumnInput(field="data", col_index=1, skip_if_invalid_date=True),
                ColumnInput(field="valor", col_index=4),
            ]),
        ],
        comparison=ComparisonInput(match_fields=["data", "valor"], one_to_one=False),
    )

    saved = save(profile_in)  # caminho web: grava em profiles/ via save_profile
    try:
        # 1. Round-trip: o que o desktop leria do disco == o que a web gravou.
        reloaded = load_profile(saved["id"])
        assert reloaded == saved, "perfil recarregado difere do salvo"

        # 2. output/comparison vêm dos builders compartilhados (idêntico ao desktop).
        sheets = profile_in.model_dump()["sheets"]
        assert saved["comparison"] == build_comparison("dual", ["data", "valor"], False)
        assert saved["output"] == build_default_output("dual", sheets)

        # 3. Passa na mesma validação usada pelos dois lados.
        assert validate_profile(saved) is None
    finally:
        delete_profile(saved["id"])
        assert load_profile(saved["id"]) is None, "perfil de teste não foi removido"


if __name__ == "__main__":
    run_suite([
        ("perfil criado na web abre no desktop (round-trip + builders)", test_web_profile_opens_on_desktop),
    ])

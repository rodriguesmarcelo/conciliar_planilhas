# -*- coding: utf-8 -*-
"""Casos de borda (Task 09): .xls recusado, coluna fora do range, planilha
vazia, one_to_one (cheques) e datas inválidas.

    python tests/test_edge_cases.py   (ou: pytest tests/test_edge_cases.py)
"""
import copy
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import HTTPException

from _helpers import (
    compare_workbooks,
    counts_of,
    make_upload,
    make_xlsx,
    run_desktop_path,
    run_suite,
    run_web_path,
)
from core.profile_manager import delete_profile, load_profile, save_profile
from web.modules.conciliador.router import XLS_MESSAGE, run_reconciliation


def _row(n_cols, values_by_col):
    row = [None] * n_cols
    for col, val in values_by_col.items():
        row[col - 1] = val
    return row


def test_xls_rejected():
    tmp = tempfile.mkdtemp(prefix="edge_xls_")
    # Arquivo válido, mas apresentado com extensão .xls → deve ser recusado antes de ler.
    valid = make_xlsx(os.path.join(tmp, "real.xlsx"), 11, [_row(4, {1: "01/01/2024", 4: 1})], 4)
    upload = make_upload(valid, filename="extrato_antigo.xls")
    try:
        try:
            run_reconciliation("droga_bem", upload, upload)
            raise AssertionError("esperava HTTPException para .xls")
        except HTTPException as e:
            assert e.status_code == 400, e.status_code
            assert e.detail == XLS_MESSAGE
    finally:
        upload.file.close()


def test_column_out_of_range():
    profile = copy.deepcopy(load_profile("droga_bem"))
    profile["id"] = "__test_badcol__"
    profile["name"] = "__TEST_BADCOL__"
    # Aponta uma coluna inexistente na planilha B (extrato terá só 4 colunas).
    profile["sheets"][1]["columns"][1]["col_index"] = 99
    save_profile(profile)
    tmp = tempfile.mkdtemp(prefix="edge_col_")
    path_a = make_xlsx(os.path.join(tmp, "razao.xlsx"), 10,
                       [_row(10, {1: "01/01/2024", 3: "x", 9: 10.0})], 10)
    path_b = make_xlsx(os.path.join(tmp, "extrato.xlsx"), 11,
                       [_row(4, {1: "01/01/2024", 2: "x", 4: 10.0})], 4)
    try:
        try:
            run_web_path("__test_badcol__", path_a, path_b, os.path.join(tmp, "out.xlsx"))
            raise AssertionError("esperava HTTPException para coluna fora do range")
        except HTTPException as e:
            assert e.status_code == 400, e.status_code
            assert "não foi encontrada" in e.detail, e.detail
    finally:
        delete_profile("__test_badcol__")


def test_empty_sheet():
    profile = load_profile("droga_bem")
    tmp = tempfile.mkdtemp(prefix="edge_empty_")
    # Só cabeçalho 'lixo' (n_cols suficiente para validate_columns), sem dados.
    path_a = make_xlsx(os.path.join(tmp, "razao.xlsx"), 10, [], 10)
    path_b = make_xlsx(os.path.join(tmp, "extrato.xlsx"), 11, [], 4)
    out_desk, result = run_desktop_path(profile, path_a, path_b, os.path.join(tmp, "desk.xlsx"))
    out_web, resp = run_web_path("droga_bem", path_a, path_b, os.path.join(tmp, "web.xlsx"))
    assert counts_of(result) == {"conciliados": 0, "nao_conciliados_a": 0, "nao_conciliados_b": 0}, \
        counts_of(result)
    assert resp.counts == counts_of(result)
    compare_workbooks(out_desk, out_web)


def test_one_to_one_mrs():
    profile = load_profile("mrs")
    assert profile, "perfil 'mrs' não encontrado"
    tmp = tempfile.mkdtemp(prefix="edge_oto_")
    # Cheques (start_row 2): nota@1, cnpj@2, fornecedor@3, numero_cheque@4, valor@5
    cheques = [
        _row(5, {1: "NF1", 2: "111", 3: "Forn A", 4: "1.001", 5: 100}),
        _row(5, {1: "NF2", 2: "222", 3: "Forn B", 4: "1.001", 5: 100}),  # chave repetida
        _row(5, {1: "NF3", 2: "333", 3: "Forn C", 4: "2.002", 5: 200}),
    ]
    # Extrato (start_row 3): data@1, numero_cheque@2, historico@3, valor@4
    extrato = [
        _row(4, {1: "01/01/2024", 2: "1001", 3: "h1", 4: "100,00 C"}),
        _row(4, {1: "02/01/2024", 2: "2002", 3: "h2", 4: "200,00 D"}),
        _row(4, {1: "03/01/2024", 2: "3003", 3: "h3", 4: "300,00 C"}),  # só em B
    ]
    path_a = make_xlsx(os.path.join(tmp, "cheques.xlsx"), 2, cheques, 5)
    path_b = make_xlsx(os.path.join(tmp, "extrato.xlsx"), 3, extrato, 4)
    out_desk, result = run_desktop_path(profile, path_a, path_b, os.path.join(tmp, "desk.xlsx"))
    out_web, resp = run_web_path("mrs", path_a, path_b, os.path.join(tmp, "web.xlsx"))
    # 1001: A=2,B=1 → 1 conc + 1 sobra A; 2002: 1 conc; 3003: 1 sobra B.
    assert counts_of(result) == {"conciliados": 2, "nao_conciliados_a": 1, "nao_conciliados_b": 1}, \
        counts_of(result)
    assert resp.counts == counts_of(result)
    compare_workbooks(out_desk, out_web)


def test_invalid_date_skipped():
    profile = load_profile("droga_bem")
    tmp = tempfile.mkdtemp(prefix="edge_date_")
    razao = [
        _row(10, {1: "04/01/2024", 3: "Valida", 9: 300.00}),
        _row(10, {1: "data-invalida", 3: "Lixo", 9: 400.00}),  # skip_if_invalid_date
    ]
    extrato = [_row(4, {1: "04/01/2024", 2: "Ext", 4: 300.00})]
    path_a = make_xlsx(os.path.join(tmp, "razao.xlsx"), 10, razao, 10)
    path_b = make_xlsx(os.path.join(tmp, "extrato.xlsx"), 11, extrato, 4)
    _out, result = run_desktop_path(profile, path_a, path_b, os.path.join(tmp, "desk.xlsx"))
    # A linha de data inválida é descartada (não entra em nao_conciliados_a).
    assert counts_of(result) == {"conciliados": 1, "nao_conciliados_a": 0, "nao_conciliados_b": 0}, \
        counts_of(result)


if __name__ == "__main__":
    run_suite([
        (".xls recusado (400 + mensagem)", test_xls_rejected),
        ("coluna fora do range (400 legível)", test_column_out_of_range),
        ("planilha vazia (contagens 0, sem erro)", test_empty_sheet),
        ("one_to_one cheques (min por chave + sobras)", test_one_to_one_mrs),
        ("data inválida descartada (skip_if_invalid_date)", test_invalid_date_skipped),
    ])

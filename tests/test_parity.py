# -*- coding: utf-8 -*-
"""Paridade web vs desktop (Task 09): mesmas entradas → mesmas abas de dados.

Ambos os caminhos usam o mesmo core/, então o teste prova que a 'cola' web
(router/storage/exporter) não divergiu do desktop. Roda com:

    python tests/test_parity.py      (ou: pytest tests/test_parity.py)
"""
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from _helpers import (
    compare_workbooks,
    counts_of,
    make_xlsx,
    run_desktop_path,
    run_suite,
    run_web_path,
)
from core.profile_manager import load_profile


def _row(n_cols, values_by_col):
    row = [None] * n_cols
    for col, val in values_by_col.items():
        row[col - 1] = val
    return row


def test_dual_droga_bem():
    profile = load_profile("droga_bem")
    assert profile, "perfil 'droga_bem' não encontrado em profiles/"
    tmp = tempfile.mkdtemp(prefix="parity_dual_")

    # Razão (start_row 10): data@1, historico@3, valor_debito@9, valor_credito@10
    razao = [
        _row(10, {1: "01/01/2024", 3: "Pagamento 1", 9: 100.00}),
        _row(10, {1: "02/01/2024", 3: "Recebimento 2", 10: 50.00}),  # fallback crédito ×-1
        _row(10, {1: "03/01/2024", 3: "Pagamento 3", 9: 200.00}),    # sem par
    ]
    # Extrato (start_row 11): data@1, historico@2, valor@4
    extrato = [
        _row(4, {1: "01/01/2024", 2: "Ext 1", 4: 100.00}),  # casa Razão 1
        _row(4, {1: "02/01/2024", 2: "Ext 2", 4: 50.00}),   # casa Razão 2 (abs)
        _row(4, {1: "05/01/2024", 2: "Ext 3", 4: 999.00}),  # sem par
    ]
    path_a = make_xlsx(os.path.join(tmp, "razao.xlsx"), 10, razao, 10)
    path_b = make_xlsx(os.path.join(tmp, "extrato.xlsx"), 11, extrato, 4)

    out_desk, result = run_desktop_path(profile, path_a, path_b, os.path.join(tmp, "desk.xlsx"))
    out_web, resp = run_web_path("droga_bem", path_a, path_b, os.path.join(tmp, "web.xlsx"))

    assert counts_of(result) == {"conciliados": 2, "nao_conciliados_a": 1, "nao_conciliados_b": 1}, \
        counts_of(result)
    assert resp.counts == counts_of(result), (resp.counts, counts_of(result))
    compare_workbooks(out_desk, out_web)


def test_single_clube():
    profile = load_profile("clube")
    assert profile, "perfil 'clube' não encontrado em profiles/"
    tmp = tempfile.mkdtemp(prefix="parity_single_")

    # Duplicatas (start_row 12): nota@2, cpf@11, data@23, parcela@20, juros@25, desconto@28
    dup = [
        _row(28, {2: "000123-45", 11: "12345678000199", 23: "10/01/2024",
                  20: 1500.00, 25: 0, 28: 0}),
        _row(28, {2: "000200", 11: "98765432000111", 23: "11/01/2024",
                  20: 2000.00, 25: 10.5, 28: 5.0}),
    ]
    path_a = make_xlsx(os.path.join(tmp, "dup.xlsx"), 12, dup, 28)

    out_desk, result = run_desktop_path(profile, path_a, None, os.path.join(tmp, "desk.xlsx"))
    out_web, resp = run_web_path("clube", path_a, None, os.path.join(tmp, "web.xlsx"))

    assert counts_of(result) == {"normalizados": 2}, counts_of(result)
    assert resp.counts == counts_of(result), (resp.counts, counts_of(result))
    compare_workbooks(out_desk, out_web)


if __name__ == "__main__":
    run_suite([
        ("dual / Droga Bem (data+valor, fallback déb/créd)", test_dual_droga_bem),
        ("single / Clube (Duplicatas: máscara CNPJ, fixed_value)", test_single_clube),
    ])

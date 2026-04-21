# -*- coding: utf-8 -*-
from __future__ import annotations

import math
from datetime import date
from typing import Optional

import pandas as pd

NUMERIC_TOLERANCE = 0.01


# ---------------------------------------------------------------------------
# Helpers de comparação
# ---------------------------------------------------------------------------

def _values_match(va, vb, field: str) -> bool:
    """Compara dois valores de acordo com o tipo do campo."""
    # Nulos nunca fazem match
    if va is None or vb is None:
        return False
    if _is_na(va) or _is_na(vb):
        return False

    # Datas: comparar como date
    if isinstance(va, date) or isinstance(vb, date):
        try:
            da = va if isinstance(va, date) else None
            db = vb if isinstance(vb, date) else None
            return da == db
        except Exception:
            return False

    # Inteiros (numero_cheque): comparação exata
    if _is_int_like(va) and _is_int_like(vb):
        return int(va) == int(vb)

    # Numéricos com tolerância
    try:
        fa, fb = float(va), float(vb)
        # Comparar valor absoluto (Razão tem sinal oposto ao Extrato)
        return abs(abs(fa) - abs(fb)) <= NUMERIC_TOLERANCE
    except (ValueError, TypeError):
        pass

    # Strings: comparação exata
    return str(va).strip() == str(vb).strip()


def _is_na(v) -> bool:
    """Verifica se o valor é NA/None."""
    if v is None:
        return True
    try:
        if pd.isna(v):
            return True
    except (TypeError, ValueError):
        pass
    return False


def _is_int_like(v) -> bool:
    """Verifica se o valor é inteiro ou Int64 pandas."""
    if isinstance(v, int):
        return True
    try:
        import pandas as pd
        if isinstance(v, pd.NA.__class__):
            return False
    except Exception:
        pass
    # Verificar pelo dtype se vier de um pd.Series
    return False


# ---------------------------------------------------------------------------
# Mapeamento de colunas de saída
# ---------------------------------------------------------------------------

def _apply_output_transform(value, transform: Optional[str]):
    """Aplica transformação de saída em um valor (ex: strip_after_slash)."""
    if transform is None or value is None:
        return value
    if transform == 'strip_after_slash':
        return str(value).split('/')[0].strip()
    if transform == 'strip_after_dash':
        return str(value).split('-')[0].strip()
    return value


def _build_output_df(source_df: pd.DataFrame, tab_config: dict) -> pd.DataFrame:
    """
    Constrói DataFrame de saída a partir de source_df conforme mapeamento de colunas do perfil.
    """
    if source_df is None or source_df.empty:
        headers = [c['header'] for c in tab_config.get('columns', [])]
        return pd.DataFrame(columns=headers)

    out_rows = []
    for _, row in source_df.iterrows():
        out_row = {}
        for col_def in tab_config.get('columns', []):
            header = col_def['header']
            field = col_def.get('field')
            fixed = col_def.get('fixed_value')
            transform = col_def.get('transform_output')

            if fixed is not None:
                # Valor fixo — converter para número se possível
                try:
                    out_row[header] = float(fixed) if fixed != '' else ''
                except (ValueError, TypeError):
                    out_row[header] = fixed
            elif field and field in row.index:
                val = row[field]
                val = _apply_output_transform(val, transform)
                out_row[header] = val
            else:
                out_row[header] = None

        out_rows.append(out_row)

    return pd.DataFrame(out_rows)


# ---------------------------------------------------------------------------
# Algoritmo base (one_to_one=false) — Modelos 1 e 3
# ---------------------------------------------------------------------------

def _match_base(df_a: pd.DataFrame, df_b: pd.DataFrame, match_fields: list) -> dict:
    """
    Algoritmo de conciliação padrão: cada registro de B pode ser usado uma vez.
    Retorna dict com índices usados de A e B.
    """
    usados_b = set()
    pares = []  # lista de (idx_a, idx_b)

    b_indices = list(df_b.index)

    for idx_a, row_a in df_a.iterrows():
        for idx_b in b_indices:
            if idx_b in usados_b:
                continue
            row_b = df_b.loc[idx_b]
            if all(_values_match(row_a[f], row_b[f], f) for f in match_fields
                   if f in row_a.index and f in row_b.index):
                pares.append((idx_a, idx_b))
                usados_b.add(idx_b)
                break

    usados_a = {p[0] for p in pares}

    nao_a = df_a[~df_a.index.isin(usados_a)].copy()
    nao_b = df_b[~df_b.index.isin(usados_b)].copy()

    # Construir DataFrame de conciliados com colunas de ambos os lados
    conc_rows = []
    for idx_a, idx_b in pares:
        ra = df_a.loc[idx_a].to_dict()
        rb = df_b.loc[idx_b].to_dict()
        merged = {}
        # Renomear __linha__ de cada lado
        for k, v in ra.items():
            if k == '__linha__':
                merged['__linha___a'] = v
            else:
                merged[k] = v
        for k, v in rb.items():
            if k == '__linha__':
                merged['__linha___b'] = v
            elif k not in merged:
                # Campos exclusivos de B (ex: historico do extrato)
                merged[k] = v
            # Campos duplicados: manter o de A (já está em merged)
        conc_rows.append(merged)

    conciliados = pd.DataFrame(conc_rows) if conc_rows else pd.DataFrame()
    return {
        'conciliados': conciliados,
        'nao_conciliados_a': nao_a,
        'nao_conciliados_b': nao_b,
    }


# ---------------------------------------------------------------------------
# Algoritmo one-to-one (one_to_one=true) — Modelo 2
# ---------------------------------------------------------------------------

def _match_one_to_one(df_a: pd.DataFrame, df_b: pd.DataFrame, match_fields: list) -> dict:
    """
    Algoritmo one-to-one: para cada chave, min(count_a, count_b) são conciliados.
    Sobras de cada lado vão para não conciliados.
    """
    # Usar o primeiro match_field como chave (numero_cheque)
    key_field = match_fields[0]

    # Agrupar por chave, preservando ordem de aparecimento
    groups_a: dict = {}
    for idx, row in df_a.iterrows():
        k = row.get(key_field)
        if _is_na(k):
            continue
        k = int(k) if not _is_na(k) else k
        groups_a.setdefault(k, []).append((idx, row))

    groups_b: dict = {}
    for idx, row in df_b.iterrows():
        k = row.get(key_field)
        if _is_na(k):
            continue
        try:
            k = int(k)
        except (ValueError, TypeError):
            continue
        groups_b.setdefault(k, []).append((idx, row))

    conc_rows = []
    nao_a_indices = []
    nao_b_indices = []

    all_keys = set(groups_a.keys()) | set(groups_b.keys())

    for key in all_keys:
        lista_a = groups_a.get(key, [])
        lista_b = groups_b.get(key, [])
        n_match = min(len(lista_a), len(lista_b))

        # Conciliados: pegar os primeiros n_match de cada lado
        for i in range(n_match):
            idx_a, row_a = lista_a[i]
            idx_b, row_b = lista_b[i]
            merged = {}
            for k, v in row_a.items():
                merged['__linha___a' if k == '__linha__' else k] = v
            for k, v in row_b.items():
                if k == '__linha__':
                    merged['__linha___b'] = v
                elif k not in merged:
                    merged[k] = v
            conc_rows.append(merged)

        # Sobras de A
        for i in range(n_match, len(lista_a)):
            nao_a_indices.append(lista_a[i][0])

        # Sobras de B
        for i in range(n_match, len(lista_b)):
            nao_b_indices.append(lista_b[i][0])

    # Cheques em B sem correspondência em A (chave só existe em B)
    conciliados = pd.DataFrame(conc_rows) if conc_rows else pd.DataFrame()
    nao_a = df_a.loc[nao_a_indices].copy() if nao_a_indices else pd.DataFrame(columns=df_a.columns)
    nao_b = df_b.loc[nao_b_indices].copy() if nao_b_indices else pd.DataFrame(columns=df_b.columns)

    return {
        'conciliados': conciliados,
        'nao_conciliados_a': nao_a,
        'nao_conciliados_b': nao_b,
    }


# ---------------------------------------------------------------------------
# Função principal
# ---------------------------------------------------------------------------

def run(profile: dict, df_a: pd.DataFrame, df_b: Optional[pd.DataFrame] = None) -> dict:
    """
    Executa a conciliação conforme o perfil.

    Retorna dict com chaves:
      - conciliados       (DataFrame ou None)
      - nao_conciliados_a (DataFrame ou None)
      - nao_conciliados_b (DataFrame ou None)
      - normalizados      (DataFrame ou None)
    """
    mode = profile.get('mode', 'dual')
    output_tabs = profile.get('output', {}).get('tabs', [])

    result = {
        'conciliados': None,
        'nao_conciliados_a': None,
        'nao_conciliados_b': None,
        'normalizados': None,
    }

    # ── Modo single ──────────────────────────────────────────────────────────
    if mode == 'single':
        tab = next((t for t in output_tabs if t['source'] == 'normalizados'), None)
        if tab:
            result['normalizados'] = _build_output_df(df_a, tab)
        else:
            result['normalizados'] = df_a.copy()
        return result

    # ── Modo dual ────────────────────────────────────────────────────────────
    comparison = profile.get('comparison', {})
    match_fields = comparison.get('match_fields', [])
    one_to_one = comparison.get('one_to_one', False)

    if df_b is None:
        raise ValueError("Modo dual requer df_b.")

    if one_to_one:
        matched = _match_one_to_one(df_a, df_b, match_fields)
    else:
        matched = _match_base(df_a, df_b, match_fields)

    # Aplicar mapeamento de saída para cada aba
    tab_map = {t['source']: t for t in output_tabs}

    # Conciliados
    tab_conc = tab_map.get('conciliados')
    if tab_conc and not matched['conciliados'].empty:
        result['conciliados'] = _build_output_df(matched['conciliados'], tab_conc)
    else:
        headers = [c['header'] for c in (tab_conc or {}).get('columns', [])]
        result['conciliados'] = pd.DataFrame(columns=headers)

    # Não conciliados A
    tab_nca = tab_map.get('nao_conciliados_a')
    if tab_nca:
        result['nao_conciliados_a'] = _build_output_df(matched['nao_conciliados_a'], tab_nca)
    else:
        result['nao_conciliados_a'] = matched['nao_conciliados_a']

    # Não conciliados B
    tab_ncb = tab_map.get('nao_conciliados_b')
    if tab_ncb:
        result['nao_conciliados_b'] = _build_output_df(matched['nao_conciliados_b'], tab_ncb)
    else:
        result['nao_conciliados_b'] = matched['nao_conciliados_b']

    return result

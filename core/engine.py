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

# ---------------------------------------------------------------------------
# Algoritmo base (one_to_one=false) — Modelos 1 e 3
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Algoritmo base (one_to_one=false) — Modelos 1 e 3
# ---------------------------------------------------------------------------

def _prep_date_key(v):
    """Normaliza data para objeto date usado como chave de agrupamento."""
    if v is None:
        return None
    try:
        if pd.isna(v):
            return None
    except (TypeError, ValueError):
        pass
    if isinstance(v, date):
        return v
    return None


def _match_base(df_a: pd.DataFrame, df_b: pd.DataFrame, match_fields: list) -> dict:
    """
    Algoritmo de conciliação otimizado via agrupamento por data + greedy por valor.

    Estratégia:
      - Se match_fields inclui 'data': agrupa por data (O(n)), depois para cada grupo
        faz sub-matching greedy por valor com tolerância 0.01 (ordenação + two-pointer).
      - Se match_fields é só valor (sem data): fallback para merge por valor arredondado.
      - Resultado: O(n log n) na prática, sem falsos positivos, suporta 3000+ linhas.
    """
    if df_a.empty or df_b.empty:
        return {
            'conciliados':       pd.DataFrame(),
            'nao_conciliados_a': df_a.copy(),
            'nao_conciliados_b': df_b.copy(),
        }

    has_date  = 'data'  in match_fields
    has_value = 'valor' in match_fields

    a = df_a.reset_index(drop=True).copy()
    b = df_b.reset_index(drop=True).copy()

    if has_date:
        return _match_by_date_then_value(a, b, match_fields)
    else:
        return _match_by_value_only(a, b, match_fields)


def _match_by_date_then_value(a: pd.DataFrame, b: pd.DataFrame, match_fields: list) -> dict:
    """
    Agrupa por data, depois faz sub-matching greedy por valor com tolerância 0.01.
    """
    has_value = 'valor' in match_fields

    # Separar linhas com data válida
    a['_dkey'] = a['data'].apply(_prep_date_key)
    b['_dkey'] = b['data'].apply(_prep_date_key)
    a_valid   = a[a['_dkey'].notna()].copy()
    b_valid   = b[b['_dkey'].notna()].copy()
    a_invalid = a[a['_dkey'].isna()].copy()
    b_invalid = b[b['_dkey'].isna()].copy()

    # Agrupar índices por data
    grp_a = {}
    for idx, row in a_valid.iterrows():
        grp_a.setdefault(row['_dkey'], []).append(idx)
    grp_b = {}
    for idx, row in b_valid.iterrows():
        grp_b.setdefault(row['_dkey'], []).append(idx)

    used_a = set()
    used_b = set()
    pares  = []

    for d in set(grp_a.keys()) & set(grp_b.keys()):
        idxs_a = [i for i in grp_a[d] if i not in used_a]
        idxs_b = [i for i in grp_b[d] if i not in used_b]
        if not idxs_a or not idxs_b:
            continue

        if has_value:
            # Ordenar por valor absoluto → two-pointer greedy
            def abs_val(df, i):
                v = df.at[i, 'valor']
                try:
                    return abs(float(v)) if v is not None else float('inf')
                except (TypeError, ValueError):
                    return float('inf')

            idxs_a_s = sorted(idxs_a, key=lambda i: abs_val(a, i))
            idxs_b_s = sorted(idxs_b, key=lambda i: abs_val(b, i))

            local_used_b = set()
            for idx_a in idxs_a_s:
                va = a.at[idx_a, 'valor']
                if va is None:
                    continue
                try:
                    va_abs = abs(float(va))
                except (TypeError, ValueError):
                    continue
                for idx_b in idxs_b_s:
                    if idx_b in local_used_b:
                        continue
                    vb = b.at[idx_b, 'valor']
                    if vb is None:
                        continue
                    try:
                        vb_abs = abs(float(vb))
                    except (TypeError, ValueError):
                        continue
                    if abs(va_abs - vb_abs) <= NUMERIC_TOLERANCE:
                        pares.append((idx_a, idx_b))
                        used_a.add(idx_a)
                        used_b.add(idx_b)
                        local_used_b.add(idx_b)
                        break
        else:
            # Sem campo valor: casar na ordem (cumcount implícito)
            for idx_a, idx_b in zip(idxs_a, idxs_b):
                pares.append((idx_a, idx_b))
                used_a.add(idx_a)
                used_b.add(idx_b)

    return _build_match_result(a, b, pares, used_a, used_b, a_invalid, b_invalid)


def _match_by_value_only(a: pd.DataFrame, b: pd.DataFrame, match_fields: list) -> dict:
    """Fallback para match_fields que não incluem 'data' (ex: só numero_cheque)."""
    used_a = set()
    used_b = set()
    pares  = []
    b_indices = list(b.index)

    for idx_a, row_a in a.iterrows():
        for idx_b in b_indices:
            if idx_b in used_b:
                continue
            row_b = b.loc[idx_b]
            if all(_values_match(row_a.get(f), row_b.get(f), f) for f in match_fields):
                pares.append((idx_a, idx_b))
                used_a.add(idx_a)
                used_b.add(idx_b)
                break

    empty_a = pd.DataFrame(columns=a.columns)
    empty_b = pd.DataFrame(columns=b.columns)
    return _build_match_result(a, b, pares, used_a, used_b, empty_a, empty_b)


def _build_match_result(a, b, pares, used_a, used_b, a_extra, b_extra) -> dict:
    """Constrói o dict de resultado a partir dos pares encontrados."""
    conc_rows = []
    for idx_a, idx_b in pares:
        ra = a.loc[idx_a].to_dict()
        rb = b.loc[idx_b].to_dict()
        rec = {}
        _internal = lambda c: c.startswith('_') and not c.startswith('__')
        for k, v in ra.items():
            if _internal(k):
                continue
            rec['__linha___a' if k == '__linha__' else k] = v
        for k, v in rb.items():
            if _internal(k):
                continue
            if k == '__linha__':
                rec['__linha___b'] = v
            elif k not in rec:
                rec[k] = v
        conc_rows.append(rec)

    conciliados = pd.DataFrame(conc_rows) if conc_rows else pd.DataFrame()

    all_a_idx = list(a.index) + list(a_extra.index)
    all_b_idx = list(b.index) + list(b_extra.index)
    nao_a_idx = sorted(i for i in set(all_a_idx) if i not in used_a)
    nao_b_idx = sorted(i for i in set(all_b_idx) if i not in used_b)

    # Reconstruir df originals sem colunas de trabalho internas (prefixo '_' simples)
    # mas preservando '__linha__' que começa com '__' e é necessário para a saída
    _internal = lambda c: c.startswith('_') and not c.startswith('__')
    orig_a = a.drop(columns=[c for c in a.columns if _internal(c)], errors='ignore')
    orig_b = b.drop(columns=[c for c in b.columns if _internal(c)], errors='ignore')

    nao_a = orig_a.loc[[i for i in nao_a_idx if i in orig_a.index]].copy()
    nao_b = orig_b.loc[[i for i in nao_b_idx if i in orig_b.index]].copy()

    return {
        'conciliados':       conciliados,
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

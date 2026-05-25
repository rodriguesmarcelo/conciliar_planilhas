# -*- coding: utf-8 -*-
"""Modelos Pydantic do módulo Conciliador (contratos da API)."""
from typing import Optional

from pydantic import BaseModel, ConfigDict


class ColumnInput(BaseModel):
    # extra="allow" preserva campos como blank_limit (Modelo 4) e futuros.
    model_config = ConfigDict(extra="allow")

    field: str
    col_index: int
    transformations: list[str] = []
    multiply_minus_one: bool = False
    is_fallback_of: Optional[str] = None
    skip_if_empty: bool = False
    skip_if_invalid_date: bool = False


class SheetInput(BaseModel):
    label: str = ""
    start_row: int = 1
    columns: list[ColumnInput] = []


class ComparisonInput(BaseModel):
    match_fields: list[str] = []
    one_to_one: bool = False


class ProfileInput(BaseModel):
    id: Optional[str] = None
    name: str
    mode: str = "dual"
    date_format: str = "dd/mm/yyyy"
    sheets: list[SheetInput] = []
    comparison: Optional[ComparisonInput] = None


class PreviewResponse(BaseModel):
    header: list[str]
    rows: list[list[str]]


class RunResponse(BaseModel):
    mode: str
    counts: dict
    download_token: str
    suggested_filename: str

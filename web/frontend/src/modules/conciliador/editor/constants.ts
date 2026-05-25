import type { ProfileColumn, ProfileSheet } from "@/modules/conciliador/api"

// Campos reconhecidos (espelha FIELD_OPTIONS de ui/screen_profile.py, sem o sentinel).
export const FIELD_OPTIONS = [
  "data",
  "valor",
  "valor_debito",
  "valor_credito",
  "historico",
  "numero_cheque",
  "numero_nota",
  "cnpj",
  "fornecedor",
  "cpf_cnpj",
  "valor_parcela",
  "valor_juros",
  "valor_desconto",
  "documento",
] as const

export const CUSTOM_FIELD = "(personalizado...)"

// As 12 transformações de core/reader.TRANSFORMATIONS, na ordem do desktop.
export const ALL_TRANSFORMS: ReadonlyArray<readonly [string, string]> = [
  ["remove_newlines", "Remover quebras de linha"],
  ["remove_semicolons", "Remover ponto-e-vírgula (;)"],
  ["remove_dots", "Remover pontos (.)"],
  ["remove_commas", "Converter vírgula em ponto"],
  ["remove_special_chars", "Manter apenas dígitos"],
  ["to_int", "Converter para inteiro"],
  ["remove_cd_suffix", "Remover sufixo C/D (extrato)"],
  ["absolute_value", "Valor absoluto"],
  ["strip_after_dash", "Cortar após hífen (-)"],
  ["strip_after_slash", "Cortar após barra (/)"],
  ["lstrip_zeros", "Remover zeros à esquerda"],
  ["apply_cnpj_mask", "Aplicar máscara CNPJ"],
]

export const DATE_FORMATS = ["dd/mm/yyyy", "mm/dd/yyyy", "yyyy-mm-dd"]

export const MATCH_FIELDS = ["data", "valor", "numero_cheque", "numero_nota", "documento"]

// Caracteres proibidos em nomes de arquivo no Windows (espelha profile_builder.py).
export const INVALID_FILENAME_CHARS = '/\\|:*?"<>'

export const XLS_MESSAGE =
  "O arquivo selecionado está no formato antigo '.xls'. " +
  "Abra no Excel, use Arquivo → Salvar Como e escolha 'Pasta de Trabalho do Excel (*.xlsx)'. " +
  "O sistema aceita apenas arquivos .xlsx ou .csv."

// Grid compartilhado entre o cabeçalho e cada ColumnRow (8 colunas).
export const COL_GRID =
  "grid grid-cols-[minmax(140px,2fr)_72px_minmax(130px,1.5fr)_56px_56px_56px_72px_40px] items-center gap-2"

// Tipos internos do editor: acrescentam um _uid estável para a renderização de listas.
export type EditorColumn = ProfileColumn & { _uid: string }
export type EditorSheet = {
  _uid: string
  label: string
  start_row: number
  columns: EditorColumn[]
}

let _counter = 0
export function uid(): string {
  _counter += 1
  return `u${Date.now().toString(36)}_${_counter}`
}

export function newColumn(): EditorColumn {
  return {
    _uid: uid(),
    field: "data",
    col_index: 1,
    transformations: [],
    multiply_minus_one: false,
    is_fallback_of: null,
    skip_if_empty: false,
    skip_if_invalid_date: false,
  }
}

export function newSheet(label: string): EditorSheet {
  return { _uid: uid(), label, start_row: 1, columns: [] }
}

export function toEditorSheet(s: ProfileSheet): EditorSheet {
  return {
    _uid: uid(),
    label: s.label ?? "",
    start_row: s.start_row ?? 1,
    columns: (s.columns ?? []).map((c) => ({ ...c, _uid: uid() })),
  }
}

// Remove os campos internos (_uid) antes de enviar ao backend.
export function stripSheet(s: EditorSheet): ProfileSheet {
  return {
    label: s.label.trim(),
    start_row: s.start_row,
    columns: s.columns.map((c): ProfileColumn => ({
      field: c.field,
      col_index: c.col_index,
      transformations: c.transformations,
      multiply_minus_one: c.multiply_minus_one,
      is_fallback_of: c.is_fallback_of,
      skip_if_empty: c.skip_if_empty,
      skip_if_invalid_date: c.skip_if_invalid_date,
      ...(c.blank_limit !== undefined ? { blank_limit: c.blank_limit } : {}),
    })),
  }
}

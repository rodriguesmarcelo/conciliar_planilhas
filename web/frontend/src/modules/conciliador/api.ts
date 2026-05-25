import { apiGet, apiSend, apiUpload } from "@/lib/api"

export type ProfileColumn = {
  field: string
  col_index: number
  transformations: string[]
  multiply_minus_one: boolean
  is_fallback_of: string | null
  skip_if_empty: boolean
  skip_if_invalid_date: boolean
  blank_limit?: number
}

export type ProfileSheet = {
  label: string
  start_row: number
  columns: ProfileColumn[]
}

export type Comparison = {
  enabled?: boolean
  match_fields: string[]
  one_to_one: boolean
}

export type Profile = {
  id: string
  name: string
  mode: "dual" | "single"
  date_format: string
  sheets: ProfileSheet[]
  comparison?: Comparison
  output?: unknown
}

// Payload mínimo enviado ao backend. O backend gera output/id e valida;
// `id` é incluído ao editar para que o output existente seja preservado.
export type ProfilePayload = {
  id?: string
  name: string
  mode: "dual" | "single"
  date_format: string
  sheets: ProfileSheet[]
  comparison: { match_fields: string[]; one_to_one: boolean }
}

export type PreviewResult = {
  header: string[]
  rows: string[][]
}

export function listProfiles() {
  return apiGet<Profile[]>("/conciliador/profiles")
}

export function getProfile(id: string) {
  return apiGet<Profile>(`/conciliador/profiles/${id}`)
}

export function saveProfile(payload: ProfilePayload) {
  return apiSend<Profile>("/conciliador/profiles", "POST", payload)
}

export function duplicateProfile(id: string) {
  return apiSend<Profile>(`/conciliador/profiles/${id}/duplicate`, "POST")
}

export function deleteProfile(id: string) {
  return apiSend<{ deleted: boolean }>(`/conciliador/profiles/${id}`, "DELETE")
}

export function preview(file: File) {
  const form = new FormData()
  form.append("file", file)
  return apiUpload<PreviewResult>("/conciliador/preview", form)
}

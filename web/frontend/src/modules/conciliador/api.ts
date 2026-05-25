import { apiGet, apiSend } from "@/lib/api"

export type ProfileSheet = {
  label?: string
  start_row?: number
  columns?: unknown[]
}

export type Profile = {
  id: string
  name: string
  mode: "dual" | "single"
  date_format?: string
  sheets?: ProfileSheet[]
  comparison?: unknown
  output?: unknown
}

export function listProfiles() {
  return apiGet<Profile[]>("/conciliador/profiles")
}

export function duplicateProfile(id: string) {
  return apiSend<Profile>(`/conciliador/profiles/${id}/duplicate`, "POST")
}

export function deleteProfile(id: string) {
  return apiSend<{ deleted: boolean }>(`/conciliador/profiles/${id}`, "DELETE")
}

export type ModuleManifest = {
  id: string
  title: string
  description: string
  icon: string
}

const BASE = "/api"

async function handle<T>(res: Response): Promise<T> {
  if (!res.ok) {
    let detail: string = res.statusText
    try {
      const data = await res.json()
      if (data && typeof data.detail === "string") detail = data.detail
    } catch {
      /* corpo não-JSON */
    }
    throw new Error(detail || "Erro na requisição")
  }
  return res.json() as Promise<T>
}

export async function apiGet<T>(path: string): Promise<T> {
  return handle<T>(await fetch(`${BASE}${path}`))
}

export async function apiSend<T>(path: string, method: string, body?: unknown): Promise<T> {
  return handle<T>(
    await fetch(`${BASE}${path}`, {
      method,
      headers: { "Content-Type": "application/json" },
      body: body !== undefined ? JSON.stringify(body) : undefined,
    }),
  )
}

// Multipart upload. Não definir Content-Type manualmente: o browser inclui o boundary.
export async function apiUpload<T>(path: string, form: FormData, method = "POST"): Promise<T> {
  return handle<T>(await fetch(`${BASE}${path}`, { method, body: form }))
}

export async function getModules(): Promise<ModuleManifest[]> {
  return apiGet<ModuleManifest[]>("/modules")
}

import type { ComponentType } from "react"
import ConciliadorModule from "@/modules/conciliador"

export type FrontendModule = {
  id: string
  title: string
  icon: string
  basePath: string
  element: ComponentType
}

// Registro de módulos do frontend (rotas + navegação).
// Adicionar um módulo = nova entrada aqui + registro no backend (web/modules/registry.py).
export const MODULES: FrontendModule[] = [
  {
    id: "conciliador",
    title: "Conciliador de Planilhas",
    icon: "file-spreadsheet",
    basePath: "/conciliador",
    element: ConciliadorModule,
  },
]

export function moduleById(id: string): FrontendModule | undefined {
  return MODULES.find((m) => m.id === id)
}

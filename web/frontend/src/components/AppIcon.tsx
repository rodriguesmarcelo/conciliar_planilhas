import { FileSpreadsheet, LayoutGrid, type LucideIcon } from "lucide-react"

// Mapa nome (manifesto) -> ícone lucide. Ao adicionar um módulo novo com um
// ícone diferente, registre-o aqui.
const ICONS: Record<string, LucideIcon> = {
  "file-spreadsheet": FileSpreadsheet,
  "layout-grid": LayoutGrid,
}

export function AppIcon({ name, className }: { name: string; className?: string }) {
  const Icon = ICONS[name] ?? LayoutGrid
  return <Icon className={className} />
}

import { useQuery } from "@tanstack/react-query"
import { Link } from "react-router-dom"
import { getModules } from "@/lib/api"
import { moduleById } from "@/modules/registry"
import { AppIcon } from "@/components/AppIcon"
import { Card, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"

export default function Hub() {
  const { data, isLoading, isError, error } = useQuery({
    queryKey: ["modules"],
    queryFn: getModules,
  })

  if (isLoading) return <p className="text-muted-foreground">Carregando módulos…</p>
  if (isError)
    return <p className="text-destructive">Erro ao carregar módulos: {(error as Error).message}</p>

  const mods = data ?? []
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold">Automações</h1>
        <p className="text-muted-foreground">Selecione um módulo para começar.</p>
      </div>
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {mods.map((m) => {
          const to = moduleById(m.id)?.basePath ?? "/"
          return (
            <Link key={m.id} to={to}>
              <Card className="h-full transition-colors hover:border-primary hover:bg-accent/40">
                <CardHeader>
                  <div className="mb-2 flex size-10 items-center justify-center rounded-md bg-primary/10 text-primary">
                    <AppIcon name={m.icon} className="size-5" />
                  </div>
                  <CardTitle>{m.title}</CardTitle>
                  <CardDescription>{m.description}</CardDescription>
                </CardHeader>
              </Card>
            </Link>
          )
        })}
      </div>
    </div>
  )
}

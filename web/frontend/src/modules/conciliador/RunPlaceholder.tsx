import { useParams } from "react-router-dom"

export default function RunPlaceholder() {
  const { id } = useParams()
  return (
    <div className="space-y-2">
      <h1 className="text-2xl font-semibold">Executar conciliação</h1>
      <p className="text-muted-foreground">
        Tela de execução em construção (Task 06) — perfil: {id}.
      </p>
    </div>
  )
}

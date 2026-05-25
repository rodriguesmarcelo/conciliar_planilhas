import type { ReactNode } from "react"
import { Navigate } from "react-router-dom"
import { useAuth } from "@/auth/AuthProvider"

// Pass-through enquanto a autenticação está desativada.
export function RequireAuth({ children }: { children: ReactNode }) {
  const { isAuthenticated } = useAuth()
  if (!isAuthenticated) return <Navigate to="/login" replace />
  return <>{children}</>
}

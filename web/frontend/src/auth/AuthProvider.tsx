import { createContext, useContext, type ReactNode } from "react"

type User = { id: string; name: string }
type AuthState = { user: User | null; isAuthenticated: boolean }

const ANONYMOUS: User = { id: "anon", name: "Anônimo" }

// Auth desativada nesta fase: usuário anônimo, sempre autenticado.
// A estrutura existe para ligar login no futuro (ver web/auth.py no backend).
const AuthContext = createContext<AuthState>({
  user: ANONYMOUS,
  isAuthenticated: true,
})

export function AuthProvider({ children }: { children: ReactNode }) {
  const value: AuthState = { user: ANONYMOUS, isAuthenticated: true }
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  return useContext(AuthContext)
}

import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import { BrowserRouter, Route, Routes } from "react-router-dom"
import { AuthProvider } from "@/auth/AuthProvider"
import { RequireAuth } from "@/auth/RequireAuth"
import { AppShell } from "@/layout/AppShell"
import { Toaster } from "@/components/ui/sonner"
import { MODULES } from "@/modules/registry"
import Hub from "@/pages/Hub"
import Login from "@/pages/Login"

const queryClient = new QueryClient()

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <BrowserRouter>
          <Routes>
            <Route path="/login" element={<Login />} />
            <Route
              element={
                <RequireAuth>
                  <AppShell />
                </RequireAuth>
              }
            >
              <Route path="/" element={<Hub />} />
              {MODULES.map((m) => {
                const El = m.element
                return <Route key={m.id} path={`${m.basePath}/*`} element={<El />} />
              })}
            </Route>
          </Routes>
        </BrowserRouter>
      </AuthProvider>
      <Toaster />
    </QueryClientProvider>
  )
}

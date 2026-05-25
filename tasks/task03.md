# Task 03 — Scaffolding do frontend (React + Vite + Tailwind + shadcn/ui) + AppShell + Hub

## Objetivo
Criar o projeto frontend moderno da plataforma com React, Vite, TypeScript, Tailwind e shadcn/ui; montar o layout (AppShell com logo/navegação), o roteamento, o stub de autenticação (pass-through) e o **Hub** que lista os módulos a partir de `GET /api/modules`. Ao final, abrir o app no navegador mostra o Hub com o card do Conciliador.

## Pré-requisitos
- Task 01 (`/api/modules`) e Task 02 (módulo registrado).

## Escopo / Passos

### Início — projeto e dependências
1. Criar projeto em `web/frontend/` com Vite (`react-ts`).
2. Instalar e configurar **Tailwind** e inicializar **shadcn/ui** (`components/ui/`).
3. Adicionar `react-router-dom`; opcionalmente TanStack Query para dados assíncronos.
4. Configurar proxy do Vite: `/api` → `http://localhost:8000` (dev).

### Meio — estrutura base
5. `src/lib/api.ts`: cliente HTTP central (base `/api`, tratamento de erro → toast).
6. `src/auth/`: `AuthProvider` (contexto) + `RequireAuth` (hoje sempre libera) + rota `/login` stub. Estrutura pronta para ativar depois.
7. `src/layout/AppShell.tsx`: cabeçalho/sidebar com espaço para o **logo da Barelli** e navegação; área de conteúdo via `<Outlet/>`.
8. `src/modules/registry.ts`: array de módulos do frontend `{id, title, icon, basePath, element}`. Inicialmente só o Conciliador (telas reais vêm nas Tasks 04–06; aqui podem ser placeholders).
9. `src/pages/Hub.tsx`: busca `GET /api/modules` e renderiza um **grid de cards** (shadcn `Card`), cada card linkando para o `basePath` do módulo.
10. `src/App.tsx` + `src/main.tsx`: providers (auth, query, toaster) + rotas (`/` → Hub; rotas dos módulos a partir do registry).

### Fim — validação
11. `npm run dev`, abrir `http://localhost:5173`, ver o Hub com o card "Conciliador de Planilhas" navegável (mesmo que a tela interna ainda seja placeholder).

## Arquivos
- `web/frontend/` (projeto Vite novo): `package.json`, `vite.config.ts`, `tailwind.config.js`, `index.html`
- `src/{main.tsx, App.tsx}`, `src/lib/api.ts`
- `src/layout/AppShell.tsx`, `src/auth/*`, `src/components/ui/*` (shadcn)
- `src/modules/registry.ts`, `src/pages/Hub.tsx`

## Critérios de aceite
- [ ] `npm install && npm run dev` sobe o frontend sem erros.
- [ ] Hub lista módulos a partir de `/api/modules` (proxy funcionando).
- [ ] Navegação para o módulo Conciliador funciona (placeholder aceitável aqui).
- [ ] AppShell renderiza com área reservada para o logo e navegação.
- [ ] Auth stub não bloqueia nenhuma rota.

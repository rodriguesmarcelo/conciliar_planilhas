# Task 01 — Scaffolding do backend FastAPI (plataforma + registro de módulos + auth stub)

## Objetivo
Criar a base do servidor web da plataforma `barelli.automacao`: app FastAPI, registro plugável de módulos, stub de autenticação desativado e o endpoint que alimenta o Hub. Ao final, o servidor sobe e `GET /api/modules` responde com a lista de módulos (ainda sem o Conciliador real).

## Pré-requisitos
Nenhum (primeira tarefa).

## Escopo / Passos

### Início — dependências e estrutura
1. Adicionar ao `requirements.txt`: `fastapi`, `uvicorn[standard]`, `python-multipart`.
2. Criar a árvore:
   ```
   web/__init__.py
   web/server.py
   web/auth.py
   web/modules/__init__.py
   web/modules/registry.py
   run_web.py
   ```

### Meio — implementação
3. `web/auth.py`: dependency `get_current_user()` que lê uma flag `AUTH_ENABLED` (env, default `false`). Com a flag desligada, retorna um usuário anônimo fixo (`{"id": "anon", "name": "Anônimo"}`) sem bloquear. Deixar o ponto de extensão documentado para login futuro.
4. `web/modules/registry.py`: estrutura de "módulo de backend" = manifesto (`id`, `title`, `description`, `icon`) + `router` (APIRouter). Expor `ALL_MODULES: list` e uma função `get_manifests()` (só os metadados, para o Hub). Inicialmente a lista pode estar vazia ou conter um placeholder.
5. `web/server.py`:
   - Cria `app = FastAPI(title="barelli.automacao")`.
   - CORS liberado para a intranet em dev (origem do Vite `http://localhost:5173`).
   - Inclui cada `router` de `ALL_MODULES` sob `/api`.
   - `GET /api/modules` → retorna `get_manifests()`.
   - `GET /api/health` → `{"status": "ok"}`.
   - Aplica a dependency `get_current_user` globalmente (ou por router) para já existir o ponto de injeção.
6. `run_web.py`: sobe `uvicorn web.server:app --host 0.0.0.0 --port 8000` (porta configurável por env `PORT`).

### Fim — validação
7. Rodar `python run_web.py` e confirmar que `GET /api/health` e `GET /api/modules` respondem 200.

## Arquivos
- `requirements.txt` (editar)
- `web/__init__.py`, `web/server.py`, `web/auth.py` (novos)
- `web/modules/__init__.py`, `web/modules/registry.py` (novos)
- `run_web.py` (novo)

## Critérios de aceite
- [ ] `python run_web.py` inicia o servidor sem erros em `0.0.0.0:8000`.
- [ ] `GET /api/health` retorna `{"status":"ok"}`.
- [ ] `GET /api/modules` retorna uma lista JSON (vazia ou com placeholder).
- [ ] Auth desativada por padrão; nenhuma rota exige login.
- [ ] `core/`, `ui/`, `main.py` permanecem intactos.

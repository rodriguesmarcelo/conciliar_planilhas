# Task 02 — Backend do módulo Conciliador (endpoints reusando o `core/`)

## Objetivo
Implementar todos os endpoints do Conciliador como um módulo plugável do backend, **reaproveitando o `core/` sem reescrever lógica**. Ao final, é possível listar/criar/editar/duplicar/excluir perfis, pré-visualizar planilha e executar a conciliação com download do `.xlsx`, tudo via API.

## Pré-requisitos
- Task 01 (servidor FastAPI + registry + auth stub).

## Escopo / Passos

### Início — estrutura do módulo
1. Criar `web/modules/conciliador/__init__.py` e `web/modules/conciliador/router.py` (um `APIRouter` com prefixo `/conciliador`).
2. Registrar o módulo em `web/modules/registry.py` com manifesto `{id:"conciliador", title:"Conciliador de Planilhas", description:"...", icon:"..."}`.
3. Criar utilitário de temporários `web/modules/conciliador/storage.py` (ou função em `router.py`): salvar uploads e resultados em `tempfile`, gerando tokens únicos; helper de limpeza por idade.

### Meio — endpoints (reusando `core/`)
4. `GET /api/conciliador/profiles` → `profile_manager.load_all_profiles()`.
5. `GET /api/conciliador/profiles/{id}` → `load_profile()` (404 se não existir).
6. `POST /api/conciliador/profiles` → valida payload e `save_profile()` (cria/atualiza). Retorna o perfil salvo com `id`.
7. `POST /api/conciliador/profiles/{id}/duplicate` → `duplicate_profile()`.
8. `DELETE /api/conciliador/profiles/{id}` → `delete_profile()`.
9. `POST /api/conciliador/preview` (multipart) → salva upload em temp; **recusa `.xls`** com mensagem de conversão (mesma do desktop); chama `reader.preview_sheet(path, 20)`; retorna JSON `{header, rows}`.
10. `POST /api/conciliador/run/{id}` (multipart, 1 ou 2 arquivos):
    - Carrega o perfil; valida presença dos arquivos conforme `mode`.
    - `reader.validate_columns()` para cada planilha; mapear `ColumnNotFoundError`/`InvalidFileError` para respostas 400 com a mensagem.
    - `engine.run(profile, df_a, df_b)`; `exporter.export_result(...)` grava em arquivo temp com token.
    - Retorna JSON `{counts:{conciliados, nao_conciliados_a, nao_conciliados_b|normalizados}, download_token, suggested_filename}`.
11. `GET /api/conciliador/run/result/{token}` → `FileResponse` do `.xlsx` com `Content-Disposition` usando `Resultado_{perfil}_{dd-mm-aaaa}.xlsx`.

### Fim — validação
12. Testar cada rota via `curl`/cliente HTTP (ou docs `/docs` do FastAPI), incluindo um `run` dual e um single, e o download do arquivo.

## Arquivos
- `web/modules/conciliador/{__init__.py, router.py, storage.py}` (novos)
- `web/modules/registry.py` (editar — registrar o módulo)
- `core/*` — **sem alteração** (opcional: permitir `BytesIO` no `exporter`, só se desejado)

## Critérios de aceite
- [ ] `GET /api/modules` agora inclui o Conciliador.
- [ ] CRUD de perfis funciona e reflete nos arquivos de `profiles/`.
- [ ] `preview` retorna ~20 linhas; `.xls` é recusado com a mensagem correta.
- [ ] `run` dual (ex.: Droga Bem) e single (Modelo 4) geram `.xlsx` baixável com contagens corretas.
- [ ] Erros de coluna/arquivo retornam 400 com mensagem legível.

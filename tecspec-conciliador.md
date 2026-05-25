# Tech Spec — Conciliador / Plataforma `barelli.automacao`

> Especificação técnica do Conciliador e da sua migração para a plataforma web. Complementa o `prd-conciliador.md` (regras de negócio). Para o detalhamento de execução, ver `tasks/task01.md`..`task09.md`.

---

## 1. Estado atual (desktop)

Aplicação desktop em **Python** com interface **customtkinter/Tkinter**, empacotada em `.exe` via PyInstaller.

### Arquitetura em camadas
```
main.py                    # entrada: instancia ui.app.App e roda o mainloop
core/                      # lógica de negócio PURA (sem dependência de UI)
  utils.py                 # resolução de caminhos (dev x PyInstaller)
  profile_manager.py       # CRUD de perfis (arquivos JSON)
  reader.py                # leitura de xlsx/csv + transformações → DataFrame
  engine.py                # algoritmo de conciliação
  exporter.py              # geração do Excel de resultado (formatado)
ui/                        # telas Tkinter (app, screen_home, screen_profile, screen_run)
profiles/                  # perfis JSON (4 defaults + criados pelo usuário)
config.json                # preferências da UI desktop
assets/icon.ico            # ícone
```

**Decisão-chave:** o `core/` é Python puro (pandas + openpyxl), **sem nenhum acoplamento à UI**. É reaproveitado integralmente na web; apenas `ui/` (Tkinter) deixa de ser usado no navegador.

### Dependências atuais
`pandas>=2.0.0`, `openpyxl>=3.1.0`, `customtkinter>=5.2.0`, `pyinstaller>=6.0.0`.

---

## 2. Arquitetura-alvo (web)

Plataforma `barelli.automacao`: SPA React + backend FastAPI, hospedada na **intranet**.

```
Navegador (SPA React) ──HTTP /api──► FastAPI ──► core/ (módulo conciliador)
        ▲                               │
        └─── estáticos (SPA buildada) ◄──┘
```

### Decisões técnicas tomadas
| Tema | Decisão |
|------|---------|
| Backend | **FastAPI** + **Uvicorn**, reaproveitando `core/` |
| Frontend | **React + Vite + TypeScript** |
| Estilo/UI | **Tailwind CSS + shadcn/ui** (Radix), componentes copiados para `src/components/ui/` |
| Dados assíncronos | TanStack Query (recomendado) |
| Roteamento | React Router |
| Hospedagem | Servidor da **intranet**, Uvicorn em `0.0.0.0:8000` |
| Autenticação | **Stub desativado** por flag `AUTH_ENABLED` (estrutura pronta, sem exigir login) |
| Multi-módulo | **Arquitetura plugável**: registro de módulos no backend e no frontend |
| Desktop | **Mantido** em paralelo, compartilhando `core/` e `profiles/` |
| Build/toolchain | Node apenas no frontend; backend permanece Python puro |

---

## 3. Camada `core/` — detalhamento técnico

### 3.1. `profile_manager.py`
CRUD de perfis em arquivos JSON na pasta de perfis. Funções: `load_all_profiles()`, `load_profile(id)`, `save_profile(profile)` (gera `uuid` se não houver `id`; nome de arquivo saneado), `delete_profile(id)`, `duplicate_profile(id)`. Sem mudança para a web.

### 3.2. `reader.py`
Lê `.xlsx` (openpyxl, `data_only=True`) ou `.csv` (pandas) e devolve um `DataFrame` com colunas padronizadas + a coluna interna **`__linha__`** (número real da linha de origem).

Pontos técnicos relevantes:
- **`start_row`** define a primeira linha de dados (ignora cabeçalhos).
- **Transformações** aplicadas em sequência como string (dicionário `TRANSFORMATIONS`):
  `remove_newlines`, `remove_semicolons`, `remove_dots`, `remove_commas`, `remove_special_chars`, `to_int`, `remove_cd_suffix`, `absolute_value`, `strip_after_dash`, `strip_after_slash`, `lstrip_zeros`, `apply_cnpj_mask`.
- **Conversão numérica:** sem transformações textuais, tenta converter direto para `float`. Com `to_int`, vira inteiro; ao final, colunas com `to_int` são convertidas para `Int64` nullable do pandas.
- **Datas:** `_parse_date` aceita `dd/mm/yyyy`, `mm/dd/yyyy`, `yyyy-mm-dd`; datas inválidas viram `None`.
- **Flags por coluna:** `multiply_minus_one`, `skip_if_empty`, `skip_if_invalid_date`.
- **Fallback débito/crédito:** coluna com `is_fallback_of` ("valor") gera o campo `valor` pela regra "se débito vazio/zero → usa crédito".
- **`blank_limit`:** encerra a leitura após N linhas em branco consecutivas no campo de controle.
- **Validação/Preview:** `validate_columns(filepath, sheet_config)` confere se os `col_index` existem (senão `ColumnNotFoundError`); `preview_sheet(filepath, max_rows=20)` retorna as primeiras linhas com cabeçalho de colunas numeradas. Exceções: `ColumnNotFoundError`, `InvalidFileError`.

### 3.3. `engine.py`
Função principal `run(profile, df_a, df_b)`; constante **`NUMERIC_TOLERANCE = 0.01`**.

- **Modo single:** monta apenas o DataFrame de saída a partir do mapeamento de colunas.
- **Modo dual — `match_fields` com `data`:** agrupa por data e, dentro de cada data, faz **pareamento guloso por valor** (ordenação + two-pointer) com tolerância de 0,01, comparando **valor absoluto** (sinais opostos entre Razão/Extrato). Complexidade prática ~O(n log n); suporta milhares de linhas.
- **Modo dual — sem `data`:** fallback de comparação campo a campo.
- **Um-para-um (`one_to_one=true`):** agrupa por chave (ex.: número do cheque) e concilia `min(qtd_A, qtd_B)` por chave; sobras vão para não conciliados.
- **Regras:** nulos nunca conciliam; datas comparadas como `date`; inteiros comparados de forma exata; pareamento sem reuso (cada lançamento casa no máximo uma vez).
- As linhas de origem entram no resultado como `__linha___a` / `__linha___b`.

### 3.4. `exporter.py`
Gera `.xlsx` formatado com **openpyxl**.
- Uma aba por `source` do perfil (`conciliados`, `nao_conciliados_a`, `nao_conciliados_b`) ou `normalizados`, mais a aba **Resumo** (perfil, modo, data/hora, arquivos, contagens).
- Formatação: cabeçalho azul (`1F497D`), zebra, bordas, `freeze_panes`, largura automática.
- Detecção de tipo por palavra-chave no header para aplicar formato de **data** (`DD/MM/YYYY`), **número** (`#,##0.00`) ou **linha** (inteiro).
- Assinatura: `export_result(result, profile, output_path, file_a, file_b)` — grava em `output_path` e o retorna.

### 3.5. `utils.py`
Resolução de caminhos para dev x PyInstaller (`resource_path`, `get_user_data_dir`, `get_profiles_dir`, `get_config_path`). Copia perfis default para a pasta gravável na primeira execução. Rodando como Python normal (web), resolve para a raiz do projeto.

---

## 4. Schema do perfil (JSON)

```jsonc
{
  "id": "string (uuid ou slug)",
  "name": "string",
  "mode": "dual | single",
  "date_format": "dd/mm/yyyy | mm/dd/yyyy | yyyy-mm-dd",
  "sheets": [
    {
      "label": "string",
      "start_row": 1,
      "columns": [
        {
          "field": "data | valor | valor_debito | valor_credito | historico | numero_cheque | numero_nota | cnpj | fornecedor | cpf_cnpj | valor_parcela | valor_juros | valor_desconto | documento | <custom>",
          "col_index": 1,                  // 1-based
          "transformations": ["remove_dots", "to_int"],
          "multiply_minus_one": false,
          "is_fallback_of": null,          // ex.: "valor"
          "skip_if_empty": false,
          "skip_if_invalid_date": false
          // opcional: "blank_limit": N
        }
      ]
    }
  ],
  "comparison": {                          // relevante apenas no modo dual
    "enabled": true,
    "match_fields": ["data", "valor"],     // ou ["numero_cheque"], etc.
    "one_to_one": false
  },
  "output": {
    "tabs": [
      {
        "name": "Dados Conciliados",
        "source": "conciliados | nao_conciliados_a | nao_conciliados_b | normalizados",
        "columns": [
          { "header": "Data", "field": "data", "fixed_value": null }
          // fixed_value preenche um valor constante (ex.: juros = 0)
          // headers especiais: "__linha___a" / "__linha___b" (origem)
        ]
      }
    ]
  }
}
```

> O schema é **compartilhado entre desktop e web**; perfis criados em um devem abrir no outro. A web deve gerar exatamente o mesmo JSON (mesma validação e mesmo `output` default que `ui/screen_profile.py`).

---

## 5. Backend web — estrutura e contratos

### 5.1. Estrutura
```
web/
  server.py            # FastAPI: inclui routers dos módulos, serve SPA, /api/modules, /api/health
  auth.py              # get_current_user (NO-OP enquanto AUTH_ENABLED=false)
  modules/
    registry.py        # ALL_MODULES (manifesto {id,title,description,icon} + APIRouter)
    conciliador/
      router.py        # endpoints do conciliador (reusam core/)
      storage.py       # uploads/resultados em tempfile + tokens + limpeza por TTL
run_web.py             # uvicorn web.server:app --host 0.0.0.0 --port ${PORT:-8000}
```

### 5.2. Endpoints (módulo conciliador, prefixo `/api/conciliador`)
| Método | Rota | Reuso de `core/` |
|--------|------|------------------|
| GET | `/api/modules` | manifesto dos módulos (Hub) |
| GET | `/api/conciliador/profiles` | `load_all_profiles` |
| GET | `/api/conciliador/profiles/{id}` | `load_profile` |
| POST | `/api/conciliador/profiles` | `save_profile` |
| POST | `/api/conciliador/profiles/{id}/duplicate` | `duplicate_profile` |
| DELETE | `/api/conciliador/profiles/{id}` | `delete_profile` |
| POST | `/api/conciliador/preview` | `preview_sheet` (recusa `.xls`) |
| POST | `/api/conciliador/run/{id}` | `validate_columns` → `engine.run` → `exporter.export_result` |
| GET | `/api/conciliador/run/result/{token}` | `FileResponse` do `.xlsx` |

### 5.3. Manipulação de arquivos (substitui diálogos nativos)
- **Upload** (`multipart/form-data`, requer `python-multipart`) → grava em arquivo temporário.
- **Preview/Run** operam sobre o caminho temporário (funções de `core/` recebem path → zero mudança).
- **Resultado:** `export_result` grava em temp identificado por **token**; `run` retorna `{counts, download_token, suggested_filename}`; o GET do token devolve o arquivo com `Content-Disposition` (`Resultado_{perfil}_{dd-mm-aaaa}.xlsx`).
- **Limpeza:** remover temporários na inicialização e/ou por idade (TTL).
- Processamento é **síncrono** no request (pandas é CPU-bound; sem ganho em async).

### 5.4. Mapeamento de erros
`ColumnNotFoundError`/`InvalidFileError` → HTTP 400 com a mensagem original; perfil inexistente → 404.

### 5.5. Autenticação (preparada, desativada)
`auth.py` expõe a dependency `get_current_user`, hoje retornando usuário anônimo sem bloquear; flag `AUTH_ENABLED` (env, default `false`). Os routers já declaram a dependency para que o ponto de injeção exista.

---

## 6. Frontend web — estrutura

```
web/frontend/
  package.json, vite.config.ts, tailwind.config.js, index.html
  src/
    main.tsx, App.tsx            # providers (auth, query, toaster) + rotas
    lib/api.ts                   # cliente HTTP base /api + tratamento de erro (toast/sonner)
    components/ui/               # componentes shadcn/ui
    layout/AppShell.tsx          # logo Barelli + navegação (Outlet)
    auth/{AuthProvider,RequireAuth}.tsx  # stub pass-through; rota /login stub
    modules/
      registry.ts                # módulos do frontend {id,title,icon,basePath,element}
      conciliador/
        api.ts
        Home.tsx                 # lista de perfis (cards) + criar/editar/duplicar/excluir
        ProfileEditor.tsx        # geral, comparação, abas de planilha, colunas dinâmicas, transformações (Dialog), preview (Table)
        Run.tsx                  # upload, executar, contagens, download
    pages/Hub.tsx                # grid de cards a partir de /api/modules
```

- **Dev:** Vite dev server (5173) com **proxy `/api` → 8000**.
- **Telas do conciliador** replicam o comportamento das telas Tkinter (`screen_home`, `screen_profile`, `screen_run`), incluindo recusa de `.xls` e as validações de perfil.

---

## 7. Pluggabilidade (adicionar novo módulo)

Adicionar uma automação = **(1)** criar `web/modules/<nome>/router.py` + manifesto e registrá-lo em `registry.py`; **(2)** criar `src/modules/<nome>/` no frontend e adicioná-lo a `registry.ts`. O Hub passa a exibir o card automaticamente, **sem alterar** o núcleo da plataforma nem o módulo Conciliador.

---

## 8. Deploy na intranet

- **Build:** `npm run build` → `web/frontend/dist`.
- **Serviço de estáticos:** FastAPI monta `StaticFiles(dist)` + **catch-all** que retorna `index.html` (roteamento client-side), exceto rotas `/api/*`.
- **Execução:** `run_web.py` sobe Uvicorn em `0.0.0.0:8000` (SPA + API no mesmo processo). Acesso na rede via `http://<ip-do-servidor>:8000`.
- **Inicialização:** `iniciar_barelli_automacao.bat` (Windows); opcional como tarefa agendada/serviço.
- **Segurança:** sem login ativo (aceitável em intranet confiável; estrutura pronta para ligar depois).

---

## 9. Dependências adicionais (web)

Backend: `fastapi`, `uvicorn[standard]`, `python-multipart` (mantém `pandas`, `openpyxl`; `customtkinter`/`pyinstaller` seguem para o desktop).
Frontend: `react`, `react-dom`, `react-router-dom`, `vite`, `typescript`, `tailwindcss`, shadcn/ui (Radix), `@tanstack/react-query` (opcional), `sonner` (toasts).

---

## 10. Registro de decisões

- **Reusar `core/` em vez de reescrever** (menor risco; lógica de conciliação já validada).
- **shadcn/ui + Tailwind** escolhidos pelo usuário (sobre Mantine).
- **Login preparado, não ativado** nesta fase.
- **Desktop e web coexistem**, compartilhando `core/` e `profiles/`.
- **Single-user na intranet**, sem multiusuário/perfis por usuário neste momento.
- **`.xls` não suportado** (orientar conversão para `.xlsx`).
- **Tolerância de valor fixa em R$ 0,01**; comparação por valor absoluto.

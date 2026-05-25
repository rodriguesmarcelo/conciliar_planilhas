# Task 08 — Empacotamento e deploy na intranet

## Objetivo
Tornar a plataforma executável num servidor da intranet: o FastAPI serve o build do frontend e fica acessível na rede; criar script de inicialização, limpeza de temporários e documentação de implantação.

## Pré-requisitos
- Tasks 01–06 funcionando (e idealmente 07).

## Escopo / Passos

### Início — build e serviço de estáticos
1. Configurar `vite.config.ts` com `base` adequado e build para `web/frontend/dist`.
2. Em `web/server.py`: montar `StaticFiles` servindo `web/frontend/dist` e um **catch-all** que retorna `index.html` (para o roteamento client-side do React Router) — sem capturar as rotas `/api/*`.

### Meio — execução e robustez
3. `run_web.py`: subir uvicorn em `0.0.0.0:${PORT:-8000}` servindo a SPA + API no mesmo processo.
4. **Limpeza de temporários:** remover uploads/resultados antigos na inicialização e/ou por idade (TTL), evitando acúmulo no servidor.
5. Criar `iniciar_barelli_automacao.bat` (Windows) que ativa o ambiente e roda `python run_web.py`. Opcional: documentar como tarefa agendada/serviço para subir no boot.

### Fim — documentação e validação
6. Atualizar o `README.md` com: pré-requisitos, `pip install -r requirements.txt`, `npm install && npm run build`, como iniciar o servidor e o IP/porta de acesso na rede.
7. Validar acesso de **outro PC da intranet** via `http://<ip-do-servidor>:8000`.

## Arquivos
- `web/server.py` (editar — StaticFiles + catch-all)
- `web/frontend/vite.config.ts` (editar — base/build)
- `run_web.py` (editar — limpeza/porta)
- `iniciar_barelli_automacao.bat` (novo)
- `README.md` (editar — seção de deploy web)

## Critérios de aceite
- [ ] `npm run build` gera `dist`; FastAPI serve a SPA em `0.0.0.0:8000`.
- [ ] Recarregar uma rota interna (ex.: `/conciliador`) funciona (catch-all → index.html).
- [ ] Acesso de outro PC da intranet confirmado.
- [ ] `.bat` inicia a plataforma; temporários são limpos automaticamente.
- [ ] README documenta build + execução + acesso na rede.

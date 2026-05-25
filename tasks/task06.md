# Task 06 — Frontend Conciliador: tela de Execução (upload, executar, download)

## Objetivo
Implementar a tela de execução da conciliação: seleção (upload) dos arquivos, validação, disparo do processamento e **download** do `.xlsx` com exibição das contagens — paridade com a `screen_run.py` do desktop.

## Pré-requisitos
- Task 02 (`run` + `result`) e Task 04 (Home navega para a execução com o `id`).

## Escopo / Passos

### Início — carregamento do perfil
1. `Run.tsx` em rota `/conciliador/run/:id`. Carregar o perfil para saber `mode` e os rótulos das planilhas.
2. Renderizar 1 seletor de arquivo (Single) ou 2 (Dual), com os rótulos `sheets[].label` ("Planilha A — Razão", etc.). Recusar `.xls` com a mensagem de conversão.

### Meio — execução
3. Botão **Executar Conciliação** (desabilitado até os arquivos necessários estarem selecionados).
4. Enviar `POST /api/conciliador/run/{id}` (multipart) com indicador de progresso/carregando. Tratar erros 400 (coluna/arquivo) exibindo a mensagem retornada.
5. Ao concluir, exibir o **painel de resultado** com as contagens:
   - Single: registros normalizados.
   - Dual: conciliados / não conciliados A / não conciliados B (destacar em vermelho quando > 0).

### Fim — download e nova execução
6. Botão **Baixar resultado** → `GET /api/conciliador/run/result/{token}` (dispara download com o nome sugerido).
7. Botão **Nova conciliação** → volta à Home (ou limpa o formulário).

## Arquivos
- `src/modules/conciliador/Run.tsx` (novo) + componente `FileDropField`
- `src/modules/conciliador/api.ts` (editar — `runReconciliation`, `resultUrl`)

## Critérios de aceite
- [ ] Upload de 1/2 arquivos conforme o modo; `.xls` recusado.
- [ ] Executar mostra carregando e, ao fim, as contagens corretas.
- [ ] Download entrega o `.xlsx` com o nome `Resultado_{perfil}_{dd-mm-aaaa}.xlsx`.
- [ ] Erros de validação (coluna fora do range, arquivo inválido) aparecem de forma legível.

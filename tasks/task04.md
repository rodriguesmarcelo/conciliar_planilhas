# Task 04 — Frontend Conciliador: tela Home (lista de perfis + ações)

## Objetivo
Implementar a tela inicial do módulo Conciliador: grade de cards de perfis com ações de **selecionar (executar)**, **criar**, **editar**, **duplicar** e **excluir** — paridade com a `screen_home.py` do desktop.

## Pré-requisitos
- Task 02 (endpoints de perfis) e Task 03 (scaffolding do frontend).

## Escopo / Passos

### Início — dados
1. Em `src/modules/conciliador/api.ts`: funções `listProfiles`, `duplicateProfile`, `deleteProfile` (consumindo a API da Task 02).
2. Criar `Home.tsx` na rota base do módulo (ex.: `/conciliador`).

### Meio — UI
3. Buscar perfis e renderizar **cards** (shadcn `Card`), exibindo nome, modo (badge Dual/Single) e nº de planilhas.
4. Botões por card: **Editar** (→ editor da Task 05), **Duplicar** (chama API e atualiza a lista), **Excluir** (abre `AlertDialog` de confirmação e chama API).
5. Clique no card → navega para a tela de Execução (Task 06) com o `id` do perfil.
6. Botão global **＋ Novo Perfil** → editor em modo "new".
7. Estado vazio ("Nenhum perfil encontrado") e estados de carregando/erro (toasts).

### Fim — validação
8. Verificar que criar (via editor), duplicar e excluir refletem imediatamente na lista e nos arquivos de `profiles/`.

## Arquivos
- `src/modules/conciliador/api.ts` (editar/criar)
- `src/modules/conciliador/Home.tsx` (novo)
- `src/modules/registry.ts` (apontar a rota base para `Home`)

## Critérios de aceite
- [ ] Os 4 perfis default aparecem como cards com badge de modo.
- [ ] Duplicar e excluir funcionam (com confirmação) e atualizam a lista.
- [ ] "Novo Perfil" e "Editar" abrem o editor; clicar no card abre a Execução.
- [ ] Estados de vazio/carregando/erro tratados.

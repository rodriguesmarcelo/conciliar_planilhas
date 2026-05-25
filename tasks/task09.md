# Task 09 — Verificação de paridade e teste de pluggabilidade

## Objetivo
Garantir que a versão web produz exatamente os mesmos resultados do desktop e que a arquitetura plugável de módulos realmente funciona (adicionar um novo módulo é simples).

## Pré-requisitos
- Tasks 01–08 concluídas.

## Escopo / Passos

### Início — paridade de resultados
1. Selecionar arquivos reais usados no `.exe` para um perfil **dual** (ex.: Droga Bem) e um **single** (Modelo 4 / Duplicatas Pagas).
2. Gerar o `.xlsx` pelo **desktop** e pela **web** com os mesmos arquivos.
3. Comparar: número de abas, nomes, **contagens** (conciliados / não conciliados / normalizados), colunas de saída e formatação. Devem ser equivalentes (mesmo `core/`).

### Meio — robustez e bordas
4. Testar casos de borda: arquivo `.xls` (recusado), coluna fora do range (erro 400 legível), planilha vazia, `one_to_one` (cheques), fallback débito/crédito, datas inválidas (`skip_if_invalid_date`).
5. Conferir interoperabilidade de perfis: perfil criado na web abre no desktop e vice-versa.

### Fim — pluggabilidade
6. Criar um **módulo dummy** ("Olá Mundo"): router backend mínimo + manifesto no `registry.py` + entrada no `registry.ts` + uma tela simples. Confirmar que ele aparece como novo card no Hub **sem alterar** o núcleo da plataforma nem o módulo Conciliador.
7. Remover o dummy ao final (ou deixar documentado como exemplo).
8. Registrar no README o **passo a passo de "como adicionar um novo módulo"**.

## Arquivos
- Nenhum de produção obrigatório (validação). Opcional: módulo dummy temporário + seção no `README.md`.

## Critérios de aceite
- [ ] Resultados web == desktop para um perfil dual e um single (mesmos arquivos).
- [ ] Casos de borda tratados com mensagens claras.
- [ ] Perfis são intercambiáveis entre web e desktop.
- [ ] Um módulo novo aparece no Hub apenas registrando-o (pluggabilidade comprovada).
- [ ] README documenta como adicionar módulos.

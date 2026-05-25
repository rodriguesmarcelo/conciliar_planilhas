# Task 05 — Frontend Conciliador: Editor de Perfil

## Objetivo
Implementar a tela mais complexa do módulo: criação/edição de perfis com paridade total à `screen_profile.py` do desktop — dados gerais, critérios de comparação, configuração dinâmica de planilhas/colunas, transformações e pré-visualização — gerando o mesmo JSON de perfil consumido pelo `core/`.

## Pré-requisitos
- Task 02 (endpoints de perfil + preview) e Task 04 (Home com navegação para o editor).

## Escopo / Passos

### Início — carregamento e seção geral
1. `ProfileEditor.tsx` em rota `/conciliador/profiles/new` e `/conciliador/profiles/:id/edit`. Em edição, carregar o perfil via API.
2. Seção **Geral**: nome do perfil (com validação de caracteres proibidos do Windows `/\\|:*?"<>`), modo (radio Dual/Single), formato de data (Select: `dd/mm/yyyy`, `mm/dd/yyyy`, `yyyy-mm-dd`).
3. Seção **Comparação** (visível só no modo Dual): checkboxes de `match_fields` (`data`, `valor`, `numero_cheque`, `numero_nota`, `documento`) e checkbox **Conciliação Um-para-Um**.

### Meio — planilhas e colunas (estado dinâmico)
4. Abas por planilha (1 no Single, 2 no Dual). Por planilha: rótulo (`label`) e linha inicial (`start_row`).
5. **Pré-visualização:** upload de arquivo → `POST /api/conciliador/preview` → renderizar tabela (shadcn `Table`) das ~20 primeiras linhas. Recusar `.xls` com a mensagem de conversão.
6. **Tabela de colunas dinâmica:** adicionar/remover linhas; cada linha = `field` (Select com a lista de campos + "personalizado"), `col_index` (input), **Transformações** (Dialog com checkboxes — as 12 transformações de `reader.TRANSFORMATIONS`), `multiply_minus_one`, `skip_if_empty`, `skip_if_invalid_date` (este só habilitado quando `field === "data"`).
7. Suportar o **fallback débito/crédito** (`is_fallback_of`) presente nos perfis existentes (preservar ao editar; permitir configurar).

### Fim — salvar e validar
8. **Validação** (espelhar `_validate` do desktop): nome obrigatório/sem caracteres inválidos; cada planilha com ≥1 coluna; `col_index ≥ 1`.
9. **Montar o JSON** (espelhar `_collect` + `_default_output`): `id`, `name`, `mode`, `date_format`, `sheets`, `comparison`, `output` (gerar `output.tabs` default; preservar o `output` existente ao editar). `POST /api/conciliador/profiles` → toast de sucesso → voltar à Home.
10. Conferir que um perfil criado pela web abre corretamente no desktop e vice-versa (mesmo schema).

## Arquivos
- `src/modules/conciliador/ProfileEditor.tsx` (novo) + subcomponentes (`SheetPanel`, `ColumnRow`, `TransformDialog`, `PreviewTable`)
- `src/modules/conciliador/api.ts` (editar — `getProfile`, `saveProfile`, `preview`)
- Referência de schema: `profiles/droga_bem.json` e `ui/screen_profile.py` (`FIELD_OPTIONS`, `ALL_TRANSFORMS`, `_default_output`).

## Critérios de aceite
- [ ] Criar e editar perfis gera JSON idêntico em estrutura ao do desktop.
- [ ] Alternar modo Dual/Single mostra/oculta comparação e ajusta o nº de abas.
- [ ] Pré-visualização funciona; `.xls` recusado.
- [ ] Transformações, ×(-1), pular-se-vazio, pular-se-data-inválida e fallback débito/crédito persistem corretamente.
- [ ] Validações replicam as do desktop; perfil salvo é lido pelo desktop sem erro.

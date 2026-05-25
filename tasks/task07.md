# Task 07 — Identidade visual da Barelli (logo + paleta) e refino do tema

## Objetivo
Aplicar a identidade visual da Barelli (logo e cores fornecidos pelo usuário) ao tema da plataforma, deixando o visual coeso e profissional no AppShell, no Hub e nas telas do Conciliador.

## Pré-requisitos
- Task 03 (AppShell + Tailwind + shadcn) e telas das Tasks 04–06.
- **Insumo do usuário:** arquivo do logo + códigos hex da paleta.

## Escopo / Passos

### Início — assets e tokens
1. Adicionar o(s) arquivo(s) de logo em `web/frontend/src/assets/`.
2. Definir a paleta no `tailwind.config.js` e nas variáveis CSS do shadcn (`--primary`, `--background`, `--foreground`, etc.), claro/escuro se aplicável.

### Meio — aplicação
3. Inserir o logo no `AppShell` (cabeçalho/sidebar) e o nome "barelli.automacao".
4. Ajustar `Card`, `Button`, badges e estados (foco/hover) à paleta da marca.
5. Definir `favicon` e `title` da aba (`index.html`).
6. Garantir tipografia/espaçamentos consistentes e responsividade básica (uso em diferentes resoluções dos PCs da intranet).

### Fim — validação
7. Revisão visual de Hub, Home, Editor e Execução com a marca aplicada.

## Arquivos
- `web/frontend/src/assets/*` (logo)
- `web/frontend/tailwind.config.js`, CSS global do tema (variáveis shadcn)
- `web/frontend/index.html` (favicon/title), `src/layout/AppShell.tsx`

## Critérios de aceite
- [ ] Logo e paleta da Barelli presentes no AppShell e refletidos nos componentes.
- [ ] Favicon e título da aba corretos.
- [ ] Visual consistente e responsivo nas 4 telas principais.

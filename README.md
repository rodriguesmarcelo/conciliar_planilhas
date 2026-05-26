# Conciliador de Planilhas

Sistema desktop em Python para **conciliar e normalizar planilhas Excel**, com suporte a 4 modelos pré-configurados e criação de perfis customizados.

---

## Funcionalidades

- Conciliação de duas planilhas por campos configuráveis (data + valor, número de cheque, etc.)
- Normalização de planilha única com transformações de dados
- 4 perfis default prontos para uso (Droga Bem, MRS, Cristo Rei, Clube)
- Criação, edição e duplicação de perfis customizados
- Pré-visualização da planilha antes de configurar o perfil
- Exportação do resultado em `.xlsx` com formatação profissional e aba de resumo
- Validação de colunas antes da execução (evita erros silenciosos)
- Interface gráfica desktop com tema dark

---

## Requisitos

- **Python 3.10** ou superior
- Dependências listadas em `requirements.txt`

```
pandas>=2.0.0
openpyxl>=3.1.0
customtkinter>=5.2.0
pyinstaller>=6.0.0
```

---

## Instalação e Execução

### 1. Clonar / extrair o projeto

```bash
# Extraia o ZIP ou clone o repositório na pasta desejada
```

### 2. Instalar dependências

```bash
pip install -r requirements.txt
```

### 3. Executar

```bash
python main.py
```

---

## Plataforma Web (barelli.automacao)

Além do app desktop, o mesmo `core/` é exposto numa plataforma web (FastAPI + SPA
React) para uso na intranet — vários PCs acessam pelo navegador, sem instalar nada.

### Pré-requisitos

- **Python 3.10+** e **Node 18+** (apenas para gerar o build do frontend).

### 1. Dependências do backend

```bash
pip install -r requirements.txt
```

### 2. Build do frontend

```bash
cd web/frontend
npm install
npm run build      # gera web/frontend/dist
cd ../..
```

### 3. Iniciar o servidor

Na raiz do projeto:

```bash
python run_web.py
```

No Windows, basta dar duplo clique em **`iniciar_barelli_automacao.bat`** (ativa o
`.venv`, se existir, e sobe o servidor). O FastAPI serve a SPA e a API no mesmo
processo, em `0.0.0.0:8000`.

> Sem o build (`web/frontend/dist`), o servidor sobe só com a API — para
> desenvolvimento, rode o Vite à parte: `cd web/frontend && npm run dev` (porta
> 5173, com proxy `/api` → 8000).

### 4. Acesso na rede

- No servidor, descubra o IP com `ipconfig` (ex.: `192.168.0.10`).
- Em qualquer PC da intranet, abra `http://<ip-do-servidor>:8000`.
- **Firewall do Windows:** libere a entrada na porta 8000 (sem isso, outros PCs
  não conseguem acessar):

  ```bat
  netsh advfirewall firewall add rule name="barelli.automacao" dir=in action=allow protocol=TCP localport=8000
  ```

> Opcional: para subir no boot, cadastre o `.bat` no **Agendador de Tarefas** do
> Windows (gatilho "Ao iniciar o computador").

### Configuração (`.env`)

Copie `.env.example` para `.env` e ajuste se necessário (prefixo `BARELLI_`):

| Variável | Padrão | Descrição |
|----------|--------|-----------|
| `BARELLI_PORT` | `8000` | Porta do servidor web |
| `BARELLI_AUTH_ENABLED` | `false` | Login (desativado nesta fase) |
| `BARELLI_CORS_ORIGINS` | `["http://localhost:5173"]` | Origens liberadas no CORS (Vite dev) |
| `BARELLI_DATA_DIR` | (vazio) | Pasta de dados/perfis; vazio = `profiles/` na raiz (compartilhada com o desktop) |

Os arquivos temporários (uploads/resultados) ficam em `%TEMP%\barelli_automacao` e
são limpos na inicialização e a cada 2 horas automaticamente.

### Como adicionar um novo módulo

A plataforma é plugável: um módulo novo aparece no Hub apenas sendo **registrado**,
sem alterar o núcleo (`web/server.py`) nem o módulo Conciliador. São 2 pontos de
toque no backend e 2 no frontend. Exemplo de um módulo "Olá Mundo":

1. **Backend — router** (`web/modules/hello/router.py`):
   ```python
   from fastapi import APIRouter
   router = APIRouter(prefix="/hello", tags=["hello"])

   @router.get("/ping")
   def ping() -> dict:
       return {"message": "Olá, mundo!"}
   ```
2. **Backend — registro** (`web/modules/registry.py`): adicione ao final
   ```python
   from web.modules.hello.router import router as _hello_router
   ALL_MODULES.append(Module(
       manifest=ModuleManifest(id="hello", title="Olá Mundo",
           description="Módulo de exemplo.", icon="layout-grid"),
       router=_hello_router))
   ```
3. **Frontend — tela** (`web/frontend/src/modules/hello/index.tsx`): um componente
   React exportado como `default` (pode conter suas próprias rotas, como
   `modules/conciliador/index.tsx`).
4. **Frontend — registro** (`web/frontend/src/modules/registry.ts`): uma entrada
   em `MODULES` com `{ id, title, icon, basePath: "/hello", element: HelloModule }`.

Pronto: o card surge no Hub e a navegação na sidebar é automática. O `icon` é um
nome de [lucide-react](https://lucide.dev); ícones desconhecidos caem no padrão
`LayoutGrid` — para um ícone próprio, registre-o em
`web/frontend/src/components/AppIcon.tsx` (opcional). As rotas do módulo ficam sob
`/api/<prefix>` (backend) e `/<basePath>` (frontend).

---

## Gerar Executável (.exe) — Windows

```bash
pyinstaller --onefile --windowed ^
  --name "Conciliador" ^
  --icon assets\icon.ico ^
  --add-data "profiles;profiles" ^
  --add-data "config.json;." ^
  main.py
```

O executável será gerado em `dist/Conciliador.exe`.  
Novos perfis criados pelo usuário são salvos na mesma pasta do `.exe`.

> **macOS / Linux:** substitua `;` por `:` nos parâmetros `--add-data`.

---

## Modelos Default

### Modelo 1
Concilia **Razão × Extrato** comparando data e valor.  
- Razão: linha 10, débito col. 18 (×-1), crédito col. 20, histórico col. 6  
- Extrato: linha 11, valor col. 4, histórico col. 2

### Modelo 2
Concilia **Cheques × Extrato** comparando número de cheque (one-to-one).  
- Cheques: linha 2, cheque col. 4 (remove pontos → inteiro)  
- Extrato: linha 3, cheque col. 2, valor col. 4 (remove sufixo C/D → absoluto)  
- Saída inclui NUMERO_NOTA, CPF_CNPJ, DATA, VALOR, JUROS=0, MULTA=0, DESCONTO=0

### Modelo 3
Concilia **Razão × Extrato** comparando data e valor.  
- Razão: linha 10, débito col. 8, crédito col. 9 (×-1), histórico col. 3  
- Extrato: linha 2, valor col. 3, histórico col. 2

### Modelo 4
**Normalização** de Duplicatas Pagas (sem comparação).  
- Linha 12, nota col. 2 (strip após "-", remove zeros), CNPJ col. 11 (máscara)  
- Saída: NUMERO_NOTA, CPF_CNPJ, DATA, VALOR_PARCELA, JUROS, MULTA=0, DESCONTO

---

## Como Criar um Novo Perfil

1. Na tela inicial, clique em **＋ Novo Perfil**
2. Defina o nome, modo (1 ou 2 planilhas) e formato de data
3. Para cada planilha:
   - Informe o nome e a linha de início dos dados
   - Clique em **📂 Selecionar arquivo** para pré-visualizar as colunas
   - Adicione os campos com **＋ Adicionar Campo**, configurando:
     - Qual campo (data, valor, histórico, etc.)
     - Número da coluna
     - Transformações aplicadas (remover pontos, converter para inteiro, etc.)
     - Opções: multiplicar por -1, pular se vazio, pular se data inválida
4. Clique em **💾 Salvar Perfil**

Perfis salvos ficam na pasta `profiles/` e aparecem automaticamente na tela inicial.

---

## Estrutura do Projeto

```
conciliador/
├── main.py                  # Ponto de entrada
├── requirements.txt
├── config.json              # Configurações persistentes
├── profiles/                # Perfis JSON (default + usuário)
├── core/
│   ├── utils.py             # Caminhos (dev e .exe)
│   ├── profile_manager.py   # CRUD de perfis
│   ├── reader.py            # Leitura e transformações
│   ├── engine.py            # Motor de conciliação
│   └── exporter.py          # Exportação Excel
├── ui/
│   ├── app.py               # Janela principal
│   ├── screen_home.py       # Tela de seleção de perfil
│   ├── screen_profile.py    # Criação/edição de perfil
│   └── screen_run.py        # Execução da conciliação
└── assets/
    └── icon.ico             # Ícone (opcional)
```

---

## Arquivo de Resultado

O Excel gerado contém:

- **Resumo** — nome do perfil, data/hora, arquivos usados, contagens
- **Dados Conciliados** — registros que casaram entre as planilhas
- **Não Conciliados — [Planilha A]** — registros sem par em B
- **Não Conciliados — [Planilha B]** — registros sem par em A

(Modo single: apenas **Dados Normalizados**)

---

## Licença

Uso interno. Todos os direitos reservados.

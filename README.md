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

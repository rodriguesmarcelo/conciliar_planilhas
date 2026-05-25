# PRD — Conciliador de Planilhas

> Documento de regras de negócio do módulo **Conciliador**. Descreve **o que** o sistema faz e **como deve se comportar**, sem detalhes de implementação.

---

## 1. Visão geral

O Conciliador é uma ferramenta que **compara e normaliza planilhas** (tipicamente extratos bancários, razões contábeis, listas de cheques e duplicatas) para identificar quais lançamentos de uma planilha correspondem aos de outra, e para padronizar dados em um formato de saída limpo.

O objetivo é **substituir a conferência manual** de planilhas, que é demorada e sujeita a erro, gerando automaticamente um relatório que mostra o que **bateu** (conciliado) e o que **não bateu** (pendências) entre duas fontes — ou, no caso de uma única planilha, entregando os dados já organizados.

---

## 2. Conceitos principais

- **Planilha:** um arquivo de entrada (Excel ou CSV) com os lançamentos. Cada conciliação usa uma ou duas planilhas.
- **Perfil:** um modelo de configuração reutilizável que descreve **como ler** cada planilha, **como comparar** os dados e **como apresentar** o resultado. Cada cliente/cenário tem seu perfil.
- **Campo:** o significado de uma coluna da planilha para o negócio (ex.: data, valor, número do cheque, histórico).
- **Conciliação:** o ato de comparar duas planilhas e parear os lançamentos equivalentes.
- **Normalização:** o ato de limpar e padronizar os dados de uma única planilha (sem comparação).

---

## 3. Modos de operação

O perfil define um de dois modos:

1. **Dual (duas planilhas):** compara a Planilha A com a Planilha B e separa os lançamentos em **conciliados** e **não conciliados** (de cada lado).
2. **Single (uma planilha):** apenas normaliza/padroniza os dados de uma planilha, sem comparação.

---

## 4. O que um perfil configura

Cada perfil define, em linguagem de negócio:

- **Nome** do perfil (identifica o cliente/cenário).
- **Modo** (uma ou duas planilhas).
- **Formato de data** esperado nos arquivos (dia/mês/ano, mês/dia/ano ou ano-mês-dia).
- Para **cada planilha**:
  - Um **rótulo** (ex.: "Razão", "Extrato", "Cheques").
  - A **linha em que os dados começam** (para ignorar cabeçalhos/títulos no topo do arquivo).
  - A lista de **campos**: para cada campo, qual coluna do arquivo ele ocupa, quais **limpezas** aplicar e quais **regras especiais** valem.
- **Critérios de comparação** (apenas no modo Dual): por quais campos os lançamentos devem bater.
- **Formato de saída**: quais colunas aparecem no relatório final.

---

## 5. Campos reconhecidos

Os campos que um perfil pode mapear incluem: **data, valor, valor (débito), valor (crédito), histórico, número do cheque, número da nota, CNPJ, fornecedor, CPF/CNPJ, valor da parcela, juros, desconto, documento** — além de campos **personalizados** quando necessário.

---

## 6. Regras de limpeza de dados (transformações)

Cada coluna pode ter uma ou mais limpezas aplicadas na leitura, na ordem em que são definidas. As regras disponíveis:

- **Remover quebras de linha** — junta textos quebrados em várias linhas numa só.
- **Remover ponto-e-vírgula** — retira `;` do texto.
- **Remover pontos** — retira `.` (útil para separadores de milhar).
- **Converter vírgula em ponto** — trata a vírgula decimal brasileira como separador decimal.
- **Manter apenas dígitos** — descarta tudo que não for número (ex.: para documentos).
- **Converter para inteiro** — transforma o valor em número inteiro.
- **Remover sufixo C/D** — tira o indicador de Crédito/Débito ao final de valores do extrato.
- **Valor absoluto** — ignora o sinal (positivo/negativo).
- **Cortar após hífen (-)** — mantém só o que vem antes do `-`.
- **Cortar após barra (/)** — mantém só o que vem antes da `/`.
- **Remover zeros à esquerda** — ex.: `000123` → `123`.
- **Aplicar máscara de CNPJ** — formata os dígitos no padrão `00.000.000/0000-00`.

---

## 7. Regras especiais por campo

- **Multiplicar por -1 (inverter sinal):** usado quando uma planilha registra valores com sinal oposto ao da outra (ex.: crédito na razão x débito no extrato).
- **Pular linha se o campo estiver vazio:** quando este campo é obrigatório (ex.: número do cheque), a linha sem esse dado é ignorada.
- **Pular linha se a data for inválida:** linhas cuja data não puder ser interpretada são ignoradas (descarta rodapés, totais e linhas em branco).
- **Limite de linhas em branco consecutivas:** ao encontrar uma sequência de linhas vazias, a leitura é encerrada (evita ler "lixo" após o fim real dos dados).

### Regra de fallback débito/crédito
Quando uma planilha tem **duas colunas** para o mesmo valor (uma de débito e outra de crédito), o sistema monta um único campo **valor** com a regra: **se o débito estiver vazio ou zero, usa o crédito** (normalmente com o sinal invertido); caso contrário, usa o débito.

---

## 8. Regras de conciliação (modo Dual)

A conciliação pareia lançamentos da Planilha A com os da Planilha B segundo os **critérios de comparação** definidos no perfil.

### 8.1. Comparação por data + valor (caso mais comum)
- Os lançamentos são agrupados por **data** e, dentro de cada data, pareados por **valor**.
- A comparação de valor usa **tolerância de R$ 0,01** (diferenças de centavo por arredondamento são aceitas como iguais).
- A comparação é feita pelo **valor absoluto**, pois as duas planilhas costumam registrar o mesmo lançamento com sinais opostos.
- Cada lançamento de A pode parear com **apenas um** lançamento de B (e vice-versa). Não há reuso.

### 8.2. Comparação um-para-um por chave (cheques)
- Indicado quando a comparação é por uma chave única, como o **número do cheque**.
- Para cada chave presente nos dois lados, o sistema concilia a **menor quantidade** entre A e B (ex.: 3 cheques iguais de um lado e 2 do outro → 2 conciliados); as **sobras** vão para não conciliados.

### 8.3. Regras gerais
- **Valores nulos/ausentes nunca conciliam.**
- **Datas** são comparadas como datas (não como texto).
- **Números inteiros** (ex.: cheque) são comparados de forma exata.
- Lançamentos sem par vão para a lista de **não conciliados** do respectivo lado.

---

## 9. Resultado (saída)

O sistema gera uma planilha Excel formatada como relatório.

### Modo Dual — abas:
- **Resumo** — perfil utilizado, modo, data/hora da execução, arquivos usados e contagens.
- **Dados Conciliados** — lançamentos que bateram entre A e B (com indicação da linha de origem em cada planilha).
- **Não Conciliados — [Planilha A]** — lançamentos de A sem correspondência em B.
- **Não Conciliados — [Planilha B]** — lançamentos de B sem correspondência em A.

### Modo Single — abas:
- **Dados Normalizados** — os dados limpos e padronizados.
- **Resumo** — perfil, data/hora e total de registros.

As colunas de cada aba seguem o **formato de saída** definido no perfil, podendo incluir valores fixos (ex.: juros = 0).

---

## 10. Modelos padrão (perfis prontos)

A ferramenta já vem com perfis configurados para cenários reais:

- **Razão × Extrato (por data e valor):** concilia a razão contábil com o extrato bancário, casando lançamentos pela data e pelo valor (absoluto, com tolerância de centavo). Há mais de um perfil desse tipo, variando as colunas conforme o layout do cliente.
- **Cheques × Extrato (um-para-um por número do cheque):** concilia uma lista de cheques com o extrato pelo número do cheque. A saída inclui número da nota, CPF/CNPJ, data e valor (com juros, multa e desconto fixados em zero).
- **Normalização de Duplicatas Pagas (uma planilha):** apenas padroniza os dados de duplicatas pagas — ajusta o número da nota, aplica máscara de CNPJ e organiza valores — sem comparação.

Novos perfis podem ser **criados, editados, duplicados e excluídos** pelo usuário, e ficam disponíveis para reuso.

---

## 11. Arquivos aceitos e restrições

- Formatos aceitos: **Excel (.xlsx)** e **CSV (.csv)**.
- O formato **antigo .xls não é aceito**; o usuário é orientado a salvar o arquivo como .xlsx antes de usar.

---

## 12. Validações antes da execução

- O perfil precisa ter um **nome** (sem caracteres inválidos para nome de arquivo) e ao menos **um campo** configurado por planilha.
- Antes de processar, o sistema verifica se **todas as colunas configuradas existem** no arquivo selecionado; se uma coluna estiver fora do alcance da planilha, a execução é interrompida com uma mensagem clara.
- No modo Dual, **ambas as planilhas** precisam ser fornecidas.

---

## 13. Pré-visualização

Ao configurar um perfil, o usuário pode **pré-visualizar as primeiras linhas** de um arquivo de exemplo, com as colunas numeradas, para identificar com facilidade em qual coluna está cada campo (data, valor, histórico etc.).

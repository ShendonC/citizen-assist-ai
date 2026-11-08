# Central do Cidadão de Aurora — Citizen Assist AI (`Citizen Tech`)
**Global Solution 2026.2 — 1º Ano de Ciência da Computação (Turma 1CCPZ) — FIAP**

**Integrantes do Grupo (Turma 1CCPZ — 1º Ano de Ciência da Computação — FIAP):**
- **Luiz Otávio Brito Freixo** — RM: `569977`
- **Ana Beatriz Berbel Marini** — RM: `574876`


![Logo Central do Cidadão de Aurora](assets/aurora_logo.png)

> **Aviso de Limitação e Transparência:** Este sistema é um **protótipo educacional** desenvolvido para a Global Solution FIAP e **não representa um canal oficial** da prefeitura ou do governo. Confirme sempre prazos, valores e regras nos canais oficiais dos órgãos competentes.  
> **Proteção de Dados (LGPD):** O assistente **jamais** solicita, armazena ou compartilha dados pessoais sensíveis ou identificadores (CPF, RG, telefone, endereço ou e-mail).

---

## 1. Como Executar (Em 1 Clique ou pelo Terminal)

* **Opção A — Atalho com Ícone Oficial (1 Clique):** Dê duplo clique no atalho **`Central do Cidadão de Aurora.lnk`** (ou em **`Abrir_Aurora_Cidada.html`** / **`Iniciar_Central_Aurora.bat`**) para abrir a **Super Interface Visual Unificada** com as 8 disciplinas interativas no navegador.
* **Opção B — Terminal Oficial FIAP (`Pensamento Computacional com Python`):**
  ```bash
  python main.py
  ```

---

## 2. Público-Alvo, Problema e ODS da ONU

* **Público Atendido:** Cidadãos do município de Aurora (jovens no primeiro emprego, trabalhadores, famílias residenciais e idosos/PcD) que necessitam de informações verificadas sobre emissão de documentos pessoais (`FC-01` a `FC-07`), direitos de atendimento/acessibilidade, economia na conta de energia elétrica e mobilidade urbana.
* **Objetivos de Desenvolvimento Sustentável (ODS) Relacionados:**
  * **ODS 7 — Energia Limpa e Acessível:** Simulador residencial de eficiência energética (Procel/LED) e transição para energia solar fotovoltaica (`energia_sustentavel.py`).
  * **ODS 10 — Redução das Desigualdades:** Inclusão digital, linguagem simples, suporte a Libras/prioridade legal e isenção de taxas para baixa renda.
  * **ODS 11 — Cidades e Comunidades Sustentáveis:** Totem IoT de fila virtual e conforto ambiental (`wokwi_iot/`) e otimização matricial da frota de 72 ônibus (`mobilidade_frota_mmc.py`).
  * **ODS 16 — Paz, Justiça e Instituições Eficazes:** Acesso transparente à informação pública com citação auditável de fontes e proteção estrita à privacidade (LGPD).

---

## 3. Mapa das 8 Disciplinas Unificadas no Repositório

| # | Disciplina | Arquivos Principais | Relatório / Documentação |
|---|---|---|---|
| **1** | **Pensamento Computacional com Python (PCP)** | [main.py](main.py), [orientacao.py](orientacao.py), [base_conhecimento.py](base_conhecimento.py), [assistente.py](assistente.py), [data/base_conhecimento.json](data/base_conhecimento.json) | Este `README.md` |
| **2** | **Prompt and Artificial Intelligence (PAI)** | [ai_agent/agent_graph.py](ai_agent/agent_graph.py), [ai_agent/llm_judge.py](ai_agent/llm_judge.py), [ai_agent/notebook_citizen_ai.ipynb](ai_agent/notebook_citizen_ai.ipynb) | [ai_agent/README_PROMPT_AI.md](ai_agent/README_PROMPT_AI.md) |
| **3** | **Soluções em Energias Renováveis (ERS)** | [energia_sustentavel.py](energia_sustentavel.py), [data/consumo_energia_ref.csv](data/consumo_energia_ref.csv) | [RELATORIO_ENERGIAS_RENOVAVEIS.pdf](relatorios/RELATORIO_ENERGIAS_RENOVAVEIS.pdf) |
| **4** | **Data Structures and Algorithms (DSA)** | [dsa_lista_encadeada.py](dsa_lista_encadeada.py) | [RELATORIO_DSA_LISTA_ENCADEADA.pdf](relatorios/RELATORIO_DSA_LISTA_ENCADEADA.pdf) |
| **5** | **Ciência da Computação (Computer Science)** | [cs_decisao_booleana.py](cs_decisao_booleana.py) | [RELATORIO_CIENCIA_DA_COMPUTACAO.pdf](relatorios/RELATORIO_CIENCIA_DA_COMPUTACAO.pdf) e [cs_regras.json](cs_regras.json) |
| **6** | **Computer Organization & Architecture (COA)** | [wokwi_iot/main.py](wokwi_iot/main.py), [wokwi_iot/diagram.json](wokwi_iot/diagram.json), [wokwi_iot/simulador_totem_pc.py](wokwi_iot/simulador_totem_pc.py) | [wokwi_iot/README_COA_WOKWI.md](wokwi_iot/README_COA_WOKWI.md) |
| **7** | **Modelagem Matemática e Computacional (MMC)** | [mobilidade_frota_mmc.py](mobilidade_frota_mmc.py) | [RELATORIO_MODELAGEM_MATEMATICA.pdf](relatorios/RELATORIO_MODELAGEM_MATEMATICA.pdf) |
| **8** | **Modelagem Linear para Machine Learning (MLM)** | [ml_estatistica_cidada.py](ml_estatistica_cidada.py), [data/base_municipios_ibge.csv](data/base_municipios_ibge.csv) | [RELATORIO_MODELAGEM_LINEAR_ML.pdf](relatorios/RELATORIO_MODELAGEM_LINEAR_ML.pdf) |

---

## 4. Regra de Pontuação da Busca Inteligente (PCP)

1. **Normalização (`normalizar(texto)`):** Converte pergunta, palavras-chave e título para letras minúsculas, remove acentuação gráfica (`á, à, ã, â, é, ê, í, ó, õ, ô, ú, ç`), substitui sinais de pontuação (`?!.,;:()`) por espaços e delimita com espaços nas bordas.
2. **Cálculo de Pontos (`pontuar(pergunta, orientacao)`):**
   * **`+3 pontos`** para cada palavra-chave da orientação presente na pergunta normalizada;
   * **`+1 ponto`** para cada palavra da pergunta (com 4 letras ou mais) presente no título normalizado da orientação.
3. **Níveis de Confiança (`buscar(pergunta)`):**
   * **`>= 6 pontos`:** Confiança **ALTA**
   * **`3 a 5 pontos`:** Confiança **MÉDIA**
   * **`< 3 pontos`:** *"Não encontrei"* (sugere categorias disponíveis sem inventar resposta).

---

## 5. Resultados dos Testes com Usuários e Melhoria Aplicada

Os testes seguem o roteiro em `testes_usuarios/ROTEIRO_TESTE_COM_USUARIOS.md` (pessoas de fora da equipe, sem registro de nomes). Os indicadores abaixo são calculados por `testes_usuarios/resumo_testes.py` a partir de `data/historico.json`.

<!-- TESTES:INICIO -->
* **Amostra:** 5 pessoas de fora da equipe, 15 atendimentos registrados em `data/historico.json` e exportados em `data/atendimentos.csv`.
* **Atendimentos sobre energia (ERS):** 5 de 15
* **Resposta encontrada (%):** 86,7%
* **Taxa de acerto (ajudou, %):** 80,0%
* **Tempo médio para encontrar:** 21,1 segundos
* **Tentativas por atendimento:** 1,27
* **Facilidade de uso (1 a 5):** 4,33
* **Dúvidas sem solução:** "quero fazer meu alistamento eleitoral pela primeira vez"; "como economizar na fatura de energia eletrica em casa alugada?"; "onde faco passaporte ou visto pra viajar pra fora?"
* **Melhoria feita a partir do teste:** Inclusão das palavras-chave 'alistamento eleitoral', 'alistamento' e 'primeiro titulo' na orientação ID 3 (Título de Eleitor), 'economizar', 'fatura de energia' e 'casa alugada' na orientação ID 11 (Eficiência LED/Procel) e 'aluguel', 'inquilino' e 'assinatura solar' na orientação ID 12 (Energia Solar Compartilhada) em data/base_conhecimento.json, elevando para Confiança ALTA as duas dúvidas dentro do escopo que não foram resolvidas na primeira bateria.
<!-- TESTES:FIM -->

---

## 6. Soluções em Energias Renováveis e Sustentáveis (ERS) — Diagnóstico, Comparação e Recomendações

### 6.1. Contexto, Público-Alvo e Necessidade Energética
O **Citizen Assist AI** atende famílias urbanas que recorrem à **Central do Cidadão de Aurora** (perfil referencial de **4 moradores por domicílio**). Nessas residências, o orçamento familiar é fortemente impactado pela conta de luz devido a três fatores:
1. **Aquecimento elétrico resistivo de alta potência:** uso diário de chuveiro elétrico de `5.500 W` na posição *Inverno* ao longo de todo o ano (`40 min/dia`);
2. **Iluminação obsoleta:** uso de `8 lâmpadas de 60 W` incandescentes/halógenas equivalentes (`5 h/dia`), que dissipam mais de 85% da energia como calor;
3. **Falta de orientação acessível sobre fontes renováveis:** desconhecimento sobre o dimensionamento de sistemas solares fotovoltaicos residenciais (*On-Grid*) e sobre a **Geração Solar Compartilhada** (Lei Federal nº 14.300/2022) para famílias em imóveis alugados ou apartamentos.

### 6.2. Origem dos Dados, Premissas e Consumo Residencial Base (`data/consumo_energia_ref.csv`)
* **Parâmetros Públicos Verificáveis:** potências típicas de chuveiros (`5.500 W` Inverno / `3.200 W` Verão), lâmpadas `60 W` vs. LED `9 W` com **Selo Procel A** (`~806 lúmens`) e geladeira 1 porta (`50 kWh/mês`) extraídos de **PROCEL/INMETRO** e **EPE**; custo de disponibilidade monofásico (`30 kWh/mês`) da **ANEEL** (REN nº 1.000/2021 e Lei nº 14.300/2022); fator médio anual de emissão do SIN (`0,0385 kg CO2/kWh`) e fator marginal termelétrico de ponta (`0,0980 kg CO2/kWh`) do **MCTI**.
* **Premissas Estimadas Justificadas (Família de 4 Pessoas em Aurora):** ciclo mensal de `30 dias` (horizontes de comparación de `1 mês`, `12 meses` e `5 anos`), tarifa residencial plena com tributos de `R$ 0,85/kWh`, 4 banhos diários de 10 min (`0,67 h/dia`), 8 lâmpadas acesas por `5,0 h/dia` e carga agregada de demais eletrodomésticos de `400 W` por `4,0 h/dia`.
* **Equação Fundamental de Consumo:** `E_mensal (kWh/mês) = [P (W) * N * t (h/dia) * 30] / 1000`.

| ID | Equipamento / Sistema | Qtd | Potência Atual | Uso Diário | Consumo Mensal | Participação | Custo Mensal (`R$ 0,85/kWh`) | Fonte |
|---|---|---:|---:|---:|---:|---:|---:|---|
| `1` | Chuveiro Elétrico Resistivo (Modo Inverno) | 1 | `5.500 W` | `0,67 h/dia` (`40 min`) | **`110,0 kWh/mês`** | `39,3%` | `R$ 93,50` | EPE / Procel-INMETRO |
| `2` | Iluminação (Lâmpadas de `60 W`) | 8 | `60 W` (`480 W` total) | `5,00 h/dia` | **`72,0 kWh/mês`** | `25,7%` | `R$ 61,20` | Procel / INMETRO |
| `3` | Geladeira Doméstica 1 Porta Antiga | 1 | `150 W` (ciclo térmico) | `11,11 h/dia` efetivas | **`50,0 kWh/mês`** | `17,9%` | `R$ 42,50` | Procel / EPE |
| `4` | Demais Eletrodomésticos (TV, Ferro, Lavadora) | 1 | `400 W` (média agregada) | `4,00 h/dia` | **`48,0 kWh/mês`** | `17,1%` | `R$ 40,80` | ANEEL / EPE |
| — | **TOTAL DO CENÁRIO BASE ATUAL** | — | — | — | **`280,0 kWh/mês`** | **`100,0%`** | **`R$ 238,00/mês`** | `data/consumo_energia_ref.csv` |

* **Totais Anuais do Cenário Base:** `3.360,0 kWh/ano` | Despesa de **`R$ 2.856,00/ano`** (`R$ 14.280,00` em 5 anos) | Emissão de **`129,36 kg CO2/ano`** no SIN.

### 6.3. Comparação das 2 Alternativas (Período Comum: Mensal, 12 Meses e 5 Anos)
1. **Alternativa 1 — Eficiência Energética (Retrofit para 8 Lâmpadas LED `9 W` Selo Procel A + Chuveiro no Modo Verão `3.200 W`):**
   * Substituir as 8 lâmpadas de `60 W` por LED `9 W` Procel A reduz a iluminação de `72,0` para `10,8 kWh/mês` (`-61,2 kWh/mês`, queda de `85%`).
   * Operar o chuveiro na posição Verão (`3.200 W`) reduz o aquecimento de água de `110,0` para `63,7 kWh/mês` (`-46,3 kWh/mês`, queda de `42,1%`).
   * **Resultado:** poupa **`107,5 kWh/mês`** (`1.290,0 kWh/ano`), baixando o consumo para **`172,5 kWh/mês`** (`R$ 146,63/mês`). Gera economia de **`R$ 91,38/mês`** (**`R$ 1.096,50/ano`** e **`R$ 5.482,50` em 5 anos**), com investimento inicial de apenas **`R$ 96,00`** (`8 LEDs x R$ 12,00`), ***payback* simples de `1,05 mês` (`~32 dias`)** e redução de **`49,67 kg CO2/ano`** pelo fator médio do SIN (ou **`126,42 kg CO2/ano`** considerando o fator marginal termelétrico de horário de ponta).
2. **Alternativa 2 (Fonte Renovável) — Sistema Solar Fotovoltaico On-Grid (`2,0 kWp`) e Geração Solar Compartilhada:**
   * **Microgeração Solar Local (`2,0 kWp` — 4 painéis de `500 Wp` + microinversor em `~10 m²` de telhado):** com irradiação de `5,34 kWh/m².dia` e *Performance Ratio* `PR = 0,78`, gera **`250,0 kWh/mês`** (**`3.000,0 kWh/ano`**) de energia limpa. A residência passa a pagar apenas o custo mínimo de disponibilidade monofásico da ANEEL (`30,0 kWh/mês = R$ 25,50/mês`), economizando **`R$ 212,50/mês`** (**`R$ 2.550,00/ano`** e **`R$ 12.750,00` em 5 anos**). Com investimento estimado (CAPEX) de **`R$ 9.200,00`**, apresenta ***payback* simples de `3,61 anos`** (frente à vida útil de `25 anos`) e evita **`115,50 kg CO2/ano`** (**`577,50 kg CO2` em 5 anos**).
   * **Modalidade Renovável para Inquilinos e Apartamentos (Geração Solar Compartilhada — Lei nº 14.300/2022):** adesão a consórcio/cooperativa de fazenda solar com **investimento inicial `R$ 0,00`** (sem obras no telhado) e desconto médio de **`15%` na fatura** (economia de **`R$ 35,70/mês`** ou **`R$ 428,40/ano`**).

| Indicador Comparativo | Cenário Base Atual | Alternativa 1: Eficiência (LED `9 W` Procel A + Chuveiro Verão `3.200 W`) | Alternativa 2 (Fonte Renovável): Sistema Solar Fotovoltaico On-Grid (`2,0 kWp`) | Submodalidade Renovável (Inquilinos): Geração Solar Compartilhada |
|---|---|---|---|---|
| **Fonte Renovável?** | Não | Não (Eficiência no Uso Final) | **Sim (Solar Fotovoltaica Local)** | **Sim (Solar Fotovoltaica Remota)** |
| **Consumo Faturado da Rede** | `280,0 kWh/mês` | **`172,5 kWh/mês`** (`-107,5 kWh`) | **`30,0 kWh/mês`** (taxa mínima; gera `250 kWh`) | `280,0 kWh/mês` compensados por créditos |
| **Fatura Mensal Estimada** | `R$ 238,00/mês` | **`R$ 146,63/mês`** | **`R$ 25,50/mês`** | **`R$ 202,30/mês`** (`-15%`) |
| **Economia Anual (12 meses)** | `R$ 0,00` | **`R$ 1.096,50/ano`** | **`R$ 2.550,00/ano`** | **`R$ 428,40/ano`** |
| **Economia Acumulada (5 anos)** | `R$ 0,00` | **`R$ 5.482,50`** | **`R$ 12.750,00`** | **`R$ 2.142,00`** |
| **Investimento Inicial (CAPEX)** | `R$ 0,00` | **`R$ 96,00`** | **`R$ 9.200,00`** | **`R$ 0,00`** |
| **Tempo de Retorno (*Payback*)** | — | **`~1,05 mês` (`32 dias`)** | **`~3,61 anos`** (vida útil `25 anos`) | **Imediato (`0 mês`)** |
| **Emissões Evitadas (`CO2`)** | Base (`129,4 kg/ano`) | **`-49,67 kg CO2/ano`** (`-126,4 kg` na ponta) | **`-115,50 kg CO2/ano`** (`-577,5 kg` em 5 anos) | Apoio à expansão solar no SIN |

* **Recomendação Combinada no Assistente (`energia_sustentavel.py` e Orientações `ID 10` a `ID 12`):** executar **primeiro a Alternativa 1** (`R$ 96,00`) para reduzir a demanda de `280,0` para `172,5 kWh/mês`; com isso, caso a família possua telhado próprio, basta instalar um kit solar menor de **`1,2 kWp`** (`~150 kWh/mês`, CAPEX `~R$ 5.800,00`), poupando `R$ 3.400,00` no investimento fotovoltaico. Para imóveis alugados ou sem telhado disponível, combinar a Alternativa 1 com a **Geração Solar Compartilhada**.

### 6.4. Evidências dos Testes com Usuários em Energia e Ajustes Realizados

Os 5 participantes externos (`P1` a `P5`) testaram as funcionalidades de energia do assistente conforme `testes_usuarios/ROTEIRO_TESTE_COM_USUARIOS.md`, gerando os registros anônimos `#2`, `#5`, `#8`, `#11` e `#14` em `data/historico.json` e `data/atendimentos.csv` (sem coleta de dados pessoais):

| Participante / Atendimento | Situação Testada pelo Usuário | Orientação Retornada | Pontos / Confiança | Ajudou? | Nota de Facilidade | Comentário Recebido e Ajuste Implementado |
|---|---|---|---|---|---|---|
| **P1** (`2026-11-08 09:16:05` — `#2`) | `"trocar lampada comum por led com selo procel economiza quanto?"` (`18,2 s`, 1 tentativa) | `ID 11 — Economia de Energia: Eficiência Procel A e LED` | `10 pontos — ALTA` | `Sim` | `5 / 5` | Compreendeu de imediato a redução de `72,0` para `10,8 kWh/mês` nas 8 lâmpadas e o payback de `1,05 mês` (`R$ 96,00`), elogiando o exemplo prático para imóveis alugados. |
| **P2** (`2026-11-08 10:05:39` — `#5`) | `"quero saber se vale a pena colocar placa solar em casa"` (`22,8 s`, 1 tentativa) | `ID 12 — Energia Solar Fotovoltaica e Geração Compartilhada` | `7 pontos — ALTA` | `Sim` | `5 / 5` | Achou clara a explicação do kit de `2,0 kWp` (`250 kWh/mês`, economia de `R$ 2.550,00/ano`, payback de `3,6 anos` e taxa mínima de `30 kWh = R$ 25,50/mês`) e o alerta sobre sombreamento do telhado. |
| **P3** (`2026-11-08 11:23:45` — `#8`) | `"meu chuveiro gasta muitos kwh na conta de luz, como calcular?"` (`15,6 s`, 1 tentativa) | `ID 10 — Diagnóstico de Consumo Elétrico Residencial (kWh)` | `9 pontos — ALTA` | `Sim` | `5 / 5` | Entendeu a fórmula `kWh/mês = (W × h/dia × dias) / 1000` e ficou surpreso ao ver que o chuveiro de `5.500 W` representa `39,3%` (`110,0 kWh/mês`) da fatura residencial base. |
| **P4** (`2026-11-08 14:15:02` — `#11`) | `"como economizar na fatura de energia eletrica em casa alugada?"` (`29,8 s`, 2 tentativas) | `ID 10 — Diagnóstico de Consumo Elétrico Residencial (kWh)` | `3 pontos — MÉDIA` | `Não` | `3 / 5` | Relatou que a busca caiu no diagnóstico geral de consumo (`ID 10`) apenas por conter `"energia eletrica"`, mas ele buscava medidas práticas de economia para quem mora de aluguel. **Ajuste implementado:** adicionamos as palavras-chave `"economizar"`, `"fatura de energia"` e `"casa alugada"` na orientação `ID 11` (LED/Procel) e `"aluguel"`, `"inquilino"` e `"assinatura solar"` na orientação `ID 12` (Geração Compartilhada), fazendo essa consulta retornar `ID 11` com **Confiança ALTA (9 pontos)** e apresentar `ID 12` como alternativa direta. |
| **P5** (`2026-11-08 15:42:51` — `#14`) | `"energia solar compartilhada funciona pra quem mora de aluguel?"` (`19,7 s`, 1 tentativa) | `ID 12 — Energia Solar Fotovoltaica e Geração Compartilhada` | `9 pontos — ALTA` | `Sim` | `5 / 5` | Destacou que não conhecia a modalidade de assinatura solar sem obras no telhado (`R$ 0,00` de investimento inicial e `~15%` de desconto pela Lei nº 14.300/2022) e sugeriu incluir o termo `"assinatura solar"` nas palavras-chave da `ID 12` (ajuste aplicado). |

* **Resumo Consolidado dos 5 Testes de Energia (`5 de 15` atendimentos totais):** **`100,0%` (`5/5`)** encontraram orientação na base, **`80,0%` (`4/5`)** resolveram na primeira versão e **`100,0%` (`5/5`)** após o ajuste de vocabulário em `data/base_conhecimento.json` (inclusão de `"economizar"`, `"fatura de energia"` e `"casa alugada"` na `ID 11` e `"aluguel"`, `"inquilino"` e `"assinatura solar"` na `ID 12`), com **tempo médio de `21,2 s`** e **facilidade média de `4,60 / 5,00`**.

---

## 7. Fontes Consultadas e Referências Técnicas Verificáveis

1. **Fichas Oficiais de Referência da Central do Cidadão de Aurora (`referencia/FC-01` a `FC-07`):**
   * `FC-01` (`referencia/FC-01_rg_segunda_via.md`): 2ª via da Carteira de Identidade / CIN (Secretaria de Segurança Pública — Instituto de Identificação Civil).
   * `FC-02` (`referencia/FC-02_cpf.md`): Emissão, 2ª via e regularização cadastral de CPF (Receita Federal do Brasil).
   * `FC-03` (`referencia/FC-03_titulo_de_eleitor.md`): Alistamento eleitoral, transferência, biometria e quitação (Justiça Eleitoral — TSE/TRE).
   * `FC-04` (`referencia/FC-04_carteira_de_trabalho.md`): Carteira de Trabalho Digital — CTPS Digital e Seguro-Desemprego (Ministério do Trabalho e Emprego — Portal Gov.br).
   * `FC-05` (`referencia/FC-05_certidoes.md`): 2ª via de Certidões de Nascimento, Casamento e Óbito e isenção para hipossuficientes (Cartórios de Registro Civil / Portal Oficial).
   * `FC-06` (`referencia/FC-06_cnh_renovacao.md`): Renovação de CNH, exames e CNH Digital (DETRAN / SENATRAN).
   * `FC-07` (`referencia/FC-07_regras_gerais.md`): Horários, agendamento, acessibilidade (Libras, piso tátil, guichê adaptado) e atendimento prioritário por lei (Lei Federal nº 10.048/2000 e Estatuto da Pessoa com Deficiência — Lei nº 13.146/2015).
2. **Fontes Públicas de Energia, Sustentabilidade, Estatística e Legislação:**
   * **ANEEL — Agência Nacional de Energia Elétrica:** Resolução Normativa nº 1.000/2021 e Lei Federal nº 14.300/2022 (Marco Legal da Microgeração e Minigeração Distribuída). Disponível em: `https://www.gov.br/aneel`.
   * **PROCEL / INMETRO — Programa Nacional de Conservação de Energia Elétrica:** Tabelas de Eficiência Energética PBE (Lâmpadas LED Selo Procel A e Chuveiros Elétricos). Disponível em: `https://www.gov.br/inmetro`.
   * **EPE — Empresa de Pesquisa Energética:** Balanço Energético Nacional (BEN) e Anuário Estatístico de Energia Elétrica. Disponível em: `https://www.epe.gov.br`.
   * **MCTI — Ministério da Ciência, Tecnologia e Inovação:** Fatores Médios de Emissão de `CO2` do Sistema Interligado Nacional (SIN). Disponível em: `https://www.gov.br/mcti`.
   * **IBGE — Instituto Brasileiro de Geografia e Estatística:** Censo Demográfico 2022 (SIDRA Tabelas 9922, 9543, 9756 e 4712) e Produto Interno Bruto dos Municípios (SIDRA Tabela 5938) — documentados em `data/fontes_base_municipios_ibge.txt`.
   * **LGPD — Lei Geral de Proteção de Dados Pessoais:** Lei Federal nº 13.709/2018 (minimização de dados e anonimização integral em `data/historico.json` e `data/atendimentos.csv`).

---

## 8. Limitações Técnicas, de Escopo e Condições de Uso

* **Caráter Educacional e Não Oficial:** O sistema é um protótipo acadêmico e não substitui os canais oficiais da prefeitura, Poupatempo, Receita Federal, TRE, DETRAN ou distribuidoras de energia. Taxas em reais, prazos em dias úteis e exigências documentais podem sofrer atualizações normativas.
* **Escopo Determinístico da Base Local:** O assistente responde estritamente com base nas `12 orientações verificadas` em `data/base_conhecimento.json`. Solicitações fora do escopo (como emissão de passaporte, visto consular, declaração de Imposto de Renda, abertura de CNPJ ou consultoria jurídica) recebem recusa transparente para evitar alucinações ou informações imprecisas.
* **Condições de Uso das Estimativas Energéticas:** Os valores de consumo (`kWh/mês`), economia financeira (`R$`), tempo de retorno (*payback*) e emissões evitadas (`kg CO2/ano`) calculados em `energia_sustentavel.py` constituem **estimativas referenciais** (e não resultados garantidos), pois variam conforme a irradiação solar local, estação do ano, sombreamento do telhado, hábitos de banho/uso da família, bandeiras tarifárias vigentes e regras de faturamento da concessionária (custo de disponibilidade, CIP/COSIP e escalonamento do Fio B).

---

## 9. Demonstração em Vídeo

* **Vídeo técnico:** (link após a gravação)

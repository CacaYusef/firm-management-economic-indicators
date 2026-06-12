# Práticas de Gestão Empresarial e Indicadores Macroeconômicos

Este projeto realiza uma análise exploratória sobre a relação entre práticas de gestão empresarial e indicadores macroeconômicos em nível nacional. A investigação combina uma base de dados de empresas, com medidas de qualidade de gestão, e uma base de indicadores econômicos do World Bank Data 2025.

O objetivo central é verificar se países com melhores índices médios de gestão empresarial tendem a apresentar melhores indicadores econômicos, como maior PIB per capita, menor taxa de desemprego e menor inflação.

> Importante: os resultados devem ser interpretados como evidências de associação estatística, não como relações causais.

---

## Objetivo do projeto

O trabalho busca responder à seguinte pergunta:

**Países com melhores práticas médias de gestão empresarial apresentam melhores indicadores macroeconômicos?**

Para isso, o projeto constrói um índice médio de gestão por país e ano, integra esse índice com dados macroeconômicos e estima modelos de regressão linear simples.

---

## Bases de dados utilizadas

O projeto utiliza duas bases principais:

### 1. Base de empresas

A base de empresas contém informações sobre práticas de gestão empresarial em diferentes países. A partir dessa base, são construídos indicadores médios de gestão relacionados a diferentes dimensões da administração das firmas.

As principais dimensões utilizadas são:

* `operations`: práticas operacionais;
* `monitor`: práticas de monitoramento;
* `people`: práticas de gestão de pessoas;
* `target`: práticas relacionadas a metas;
* `management`: índice médio geral de gestão.

Essas variáveis são construídas a partir de perguntas e critérios presentes na base original, inspirados na metodologia de mensuração de práticas de gestão empresarial associada à literatura de Bloom e Van Reenen.

### 2. Base macroeconômica

A base macroeconômica foi obtida a partir do World Bank Data 2025 e contém indicadores econômicos por país e ano.

As principais variáveis utilizadas foram:

* `GDP per Capita`: PIB per capita;
* `Unemployment Rate`: taxa de desemprego;
* `Inflation`: inflação;
* `year`: ano;
* `country`: país.

Também foi criada uma classificação dos países por nível de PIB per capita:

* baixo;
* médio;
* alto;
* muito alto.

Essa classificação é utilizada principalmente para destacar grupos de países nos gráficos de regressão.

---

## Metodologia

A metodologia do projeto foi dividida em cinco etapas principais.

### 1. Tratamento e padronização dos dados

Inicialmente, as bases foram importadas e tratadas com `pandas`. Foram realizados procedimentos como:

* ajuste dos nomes das colunas;
* conversão de tipos numéricos;
* padronização dos nomes dos países;
* remoção de colunas duplicadas ou desnecessárias;
* tratamento de valores ausentes;
* criação de variáveis categóricas.

Essa etapa foi necessária para permitir a integração entre a base de empresas e a base macroeconômica.

---

### 2. Construção do índice médio de gestão

A partir da base de empresas, foram construídos indicadores médios para diferentes dimensões da gestão empresarial:

* operações;
* monitoramento;
* pessoas;
* metas;
* índice geral de gestão.

Depois disso, os dados foram agregados no nível país-ano. Ou seja, para cada país e ano, foi calculada a média do índice de gestão das empresas observadas naquele grupo.

A agregação principal gera uma base com a seguinte estrutura:

```text
country | year | management_medio | operations_medio | monitor_medio | people_medio | target_medio | numero_firmas
```

---

### 3. Análise descritiva

A análise descritiva busca entender a distribuição dos índices de gestão entre países.

Foram produzidos gráficos como:

* ranking do índice médio de gestão por país;
* histogramas comparativos entre países;
* boxplots da distribuição do índice de gestão;
* gráficos de dispersão entre gestão média e indicadores macroeconômicos.

Esses gráficos ajudam a visualizar diferenças entre países e a identificar padrões iniciais nos dados.

---

### 4. Integração com indicadores macroeconômicos

Após a construção da base agregada de gestão, os dados foram integrados com a base macroeconômica por meio das variáveis:

```text
country
year
```

O resultado é uma base país-ano contendo, simultaneamente:

* índice médio de gestão;
* PIB per capita;
* taxa de desemprego;
* inflação;
* classificação do país por nível de PIB per capita.

---

### 5. Modelos de regressão linear

Foram estimados modelos de regressão linear simples para avaliar a associação entre o índice médio de gestão e diferentes indicadores macroeconômicos.

A estrutura geral dos modelos é:

```text
Indicador macroeconômico = α + β * management_medio + erro
```

Foram estimados três modelos principais:

### Modelo 1 — Gestão média e PIB per capita

Neste modelo, a variável dependente é o logaritmo do PIB per capita:

```text
log(PIB per capita) = α + β * management_medio + erro
```

O uso do logaritmo permite interpretar o coeficiente de forma aproximada como uma variação percentual associada ao aumento do índice médio de gestão.

### Modelo 2 — Gestão média e desemprego

Neste modelo, a variável dependente é a taxa de desemprego:

```text
Taxa de desemprego = α + β * management_medio + erro
```

O objetivo é verificar se países com maior índice médio de gestão tendem a apresentar menores taxas de desemprego.

### Modelo 3 — Gestão média e inflação

Neste modelo, a variável dependente é a inflação:

```text
Inflação = α + β * management_medio + erro
```

O objetivo é verificar se existe associação entre melhores práticas médias de gestão e menores níveis de inflação.

Em todos os modelos, foram utilizados erros-padrão robustos à heterocedasticidade por meio da opção `cov_type="HC3"` do `statsmodels`.

---

## Visualizações

O projeto utiliza visualizações para apoiar a interpretação dos resultados.

Os principais tipos de gráficos produzidos são:

* gráficos de barras para ranking de países;
* histogramas comparativos da distribuição do índice de gestão;
* boxplots para análise de dispersão;
* gráficos de regressão com linha estimada e intervalo de confiança de 95%;
* destaque visual para o Brasil nos gráficos de regressão.

Os gráficos buscam combinar clareza visual com interpretação econômica, evitando afirmar causalidade onde há apenas associação estatística.

---

## Estrutura do repositório

A estrutura principal do projeto é:

```text
.
├── dados/
│   ├── Empresas.xlsx
│   └── world_bank_data_2025.csv
│
├── Gráficos/
│   └── gráficos gerados pelo projeto
│
├── codigo_principal.py
├── Codigo_Principal_com_markdown_resultados.ipynb
├── Histogramas.py
├── Regressoes.py
└── README.md
```

### Arquivos principais

* `codigo_principal.py`: script principal do projeto;
* `Codigo_Principal_com_markdown_resultados.ipynb`: versão em Jupyter Notebook, com resultados e interpretações;
* `Histogramas.py`: contém a classe responsável pela geração dos histogramas comparativos;
* `Regressoes.py`: contém as funções de agregação país-ano, estimação dos modelos e geração dos gráficos de regressão;
* `dados/`: pasta com as bases utilizadas;
* `Gráficos/`: pasta destinada ao armazenamento dos gráficos gerados.

---

## Bibliotecas utilizadas

O projeto foi desenvolvido em Python e utiliza as seguintes bibliotecas:

```python
pandas
numpy
matplotlib
scipy
statsmodels
pathlib
```

---

## Como executar o projeto

Para executar o projeto, mantenha os arquivos na mesma estrutura de pastas apresentada acima.

No Jupyter Notebook ou no VS Code, execute o arquivo:

```text
Codigo_Principal_com_markdown_resultados.ipynb
```

Ou, alternativamente, execute o script principal:

```text
codigo_principal.py
```

Os arquivos auxiliares `Histogramas.py` e `Regressoes.py` devem estar na mesma pasta do arquivo principal para que as importações funcionem corretamente.

---

## Resultados esperados

O projeto gera:

* tabelas descritivas por país;
* rankings de índice médio de gestão;
* histogramas comparativos entre países;
* boxplots da distribuição do índice de gestão;
* modelos de regressão para PIB per capita, desemprego e inflação;
* gráficos de associação entre gestão média e indicadores macroeconômicos.

Os resultados permitem observar se há padrões consistentes entre melhores práticas médias de gestão empresarial e melhores indicadores econômicos nacionais.

---

## Limitações

Este projeto possui algumas limitações importantes:

1. A análise é exploratória e não causal.
2. Os modelos estimados são regressões lineares simples.
3. A base de empresas pode não representar perfeitamente todos os setores e firmas de cada país.
4. Diferenças institucionais, educacionais, tecnológicas e históricas entre países não são controladas diretamente.
5. A associação entre gestão empresarial e indicadores macroeconômicos pode refletir fatores estruturais mais amplos.

Portanto, os resultados devem ser interpretados como uma primeira aproximação empírica, e não como prova de que melhores práticas de gestão causam diretamente melhor desempenho macroeconômico.

---

## Conclusão

O projeto fornece uma análise empírica exploratória sobre a relação entre qualidade média da gestão empresarial e indicadores macroeconômicos. A partir da integração entre dados de firmas e dados do World Bank, são construídas medidas agregadas por país e estimados modelos simples de associação estatística.

A principal contribuição do trabalho é mostrar como dados microeconômicos de gestão empresarial podem ser combinados com indicadores macroeconômicos para investigar padrões comparativos entre países.

Os resultados reforçam a importância de práticas gerenciais como possível dimensão associada ao desempenho econômico, embora novas análises com controles adicionais sejam necessárias para avaliar relações causais.

---





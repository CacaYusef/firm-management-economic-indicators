# -*- coding: utf-8 -*-
"""
Created on Sat Apr 25 14:41:11 2026

@author: Cacob
"""
# PASSO 1


import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
import scipy.stats as stats
from Histogramas import ComparadorHistogramas


plt.style.use("ggplot")
plt.rcParams["font.family"] = "monospace"



# PASSO 2 (Setando o python pra funfar com esses dados)


# Código para tornar o diretório da base de dados relativo (Executar em qualquer PC)
try:
    diretorio_base = Path(__file__).resolve().parent # Funciona quando o código está em um arquivo .py
except NameError:
    diretorio_base = Path.cwd() # Funciona quando o código está em um notebook Jupyter

# Caminho relativo até a planilha Empresas.xlsx
caminho_empresas = diretorio_base / "dados" / "Empresas.xlsx"

# Importa a planilha
empresas = pd.read_excel(caminho_empresas)
empresas.info(memory_usage='deep') # examinando o tipo de arquivo de cada coluna
empresas.describe()


# Planilha de empresas sem dados faltantes na coluna "talent6"
# .copy() evita problemas posteriores ao criar novas colunas
empresas = empresas.dropna(subset=["talent6"]).copy()


# PASSO 3

colunas_criterios = {
    "operations": ["lean1", "lean2"],
    "monitor": ["perf1", "perf2", "perf3", "perf4", "perf5"],
    "people": ["talent1", "talent2", "talent3", "talent4", "talent5", "talent6"],
    "target": ["perf6", "perf7", "perf8", "perf9", "perf10"]
}

def médias_colunas(dados, critério):
    return dados[critério].mean(axis=1).round(2)


for nome_criterio, colunas in colunas_criterios.items():
    empresas[nome_criterio] = médias_colunas(empresas, colunas) # loop for para tirar as médias das colunas agrupadas em "colunas_criterios"


empresas["management"] = (empresas[["operations", "monitor", "people", "target"]].mean(axis=1).round(2)) # axis = 1 faz uma média linha a linha

# PASSO 4

colunas_ranking = [
    "country","operations","monitor",
    "people","target","management"
]

médias_por_critério = empresas.loc[:, colunas_ranking].copy()

ranking_países = (médias_por_critério.groupby("country", as_index=True).mean(numeric_only=True).round(2))

ranking_ordenado = ranking_países.sort_values(by="management",ascending=True)


# PASSO 5

plt.figure(figsize=(14, 6))

plt.barh(                      #plot gráfico de barras horizontal
    ranking_ordenado.index,
    ranking_ordenado["management"],
    color="#688dd4",
    height=0.6,
    edgecolor="black"
)

plt.tick_params(axis="y", labelsize=9)
plt.tick_params(axis="x", labelsize=10)

plt.title("Qualidade média da administração por país", fontsize=14, loc="center")
plt.xlabel("Nota média de administração", fontsize=12)

plt.subplots_adjust(left=0.35)
plt.xlim(0, 5)

plt.show()


# PASSO 6 - Criando Histogramas para comparar a distribuição das notas 

separações = np.linspace(1, 5, 26)  # criando intervalos do histrograma de 1 a 5 e repartições que são de 25 pedaços iguais ( n + 1)


def filtrar_empresas_por_pais(tabela, país):
    return tabela.loc[tabela["country"].eq(país), "management"].dropna()


paises_para_comparar = {
    "Brazil": "Brazil",
    "India": "India",
    "Mexico": "Mexico",
    "Great Britain": "Great Britain",
    "United States": "United States"
}

empresas_por_pais = {
    nome_objeto: filtrar_empresas_por_pais(médias_por_critério, nome_pais)
    for nome_objeto, nome_pais in paises_para_comparar.items()
}


brasil_empresas = empresas_por_pais["Brazil"] # filtrando base de dados para cada país
india_empresas = empresas_por_pais["India"]
Mexico_empresas = empresas_por_pais["Mexico"]
Reino_Unido_empresas = empresas_por_pais["Great Britain"]
Estados_Unidos_empresas = empresas_por_pais["United States"]

        
dados_paises = {
    "Brazil": brasil_empresas,
    "India": india_empresas,
    "Mexico": Mexico_empresas,
    "UK": Reino_Unido_empresas,
    "US": Estados_Unidos_empresas
}

cores = {
    "Brazil": "#4C72B0",
    "India": "#DD8452",
    "Mexico": "#55A868",
    "UK": "#8172B3",
    "US": "#C44E52"
}

comparador = ComparadorHistogramas(
    dados_paises=dados_paises,
    cores=cores,
    separacoes=separações,
    pais_base="Brazil"
)

comparacoes = [
    "India",
    "Mexico",
    "UK",
    "US"
]

comparador.plotar_grade(comparacoes)


# PASSO 8 BOX PLOT <- Para scatter plot precisei do amigo chat

fig, ax = plt.subplots(figsize=(8, 6))


labels = list(dados_paises.keys()) # pegando as chaves do dicionario países para definir as legendas
dados = list(dados_paises.values()) # pegando os valores do dicionario países
posicoes = np.arange(1, len(labels) + 1) # posicionando cada boxplot baseado na ordem do dicionario países

boxplot = ax.boxplot(dados, labels=labels, patch_artist=True, widths=0.5,
    flierprops=dict(
        marker='*',
        markersize=2,
        markerfacecolor='black',
        markeredgecolor='black'
    )
)

for caixa, mediana, pais in zip(boxplot["boxes"], boxplot["medians"], labels):
    cor = cores[pais]

    caixa.set_facecolor(cor)
    caixa.set_edgecolor("black")
    caixa.set_alpha(0.35)

    mediana.set_color(cor)
    mediana.set_alpha(1)
    mediana.set_linewidth(2.5)

for posicao, pais in zip(posicoes, labels):
    valores = dados_paises[pais]

    jitter = np.random.normal(loc=posicao, scale=0.05, size=len(valores))

    ax.scatter(jitter, valores, color=cores[pais],
        alpha=0.10, 
        s=20, 
        edgecolor="black", 
        linewidth=0.3, 
        zorder=3)

ax.set_title("Distribuição das notas de administração por país", fontsize=12)
ax.set_ylabel("Nota média de administração")
ax.set_ylim(1, 5)

ax.grid(axis="y", alpha=0.3)

plt.show()


# Passo 9 Medindo a confiabilidade dos Dados


paises = [
    "Brazil",
    "United States",
    "Great Britain",
    "India",
    "Mexico"
]

dados_confianca = médias_por_critério[
    médias_por_critério["country"].isin(paises)
][["country", "management"]].dropna()

tabela_confianca = (
    dados_confianca
    .groupby("country")["management"]
    .agg(
        media="mean",
        desvio_padrao="std",
        numero_firmas="count"
    )
    .reset_index()
)

tabela_confianca["erro_padrao"] = (tabela_confianca["desvio_padrao"] / np.sqrt(tabela_confianca["numero_firmas"]))

tabela_confianca["t_critico"] = stats.t.ppf(0.975,df=tabela_confianca["numero_firmas"] - 1)

tabela_confianca["margem_erro_95"] = (tabela_confianca["t_critico"] * tabela_confianca["erro_padrao"])

tabela_confianca["limite_inferior_95"] = (tabela_confianca["media"] - tabela_confianca["margem_erro_95"])

tabela_confianca["limite_superior_95"] = (tabela_confianca["media"] + tabela_confianca["margem_erro_95"])

tabela_confianca = tabela_confianca.round(3)

tabela_confianca


# passo 10 Vendo se há diferenças de eficiencia de gestão dada diferentes niveis de competitividade
# e diferentes tipos de "onwers" da empresa


def tabela_condicional(dados, grupo, variavel):
    tabela = (
        dados
        .groupby(["country", grupo])[variavel]
        .agg(
            media="mean",
            desvio_padrao="std",
            numero_firmas="count"
        )
        .reset_index()
    )

    tabela["erro_padrao"] = (tabela["desvio_padrao"] / np.sqrt(tabela["numero_firmas"]))

    tabela["t_critico"] = stats.t.ppf(0.975,df=tabela["numero_firmas"] - 1)

    tabela["margem_erro_95"] = (tabela["t_critico"] * tabela["erro_padrao"])

    tabela["limite_inferior_95"] = (tabela["media"] - tabela["margem_erro_95"])

    tabela["limite_superior_95"] = (tabela["media"] + tabela["margem_erro_95"])

    return tabela.round(3)


dados_ownership = empresas.loc[
    empresas["country"].isin(paises),
    ["country", "ownership", "management"]
].dropna()


tabela_management_ownership = tabela_condicional(
    dados_ownership,
    grupo="ownership",
    variavel="management"
)


dados_competition = empresas.loc[
    empresas["country"].isin(paises),
    ["country", "competition", "management"]
].dropna()


tabela_management_competition = tabela_condicional(
    dados_competition,
    grupo="competition",
    variavel="management"
)






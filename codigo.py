# -*- coding: utf-8 -*-
"""
Created on Sat Apr 25 14:41:11 2026

@author: Cacob
"""
# PASSO 1


import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
import math
import scipy.stats as stats
from matplotlib.ticker import PercentFormatter

plt.style.use("ggplot")
plt.rcParams["font.family"] = "monospace"



# PASSO 2 (Setando o python pra funfar com esses dados)


# Código para tornar o diretório da base de dados relativo (Executar em qualquer PC)
diretorio_base = Path(__file__).resolve().parent

# Caminho relativo até a planilha Empresas.xlsx
caminho_empresas = diretorio_base / "dados" / "Empresas.xlsx"

# Importa a planilha
empresas = pd.read_excel(caminho_empresas)
empresas.info(memory_usage = 'deep') # examinando o tipo de arquivo de cada coluna
empresas.describe()

# Planilha de empresas sem dados faltantes na coluna "talent6"
empresas = empresas.dropna(subset=['talent6'])



# PASSO 3 (Criando as colunas: operations, monitor, people & target. Colunas essas que serão uma média dos critérios semelhantes entre as várias colunas
# o objetivo aqui é filtrar todos os caras que são parecidos, e guardar em uma unica coluna para cada critéria, que será a média geral)


coluna_operations = ["lean1", "lean2"]

coluna_monitor = ["perf1", "perf2", "perf3", "perf4", "perf5"]

coluna_people = ["talent1", "talent2", "talent3", "talent4", "talent5", "talent6"]

coluna_target = ["perf6", "perf7", "perf8", "perf9", "perf10"]


def médias_colunas(dados, critério):    # <- criando função para tirar média das colunas 
    return dados[critério].mean(axis=1).round(2) # <- o mean axis = 1 faz o python tirar a média linha por linha

empresas["operations"] = médias_colunas(empresas, coluna_operations) 
empresas['monitor'] = médias_colunas(empresas, coluna_monitor)  
empresas['people'] = médias_colunas(empresas, coluna_people) 
empresas['target'] = médias_colunas(empresas, coluna_target)
empresas["management"] = empresas[["operations", "monitor", "people", "target"]].mean(axis=1).round(2)




# PASSO 4 (preparando tabela para rankear os países de acordo com cada critério)


médias_por_critério = empresas[["country", "operations", "monitor", "people", "target", "management" ]]

ranking_países = médias_por_critério.groupby("country").mean(numeric_only=True).round(2)

ranking_ordenado = ranking_países.sort_values(by=["management"], ascending = True)


# PASSO 5 (Plotando os valores dos países em um gráfico de colunas)

plt.figure(figsize=(14, 6))

plt.barh(
    ranking_ordenado.index, # categoria utilizada para a plotagem do gráfico (países)
    ranking_ordenado["management"], # critério utilizado no rankeamento
    color="#688dd4", # cor do gráfico ¯\_(ツ)_/¯
    height=0.6, 
    edgecolor="black"
)

# Ajustando o tamanho dos nomes dos países
plt.tick_params(axis="y", labelsize=9)

# Ajusta os números no eixo x
plt.tick_params(axis="x", labelsize=10)

# Título e rótulo do eixo x
plt.title("Qualidade média da administração por país", fontsize=14, loc = "center")
plt.xlabel("Nota média de administração", fontsize=12)

# Deixa espaço à esquerda para os nomes dos países
plt.subplots_adjust(left=0.35)

# nota de administração das empresas, indo numa escala de 0 a 5
plt.xlim(0, 5)

plt.show()


# Passo 6 Comparando as notas das empresas do Brasil, com a outros países

separações = np.linspace(1, 5, 26) # Definindo que o histograma vai de 1 a 5 dividido em 25 pedaçinhos ( intervalos de 0.2 em 0.2)


def filtrar_empresas_por_pais(dados, país):
    return dados[dados["country"] == país]["management"].dropna()

# Pegando a média das empresas de cada país, e transformando num vetor
brasil_empresas = filtrar_empresas_por_pais(médias_por_critério, "Brazil") # Vendo a distribuição de management quando country == Brazil
india_empresas = filtrar_empresas_por_pais(médias_por_critério, "India") # Vendo a distribuição de management quando country == India
Mexico_empresas = filtrar_empresas_por_pais(médias_por_critério, "Mexico") # Vendo a distribuição de management quando country == Mexico
Reino_Unido_empresas = filtrar_empresas_por_pais(médias_por_critério, "Great Britain")
Estados_Unidos_empresas = filtrar_empresas_por_pais(médias_por_critério, "United States")


# A partir daqui, vou transformar o número de empresas vistas em frequencia relativa, mas por que disso?
# Bom, não faria sentido eu dizer que o Brasil é melhor que a Índia em um cenário em que o 
# Brasil tenha 100 empresas e a Índia só 10, supondo hipotéticamente que ambos os países tenham todas as
# Empresas com notas identicas. Logo, por frequencia, fica mais claro ver no gráfico que ambos seriam equivalentes

def calcular_pesos(dados):
    return np.ones(len(dados)) / len(dados) # fração 1/n empresas <- peso para cada empresa no gráfico

pesos_brasil = calcular_pesos(brasil_empresas) 
pesos_india = calcular_pesos(india_empresas)
pesos_Mexico = calcular_pesos(Mexico_empresas)
pesos_Reino_Unido = calcular_pesos(Reino_Unido_empresas)
pesos_Estados_Unidos = calcular_pesos(Estados_Unidos_empresas)


fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2,2) # Quebrando o plot em 4 pedaços para 4 gráficos diferentes 


#comparação das empresas Brasil X India em um histograma
plt.subplots_adjust(hspace=0.50, wspace=0.25)

ax1.hist(brasil_empresas, 
         bins=separações, 
         weights=pesos_brasil,
         alpha=0.8,
         label="Brazil",
         color="#6cc47c",
         edgecolor="black")

ax1.hist(india_empresas,
         bins=separações,
         weights=pesos_india, 
         alpha=0.6, 
         label="India",color="#d65a31",edgecolor="black")

legenda_plot1 = ax1.legend(loc="upper right", fontsize=6)
ax1.set_title("Distribuição proporcional das empresas\npor nota Brasil x Índia", fontsize=7.5)
ax1.tick_params(axis="y", labelsize=6)

ax1.tick_params(axis="x", labelsize=6)
ax1.set_xlim(1, 5)
ax1.yaxis.set_major_formatter(PercentFormatter(1.0)) # <- usando pacote que importei para formar em %

#
#

#comparação das empresas Brasil X Mexico em um histograma
ax2.hist(brasil_empresas, 
         bins=separações, 
         weights=pesos_brasil,
         alpha=0.7,
         label="Brazil",
         color="#6cc47c",
         edgecolor="black")

ax2.hist(Mexico_empresas,
         bins=separações,
         weights=pesos_Mexico, 
         alpha=0.5, 
         label="Mexico",
         color="#265425",
         edgecolor="black")

legenda_plot2 = ax2.legend(loc="upper right", fontsize=6)
ax2.set_title("Distribuição proporcional das empresas\npor nota Brasil x Mexico", fontsize=7.5)
ax2.tick_params(axis="y", labelsize=6)

ax2.tick_params(axis="x", labelsize=6)
ax2.set_xlim(1, 5)
ax2.yaxis.set_major_formatter(PercentFormatter(1.0)) 

#
#

#comparação das empresas Brasil X Reino Unido em um histograma
ax3.hist(brasil_empresas, 
         bins=separações, 
         weights=pesos_brasil,
         alpha=0.7,label="Brazil",
         color="#6cc47c",
         edgecolor="black")

ax3.hist(Reino_Unido_empresas,
         bins=separações,
         weights=pesos_Reino_Unido, 
         alpha=0.5, 
         label="UK",
         color="#11149e",
         edgecolor="black")

legenda_plot3 = ax3.legend(loc="upper right", fontsize= 6)
ax3.set_title("Distribuição proporcional das empresas\npor nota Brasil x Reino Unido", fontsize=7.5)
ax3.tick_params(axis="y", labelsize=6)

ax3.tick_params(axis="x", labelsize=6)
ax3.set_xlim(1, 5)
ax3.yaxis.set_major_formatter(PercentFormatter(1.0)) 

#
#

#comparação das empresas Brasil X Estados Unidos em um histograma
ax4.hist(brasil_empresas, 
         bins=separações, 
         weights=pesos_brasil,
         alpha=0.7,
         label="Brazil",
         color="#6cc47c",
         edgecolor="black")

ax4.hist(Estados_Unidos_empresas,
         bins=separações,
         weights=pesos_Estados_Unidos,
         alpha=0.5, 
         label="US",
         color="#0394fc",
         edgecolor="black")

legenda_plot4 = ax4.legend(loc="upper right", fontsize= 6)
ax4.set_title("Distribuição proporcional das empresas\npor nota Brasil x Estados Unidos", fontsize=7.5)
ax4.tick_params(axis="y", labelsize=6)

ax4.tick_params(axis="x", labelsize=6)
ax4.set_xlim(1, 5)
ax4.yaxis.set_major_formatter(PercentFormatter(1.0)) 



# PASSO 8 BOX PLOT <- Para scatter plot precisei do amigo chat

fig, ax = plt.subplots(figsize=(8, 6))

dados_paises = {
    "Brazil": brasil_empresas,
    "US": Estados_Unidos_empresas,
    "UK": Reino_Unido_empresas,
    "India": india_empresas,
    "Mexico": Mexico_empresas
}

cores = {
    "Brazil": "#6cc47c",
    "US": "#0394fc",
    "UK": "#11149e",
    "India": "#d65a31",
    "Mexico": "#265425"
}

labels = list(dados_paises.keys()) # pegando as chaves do dicionario países para definir as legendas
dados = list(dados_paises.values()) # pegando os valores do dicionario países
posicoes = np.arange(1, len(labels) + 1) # posicionando cada boxplot

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

    jitter = np.random.normal(loc=posicao,scale=0.05,size=len(valores))

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

tabela_confianca["erro_padrao"] = (
    tabela_confianca["desvio_padrao"] / np.sqrt(tabela_confianca["numero_firmas"])
)

tabela_confianca["t_critico"] = stats.t.ppf(
    0.975,
    df=tabela_confianca["numero_firmas"] - 1
)

tabela_confianca["margem_erro_95"] = (
    tabela_confianca["t_critico"] * tabela_confianca["erro_padrao"]
)

tabela_confianca["limite_inferior_95"] = (
    tabela_confianca["media"] - tabela_confianca["margem_erro_95"]
)

tabela_confianca["limite_superior_95"] = (
    tabela_confianca["media"] + tabela_confianca["margem_erro_95"]
)

tabela_confianca = tabela_confianca.round(3)

tabela_confianca






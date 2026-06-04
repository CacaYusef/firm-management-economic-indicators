# -*- coding: utf-8 -*-
"""
Created on Tue Jun  2 18:51:01 2026

@author: Lenovo
"""

# ============================================================
# FUNÇÃO 1 - Preparando a base de gestão no nível país-ano
# ============================================================

def preparar_management_pais_ano(medias_por_criterio):
    """
    Esta função recebe a base médias_por_criterio, que ainda está no nível da firma,
    e agrega os dados para o nível país-ano.

    Ou seja, se houver várias empresas do Brasil em 2004, a função calcula a média
    de management dessas empresas e cria uma única linha para Brazil-2004.
    """

    management_pais_ano = (
        medias_por_criterio
        .groupby(["country", "year"], as_index=False)
        .agg(
            management_medio=("management", "mean"),
            operations_medio=("operations", "mean"),
            monitor_medio=("monitor", "mean"),
            people_medio=("people", "mean"),
            target_medio=("target", "mean"),
            desvio_management=("management", "std"),
            numero_firmas=("management", "count")
        )
        .round(3)
    )

    return management_pais_ano


# ============================================================
# FUNÇÃO 2 - Rodando regressão entre management e variável macro
# ============================================================

def rodar_modelo_management_macro(
    dados_management,
    dados_macro,
    coluna_macro,
    nome_modelo,
    titulo_grafico,
    rotulo_y,
    transformar_log=False,
    destacar_brasil=True
):
    """
    Esta função roda uma regressão linear simples entre o índice médio de gestão
    e uma variável macroeconômica escolhida.

    A ideia geral do modelo é:

        variável_macro = intercepto + beta * management_medio + erro

    A função também cria o gráfico de dispersão com:
    - pontos em cinza para os demais países;
    - pontos destacados por nível de PIB per capita;
    - Brasil destacado em vermelho;
    - linha de regressão;
    - intervalo de confiança ao redor da linha.
    """

    # ============================================================
    # Importando pacotes dentro da função
    # ============================================================
    # Estes imports estão aqui dentro porque, no Spyder/Jupyter,
    # houve bug de escopo/importação ao chamar a função a partir de outro arquivo.

    import numpy as np
    import pandas as pd
    import matplotlib.pyplot as plt
    import statsmodels.formula.api as smf


    # ============================================================
    # PASSO 1 - Criando uma cópia da base macroeconômica
    # ============================================================
    # A cópia evita alterar diretamente a base original usada no arquivo principal.

    macro = dados_macro.copy()

    # Remove espaços escondidos nos nomes das colunas
    macro.columns = macro.columns.str.strip()


    # ============================================================
    # PASSO 2 - Padronizando as colunas de ano e país
    # ============================================================
    # O merge será feito usando country e year.
    # Por isso, essas duas colunas precisam estar limpas e compatíveis
    # nas duas bases: gestão e macroeconomia.

    macro["year"] = pd.to_numeric(macro["year"]).astype("Int16")

    macro["country"] = (
        macro["country"]
        .astype(str)
        .str.strip()
    )


    # ============================================================
    # PASSO 3 - Ajustando nomes de países
    # ============================================================
    # Algumas bases usam nomes diferentes para o mesmo país.
    # Aqui, os nomes são ajustados para bater com a base de empresas.

    mapa_paises = {
        "United Kingdom": "Great Britain",
        "UK": "Great Britain",
        "United States of America": "United States",
        "USA": "United States"
    }

    macro["country"] = macro["country"].replace(mapa_paises)


    # ============================================================
    # PASSO 4 - Convertendo a variável macroeconômica para número
    # ============================================================
    # A variável macro é escolhida na chamada da função.
    # Exemplos:
    # - GDP per Capita
    # - Unemployment Rate
    # - Inflation

    macro[coluna_macro] = pd.to_numeric(macro[coluna_macro])


    # ============================================================
    # PASSO 5 - Selecionando apenas as colunas necessárias
    # ============================================================
    # A função precisa apenas de:
    # - país
    # - ano
    # - variável macroeconômica escolhida
    # - nível de PIB per capita para colorir os grupos no gráfico

    macro = macro[
        [
            "country",
            "year",
            coluna_macro,
            "nível_pib_per_capita"
        ]
    ].copy()


    # ============================================================
    # PASSO 6 - Removendo duplicatas país-ano na base macro
    # ============================================================
    # Em tese, a base macro deveria ter apenas uma linha por país e ano.
    # Esse comando evita problema caso exista alguma repetição.

    macro = macro.drop_duplicates(
        subset=["country", "year"],
        keep="first"
    ).copy()


    # ============================================================
    # PASSO 7 - Fazendo o merge entre gestão e macroeconomia
    # ============================================================
    # Aqui juntamos:
    # - dados_management: base de gestão agregada por país-ano
    # - macro: base macroeconômica também no nível país-ano
    #
    # O validate="one_to_one" garante que a junção seja uma linha para uma linha.
    # Se houver duplicatas em country-year, o pandas acusa erro.

    base = dados_management.merge(
        macro,
        on=["country", "year"],
        how="inner",
        validate="one_to_one"
    )


    # ============================================================
    # PASSO 8 - Removendo dados faltantes
    # ============================================================
    # A regressão só pode ser feita com observações que tenham:
    # - management_medio
    # - variável macroeconômica escolhida

    base = base.dropna(
        subset=["management_medio", coluna_macro]
    ).copy()


    # ============================================================
    # PASSO 9 - Criando a variável dependente do modelo
    # ============================================================
    # Se transformar_log=True, a variável macro será usada em log.
    # Isso foi usado no caso do PIB per capita.
    #
    # Se transformar_log=False, a variável entra no modelo em nível.
    # Isso foi usado para desemprego e inflação.

    if transformar_log:
        base[nome_modelo] = np.log(base[coluna_macro])
    else:
        base[nome_modelo] = base[coluna_macro]


    # ============================================================
    # PASSO 10 - Calculando a correlação simples
    # ============================================================
    # Esta correlação mede a associação linear entre:
    # - management_medio
    # - variável macroeconômica escolhida

    correlacao = base["management_medio"].corr(base[nome_modelo])

    print("=" * 70)
    print(f"MODELO: {titulo_grafico}")
    print("=" * 70)
    print(f"Correlação entre management médio e {nome_modelo}: {correlacao:.4f}")
    print(f"Observações usadas: {len(base)}")
    print("Países presentes:")
    print(base["country"].unique())


    # ============================================================
    # PASSO 11 - Estimando a regressão linear simples
    # ============================================================
    # A fórmula estimada é:
    #
    #   variável_macro = intercepto + beta * management_medio + erro
    #
    # O cov_type="HC3" usa erro-padrão robusto à heterocedasticidade.

    formula = f"{nome_modelo} ~ management_medio"

    modelo = smf.ols(
        formula=formula,
        data=base
    ).fit(cov_type="HC3")

    print(modelo.summary())


    # ============================================================
    # PASSO 12 - Selecionando países para destaque no gráfico
    # ============================================================
    # A ideia é não rotular todos os países, porque isso poluiria o gráfico.
    # Então, dentro de cada nível de PIB per capita, são escolhidos países
    # mais próximos da mediana do próprio grupo.

    base_representativa = base.copy()

    base_representativa["dist_mediana_grupo"] = (
        base_representativa
        .groupby("nível_pib_per_capita")["management_medio"]
        .transform(lambda x: np.abs(x - x.median()))
    )


    # ============================================================
    # PASSO 13 - Pegando os países mais representativos de cada grupo
    # ============================================================
    # O .head(2) seleciona dois países por grupo.
    # Esses países serão coloridos e receberão rótulo no gráfico.

    paises_destaque = (
        base_representativa
        .sort_values(["nível_pib_per_capita", "dist_mediana_grupo"])
        .groupby("nível_pib_per_capita", group_keys=False)
        .head(2)
        .copy()
    )


    # ============================================================
    # PASSO 14 - Garantindo destaque para o Brasil
    # ============================================================
    # Independentemente da seleção automática acima,
    # o Brasil será incluído entre os países destacados.

    if destacar_brasil:
        brasil = base[base["country"] == "Brazil"].copy()

        if not brasil.empty:
            paises_destaque = (
                pd.concat([paises_destaque, brasil], axis=0)
                .drop_duplicates(subset=["country", "year"], keep="last")
                .copy()
            )


    # ============================================================
    # PASSO 15 - Separando pontos de fundo e pontos destacados
    # ============================================================
    # base_fundo: países que aparecem em cinza no gráfico.
    # base_colorida: países destacados por nível de PIB per capita.

    base_fundo = base[
        ~base.index.isin(paises_destaque.index)
    ].copy()

    base_colorida = base[
        base.index.isin(paises_destaque.index)
    ].copy()


    # ============================================================
    # PASSO 16 - Definindo paleta de cores do gráfico
    # ============================================================
    # Os grupos de PIB per capita recebem tons diferentes.
    # O Brasil recebe uma cor própria, em vermelho.

    cores_grupos = {
        "baixo": "#bbadff",
        "medio": "#6c5bc2",
        "alto": "#261a66",
        "muito alto": "#0a032b",
        "sem_classificacao": "#999999"
    }

    cor_brasil = "#B22222"


    # ============================================================
    # PASSO 17 - Criando a figura e os eixos do gráfico
    # ============================================================

    fig, ax = plt.subplots(figsize=(8, 6))


    # ============================================================
    # PASSO 18 - Plotando os demais países em cinza
    # ============================================================
    # Estes pontos formam o fundo do gráfico e não recebem rótulo.

    ax.scatter(
        base_fundo["management_medio"],
        base_fundo[nome_modelo],
        color="#B8B8B8",
        alpha=0.70,
        s=34,
        edgecolor="none",
        label="Demais países"
    )


    # ============================================================
    # PASSO 19 - Plotando os países destacados
    # ============================================================
    # Os países destacados são coloridos conforme o nível de PIB per capita.
    # O Brasil é separado dos demais para receber uma cor especial.

    for grupo, dados_grupo in base_colorida.groupby("nível_pib_per_capita"):

        dados_brasil = dados_grupo[dados_grupo["country"] == "Brazil"]
        dados_outros = dados_grupo[dados_grupo["country"] != "Brazil"]

        if not dados_outros.empty:
            ax.scatter(
                dados_outros["management_medio"],
                dados_outros[nome_modelo],
                color=cores_grupos.get(grupo, "#404040"),
                alpha=0.60,
                s=72,
                edgecolor="black",
                linewidth=0.45,
                label=str(grupo)
            )

        if not dados_brasil.empty:
            ax.scatter(
                dados_brasil["management_medio"],
                dados_brasil[nome_modelo],
                color=cor_brasil,
                alpha=0.95,
                s=105,
                edgecolor="black",
                linewidth=0.8,
                label="Brazil"
            )


    # ============================================================
    # PASSO 20 - Criando os valores de x para a linha de regressão
    # ============================================================
    # x_linha cria 100 valores igualmente espaçados entre o menor e o maior
    # valor de management_medio. Esses pontos serão usados para desenhar
    # a linha de regressão de forma contínua.

    x_linha = np.linspace(
        base["management_medio"].min(),
        base["management_medio"].max(),
        100
    )


    # ============================================================
    # PASSO 21 - Calculando previsão e intervalo de confiança
    # ============================================================
    # O modelo calcula o valor previsto de y para cada valor de x_linha.
    # Também são calculados os limites inferior e superior do intervalo
    # de confiança de 95% da média prevista.

    dados_predicao = pd.DataFrame({
        "management_medio": x_linha
    })

    predicao = modelo.get_prediction(dados_predicao).summary_frame(alpha=0.05)

    y_linha = predicao["mean"]
    limite_inferior = predicao["mean_ci_lower"]
    limite_superior = predicao["mean_ci_upper"]


    # ============================================================
    # PASSO 22 - Plotando o intervalo de confiança
    # ============================================================
    # A função fill_between cria o sombreado ao redor da linha de regressão,
    # parecido com o geom_smooth do R.

    ax.fill_between(
        x_linha,
        limite_inferior,
        limite_superior,
        color="black",
        alpha=0.05,
        linewidth=0,
        label="IC 95%"
    )


    # ============================================================
    # PASSO 23 - Plotando a linha de regressão
    # ============================================================

    ax.plot(
        x_linha,
        y_linha,
        color="#262626",
        linestyle="-",
        linewidth=1.15,
        label="Linha de Regressão"
    )


    # ============================================================
    # PASSO 24 - Adicionando rótulos aos países destacados
    # ============================================================
    # Apenas os países destacados recebem nome.
    # O Brasil recebe fonte em vermelho e negrito.

    for _, linha in base_colorida.iterrows():

        if linha["country"] == "Brazil":
            ax.annotate(
                linha["country"],
                xy=(linha["management_medio"], linha[nome_modelo]),
                xytext=(4, 4),
                textcoords="offset points",
                fontsize=7.2,
                fontweight="bold",
                color=cor_brasil
            )
        else:
            ax.annotate(
                linha["country"],
                xy=(linha["management_medio"], linha[nome_modelo]),
                xytext=(4, 4),
                textcoords="offset points",
                fontsize=6.3,
                color="black"
            )


    # ============================================================
    # PASSO 25 - Configurando título, eixos e grade
    # ============================================================

    ax.set_title(titulo_grafico, fontsize=13)
    ax.set_xlabel("Índice médio de gestão", fontsize=11)
    ax.set_ylabel(rotulo_y, fontsize=11)

    ax.grid(
        axis="both",
        linestyle="-",
        linewidth=0.6,
        alpha=0.6
    )


    # ============================================================
    # PASSO 26 - Removendo bordas superiores e laterais
    # ============================================================
    # Isso deixa o gráfico com aparência mais limpa.

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)


    # ============================================================
    # PASSO 27 - Ajustando a legenda
    # ============================================================
    # Como alguns grupos podem aparecer mais de uma vez, removemos duplicatas
    # da legenda usando um dicionário.

    handles, labels = ax.get_legend_handles_labels()
    by_label = dict(zip(labels, handles))

    ax.legend(
        by_label.values(),
        by_label.keys(),
        frameon=False,
        fontsize=8,
        title="Nível de PIB per capita"
    )


    # ============================================================
    # PASSO 28 - Exibindo o gráfico e retornando resultados
    # ============================================================
    # A função retorna:
    # - base: DataFrame final usado na regressão
    # - modelo: resultado estimado pelo statsmodels

    plt.tight_layout()
    plt.show()

    return base, modelo
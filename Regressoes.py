# -*- coding: utf-8 -*-
"""
Created on Tue Jun  2 18:51:01 2026

@author: Lenovo
"""

def preparar_management_pais_ano(medias_por_criterio):
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
    import numpy as np # eu tava tendo bug em que não conseguia usar essa função sem importar os pacotes por dentro dela
    import pandas as pd # não sei a razão desse bug! mas importar dessa forma resolveu
    import matplotlib.pyplot as plt
    import statsmodels.formula.api as smf

    # resto da função continua igual

    """
    Roda regressão linear simples entre management médio e uma variável macroeconômica.

    Parâmetros:
    dados_management: DataFrame agregado no nível país-ano.
    dados_macro: DataFrame macroeconômico.
    coluna_macro: nome da coluna macroeconômica usada como variável dependente.
    nome_modelo: nome interno da variável dependente no modelo.
    titulo_grafico: título do gráfico.
    rotulo_y: rótulo do eixo y.
    transformar_log: se True, aplica log na variável macro.
    destacar_brasil: se True, destaca o Brasil em vermelho.
    """

    # ============================================================
    # Preparando base macro
    # ============================================================

    macro = dados_macro.copy()
    macro.columns = macro.columns.str.strip()

    macro["year"] = pd.to_numeric(macro["year"],).astype("Int16")

    macro["country"] = (macro["country"].astype(str).str.strip())

    mapa_paises = {
        "United Kingdom": "Great Britain",
        "UK": "Great Britain",
        "United States of America": "United States",
        "USA": "United States"
    }

    macro["country"] = macro["country"].replace(mapa_paises)

    macro[coluna_macro] = pd.to_numeric(macro[coluna_macro],)

    macro = macro[["country","year",coluna_macro,"nível_pib_per_capita"]].copy()

    macro = macro.drop_duplicates(
        subset=["country", "year"],
        keep="first"
    ).copy()

    # ============================================================
    # Merge país-ano
    # ============================================================

    base = dados_management.merge(
        macro,
        on=["country", "year"],
        how="inner",
        validate="one_to_one"
    )

    base = base.dropna(
        subset=["management_medio", coluna_macro]
    ).copy()

    # ============================================================
    # Criando variável dependente
    # ============================================================

    if transformar_log:
        base[nome_modelo] = np.log(base[coluna_macro])
    else:
        base[nome_modelo] = base[coluna_macro]

    # ============================================================
    # Correlação
    # ============================================================

    correlacao = base["management_medio"].corr(base[nome_modelo])

    print("=" * 70)
    print(f"MODELO: {titulo_grafico}")
    print("=" * 70)
    print(f"Correlação entre management médio e {nome_modelo}: {correlacao:.4f}")
    print(f"Observações usadas: {len(base)}")
    print("Países presentes:")
    print(base["country"].unique())

    # ============================================================
    # Regressão linear
    # ============================================================

    formula = f"{nome_modelo} ~ management_medio"

    modelo = smf.ols(
        formula=formula,
        data=base
    ).fit(cov_type="HC3")

    print(modelo.summary())

    # ============================================================
    # Selecionando países destacados
    # ============================================================

    base_representativa = base.copy()

    base_representativa["dist_mediana_grupo"] = (
        base_representativa
        .groupby("nível_pib_per_capita")["management_medio"]
        .transform(lambda x: np.abs(x - x.median())) # países que de regressão dada suas respectivas categorias serão os escolhidos
    )

    paises_destaque = (
        base_representativa
        .sort_values(["nível_pib_per_capita", "dist_mediana_grupo"])
        .groupby("nível_pib_per_capita", group_keys=False)
        .head(2)
        .copy()
    )

    if destacar_brasil:
        brasil = base[base["country"] == "Brazil"].copy()

        if not brasil.empty:
            paises_destaque = (
                pd.concat([paises_destaque, brasil], axis=0)
                .drop_duplicates(subset=["country", "year"], keep="last")
                .copy()
            )

    base_fundo = base[
        ~base.index.isin(paises_destaque.index)
    ].copy()

    base_colorida = base[
        base.index.isin(paises_destaque.index)
    ].copy()

    # ============================================================
    # Gráfico
    # ============================================================

    cores_grupos = {
        "baixo": "#bbadff",
        "medio": "#6c5bc2",
        "alto": "#261a66",
        "muito alto": "#0a032b",
        "sem_classificacao": "#999999"
    }

    cor_brasil = "#B22222"

    fig, ax = plt.subplots(figsize=(8, 6))

    # Demais países em cinza
    ax.scatter(
        base_fundo["management_medio"],
        base_fundo[nome_modelo],
        color="#B8B8B8",
        alpha=0.70,
        s=34,
        edgecolor="none",
        label="Demais países"
    )

    # Países destacados por nível de PIB per capita
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

    # intervalos por onde a reta vai passar
    
    x_linha = np.linspace(
        base["management_medio"].min(),
        base["management_medio"].max(),
        100
    )

    # Reta de regressão com intervalo de confiança

    dados_predicao = pd.DataFrame({"management_medio": x_linha})
    predicao = modelo.get_prediction(dados_predicao).summary_frame(alpha=0.05)
    
    y_linha = predicao["mean"]
    limite_inferior = predicao["mean_ci_lower"]
    limite_superior = predicao["mean_ci_upper"]
    
    ax.fill_between(
    x_linha,
    limite_inferior,
    limite_superior,
    color="black",
    alpha=0.05,
    linewidth=0,
    label="IC 95%"
    )
    
    ax.plot(
        x_linha,
        y_linha,
        color="#262626",
        linestyle="-",
        linewidth=1.15,
        label="Linha de Regressão"
    )

    # Rótulos dos países destacados
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

    ax.set_title(titulo_grafico, fontsize=13)
    ax.set_xlabel("Índice médio de gestão", fontsize=11)
    ax.set_ylabel(rotulo_y, fontsize=11)

    ax.grid(
        axis="both",
        linestyle="-",
        linewidth=0.6,
        alpha=0.6
    )

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    handles, labels = ax.get_legend_handles_labels()
    by_label = dict(zip(labels, handles))

    ax.legend(
        by_label.values(),
        by_label.keys(),
        frameon=False,
        fontsize=8,
        title="Nível de PIB per capita"
    )

    plt.tight_layout()
    plt.show()

    return base, modelo
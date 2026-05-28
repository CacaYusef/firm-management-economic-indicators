


import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import PercentFormatter

class ComparadorHistogramas:
    # Classe para comparar a distribuição das notas de management entre países

    def __init__(self, dados_paises, cores, separacoes, pais_base="Brazil"):
        self.dados_paises = dados_paises
        self.cores = cores
        self.separacoes = separacoes
        self.pais_base = pais_base

    def calcular_pesos(self, dados):
        # Cada observação recebe peso 1/n, para o histograma virar frequência relativa
        if len(dados) == 0:
            raise ValueError("A série está vazia. Verifique se o país foi filtrado corretamente.")

        return np.full(len(dados), 1 / len(dados))

    def configurar_eixo(self, ax):
        # Configura aparência dos histogramas
        ax.tick_params(axis="y", labelsize=6)
        ax.tick_params(axis="x", labelsize=6)
        ax.set_xlim(1, 5)
        ax.yaxis.set_major_formatter(PercentFormatter(1.0))
        ax.legend(loc="upper right", fontsize=6)

    def plotar_comparacao(self, ax, pais_comparado, alpha_base=0.7, alpha_comparado=0.5):
        # Busca os dados do país base e do país comparado
        dados_base = self.dados_paises[self.pais_base]
        dados_comparado = self.dados_paises[pais_comparado]

        # A classe calcula os pesos internamente
        pesos_base = self.calcular_pesos(dados_base)
        pesos_comparado = self.calcular_pesos(dados_comparado)

        ax.hist(
            dados_base,
            bins=self.separacoes,
            weights=pesos_base,
            alpha=alpha_base,
            label=self.pais_base,
            color=self.cores[self.pais_base],
            edgecolor="black"
        )

        ax.hist(
            dados_comparado,
            bins=self.separacoes,
            weights=pesos_comparado,
            alpha=alpha_comparado,
            label=pais_comparado,
            color=self.cores[pais_comparado],
            edgecolor="black"
        )

        ax.set_title(
            f"Proporção das empresas\npor nota ({self.pais_base} x {pais_comparado})", #usando f print para não ter trabalho de fazer na mão os titulos
            fontsize=7.5
        )

        self.configurar_eixo(ax)

    def plotar_grade(self, comparacoes):
        # Cria a grade 2x2 de gráficos
        fig, axes = plt.subplots(2, 2)

        # Transforma a matriz 2x2 em uma lista que me permite usar loop for
        axes = axes.flatten()

        fig.subplots_adjust(hspace=0.50, wspace=0.25)

        for ax, pais in zip(axes, comparacoes):
            self.plotar_comparacao(ax, pais)

        plt.show()
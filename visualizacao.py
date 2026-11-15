import numpy as np
import matplotlib.pyplot as plt

def visualizar_codificacao(bits, sinal, nome_codificacao):
    quantidade_bits = min(len(bits), 20)

    if nome_codificacao == "Manchester":
        quantidade_amostras = quantidade_bits * 2
        tempo = np.arange(quantidade_amostras) / 2

    else:
        quantidade_amostras = quantidade_bits
        tempo = np.arange(quantidade_amostras)

    sinal_plot = np.asarray(sinal[:quantidade_amostras])

    plt.figure(figsize=(12, 4))

    plt.step(tempo, sinal_plot, where="post", linewidth=2)

    plt.title(f"Codificação de Linha - {nome_codificacao}")
    plt.xlabel("Tempo (períodos de bit)")
    plt.ylabel("Amplitude")

    plt.yticks([-1, 0, 1])
    plt.ylim(-1.5, 1.5)
    plt.grid(True)

    # Identifica os bits transmitidos
    for i in range(quantidade_bits):
        plt.text(i + 0.5, 1.2, str(bits[i]), ha="center")

    plt.xlim(0, quantidade_bits)
    plt.tight_layout()
    plt.show()


def visualizar_constelacao(
    simbolos_transmitidos,
    simbolos_recebidos,
    nome_modulacao
):

    transmitidos = np.asarray(simbolos_transmitidos)
    recebidos = np.asarray(simbolos_recebidos)

    # Limita a quantidade de pontos para facilitar a visualização
    quantidade = min(len(transmitidos), 1000)

    transmitidos = transmitidos[:quantidade]
    recebidos = recebidos[:quantidade]

    plt.figure(figsize=(7, 7))

    plt.scatter(
        recebidos.real,
        recebidos.imag,
        alpha=0.35,
        s=15,
        label="Recebidos"
    )

    plt.scatter(
        transmitidos.real,
        transmitidos.imag,
        color="red",
        marker="x",
        s=65,
        label="Transmitidos"
    )

    plt.title(f"Constelação - {nome_modulacao}")

    plt.xlabel("Componente em fase (I)")
    plt.ylabel("Componente em quadratura (Q)")

    plt.axhline(0, color="gray", linewidth=0.8)
    plt.axvline(0, color="gray", linewidth=0.8)

    plt.grid(True)
    plt.axis("equal")
    plt.legend()
    plt.tight_layout()
    plt.show()


def visualizar_linha_ruidosa(sinal_original, sinal_recebido, nome_codificacao):
    original = np.asarray(sinal_original)
    recebido = np.asarray(sinal_recebido)

    quantidade = min(len(original), 40)

    tempo = np.arange(quantidade)

    if nome_codificacao == "Manchester":
        tempo = tempo / 2

    plt.figure(figsize=(12, 5))

    plt.step(
        tempo,
        original[:quantidade],
        where="post",
        label="Sinal original",
        linewidth=2
    )

    plt.plot(
        tempo,
        recebido[:quantidade],
        "o--",
        label="Sinal recebido",
        alpha=0.7
    )

    plt.title(f"Codificação {nome_codificacao} - Sinal com Ruído")

    plt.xlabel("Tempo (períodos de bit)")
    plt.ylabel("Amplitude")

    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()

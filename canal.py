import numpy as np
import matplotlib.pyplot as plt
from modulacao import (
    modular_bpsk,
    demodular_bpsk,
    modular_qpsk,
    demodular_qpsk,
    modular_16qam,
    demodular_16qam
)

# Adiciona ruido AWGN
# snr_db: relacao Eb/N0 em decibeis
# bits_por_simbolo: 1 para BPSK, 2 para QPSK e 4 para 16-QAM.
def adicionar_awgn(simbolos, snr_db, bits_por_simbolo, rng=None):
    if bits_por_simbolo <= 0:
        raise ValueError("Quantidade de bits por simbolo invalida.")

    if rng is None:
        rng = np.random.default_rng()

    # Conversao de dB para escala linear
    snr_linear = 10 ** (snr_db / 10)

    # Energia media por simbolo
    energia_simbolo = np.mean(np.abs(simbolos) ** 2)

    # Densidade espectral de ruido
    N0 = energia_simbolo / (bits_por_simbolo * snr_linear)

    # Desvio padrao de cada componente do ruido
    sigma = np.sqrt(N0 / 2)

    # Geracao do ruido gaussiano
    ruido = sigma * (
        rng.normal(size=len(simbolos))
        + 1j * rng.normal(size=len(simbolos))
    )

    # Soma do ruido ao sinal
    sinal_recebido = simbolos + ruido

    return sinal_recebido


# Calculo de BER
def calcular_ber(bits_originais, bits_recebidos):
    if len(bits_originais) != len(bits_recebidos):
        raise ValueError("As sequencias possuem tamanhos diferentes.")

    erros = sum(
        bit_original != bit_recebido
        for bit_original, bit_recebido
        in zip(bits_originais, bits_recebidos)
    )

    ber = erros / len(bits_originais) if bits_originais else 0

    return ber, erros


# Vizualizacao da Costelacao
def plotar_comparacao(simbolos_originais, simbolos_recebidos, nome, snr_db):
    plt.figure(figsize=(8, 6))

    plt.scatter(
        simbolos_originais.real,
        simbolos_originais.imag,
        label="Transmitidos",
        marker="x",
        s=80
    )

    plt.scatter(
        simbolos_recebidos.real,
        simbolos_recebidos.imag,
        label="Recebidos com ruido",
        alpha=0.5,
        s=25
    )

    plt.axhline(0, linewidth=0.8)
    plt.axvline(0, linewidth=0.8)

    plt.title(f"{nome} - Eb/N0 = {snr_db} dB")
    plt.xlabel("Eixo I")
    plt.ylabel("Eixo Q")

    plt.legend()
    plt.grid(True)
    plt.axis("equal")

    plt.show()


# Ruido em rajadas
def adicionar_ruido_em_rajadas(
    simbolos,
    snr_db,
    bits_por_simbolo,
    rng=None,
    probabilidade_rajada = 0.01, # Probabilidade de início de uma rajada em cada símbolo.
    duracao_rajada = 10, # Quantidade de símbolos afetados por cada rajada.
    fator_intensidade = 5 # Multiplicador da intensidade do ruído adicional.
):

    if rng is None:
        rng = np.random.default_rng()

    # Calcula a potência do ruído de fundo
    snr_linear = 10 ** (snr_db / 10)

    energia_simbolo = np.mean(np.abs(simbolos) ** 2)

    N0 = energia_simbolo / (bits_por_simbolo * snr_linear)

    sigma = np.sqrt(N0 / 2)

    # Gera o ruído AWGN de fundo
    ruido = sigma * (
        rng.normal(size=len(simbolos))
        + 1j * rng.normal(size=len(simbolos))
    )

    # Cria uma máscara para identificar as rajadas
    mascara_rajadas = np.zeros(len(simbolos), dtype=bool)

    inicios = np.where(
        rng.random(len(simbolos)) < probabilidade_rajada
    )[0]

    # Marca os intervalos afetados
    for inicio in inicios:
        fim = min(inicio + duracao_rajada, len(simbolos))
        mascara_rajadas[inicio:fim] = True

    # Gera o ruído adicional das rajadas
    ruido_adicional = fator_intensidade * sigma * (
        rng.normal(size=len(simbolos))
        + 1j * rng.normal(size=len(simbolos))
    )

    # Aplica o ruído adicional somente nas rajadas
    ruido[mascara_rajadas] += ruido_adicional[mascara_rajadas]

    # Produz o sinal recebido
    sinal_recebido = simbolos + ruido

    return sinal_recebido, mascara_rajadas


if __name__ == "__main__":
    # Gerador aleatorio reproduzivel
    rng = np.random.default_rng(42)

    # Geracao de 100.000 bits
    bits = rng.integers(0, 2, size=100_000).tolist()

    # SNR de teste
    snr_db = 10

    # TESTE BPSK
    simbolos = modular_bpsk(bits)

    recebidos = adicionar_awgn(simbolos, snr_db, 1, rng)

    bits_recuperados = demodular_bpsk(recebidos)

    ber, erros = calcular_ber(bits, bits_recuperados)

    print("\n--- BPSK ---")
    print("SNR:", snr_db, "dB")
    print("Bits transmitidos:", len(bits))
    print("Erros:", erros)
    print("BER:", ber)

    plotar_comparacao(simbolos[:1000], recebidos[:1000], "BPSK", snr_db)

    # Teste QPSK
    simbolos = modular_qpsk(bits)

    recebidos = adicionar_awgn(simbolos, snr_db, 2, rng)

    bits_recuperados = demodular_qpsk(recebidos)

    ber, erros = calcular_ber(bits, bits_recuperados)

    print("\n--- QPSK ---")
    print("SNR:", snr_db, "dB")
    print("Bits transmitidos:", len(bits))
    print("Erros:", erros)
    print("BER:", ber)

    plotar_comparacao(
        simbolos[:1000],
        recebidos[:1000],
        "QPSK",
        snr_db
    )

    # Teste 16-QAM
    simbolos = modular_16qam(bits)

    recebidos = adicionar_awgn(
        simbolos, snr_db, 4, rng
    )

    bits_recuperados = demodular_16qam(recebidos)

    ber, erros = calcular_ber(bits, bits_recuperados)

    print("\n--- 16-QAM ---")
    print("SNR:", snr_db, "dB")
    print("Bits transmitidos:", len(bits))
    print("Erros:", erros)
    print("BER:", ber)

    plotar_comparacao(
        simbolos[:1000],
        recebidos[:1000],
        "16-QAM",
        snr_db
    )


    # Teste do canal com ruído em rajadas
    rng = np.random.default_rng(42)

    bits = rng.integers(0, 2, 100000).tolist()

    modulacoes = [
        ("BPSK", modular_bpsk, demodular_bpsk, 1),
        ("QPSK", modular_qpsk, demodular_qpsk, 2),
        ("16-QAM", modular_16qam, demodular_16qam, 4)
    ]

    for nome, modular, demodular, bits_por_simbolo in modulacoes:
        simbolos = modular(bits)

        recebidos, mascara = adicionar_ruido_em_rajadas(
            simbolos,
            snr_db=10,
            bits_por_simbolo=bits_por_simbolo,
            rng=rng
        )

        bits_recuperados = demodular(recebidos)

        ber, erros = calcular_ber(bits, bits_recuperados)

        percentual_rajadas = np.mean(mascara) * 100

        print(f"\nModulação: {nome}")
        print(f"Bits transmitidos: {len(bits)}")
        print(f"Bits incorretos: {erros}")
        print(f"BER: {ber:.6f}")
        print(f"Símbolos afetados por rajadas: {percentual_rajadas:.2f}%")

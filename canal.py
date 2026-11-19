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

# Aplica AWGN com SNR por símbolo
def adicionar_awgn(simbolos, snr_db, bits_por_simbolo=None, rng=None):
    if rng is None: rng = np.random.default_rng()

    simbolos = np.asarray(simbolos, dtype=complex)

    if simbolos.size == 0: 
        raise ValueError("A sequência de símbolos está vazia.")

    potencia_sinal = np.mean(np.abs(simbolos) ** 2)

    if potencia_sinal <= 0:
        raise ValueError("A potência do sinal deve ser positiva.")

    snr_linear = 10 ** (snr_db / 10)
    potencia_ruido = potencia_sinal / snr_linear

    # O ruído complexo possui duas componentes independentes:
    # I (real) e Q (imaginária).
    sigma = np.sqrt(potencia_ruido / 2)

    ruido = sigma * (rng.normal(size=simbolos.size) + 1j * rng.normal(size=simbolos.size))

    return simbolos + ruido


# Aplica AWGN de fundo mais ruído adicional em rajadas.
def adicionar_ruido_em_rajadas(
    simbolos,
    snr_db,
    bits_por_simbolo=None,
    rng=None,
    probabilidade_rajada=0.01,
    duracao_rajada=10,
    fator_intensidade=5
):
    
    if rng is None:
        rng = np.random.default_rng()

    simbolos = np.asarray(simbolos, dtype=complex)

    if simbolos.size == 0:
        raise ValueError("A sequência de símbolos está vazia.")

    if not 0 <= probabilidade_rajada <= 1:
        raise ValueError("Probabilidade de rajada inválida.")

    if duracao_rajada < 1:
        raise ValueError("Duração de rajada inválida.")

    if fator_intensidade < 0:
        raise ValueError("Fator de intensidade inválido.")

    potencia_sinal = np.mean(np.abs(simbolos) ** 2)

    if potencia_sinal <= 0:
        raise ValueError("A potência do sinal deve ser positiva.")

    snr_linear = 10 ** (snr_db / 10)
    potencia_ruido = potencia_sinal / snr_linear
    sigma = np.sqrt(potencia_ruido / 2)

    # Ruído AWGN de fundo
    ruido = sigma * (
        rng.normal(size=simbolos.size)
        + 1j * rng.normal(size=simbolos.size)
    )

    # Identificação dos intervalos com rajadas
    mascara = np.zeros(simbolos.size, dtype=bool)

    inicios = np.where(
        rng.random(simbolos.size) < probabilidade_rajada
    )[0]

    for inicio in inicios:
        fim = min(inicio + duracao_rajada, simbolos.size)
        mascara[inicio:fim] = True

    # Ruído adicional durante as rajadas
    ruido_extra = fator_intensidade * sigma * (
        rng.normal(size=simbolos.size)
        + 1j * rng.normal(size=simbolos.size)
    )

    ruido[mascara] += ruido_extra[mascara]

    return simbolos + ruido, mascara


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

    plt.title(f"{nome} - SNR = {snr_db} dB")
    plt.xlabel("Eixo I")
    plt.ylabel("Eixo Q")

    plt.legend()
    plt.grid(True)
    plt.axis("equal")

    plt.show()


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

    recebidos = adicionar_awgn(simbolos, snr_db, 4, rng)

    bits_recuperados = demodular_16qam(recebidos)

    ber, erros = calcular_ber(bits, bits_recuperados)

    print("\n--- 16-QAM ---")
    print("SNR:", snr_db, "dB")
    print("Bits transmitidos:", len(bits))
    print("Erros:", erros)
    print("BER:", ber)

    plotar_comparacao(simbolos[:1000], recebidos[:1000], "16-QAM", snr_db)

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

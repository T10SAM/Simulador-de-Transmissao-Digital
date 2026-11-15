import numpy as np
import matplotlib.pyplot as plt

# Modulacao BPSK
def modular_bpsk(bits):
    if any(bit not in (0, 1) for bit in bits):
        raise ValueError("Os bits devem ser 0 ou 1.")

    # 0 -> -1
    # 1 -> +1
    simbolos = np.array([
        -1 if bit == 0 else 1
        for bit in bits
    ], dtype=complex)

    return simbolos

# Demodulacao BPSK
def demodular_bpsk(simbolos):
    bits = []

    for simbolo in simbolos:
        if simbolo.real >= 0:
            bits.append(1)
        else:
            bits.append(0)

    return bits

# Modulacao QPSK
def modular_qpsk(bits):
    if any(bit not in (0, 1) for bit in bits):
        raise ValueError("Os bits devem ser 0 ou 1.")

    if len(bits) % 2 != 0:
        raise ValueError("QPSK exige quantidade par de bits.")

    simbolos = []

    for i in range(0, len(bits), 2):
        b1 = bits[i]
        b2 = bits[i + 1]

        # Mapeamento Gray
        I = 1 if b1 == 0 else -1
        Q = 1 if b2 == 0 else -1

        simbolo = (I + 1j * Q) / np.sqrt(2)

        simbolos.append(simbolo)

    return np.array(simbolos)

# Demodulacao QPSK
def demodular_qpsk(simbolos):
    bits = []

    for simbolo in simbolos:

        b1 = 0 if simbolo.real >= 0 else 1
        b2 = 0 if simbolo.imag >= 0 else 1

        bits.extend([b1, b2])

    return bits

# Modulacao 16-QAM
def modular_16qam(bits):
    if any(bit not in (0, 1) for bit in bits):
        raise ValueError("Os bits devem ser 0 ou 1.")

    if len(bits) % 4 != 0:
        raise ValueError("16-QAM exige multiplos de 4 bits.")

    # Mapeamento Gray para cada eixo
    mapa = {
        (0, 0): 3,
        (0, 1): 1,
        (1, 1): -1,
        (1, 0): -3
    }

    simbolos = []

    for i in range(0, len(bits), 4):
        grupo_I = (bits[i], bits[i + 1])
        grupo_Q = (bits[i + 2], bits[i + 3])

        I = mapa[grupo_I]
        Q = mapa[grupo_Q]

        # Normalizacao da energia media
        simbolo = (I + 1j * Q) / np.sqrt(10)

        simbolos.append(simbolo)

    return np.array(simbolos)

# Demodulacao 16-QAM
def demodular_16qam(simbolos):
    bits = []

    for simbolo in simbolos:
        I = simbolo.real * np.sqrt(10)
        Q = simbolo.imag * np.sqrt(10)

        # Decisao do eixo I
        if I > 2:
            bits_I = [0, 0]

        elif I > 0:
            bits_I = [0, 1]

        elif I > -2:
            bits_I = [1, 1]

        else:
            bits_I = [1, 0]

        # Decisao do eixo Q
        if Q > 2:
            bits_Q = [0, 0]

        elif Q > 0:
            bits_Q = [0, 1]

        elif Q > -2:
            bits_Q = [1, 1]

        else:
            bits_Q = [1, 0]

        bits.extend(bits_I + bits_Q)

    return bits

# Vizualizacoes das Costelacoes
def plotar_constelacoes():
    # Todos os pontos possiveis de cada modulacao
    bpsk = np.array([-1, 1], dtype=complex)

    qpsk = np.array([
        (I + 1j * Q) / np.sqrt(2)
        for I in [-1, 1]
        for Q in [-1, 1]
    ])

    qam16 = np.array([
        (I + 1j * Q) / np.sqrt(10)
        for I in [-3, -1, 1, 3]
        for Q in [-3, -1, 1, 3]
    ])

    fig, graficos = plt.subplots(1, 3, figsize=(15, 5))

    constelacoes = [
        (bpsk, "BPSK"),
        (qpsk, "QPSK"),
        (qam16, "16-QAM")
    ]

    for ax, (simbolos, nome) in zip(graficos, constelacoes):
        ax.scatter(simbolos.real, simbolos.imag, s=65)

        ax.axhline(0, linewidth=0.8)
        ax.axvline(0, linewidth=0.8)

        ax.set_title(nome)
        ax.set_xlabel("Eixo I")
        ax.set_ylabel("Eixo Q")

        ax.grid(True)
        ax.set_aspect("equal")

    plt.tight_layout()
    plt.show()


# Testagem
if __name__ == "__main__":
    bits = [
        0, 1, 1, 0,
        0, 0, 1, 1,
        1, 0, 0, 1,
        1, 1, 0, 0
    ]

    print("Bits originais:", bits)

    # BPSK
    sinais_bpsk = modular_bpsk(bits)
    bits_bpsk = demodular_bpsk(sinais_bpsk)

    # QPSK
    sinais_qpsk = modular_qpsk(bits)
    bits_qpsk = demodular_qpsk(sinais_qpsk)

    # 16-QAM
    sinais_16qam = modular_16qam(bits)
    bits_16qam = demodular_16qam(sinais_16qam)


    # Resultados

    print("\n--- BPSK ---")
    print("Simbolos:", sinais_bpsk)
    print("Bits recuperados:", bits_bpsk)
    print("Recuperacao correta:", bits == bits_bpsk)

    print("\n--- QPSK ---")
    print("Simbolos:", sinais_qpsk)
    print("Bits recuperados:", bits_qpsk)
    print("Recuperacao correta:", bits == bits_qpsk)

    print("\n--- 16-QAM ---")
    print("Simbolos:", sinais_16qam)
    print("Bits recuperados:", bits_16qam)
    print("Recuperacao correta:", bits == bits_16qam)

    # Quantidade de simbolos utilizados

    print("\n--- COMPARACAO ---")
    print("Bits transmitidos:", len(bits))
    print("Simbolos BPSK:", len(sinais_bpsk))
    print("Simbolos QPSK:", len(sinais_qpsk))
    print("Simbolos 16-QAM:", len(sinais_16qam))

    # Visualizacao
    plotar_constelacoes()

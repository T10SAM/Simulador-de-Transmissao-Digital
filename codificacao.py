import numpy as np
import matplotlib.pyplot as plt

# Codificacao AMI
def codificar_ami(bits):
    sinal = []
    ultimo_nivel = -1

    for bit in bits:
        if bit == 0:
            sinal.append(0)

        elif bit == 1:
            ultimo_nivel *= -1
            sinal.append(ultimo_nivel)

        else:
            raise ValueError("Os bits devem ser 0 ou 1.")

    return np.array(sinal)

# Codificacao Manchester
def codificar_manchester(bits):
    sinal = []
    for bit in bits:
        if bit == 0:
            sinal.extend([-1, 1])

        elif bit == 1:
            sinal.extend([1, -1])

        else:
            raise ValueError("Os bits devem ser 0 ou 1.")

    return np.array(sinal)

# Decodificacao AMI
def decodificar_ami(sinal):
    bits = []

    for nivel in sinal:
        if nivel == 0:
            bits.append(0)
        else:
            bits.append(1)

    return bits

# Decodificacao Manchester
def decodificar_manchester(sinal):
    if len(sinal) % 2 != 0:
        raise ValueError("Sinal Manchester com tamanho invalido.")

    bits = []

    for i in range(0, len(sinal), 2):

        primeiro = sinal[i]
        segundo = sinal[i + 1]

        if primeiro == -1 and segundo == 1:
            bits.append(0)

        elif primeiro == 1 and segundo == -1:
            bits.append(1)

        else:
            raise ValueError("Transicao Manchester invalida.")

    return bits

# Visualizacao dos Sinais
def plotar_sinais(bits, sinal_ami, sinal_manchester):
    fig, graficos = plt.subplots(2, 1, figsize=(12, 7))

    # Grafico AMI
    tempo_ami = np.arange(len(sinal_ami))

    graficos[0].step(
        tempo_ami,
        sinal_ami,
        where="post"
    )

    graficos[0].set_title("Codificacao AMI")
    graficos[0].set_ylabel("Amplitude")
    graficos[0].set_xlabel("Intervalo de bit")
    graficos[0].set_yticks([-1, 0, 1])
    graficos[0].grid(True)

    # Grafico Manchester
    tempo_manchester = np.arange(len(sinal_manchester)) / 2

    graficos[1].step(
        tempo_manchester,
        sinal_manchester,
        where="post"
    )

    graficos[1].set_title("Codificacao Manchester")
    graficos[1].set_ylabel("Amplitude")
    graficos[1].set_xlabel("Intervalo de bit")
    graficos[1].set_yticks([-1, 0, 1])
    graficos[1].set_xticks(np.arange(len(bits) + 1))
    graficos[1].grid(True)

    plt.tight_layout()
    plt.show()

# 0 nível próximo de zero e 1 nível positivo ou negativo
def decodificar_ami_ruidoso(sinal, limiar=0.5):
    bits = []

    for amostra in sinal:
        if abs(amostra) >= limiar:
            bits.append(1)
        else:
            bits.append(0)

    return bits

# Convenção do Manchester
# 0: [-1, +1] e 1: [+1, -1]
def decodificar_manchester_ruidoso(sinal):
    sinal = np.asarray(sinal, dtype=float)

    if len(sinal) % 2 != 0:
        raise ValueError(
            "Manchester exige número par de amostras"
        )

    bits = []

    for i in range(0, len(sinal), 2):
        primeira = sinal[i]
        segunda = sinal[i + 1]

        if primeira - segunda >= 0:
            bits.append(1)
        else:
            bits.append(0)

    return bits


# Testagem
if __name__ == "__main__":
    bits = [1, 0, 1, 1, 0, 0, 1]

    print("Bits originais:", bits)

    # Codificacao
    sinal_ami = codificar_ami(bits)
    sinal_manchester = codificar_manchester(bits)

    print("\nSinal AMI:", sinal_ami)
    print("Sinal Manchester:", sinal_manchester)

    # Decodificacao
    bits_ami = decodificar_ami(sinal_ami)
    bits_manchester = decodificar_manchester(sinal_manchester)

    print("\nBits recuperados AMI:", bits_ami)
    print("Bits recuperados Manchester:", bits_manchester)

    # Validacao
    print("\nAMI recuperou corretamente:", bits == bits_ami)
    print("Manchester recuperou corretamente:", bits == bits_manchester)

    # Visualizacao
    plotar_sinais(bits, sinal_ami, sinal_manchester)

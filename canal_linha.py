import numpy as np

def normalizar_sinal_linha(sinal, nome_codificacao):
    """
    Normaliza a energia média de referência por bit.

    AMI:
        0 -> 0
        1 -> +/-sqrt(2)

    Manchester:
        0 -> [-1, +1]
        1 -> [+1, -1]
    """

    sinal = np.asarray(sinal, dtype=float)

    if nome_codificacao == "AMI":
        return sinal * np.sqrt(2)

    if nome_codificacao == "Manchester":
        return sinal.copy()

    raise ValueError("Codificação de linha inválida")


def aplicar_canal_linha(
    sinal,
    snr_db,
    tipo_canal,
    nome_codificacao,
    rng=None,
    probabilidade_rajada=0.01,
    duracao_rajada=10,
    fator_intensidade=5
):
    """
    Aplica ruído em um sinal de linha.

    SNR = potência média das amostras / variância do ruído.

    As rajadas são definidas em períodos de bit.
    """
    if rng is None:
        rng = np.random.default_rng()

    sinal = np.asarray(sinal, dtype=float)

    if sinal.size == 0:
        raise ValueError("O sinal não pode estar vazio.")

    if nome_codificacao == "AMI":
        amostras_por_bit = 1
    elif nome_codificacao == "Manchester":
        amostras_por_bit = 2
    else:
        raise ValueError("Codificação de linha inválida.")

    if sinal.size % amostras_por_bit != 0:
        raise ValueError("Quantidade inválida de amostras.")

    mascara = np.zeros(sinal.size, dtype=bool)

    if tipo_canal == "ideal":
        return sinal.copy(), mascara

    if tipo_canal not in ("awgn", "rajadas"):
        raise ValueError("Tipo de canal inválido.")

    if not 0 <= probabilidade_rajada <= 1:
        raise ValueError("Probabilidade de rajada inválida.")

    if duracao_rajada < 1:
        raise ValueError("Duração de rajada inválida.")

    if fator_intensidade < 0:
        raise ValueError("Fator de intensidade inválido.")

    # Potência média do sinal discreto
    potencia_sinal = np.mean(sinal ** 2)

    if potencia_sinal <= 0:
        raise ValueError("A potência do sinal deve ser positiva.")

    snr_linear = 10 ** (snr_db / 10)
    potencia_ruido = potencia_sinal / snr_linear
    sigma = np.sqrt(potencia_ruido)

    # Ruído AWGN real
    ruido = rng.normal(
        loc=0,
        scale=sigma,
        size=sinal.size
    )

    if tipo_canal == "rajadas":
        quantidade_bits = sinal.size // amostras_por_bit

        inicios = np.where(
            rng.random(quantidade_bits) < probabilidade_rajada
        )[0]

        for inicio in inicios:
            fim = min(
                inicio + duracao_rajada,
                quantidade_bits
            )

            inicio_amostra = inicio * amostras_por_bit
            fim_amostra = fim * amostras_por_bit

            mascara[inicio_amostra:fim_amostra] = True

        ruido_extra = rng.normal(
            loc=0,
            scale=fator_intensidade * sigma,
            size=sinal.size
        )

        ruido[mascara] += ruido_extra[mascara]

    return sinal + ruido, mascara

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
    eb_n0_db,
    tipo_canal,
    nome_codificacao,
    rng=None,
    probabilidade_rajada=0.01,
    duracao_rajada=10,
    fator_intensidade=5
):
    """
    Aplica canal ideal, AWGN ou AWGN com rajadas.

    eb_n0_db:
        Relação Eb/N0 de referência, em dB.

    duracao_rajada:
        Duração de cada rajada em períodos de bit.

    Retorna:
        sinal_recebido, mascara_rajadas
    """

    if rng is None:
        rng = np.random.default_rng()

    sinal = np.asarray(sinal, dtype=float)

    if nome_codificacao == "AMI":
        amostras_por_bit = 1
        duracao_amostra = 1.0

    elif nome_codificacao == "Manchester":
        amostras_por_bit = 2
        duracao_amostra = 0.5

    else:
        raise ValueError("Codificação inválida")

    if len(sinal) % amostras_por_bit != 0:
        raise ValueError("Quantidade inválida de amostras")

    if tipo_canal == "ideal":
        return sinal.copy(), np.zeros(len(sinal), dtype=bool)

    if tipo_canal not in ("awgn", "rajadas"):
        raise ValueError("Tipo de canal inválido")

    eb_n0_linear = 10 ** (eb_n0_db / 10)

    # Energia por bit de referência
    eb = 1.0
    n0 = eb / eb_n0_linear

    sigma = np.sqrt(n0 / (2 * duracao_amostra))

    ruido = rng.normal(
        0,
        sigma,
        len(sinal)
    )

    mascara = np.zeros(len(sinal), dtype=bool)

    if tipo_canal == "rajadas":

        quantidade_bits = len(sinal) // amostras_por_bit

        # Decide os inícios das rajadas por período de bit
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
            0,
            fator_intensidade * sigma,
            len(sinal)
        )

        ruido[mascara] += ruido_extra[mascara]

    return sinal + ruido, mascara

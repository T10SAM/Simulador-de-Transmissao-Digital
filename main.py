import numpy as np

from dados import texto_para_bits, bits_para_texto, comparar_bits
from canal import (adicionar_awgn, adicionar_ruido_em_rajadas, calcular_ber)
from canal_linha import (normalizar_sinal_linha, aplicar_canal_linha)
from visualizacao import (visualizar_codificacao, visualizar_constelacao, visualizar_linha_ruidosa)

from codificacao import (
    codificar_ami,
    decodificar_ami,
    codificar_manchester,
    decodificar_manchester,
    decodificar_ami_ruidoso,
    decodificar_manchester_ruidoso
)

from modulacao import (
    modular_bpsk,
    demodular_bpsk,
    modular_qpsk,
    demodular_qpsk,
    modular_16qam,
    demodular_16qam
)

def executar_transmissao():

    print("\n====================================")
    print(" SIMULADOR DE TRANSMISSÃO DIGITAL")
    print("====================================")
    print()

    # Mensagem original
    mensagem = input("\nDigite a mensagem: ")

    try:
        bits_originais = texto_para_bits(mensagem)
    except UnicodeEncodeError:
        print("Erro: utilize apenas caracteres ASCII.")
        return

    if not bits_originais:
        print("Erro: a mensagem não pode estar vazia.")
        return

    print(f"\nMensagem original: {mensagem}")
    print(f"Quantidade de bits: {len(bits_originais)}")

    # Codificação de linha
    print("\nEscolha a codificação de linha:")
    print("1 - AMI")
    print("2 - Manchester")

    escolha_codigo = input("Opção: ")

    if escolha_codigo == "1":
        nome_codigo = "AMI"
        sinal_linha = codificar_ami(bits_originais)
        bits_linha = decodificar_ami(sinal_linha)

    elif escolha_codigo == "2":
        nome_codigo = "Manchester"
        sinal_linha = codificar_manchester(bits_originais)
        bits_linha = decodificar_manchester(sinal_linha)

    else:
        print("Codificação inválida.")
        return

    print(f"\nCodificação escolhida: {nome_codigo}")
    print(f"Decodificação de linha correta: {bits_linha == bits_originais}")

    # Modulação digital
    print("\nEscolha a modulação:")
    print("1 - BPSK")
    print("2 - QPSK")
    print("3 - 16-QAM")

    escolha_modulacao = input("Opção: ")

    modulacoes = {
        "1": ("BPSK", modular_bpsk, demodular_bpsk, 1),
        "2": ("QPSK", modular_qpsk, demodular_qpsk, 2),
        "3": ("16-QAM", modular_16qam, demodular_16qam, 4)
    }

    if escolha_modulacao not in modulacoes:
        print("Modulação inválida.")
        return

    nome_mod, modular, demodular, bits_por_simbolo = (
        modulacoes[escolha_modulacao]
    )

    # Escolha do canal
    print("\nEscolha o canal:")
    print("1 - Canal ideal (sem ruído)")
    print("2 - AWGN")
    print("3 - Ruído em rajadas")

    escolha_canal = input("Opção: ")

    if escolha_canal not in ("1", "2", "3"):
        print("Canal inválido.")
        return

    snr_db = None

    if escolha_canal != "1":
        try:
            snr_db = float(input("Digite SNR (dB): "))
        except ValueError:
            print("Valor de SNR inválido.")
            return

        if not np.isfinite(snr_db):
            print("SNR deve ser um número finito.")
            return

    # Transmissor
    simbolos_transmitidos = modular(bits_originais)

    # Canal
    rng = np.random.default_rng()

    if escolha_canal == "1":
        nome_canal = "Ideal"
        simbolos_recebidos = simbolos_transmitidos.copy()

    elif escolha_canal == "2":
        nome_canal = "AWGN"

        simbolos_recebidos = adicionar_awgn(
            simbolos_transmitidos,
            snr_db,
            bits_por_simbolo,
            rng
        )

    else:
        nome_canal = "Ruído em rajadas"

        simbolos_recebidos, mascara = adicionar_ruido_em_rajadas(
            simbolos_transmitidos,
            snr_db,
            bits_por_simbolo,
            rng
        )

    # Receptor
    bits_recebidos = demodular(simbolos_recebidos)

    # Reconstrução da mensagem
    mensagem_recebida = bits_para_texto(bits_recebidos)

    # Métricas
    ber, quantidade_erros = calcular_ber(bits_originais, bits_recebidos)

    posicoes_erros = comparar_bits(bits_originais, bits_recebidos)

    # Transmissão da Banda Base
    tipos_canal = {"1": "ideal", "2": "awgn", "3": "rajadas"}

    tipo_canal_linha = tipos_canal[escolha_canal]

    # Normaliza a energia de referência por bit
    sinal_linha_normalizado = normalizar_sinal_linha(sinal_linha, nome_codigo)

    # Aplica o mesmo modelo dos experimentos
    sinal_linha_recebido, mascara_linha = aplicar_canal_linha(
        sinal=sinal_linha_normalizado,
        snr_db=snr_db if snr_db is not None else 0,
        tipo_canal=tipo_canal_linha,
        nome_codificacao=nome_codigo,
        rng=np.random.default_rng(),
        probabilidade_rajada=0.01,
        duracao_rajada=10,
        fator_intensidade=5
    )

    # Decodificação do sinal recebido
    if nome_codigo == "AMI":
        bits_linha_recebidos = decodificar_ami_ruidoso(sinal_linha_recebido, limiar=np.sqrt(2) / 2)
    else:
        bits_linha_recebidos = decodificar_manchester_ruidoso(sinal_linha_recebido)

    # Calcula os erros da codificação de linha
    ber_linha, erros_linha = calcular_ber(bits_originais, bits_linha_recebidos)

    # Resultados
    print("\n====================================")
    print(" RESULTADOS DA TRANSMISSÃO")
    print("====================================")

    print(f"Codificação de linha: {nome_codigo}")
    print(f"Modulação: {nome_mod}")
    print(f"Canal: {nome_canal}")

    if snr_db is not None:
        print(f"SNR de referência: {snr_db} dB")

    print(f"\nMensagem enviada: {mensagem}")
    print(f"Mensagem recebida: {mensagem_recebida}")

    print(f"\nBits transmitidos: {len(bits_originais)}")
    print(f"Símbolos transmitidos: {len(simbolos_transmitidos)}")
    print(f"Bits incorretos: {quantidade_erros}")
    print(f"BER: {ber:.8f}")

    print(f"\nPosições dos bits incorretos: {posicoes_erros}")

    if escolha_canal == "3":
        percentual = np.mean(mascara) * 100
        print(f"Símbolos em rajadas: {percentual:.2f}%")

    if quantidade_erros == 0:
        print("\nTransmissão realizada sem erros!")
    else:
        print("\nTransmissão realizada com erros.")

    print("\n--- CODIFICAÇÃO DE LINHA ---")
    print(f"Codificação: {nome_codigo}")
    print(f"Bits incorretos: {erros_linha}")
    print(f"BER da codificação de linha: {ber_linha:.8f}")
    
    print("\n--- MODULAÇÃO DIGITAL ---")
    print(f"Modulação: {nome_mod}")
    print(f"Bits incorretos: {quantidade_erros}")
    print(f"BER da modulação: {ber:.8f}")
    
    # Visualização da transmissão
    print("\nDeseja visualizar os sinais?")
    print("1 - Sim")
    print("2 - Não")

    escolha_visualizacao = input("Opção: ")

    if escolha_visualizacao == "1":
        visualizar_codificacao(bits_originais, sinal_linha, nome_codigo)
        visualizar_constelacao(simbolos_transmitidos, simbolos_recebidos, nome_mod)
        visualizar_linha_ruidosa(sinal_linha_normalizado, sinal_linha_recebido, nome_codigo)

if __name__ == "__main__":
    while True:
        executar_transmissao()

        continuar = input("\nRealizar outra transmissão? (s/n): ")

        if continuar.strip().lower() != "s":
            print("\nSimulador encerrado.")
            break

# Digite
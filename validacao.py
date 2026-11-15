import numpy as np
from canal import adicionar_awgn, calcular_ber
from modulacao import (
    modular_bpsk,
    demodular_bpsk,
    modular_qpsk,
    demodular_qpsk,
    modular_16qam,
    demodular_16qam
)

# Configuração do teste
QUANTIDADE_BITS = 100000
SNR_ALTA = 100

rng = np.random.default_rng(42)

# Gera os bits originais
bits = rng.integers(0, 2, QUANTIDADE_BITS).tolist()

MODULACOES = [
    ("BPSK", modular_bpsk, demodular_bpsk, 1),
    ("QPSK", modular_qpsk, demodular_qpsk, 2),
    ("16-QAM", modular_16qam, demodular_16qam, 4)
]

print("================================")
print(" TESTE DE CANAL IDEAL")
print("================================")

for nome, modular, demodular, bits_por_simbolo in MODULACOES:

    # Modulação
    simbolos = modular(bits)

    # Demodulação sem adicionar ruído
    bits_recuperados = demodular(simbolos)

    ber, erros = calcular_ber(bits, bits_recuperados)

    print(f"\nModulação: {nome}")
    print(f"Bits transmitidos: {len(bits)}")
    print(f"Bits incorretos: {erros}")
    print(f"BER: {ber:.8f}")
    print(f"Recuperação correta: {bits == bits_recuperados}")


print("\n================================")
print(" TESTE AWGN COM SNR DE 100 dB")
print("================================")

for nome, modular, demodular, bits_por_simbolo in MODULACOES:

    # Modulação
    simbolos = modular(bits)

    # Adiciona ruído AWGN muito pequeno
    recebidos = adicionar_awgn(
        simbolos,
        SNR_ALTA,
        bits_por_simbolo,
        rng
    )

    # Demodulação
    bits_recuperados = demodular(recebidos)

    ber, erros = calcular_ber(bits, bits_recuperados)

    print(f"\nModulação: {nome}")
    print(f"SNR: {SNR_ALTA} dB")
    print(f"Bits incorretos: {erros}")
    print(f"BER: {ber:.8f}")
    print(f"Recuperação correta: {bits == bits_recuperados}")

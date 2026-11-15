
def texto_para_bits(mensagem):
    bits = []

    for byte in mensagem.encode("ascii"):
        binario = format(byte, "08b")
        bits.extend(int(bit) for bit in binario)

    return bits

def bits_para_texto(bits):
    if len(bits) % 8 != 0:
        raise ValueError("Quantidade de bits deve ser múltipla de 8")

    bytes_recebidos = bytearray()

    for i in range(0, len(bits), 8):
        grupo = bits[i:i + 8]
        valor = int("".join(map(str, grupo)), 2)
        bytes_recebidos.append(valor)

    return bytes_recebidos.decode("ascii", errors="replace")

def comparar_bits(bits_originais, bits_recebidos):
    if len(bits_originais) != len(bits_recebidos):
        raise ValueError("Sequências com tamanhos diferentes")

    return [
        i for i, (original, recebido)
        in enumerate(zip(bits_originais, bits_recebidos))
        if original != recebido
    ]

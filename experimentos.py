import csv
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt

from canal import (adicionar_awgn, adicionar_ruido_em_rajadas, calcular_ber)
from canal_linha import (normalizar_sinal_linha, aplicar_canal_linha)

from codificacao import (
    codificar_ami,
    codificar_manchester,
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

# CONFIGURAÇÕES
QUANTIDADE_BITS = 100000
REPETICOES = 5
VALORES_SNR = [0, 2, 4, 6, 8, 10, 12, 14]

SEMENTE_BASE = 2026

PROB_RAJADA = 0.01
DURACAO_RAJADA = 10
FATOR_INTENSIDADE = 5

PASTA_RESULTADOS = Path("resultados")
PASTA_RESULTADOS.mkdir(exist_ok=True)

CODIFICACOES = [
    ("AMI", codificar_ami, decodificar_ami_ruidoso),
    ("Manchester", codificar_manchester, decodificar_manchester_ruidoso)
]

MODULACOES = [
    ("BPSK", modular_bpsk, demodular_bpsk, 1),
    ("QPSK", modular_qpsk, demodular_qpsk, 2),
    ("16-QAM", modular_16qam, demodular_16qam, 4)
]

CANAIS = ["AWGN", "Rajadas"]

# Canal de linha normalizado
def decodificar_linha(sinal, nome):
    if nome == "AMI":
        return decodificar_ami_ruidoso(sinal, limiar=np.sqrt(2) / 2)

    return decodificar_manchester_ruidoso(sinal)


# Execução dos Experimentos
def executar_experimentos():
    registros = []

    for tipo in ["Linha", "Modulacao"]:
        if tipo == "Linha":
            metodos = CODIFICACOES
        else:
            metodos = MODULACOES

        for indice_metodo, metodo in enumerate(metodos):
            nome = metodo[0]
            print(f"\nIniciando: {tipo} - {nome}")

            for indice_snr, snr in enumerate(VALORES_SNR):
                for repeticao in range(REPETICOES):
                    # Mesmo conjunto de bits entre métodos, em cada SNR e repetição.
                    semente_bits = (SEMENTE_BASE + indice_snr * 100 + repeticao)

                    rng_bits = np.random.default_rng(semente_bits)

                    bits = rng_bits.integers(0, 2, QUANTIDADE_BITS).tolist()

                    if tipo == "Linha":
                            _, codificar, _ = metodo
                            sinal_original = codificar(bits)
                            sinal = normalizar_sinal_linha(sinal_original, nome)
                    else:
                        _, modular, _, k = metodo
                        sinal = modular(bits)

                    for indice_canal, canal in enumerate(CANAIS):
                        # Sementes independentes para cada combinação de método e canal.
                        semente_ruido = (
                            SEMENTE_BASE
                            + indice_snr * 100000
                            + repeticao * 10000
                            + indice_metodo * 1000
                            + indice_canal * 100
                            + (0 if tipo == "Linha" else 5000000)
                        )

                        rng_ruido = np.random.default_rng(semente_ruido)

                        if tipo == "Linha":
                            recebido, mascara = aplicar_canal_linha(
                                sinal=sinal,
                                snr_db=snr,
                                tipo_canal=canal.lower(),
                                nome_codificacao=nome,
                                rng=rng_ruido,
                                probabilidade_rajada=PROB_RAJADA,
                                duracao_rajada=DURACAO_RAJADA,
                                fator_intensidade=FATOR_INTENSIDADE
                            )
                            bits_recebidos = decodificar_linha(recebido,nome)

                        else:
                            if canal == "AWGN":
                                recebido = adicionar_awgn(sinal, snr, k, rng_ruido)

                            else:
                                recebido, _ = adicionar_ruido_em_rajadas(
                                    sinal,
                                    snr,
                                    k,
                                    rng_ruido,
                                    probabilidade_rajada=PROB_RAJADA,
                                    duracao_rajada=DURACAO_RAJADA,
                                    fator_intensidade=FATOR_INTENSIDADE
                                )

                            bits_recebidos = metodo[2](recebido)

                        ber, erros = calcular_ber(bits, bits_recebidos)

                        registros.append({
                            "tipo": tipo,
                            "metodo": nome,
                            "canal": canal,
                            "snr_db": snr,
                            "repeticao": repeticao + 1,
                            "bits": QUANTIDADE_BITS,
                            "erros": erros,
                            "ber": float(ber)
                        })

                # Exibe a média das cinco repetições
                for canal in CANAIS:
                    valores = [
                        r["ber"] for r in registros
                        if r["tipo"] == tipo
                        and r["metodo"] == nome
                        and r["canal"] == canal
                        and r["snr_db"] == snr
                    ]

                    print(
                        f"{nome:10s} | "
                        f"{canal:7s} | "
                        f"Eb/N0={snr:2d} dB | "
                        f"BER={np.mean(valores):.6f}"
                    )

    return registros


# Cálculo das Estatísticas
def calcular_estatisticas(registros):
    estatisticas = []

    for tipo in ["Linha", "Modulacao"]:
        metodos = (
            CODIFICACOES if tipo == "Linha"
            else MODULACOES
        )

        for metodo in metodos:
            nome = metodo[0]

            for canal in CANAIS:
                for snr in VALORES_SNR:
                    valores = np.array([
                        r["ber"] for r in registros
                        if r["tipo"] == tipo
                        and r["metodo"] == nome
                        and r["canal"] == canal
                        and r["snr_db"] == snr
                    ])

                    estatisticas.append({
                        "tipo": tipo,
                        "metodo": nome,
                        "canal": canal,
                        "snr_db": snr,
                        "ber_media": float(np.mean(valores)),
                        "desvio_padrao": float(
                            np.std(valores, ddof=1)
                        )
                    })

    return estatisticas


# Exportação dos resultados
def salvar_csv(caminho, registros):
    with open(caminho, "w", newline="", encoding="utf-8") as arquivo:
        escritor = csv.DictWriter(arquivo,fieldnames=list(registros[0].keys()))
        escritor.writeheader()
        escritor.writerows(registros)

# Eficiência espectral nominal e compromisso BER
def calcular_eficiencia_espectral():
    # Valores nominais idealizados; não medem largura de banda efetiva.
    return [
        {
            "modulacao": nome,
            "bits_por_simbolo": k,
            "eficiencia_espectral_bit_s_Hz": k
        }
        for nome, _, _, k in MODULACOES
    ]


def calcular_compromisso_ber_eficiencia(estatisticas):
    # Associa a BER média/desvio de cada canal e SNR à eficiência nominal.
    eficiencia_por_modulacao = {
        item["modulacao"]: item
        for item in calcular_eficiencia_espectral()
    }

    return [
        {
            "modulacao": registro["metodo"],
            "canal": registro["canal"],
            "snr_db": registro["snr_db"],
            "bits_por_simbolo": eficiencia_por_modulacao[registro["metodo"]]["bits_por_simbolo"],
            "eficiencia_espectral_bit_s_Hz": eficiencia_por_modulacao[registro["metodo"]]["eficiencia_espectral_bit_s_Hz"],
            "ber_media": registro["ber_media"],
            "desvio_padrao": registro["desvio_padrao"]
        }
        for registro in estatisticas
        if registro["tipo"] == "Modulacao"
    ]


# Gráficos BER X SNR
def gerar_grafico(estatisticas, tipo, canal):
    plt.figure(figsize=(10, 6))

    metodos = (CODIFICACOES if tipo == "Linha" else MODULACOES)

    for metodo in metodos:
        nome = metodo[0]

        dados = [
            r for r in estatisticas
            if r["tipo"] == tipo
            and r["metodo"] == nome
            and r["canal"] == canal
        ]

        snrs = np.array([r["snr_db"] for r in dados])
        medias = np.array([r["ber_media"] for r in dados])
        desvios = np.array([r["desvio_padrao"] for r in dados])

        # BER zero não pode ser exibida em escala log.
        medias_plot = np.where(medias > 0, medias, np.nan)

        plt.semilogy(snrs, medias_plot, marker="o", label=nome)

        inferiores = medias - desvios
        superiores = medias + desvios

        inferiores = np.where(inferiores > 0, inferiores, np.nan)
        superiores = np.where(superiores > 0, superiores, np.nan)

        plt.fill_between(snrs, inferiores, superiores, alpha=0.2)

    plt.title(f"BER x SNR - {tipo} - {canal}")
    plt.xlabel("SNR de referência (dB)")
    plt.ylabel("BER média")

    plt.grid(True, which="both", alpha=0.4)
    plt.legend()
    plt.tight_layout()

    nome_arquivo = (f"ber_{tipo.lower()}_{canal.lower()}.png")

    plt.savefig(PASTA_RESULTADOS / nome_arquivo, dpi=300)

    plt.close()


# Função Principal
def main():

    print("====================================")
    print(" EXPERIMENTOS COMPLETOS")
    print("====================================")

    registros = executar_experimentos()

    estatisticas = calcular_estatisticas(registros)

    salvar_csv(PASTA_RESULTADOS / "execucoes_detalhadas.csv", registros)
    salvar_csv(PASTA_RESULTADOS / "estatisticas.csv", estatisticas)
    salvar_csv(PASTA_RESULTADOS / "eficiencia_espectral.csv", calcular_eficiencia_espectral())
    salvar_csv(PASTA_RESULTADOS / "ber_vs_eficiencia.csv", calcular_compromisso_ber_eficiencia(estatisticas))

    for tipo in ["Linha", "Modulacao"]:
        for canal in CANAIS:
            gerar_grafico(estatisticas, tipo, canal)

    print("\n====================================")
    print(" EXPERIMENTOS FINALIZADOS")
    print("====================================")

    print(f"Total de execuções: {len(registros)}")
    print("Resultados salvos na pasta resultados/")
    print("Eficiência nominal e tabela BER x eficiência exportadas.")


if __name__ == "__main__":
    main()

"""
Disciplina: Modelagem Matematica e Computacional (MMC)
Global Solution 2026.2 - CitizenTech (FIAP - 1CC)
Projeto: Mobilidade Urbana Inteligente - Gestao da Frota de Onibus de Aurora

Implementa:
- Etapa 1 (Relatorio I): Modelagem matricial A*x = b, analise de unicidade via
  determinante, posto (Teorema de Rouche-Capelli) e matriz inversa, resolucao
  computacional em Python e verificacao dos registros operacionais.
- Etapa 2 (Relatorio II): Analise da demanda de pico, identificacao de deficits
  e superavits, proposicao de politica de redistribuicao via Transformacao
  Linear Estocastica T, demonstracao formal e computacional de conservacao da
  frota (1^T * T = 1^T) e nao-negatividade, e geracao de grafico comparativo.
"""

from __future__ import annotations

from fractions import Fraction
from pathlib import Path
from typing import Any

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


REGIOES: list[str] = ["Norte", "Sul", "Leste", "Oeste"]
SIGLAS: list[str] = ["N", "S", "L", "O"]


def resolver_etapa_1() -> dict[str, Any]:
    """
    Resolve a Etapa 1 (Relatorio I): Recuperacao da distribuicao atual da frota.

    Sistema linear:
      1*N + 1*S + 1*L + 1*O = 72  (Frota disponivel total)
      1*N + 2*S + 0*L + 1*O = 76  (Norte + Oeste + 2*Sul = 76)
      0*N + 1*S + 2*L + 0*O = 52  (Sul + 2*Leste = 52)
      1*N + 0*S + 1*L + 2*O = 76  (Norte + Leste + 2*Oeste = 76)
    """
    A = np.array(
        [
            [1.0, 1.0, 1.0, 1.0],
            [1.0, 2.0, 0.0, 1.0],
            [0.0, 1.0, 2.0, 0.0],
            [1.0, 0.0, 1.0, 2.0],
        ],
        dtype=np.float64,
    )
    b = np.array([72.0, 76.0, 52.0, 76.0], dtype=np.float64)

    det_A = float(np.round(np.linalg.det(A), 6))
    posto_A = int(np.linalg.matrix_rank(A))
    matriz_ampliada = np.column_stack((A, b))
    posto_Ab = int(np.linalg.matrix_rank(matriz_ampliada))
    num_incognitas = A.shape[1]

    A_inv = np.linalg.inv(A)
    A_inv_vezes_3 = np.round(A_inv * 3.0).astype(int)

    x_solve = np.linalg.solve(A, b)
    x_inv = A_inv @ b
    x_atual = np.round(x_solve).astype(int)

    # Verificacao de cada registro operacional do Relatorio I
    b_calculado = A @ x_atual
    residuo_max = float(np.max(np.abs(b_calculado - b)))
    verificacoes = {
        "reg_1_total_frota": {
            "expressao": "N + S + L + O",
            "calculado": int(x_atual[0] + x_atual[1] + x_atual[2] + x_atual[3]),
            "esperado": 72,
            "satisfeito": bool(int(x_atual.sum()) == 72),
        },
        "reg_2_norte_oeste_2sul": {
            "expressao": "N + 2*S + O",
            "calculado": int(x_atual[0] + 2 * x_atual[1] + x_atual[3]),
            "esperado": 76,
            "satisfeito": bool(int(x_atual[0] + 2 * x_atual[1] + x_atual[3]) == 76),
        },
        "reg_3_sul_2leste": {
            "expressao": "S + 2*L",
            "calculado": int(x_atual[1] + 2 * x_atual[2]),
            "esperado": 52,
            "satisfeito": bool(int(x_atual[1] + 2 * x_atual[2]) == 52),
        },
        "reg_4_norte_leste_2oeste": {
            "expressao": "N + L + 2*O",
            "calculado": int(x_atual[0] + x_atual[2] + 2 * x_atual[3]),
            "esperado": 76,
            "satisfeito": bool(int(x_atual[0] + x_atual[2] + 2 * x_atual[3]) == 76),
        },
    }

    inversa_fracoes = [
        [str(Fraction( int(A_inv_vezes_3[i, j]), 3 )) for j in range(4)]
        for i in range(4)
    ]

    return {
        "matriz_A": A.astype(int).tolist(),
        "vetor_b": b.astype(int).tolist(),
        "determinante_A": det_A,
        "posto_A": posto_A,
        "posto_ampliada": posto_Ab,
        "num_incognitas": num_incognitas,
        "classificacao_sistema": "Sistema Possivel e Determinado (SPD) - Solucao Unica",
        "matriz_inversa_A": np.round(A_inv, 6).tolist(),
        "matriz_inversa_fracoes": inversa_fracoes,
        "x_atual": x_atual.tolist(),
        "x_atual_por_regiao": {
            reg: int(val) for reg, val in zip(REGIOES, x_atual)
        },
        "x_via_inversa": np.round(x_inv, 6).tolist(),
        "residuo_maximo": residuo_max,
        "verificacoes": verificacoes,
        "inteiras_e_nao_negativas": bool(
            np.all(x_atual >= 0) and np.allclose(x_solve, x_atual)
        ),
    }


def resolver_etapa_2(x_atual_lista: list[int]) -> dict[str, Any]:
    """
    Resolve a Etapa 2 (Relatorio II): Demanda de pico e Transformacao Linear T
    para redistribuicao da frota preservando o total de 72 onibus.
    """
    x_atual = np.array(x_atual_lista, dtype=np.float64)
    passageiros_pico = np.array([560, 760, 720, 840], dtype=int)
    capacidade_onibus = 40

    x_necessario = (passageiros_pico // capacidade_onibus).astype(int)
    saldo_atual_menos_nec = x_atual.astype(int) - x_necessario
    necessidade_adicional = x_necessario - x_atual.astype(int)

    # Construcao da Matriz de Transformacao Linear Estocastica T (4x4)
    # Coluna 1 (Norte, 12): retem 100% (1)
    # Coluna 2 (Sul, 20): transfere 1/20 para Norte, retem 19/20 em Sul
    # Coluna 3 (Leste, 16): retem 100% (1)
    # Coluna 4 (Oeste, 24): transfere 1/24 para Norte, 2/24 para Leste, retem 21/24 em Oeste
    T = np.array(
        [
            [1.0, 1.0 / 20.0, 0.0, 1.0 / 24.0],
            [0.0, 19.0 / 20.0, 0.0, 0.0],
            [0.0, 0.0, 1.0, 2.0 / 24.0],
            [0.0, 0.0, 0.0, 21.0 / 24.0],
        ],
        dtype=np.float64,
    )

    T_fracoes = [
        ["1", "1/20", "0", "1/24"],
        ["0", "19/20", "0", "0"],
        ["0", "0", "1", "2/24 (1/12)"],
        ["0", "0", "0", "21/24 (7/8)"],
    ]

    x_novo_float = T @ x_atual
    x_novo = np.round(x_novo_float).astype(int)

    # Verificacao de propriedades matematicas (Item 2.f)
    soma_colunas_T = np.sum(T, axis=0)
    preserva_soma_colunas = bool(np.allclose(soma_colunas_T, np.ones(4)))
    todos_t_ij_nao_negativos = bool(np.all(T >= 0.0))
    todos_x_novo_nao_negativos = bool(np.all(x_novo >= 0))
    soma_antes = int(np.sum(x_atual))
    soma_depois = int(np.sum(x_novo))
    atende_100_demanda = bool(np.array_equal(x_novo, x_necessario))

    desequilibrios_detalhados = []
    for i, reg in enumerate(REGIOES):
        atual_i = int(x_atual[i])
        nec_i = int(x_necessario[i])
        saldo_i = int(saldo_atual_menos_nec[i])
        status = (
            f"Deficit de {abs(saldo_i)} onibus (-{abs(saldo_i) * capacidade_onibus} vagas)"
            if saldo_i < 0
            else f"Superavit de +{saldo_i} onibus (+{saldo_i * capacidade_onibus} vagas)"
        )
        desequilibrios_detalhados.append(
            {
                "regiao": reg,
                "passageiros_estimados": int(passageiros_pico[i]),
                "capacidade_por_onibus": capacidade_onibus,
                "frota_atual": atual_i,
                "capacidade_atual_vagas": atual_i * capacidade_onibus,
                "frota_necessaria": nec_i,
                "saldo_onibus": saldo_i,
                "diferenca_necessaria": int(necessidade_adicional[i]),
                "diagnostico": status,
                "frota_pos_redistribuicao": int(x_novo[i]),
                "capacidade_pos_vagas": int(x_novo[i] * capacidade_onibus),
            }
        )

    fluxos_transferencia = [
        {
            "origem": "Sul",
            "destino": "Norte",
            "coeficiente_T": "t_12 = 1/20 (5,00%)",
            "onibus_transferidos": 1,
            "justificativa": "Transfere o superavit integral de 1 veiculo do Sul para reduzir o deficit do Norte.",
        },
        {
            "origem": "Oeste",
            "destino": "Norte",
            "coeficiente_T": "t_14 = 1/24 (4,17%)",
            "onibus_transferidos": 1,
            "justificativa": "Complementa +1 veiculo no Norte, atingindo exatamente os 14 onibus necessarios (560 passageiros).",
        },
        {
            "origem": "Oeste",
            "destino": "Leste",
            "coeficiente_T": "t_34 = 2/24 = 1/12 (8,33%)",
            "onibus_transferidos": 2,
            "justificativa": "Transfere os 2 veiculos excedentes restantes do Oeste para zerar o deficit do Leste (18 onibus / 720 passageiros).",
        },
    ]

    return {
        "passageiros_pico": passageiros_pico.tolist(),
        "capacidade_onibus": capacidade_onibus,
        "total_passageiros": int(passageiros_pico.sum()),
        "x_necessario": x_necessario.tolist(),
        "saldo_atual_menos_necessario": saldo_atual_menos_nec.tolist(),
        "necessidade_adicional": necessidade_adicional.tolist(),
        "matriz_T_decimal": np.round(T, 6).tolist(),
        "matriz_T_fracoes": T_fracoes,
        "x_novo": x_novo.tolist(),
        "x_novo_por_regiao": {
            reg: int(val) for reg, val in zip(REGIOES, x_novo)
        },
        "soma_colunas_T": np.round(soma_colunas_T, 6).tolist(),
        "preserva_total_estocastica": preserva_soma_colunas,
        "todos_coeficientes_nao_negativos": todos_t_ij_nao_negativos,
        "alocacoes_finais_nao_negativas": todos_x_novo_nao_negativos,
        "soma_frota_antes": soma_antes,
        "soma_frota_depois": soma_depois,
        "atende_100_porcento_demanda": atende_100_demanda,
        "desequilibrios_por_regiao": desequilibrios_detalhados,
        "fluxos_transferencia": fluxos_transferencia,
    }


def gerar_grafico_mmc(
    etapa1: dict[str, Any],
    etapa2: dict[str, Any],
    caminho_saida: Path,
) -> None:
    """
    Gera visualizacao comparativa da frota Antes vs. Depois da Transformacao
    Linear T e o mapa de calor da matriz estocastica de redistribuicao.
    """
    caminho_saida.parent.mkdir(parents=True, exist_ok=True)

    x_atual = np.array(etapa1["x_atual"])
    x_novo = np.array(etapa2["x_novo"])
    saldos = np.array(etapa2["saldo_atual_menos_necessario"])
    T = np.array(etapa2["matriz_T_decimal"])

    plt.rcParams.update(
        {
            "font.family": "sans-serif",
            "font.size": 10,
            "axes.titlesize": 12,
            "axes.titleweight": "bold",
        }
    )

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6), dpi=160)
    fig.suptitle(
        "Modelagem Matemática e Computacional (MMC) — Gestão da Frota de 72 Ônibus de Aurora",
        fontsize=14,
        fontweight="bold",
        y=0.98,
    )

    # Subplot 1: Comparativo Antes vs. Depois por Regiao
    indices = np.arange(len(REGIOES))
    largura = 0.36

    barras_antes = ax1.bar(
        indices - largura / 2,
        x_atual,
        largura,
        label="Frota Atual Recuperada (x_atual)",
        color="#3b82f6",
        edgecolor="#1d4ed8",
        linewidth=1.2,
    )
    barras_depois = ax1.bar(
        indices + largura / 2,
        x_novo,
        largura,
        label="Frota Redistribuída (x_novo = T · x_atual = Demanda Pico)",
        color="#10b981",
        edgecolor="#047857",
        linewidth=1.2,
    )

    for barra in barras_antes:
        altura = int(barra.get_height())
        ax1.annotate(
            f"{altura}",
            xy=(barra.get_x() + barra.get_width() / 2, altura),
            xytext=(0, 4),
            textcoords="offset points",
            ha="center",
            va="bottom",
            fontsize=9.5,
            fontweight="bold",
            color="#1e3a8a",
        )

    for idx, barra in enumerate(barras_depois):
        altura = int(barra.get_height())
        delta = -saldos[idx]
        sinal = f"+{delta}" if delta > 0 else f"{delta}"
        ax1.annotate(
            f"{altura} ({sinal})",
            xy=(barra.get_x() + barra.get_width() / 2, altura),
            xytext=(0, 4),
            textcoords="offset points",
            ha="center",
            va="bottom",
            fontsize=9.5,
            fontweight="bold",
            color="#065f46",
        )

    ax1.set_title("Etapa 1 vs. Etapa 2: Equilíbrio entre Frota e Demanda de Pico")
    ax1.set_xlabel("Centros Operacionais Regionais")
    ax1.set_ylabel("Quantidade de Ônibus Alocados (Unidades)")
    ax1.set_xticks(indices)
    ax1.set_xticklabels(
        [f"{r}\n({p} pass.)" for r, p in zip(REGIOES, etapa2["passageiros_pico"])]
    )
    ax1.set_ylim(0, 29)
    ax1.grid(axis="y", linestyle="--", alpha=0.35)
    ax1.legend(loc="upper left", frameon=True)

    # Subplot 2: Matriz de Transformacao Linear Estocastica T
    im = ax2.imshow(T, cmap="YlGnBu", vmin=0.0, vmax=1.0)
    ax2.set_title("Matriz Associada T (Transformação Linear Estocástica)")
    ax2.set_xlabel("Região de Origem j (Frota Atual)")
    ax2.set_ylabel("Região de Destino i (Frota Nova)")
    ax2.set_xticks(range(4))
    ax2.set_yticks(range(4))
    ax2.set_xticklabels(REGIOES)
    ax2.set_yticklabels(REGIOES)

    fracoes_curtas = [
        ["1\n(100%)", "1/20\n(5,0%)", "0\n(0%)", "1/24\n(4,2%)"],
        ["0\n(0%)", "19/20\n(95,0%)", "0\n(0%)", "0\n(0%)"],
        ["0\n(0%)", "0\n(0%)", "1\n(100%)", "2/24\n(8,3%)"],
        ["0\n(0%)", "0\n(0%)", "0\n(0%)", "21/24\n(87,5%)"],
    ]

    for i in range(4):
        for j in range(4):
            cor_texto = "white" if T[i, j] > 0.55 else "#0f172a"
            ax2.text(
                j,
                i,
                fracoes_curtas[i][j],
                ha="center",
                va="center",
                color=cor_texto,
                fontsize=9.5,
                fontweight="bold",
            )

    cbar = fig.colorbar(im, ax=ax2, fraction=0.046, pad=0.04)
    cbar.set_label("Proporção de Alocação / Transferência (t_ij)")

    plt.tight_layout(rect=[0, 0.02, 1, 0.94])
    fig.savefig(caminho_saida, dpi=160)
    plt.close(fig)


def executar_pipeline_mmc() -> dict[str, Any]:
    """Executa todas as etapas de MMC, gera o grafico e exibe o relatorio no console."""
    base_dir = Path(__file__).resolve().parent
    caminho_grafico = base_dir / "relatorios" / "graficos_ml" / "mmc_frota_onibus.png"
    caminho_grafico.parent.mkdir(parents=True, exist_ok=True)

    etapa1 = resolver_etapa_1()
    etapa2 = resolver_etapa_2(etapa1["x_atual"])
    gerar_grafico_mmc(etapa1, etapa2, caminho_grafico)

    print("=" * 78)
    print("MODELAGEM MATEMATICA E COMPUTACIONAL (MMC) - GESTAO DE FROTA DE AURORA")
    print("=" * 78)
    print("\n[ETAPA 1 - DIAGNOSTICO E RECUPERACAO DA FROTA ATUAL]")
    print(f"Determinante det(A)         : {etapa1['determinante_A']:.1f} != 0")
    print(f"Posto(A) = Posto([A|b]) = n : {etapa1['posto_A']} = {etapa1['posto_ampliada']} = {etapa1['num_incognitas']}")
    print(f"Classificacao               : {etapa1['classificacao_sistema']}")
    print("Distribuicao Atual Recuperada (x_atual = A^-1 * b):")
    for reg, qtd in etapa1["x_atual_por_regiao"].items():
        print(f"  - Regiao {reg:<6}: {qtd:2d} onibus")
    print(f"  - TOTAL        : {sum(etapa1['x_atual']):2d} onibus")
    print("Verificacao dos Registros Operacionais:")
    for chave, info in etapa1["verificacoes"].items():
        print(
            f"  * {info['expressao']:<15} = {info['calculado']} "
            f"(Esperado: {info['esperado']}) -> OK: {info['satisfeito']}"
        )

    print("\n[ETAPA 2 - DEMANDA DE PICO E POLITICA DE REDISTRIBUICAO LINEAR]")
    for item in etapa2["desequilibrios_por_regiao"]:
        print(
            f"  - {item['regiao']:<6}: Passageiros={item['passageiros_estimados']:3d} | "
            f"Atual={item['frota_atual']:2d} | Necessario={item['frota_necessaria']:2d} | "
            f"{item['diagnostico']} -> Novo={item['frota_pos_redistribuicao']:2d}"
        )
    print(f"Soma das colunas de T       : {etapa2['soma_colunas_T']} (1^T * T = 1^T: {etapa2['preserva_total_estocastica']})")
    print(f"Frota Total Antes vs Depois : {etapa2['soma_frota_antes']} -> {etapa2['soma_frota_depois']} onibus")
    print(f"Grafico salvo em            : {caminho_grafico}")
    print("=" * 78)

    return {
        "etapa_1": etapa1,
        "etapa_2": etapa2,
        "grafico_path": str(caminho_grafico.relative_to(base_dir)).replace("\\", "/"),
    }


if __name__ == "__main__":
    executar_pipeline_mmc()

"""Módulo de Soluções em Energias Renováveis e Sustentáveis (ERS) — Citizen Assist AI.

Realiza o diagnóstico de consumo elétrico residencial (kWh) para famílias atendidas
pela Central do Cidadão de Aurora e compara tecnicamente duas alternativas:
1. Alternativa 1 (Eficiência Energética): Retrofit com 8 lâmpadas LED 9W (Selo Procel A)
   e operação do chuveiro elétrico no modo Verão (3.200 W).
2. Alternativa 2 (Fonte Renovável): Sistema Solar Fotovoltaico On-Grid de 2,0 kWp
   (geração média de 250,0 kWh/mês) + opção de Geração Solar Compartilhada para
   imóveis alugados ou apartamentos sem área de telhado.
"""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any


TARIFA_PADRAO_BRL_KWH = 0.85
CONSUMO_BASE_PADRAO_KWH_MES = 280.0
CUSTO_DISPONIBILIDADE_MONOFASICO_KWH = 30.0
FATOR_EMISSAO_SIN_KG_CO2_KWH = 0.0385
FATOR_EMISSAO_PONTA_TERMICA_KG_CO2_KWH = 0.0980

INVESTIMENTO_RETROFIT_LED_BRL = 96.00
ECONOMIA_PADRAO_LEDS_KWH_MES = 61.2
ECONOMIA_PADRAO_CHUVEIRO_KWH_MES = 46.3
ECONOMIA_PADRAO_RETROFIT_KWH_MES = 107.5

POTENCIA_SOLAR_PADRAO_KWP = 2.0
GERACAO_SOLAR_PADRAO_KWH_MES = 250.0
INVESTIMENTO_SOLAR_PADRAO_BRL = 9200.00
VIDA_UTIL_PAINEIS_ANOS = 25
DESCONTO_GERACAO_COMPARTILHada_PCT = 15.0


EQUIPAMENTOS_PADRAO: list[dict[str, Any]] = [
    {
        "id_equipamento": 1,
        "equipamento": "Chuveiro Eletrico Resistivo (Modo Inverno -> Modo Verao)",
        "quantidade": 1,
        "potencia_atual_w": 5500.0,
        "horas_uso_dia": 0.6667,
        "dias_mes": 30,
        "consumo_atual_kwh_mes": 110.0,
        "acao_eficiencia": "Ajuste para posicao Verao (3200W) e controle de tempo de banho",
        "potencia_eficiente_w": 3200.0,
        "consumo_eficiente_kwh_mes": 63.7,
        "economia_kwh_mes": 46.3,
        "investimento_retrofit_brl": 0.00,
        "fonte_referencia": "EPE / Procel-INMETRO (2026)",
    },
    {
        "id_equipamento": 2,
        "equipamento": "Iluminacao Residencial (Lampadas 60W -> LED 9W Procel A)",
        "quantidade": 8,
        "potencia_atual_w": 60.0,
        "horas_uso_dia": 5.0,
        "dias_mes": 30,
        "consumo_atual_kwh_mes": 72.0,
        "acao_eficiencia": "Substituicao das 8 lampadas de 60W por LEDs de 9W Selo Procel A",
        "potencia_eficiente_w": 9.0,
        "consumo_eficiente_kwh_mes": 10.8,
        "economia_kwh_mes": 61.2,
        "investimento_retrofit_brl": 96.00,
        "fonte_referencia": "Procel / INMETRO (2026)",
    },
    {
        "id_equipamento": 3,
        "equipamento": "Geladeira Domestica 1 Porta Antiga (Ciclo Termostatico)",
        "quantidade": 1,
        "potencia_atual_w": 150.0,
        "horas_uso_dia": 11.1111,
        "dias_mes": 30,
        "consumo_atual_kwh_mes": 50.0,
        "acao_eficiencia": "Manutencao de borrachas de vedacao e afastamento de fontes de calor",
        "potencia_eficiente_w": 150.0,
        "consumo_eficiente_kwh_mes": 50.0,
        "economia_kwh_mes": 0.0,
        "investimento_retrofit_brl": 0.00,
        "fonte_referencia": "Procel / EPE (2026)",
    },
    {
        "id_equipamento": 4,
        "equipamento": "Demais Eletrodomesticos (TV Ferro Lavadora Carregadores)",
        "quantidade": 1,
        "potencia_atual_w": 400.0,
        "horas_uso_dia": 4.0,
        "dias_mes": 30,
        "consumo_atual_kwh_mes": 48.0,
        "acao_eficiencia": "Desligamento de aparelhos em stand-by e uso acumulado da lavadora",
        "potencia_eficiente_w": 400.0,
        "consumo_eficiente_kwh_mes": 48.0,
        "economia_kwh_mes": 0.0,
        "investimento_retrofit_brl": 0.00,
        "fonte_referencia": "ANEEL / EPE (2026)",
    },
]


REFERENCIAS_VERIFICAVEIS: list[dict[str, str]] = [
    {
        "sigla": "ANEEL",
        "orgao": "Agência Nacional de Energia Elétrica",
        "documento": "Resolução Normativa nº 1.000/2021 e Lei nº 14.300/2022 (Marco Legal da Micro e Minigeração Distribuída)",
        "url": "https://www.gov.br/aneel",
    },
    {
        "sigla": "PROCEL / INMETRO",
        "orgao": "Programa Nacional de Conservação de Energia Elétrica / INMETRO",
        "documento": "Tabelas de Consumo e Eficiência Energética — Iluminação LED e Chuveiros Elétricos (Selo Procel A)",
        "url": "https://www.gov.br/inmetro/pt-br/assuntos/avaliacao-da-conformidade/programa-brasileiro-de-etiquetagem",
    },
    {
        "sigla": "EPE",
        "orgao": "Empresa de Pesquisa Energética — Ministério de Minas e Energia",
        "documento": "Anuário Estatístico de Energia Elétrica e Nota Técnica de Consumo Residencial por Região",
        "url": "https://www.epe.gov.br",
    },
    {
        "sigla": "MCTI",
        "orgao": "Ministério da Ciência, Tecnologia e Inovação",
        "documento": "Fatores Médios de Emissão de CO2 pela Geração Elétrica no Sistema Interligado Nacional (SIN: 0,0385 kg CO2/kWh)",
        "url": "https://www.gov.br/mcti",
    },
]


LIMITACOES_E_CONDICOES: list[str] = [
    "As economias em kWh e R$ são estimativas técnicas baseadas em perfil residencial médio (4 pessoas, 30 dias/mês) e NÃO constituem garantia financeira.",
    "A tarifa residencial varia conforme a concessionária local, alíquotas estaduais de ICMS, PIS/COFINS, CIP/COSIP e acionamento de Bandeiras Tarifárias (Verde, Amarela ou Vermelha).",
    "Na Alternativa 1 (Eficiência Energética), a economia no chuveiro elétrico depende da manutenção do hábito familiar (banhos de até 10 min na posição Verão em dias amenos/quentes).",
    "Na Alternativa 2 (Solar Fotovoltaica On-Grid), a geração real oscila conforme a sazonalidade climática, inclinação, orientação geográfica e ausência de sombreamento no telhado.",
    "A concessionária cobra sempre o custo mínimo de disponibilidade da rede (30 kWh/mês para padrão monofásico, 50 kWh/mês para bifásico e 100 kWh/mês para trifásico), além da regra de transição do Fio B (Lei 14.300/2022).",
    "Para cidadãos que residem em imóveis alugados ou apartamentos sem telhado próprio, a instalação On-Grid física não é viável; nesses casos, recomenda-se a modalidade de Geração Solar Compartilhada por assinatura.",
]


class SimuladorEnergiaSustentavel:
    """Analisa o consumo elétrico residencial e compara alternativas sustentáveis."""

    def __init__(
        self,
        caminho_csv: str = "data/consumo_energia_ref.csv",
        tarifa_kwh: float = TARIFA_PADRAO_BRL_KWH,
    ) -> None:
        self.caminho_csv = str(caminho_csv)
        self.tarifa_kwh = float(tarifa_kwh)
        self.equipamentos: list[dict[str, Any]] = []
        self.carregar_dados_referencia()

    def carregar_dados_referencia(self) -> list[dict[str, Any]]:
        """Carrega os dados de equipamentos do arquivo CSV de referência."""
        caminho = Path(self.caminho_csv)
        if not caminho.exists():
            self.equipamentos = [dict(item) for item in EQUIPAMENTOS_PADRAO]
            return self.equipamentos

        try:
            carregados: list[dict[str, Any]] = []
            with caminho.open("r", encoding="utf-8-sig", newline="") as arquivo:
                leitor = csv.DictReader(arquivo)
                for linha in leitor:
                    carregados.append(
                        {
                            "id_equipamento": int(linha["id_equipamento"]),
                            "equipamento": str(linha["equipamento"]).strip(),
                            "quantidade": int(linha["quantidade"]),
                            "potencia_atual_w": float(linha["potencia_atual_w"]),
                            "horas_uso_dia": float(linha["horas_uso_dia"]),
                            "dias_mes": int(linha["dias_mes"]),
                            "consumo_atual_kwh_mes": float(
                                linha["consumo_atual_kwh_mes"]
                            ),
                            "acao_eficiencia": str(linha["acao_eficiencia"]).strip(),
                            "potencia_eficiente_w": float(
                                linha["potencia_eficiente_w"]
                            ),
                            "consumo_eficiente_kwh_mes": float(
                                linha["consumo_eficiente_kwh_mes"]
                            ),
                            "economia_kwh_mes": float(linha["economia_kwh_mes"]),
                            "investimento_retrofit_brl": float(
                                linha["investimento_retrofit_brl"]
                            ),
                            "fonte_referencia": str(linha["fonte_referencia"]).strip(),
                        }
                    )
            self.equipamentos = carregados if carregados else [
                dict(item) for item in EQUIPAMENTOS_PADRAO
            ]
        except (OSError, KeyError, ValueError):
            self.equipamentos = [dict(item) for item in EQUIPAMENTOS_PADRAO]

        return self.equipamentos

    @staticmethod
    def calcular_consumo_aparelho_kwh(
        potencia_w: float,
        horas_dia: float,
        dias_mes: int = 30,
        quantidade: int = 1,
    ) -> float:
        """Aplica E(kWh) = (Potência(W) * horas/dia * dias * quantidade) / 1000."""
        consumo = (
            float(potencia_w) * float(horas_dia) * int(dias_mes) * int(quantidade)
        ) / 1000.0
        return round(consumo, 2)

    def calcular_comparativo(
        self,
        consumo_kwh_mes: float = CONSUMO_BASE_PADRAO_KWH_MES,
        tarifa_kwh: float | None = None,
    ) -> dict[str, Any]:
        """Calcula o comparativo técnico, econômico e ambiental completo."""
        consumo_base_mes = max(float(consumo_kwh_mes), 50.0)
        tarifa = float(tarifa_kwh if tarifa_kwh is not None else self.tarifa_kwh)

        fator_escala = consumo_base_mes / CONSUMO_BASE_PADRAO_KWH_MES

        # Cenário Base (Atual)
        consumo_base_ano = round(consumo_base_mes * 12, 1)
        gasto_base_mes = round(consumo_base_mes * tarifa, 2)
        gasto_base_ano = round(gasto_base_mes * 12, 2)
        gasto_base_5_anos = round(gasto_base_ano * 5, 2)
        co2_base_ano_kg = round(
            consumo_base_ano * FATOR_EMISSAO_SIN_KG_CO2_KWH, 2
        )

        # Alternativa 1: Eficiência Energética (Retrofit LED Procel A + Chuveiro Verão)
        economia_leds_mes = round(ECONOMIA_PADRAO_LEDS_KWH_MES * fator_escala, 1)
        economia_chuveiro_mes = round(
            ECONOMIA_PADRAO_CHUVEIRO_KWH_MES * fator_escala, 1
        )
        economia_alt1_kwh_mes = round(economia_leds_mes + economia_chuveiro_mes, 1)
        consumo_alt1_kwh_mes = round(consumo_base_mes - economia_alt1_kwh_mes, 1)
        economia_alt1_kwh_ano = round(economia_alt1_kwh_mes * 12, 1)

        gasto_alt1_mes = round(consumo_alt1_kwh_mes * tarifa, 2)
        economia_alt1_mes_brl_exata = economia_alt1_kwh_mes * tarifa
        economia_alt1_mes_brl = round(economia_alt1_mes_brl_exata, 2)
        economia_alt1_ano_brl = round(economia_alt1_mes_brl_exata * 12, 2)
        economia_alt1_5_anos_brl = round(economia_alt1_ano_brl * 5, 2)
        investimento_alt1_brl = round(INVESTIMENTO_RETROFIT_LED_BRL, 2)
        payback_alt1_meses = (
            round(investimento_alt1_brl / economia_alt1_mes_brl_exata, 2)
            if economia_alt1_mes_brl_exata > 0
            else 0.0
        )
        co2_evitado_alt1_sin_ano = round(
            economia_alt1_kwh_ano * FATOR_EMISSAO_SIN_KG_CO2_KWH, 2
        )
        co2_evitado_alt1_ponta_ano = round(
            economia_alt1_kwh_ano * FATOR_EMISSAO_PONTA_TERMICA_KG_CO2_KWH, 2
        )

        # Alternativa 2 (Fonte Renovável): Sistema Solar Fotovoltaico On-Grid + Compartilhada
        potencia_solar_kwp = round(POTENCIA_SOLAR_PADRAO_KWP * fator_escala, 2)
        geracao_solar_kwh_mes = round(
            GERACAO_SOLAR_PADRAO_KWH_MES * fator_escala, 1
        )
        geracao_solar_kwh_ano = round(geracao_solar_kwh_mes * 12, 1)
        consumo_faturado_alt2_kwh_mes = round(
            max(
                consumo_base_mes - geracao_solar_kwh_mes,
                CUSTO_DISPONIBILIDADE_MONOFASICO_KWH,
            ),
            1,
        )
        gasto_alt2_mes = round(consumo_faturado_alt2_kwh_mes * tarifa, 2)
        economia_alt2_mes_brl_exata = (
            consumo_base_mes - consumo_faturado_alt2_kwh_mes
        ) * tarifa
        economia_alt2_mes_brl = round(economia_alt2_mes_brl_exata, 2)
        economia_alt2_ano_brl = round(economia_alt2_mes_brl_exata * 12, 2)
        economia_alt2_5_anos_brl = round(economia_alt2_ano_brl * 5, 2)
        investimento_alt2_brl = round(
            INVESTIMENTO_SOLAR_PADRAO_BRL * fator_escala, 2
        )
        payback_alt2_anos = (
            round(investimento_alt2_brl / economia_alt2_ano_brl, 1)
            if economia_alt2_ano_brl > 0
            else 0.0
        )
        co2_evitado_alt2_ano = round(
            geracao_solar_kwh_ano * FATOR_EMISSAO_SIN_KG_CO2_KWH, 1
        )
        co2_evitado_alt2_5_anos = round(co2_evitado_alt2_ano * 5, 1)

        # Submodalidade Renovável para Inquilinos: Geração Solar Compartilhada
        economia_compartilhada_mes_brl = round(
            gasto_base_mes * (DESCONTO_GERACAO_COMPARTILHada_PCT / 100.0), 2
        )
        economia_compartilhada_ano_brl = round(
            economia_compartilhada_mes_brl * 12, 2
        )

        return {
            "contexto": {
                "publico_alvo": (
                    "Famílias atendidas pela Central do Cidadão de Aurora "
                    "(referência: residência com 4 moradores)"
                ),
                "problema_energetico": (
                    "Elevado comprometimento de renda com conta de energia elétrica "
                    "devido a chuveiro resistivo de alta potência (5.500 W), "
                    "iluminação incandescente/halógena (60 W) e refrigeração antiga."
                ),
                "periodo_referencia": "Mensal, Anual (12 meses) e Horizonte de 5 anos (60 meses)",
                "tarifa_referencia_brl_kwh": tarifa,
                "fator_emissao_sin_kg_co2_kwh": FATOR_EMISSAO_SIN_KG_CO2_KWH,
            },
            "equipamentos": list(self.equipamentos),
            "cenario_base": {
                "consumo_kwh_mes": consumo_base_mes,
                "consumo_kwh_ano": consumo_base_ano,
                "gasto_mensal_brl": gasto_base_mes,
                "gasto_anual_brl": gasto_base_ano,
                "gasto_5_anos_brl": gasto_base_5_anos,
                "emissoes_co2_ano_kg": co2_base_ano_kg,
            },
            "alternativa_1_eficiencia": {
                "nome": (
                    "Alternativa 1 — Eficiência Energética "
                    "(8 Lâmpadas LED 9W Procel A + Chuveiro Modo Verão 3.200W)"
                ),
                "fonte_renovavel": False,
                "consumo_rede_kwh_mes": consumo_alt1_kwh_mes,
                "economia_leds_kwh_mes": economia_leds_mes,
                "economia_chuveiro_kwh_mes": economia_chuveiro_mes,
                "economia_kwh_mes": economia_alt1_kwh_mes,
                "economia_kwh_ano": economia_alt1_kwh_ano,
                "gasto_mensal_brl": gasto_alt1_mes,
                "economia_mensal_brl": economia_alt1_mes_brl,
                "economia_anual_brl": economia_alt1_ano_brl,
                "economia_5_anos_brl": economia_alt1_5_anos_brl,
                "investimento_inicial_brl": investimento_alt1_brl,
                "payback_meses": payback_alt1_meses,
                "co2_evitado_ano_kg": co2_evitado_alt1_sin_ano,
                "co2_evitado_ponta_ano_kg": co2_evitado_alt1_ponta_ano,
                "viabilidade": (
                    "Altíssima viabilidade imediata; aplicável inclusive em imóveis "
                    "alugados e apartamentos sem necessidade de obras civis."
                ),
                "limitacoes": (
                    "Depende da disciplina de uso familiar no banho e não gera "
                    "energia própria; em dias de inverno rigoroso o uso da posição "
                    "Inverno do chuveiro reduz parte da economia térmica."
                ),
            },
            "alternativa_2_solar_renovavel": {
                "nome": (
                    f"Alternativa 2 (Fonte Renovável) — Sistema Solar Fotovoltaico "
                    f"On-Grid ({potencia_solar_kwp:.1f} kWp) / Geração Compartilhada"
                ),
                "fonte_renovavel": True,
                "potencia_kwp": potencia_solar_kwp,
                "geracao_mensal_kwh": geracao_solar_kwh_mes,
                "geracao_anual_kwh": geracao_solar_kwh_ano,
                "consumo_rede_kwh_mes": consumo_faturado_alt2_kwh_mes,
                "gasto_mensal_brl": gasto_alt2_mes,
                "economia_mensal_brl": economia_alt2_mes_brl,
                "economia_anual_brl": economia_alt2_ano_brl,
                "economia_5_anos_brl": economia_alt2_5_anos_brl,
                "investimento_inicial_brl": investimento_alt2_brl,
                "payback_anos": payback_alt2_anos,
                "vida_util_anos": VIDA_UTIL_PAINEIS_ANOS,
                "co2_evitado_ano_kg": co2_evitado_alt2_ano,
                "co2_evitado_5_anos_kg": co2_evitado_alt2_5_anos,
                "geracao_compartilhada_inquilinos": {
                    "modalidade": "Assinatura de Geração Solar Compartilhada (Lei 14.300/2022)",
                    "investimento_inicial_brl": 0.00,
                    "desconto_estimado_pct": DESCONTO_GERACAO_COMPARTILHada_PCT,
                    "economia_mensal_brl": economia_compartilhada_mes_brl,
                    "economia_anual_brl": economia_compartilhada_ano_brl,
                },
                "viabilidade": (
                    "Excelente retorno de médio/longo prazo para proprietários com "
                    "telhado livre de sombras; para inquilinos ou apartamentos, "
                    "a Geração Solar Compartilhada viabiliza o acesso sem obras."
                ),
                "limitacoes": (
                    "Exige investimento inicial (R$ 9.200,00 para 2,0 kWp), área de "
                    "telhado sem sombreamento e homologação na distribuidora; "
                    "geração varia com o clima e mantém a cobrança da taxa mínima "
                    "de disponibilidade da rede (30 kWh/mês monofásico)."
                ),
            },
            "referencias": list(REFERENCIAS_VERIFICAVEIS),
            "condicoes_e_limitacoes": list(LIMITACOES_E_CONDICOES),
        }

    def exibir_relatorio_terminal(
        self,
        consumo_kwh_mes: float = CONSUMO_BASE_PADRAO_KWH_MES,
    ) -> dict[str, Any]:
        """Imprime no terminal o comparativo detalhado das duas alternativas."""
        dados = self.calcular_comparativo(consumo_kwh_mes=consumo_kwh_mes)
        base = dados["cenario_base"]
        alt1 = dados["alternativa_1_eficiencia"]
        alt2 = dados["alternativa_2_solar_renovavel"]
        comp = alt2["geracao_compartilhada_inquilinos"]

        print("\n" + "=" * 76)
        print("DIAGNÓSTICO E SIMULAÇÃO DE ENERGIA SUSTENTÁVEL — CENTRAL DE AURORA")
        print("=" * 76)
        print(f"Público-Alvo     : {dados['contexto']['publico_alvo']}")
        print(
            f"Consumo Analisado: {base['consumo_kwh_mes']:.1f} kWh/mês "
            f"({base['consumo_kwh_ano']:.1f} kWh/ano)"
        )
        print(
            f"Tarifa Referência: R$ {dados['contexto']['tarifa_referencia_brl_kwh']:.2f}/kWh "
            f"| Fatura Atual: R$ {base['gasto_mensal_brl']:.2f}/mês "
            f"(R$ {base['gasto_anual_brl']:.2f}/ano)"
        )
        print("-" * 76)
        print("1) ALTERNATIVA 1 — EFICIÊNCIA ENERGÉTICA (PROCEL A / LED + CHUVEIRO VERÃO)")
        print(
            f"   - Novo consumo da rede : {alt1['consumo_rede_kwh_mes']:.1f} kWh/mês "
            f"(economia de {alt1['economia_kwh_mes']:.1f} kWh/mês)"
        )
        print(
            f"   - Nova fatura mensal   : R$ {alt1['gasto_mensal_brl']:.2f}/mês "
            f"| Economia anual: R$ {alt1['economia_anual_brl']:.2f}/ano"
        )
        print(
            f"   - Investimento inicial : R$ {alt1['investimento_inicial_brl']:.2f} "
            f"| Tempo de retorno (Payback): {alt1['payback_meses']:.2f} mês"
        )
        print(
            f"   - Impacto ambiental    : {alt1['economia_kwh_ano']:.1f} kWh/ano poupados "
            f"({alt1['co2_evitado_ano_kg']:.2f} kg CO2/ano evitados no SIN)"
        )
        print(f"   - Viabilidade/Limitação: {alt1['limitacoes']}")
        print("-" * 76)
        print("2) ALTERNATIVA 2 (FONTE RENOVÁVEL) — ENERGIA SOLAR FOTOVOLTAICA ON-GRID")
        print(
            f"   - Sistema dimensionado : {alt2['potencia_kwp']:.1f} kWp "
            f"(geração média de {alt2['geracao_mensal_kwh']:.1f} kWh/mês | "
            f"{alt2['geracao_anual_kwh']:.1f} kWh/ano)"
        )
        print(
            f"   - Consumo faturado rede: {alt2['consumo_rede_kwh_mes']:.1f} kWh/mês "
            "(taxa mínima de disponibilidade monofásica)"
        )
        print(
            f"   - Nova fatura mensal   : R$ {alt2['gasto_mensal_brl']:.2f}/mês "
            f"| Economia anual: R$ {alt2['economia_anual_brl']:.2f}/ano"
        )
        print(
            f"   - Investimento inicial : R$ {alt2['investimento_inicial_brl']:.2f} "
            f"| Payback: {alt2['payback_anos']:.1f} anos "
            f"(vida útil de {alt2['vida_util_anos']} anos)"
        )
        print(
            f"   - Impacto ambiental    : {alt2['co2_evitado_ano_kg']:.1f} kg CO2/ano "
            f"evitados ({alt2['co2_evitado_5_anos_kg']:.1f} kg CO2 em 5 anos)"
        )
        print(
            f"   - Opção p/ Inquilinos  : {comp['modalidade']} — Investimento R$ 0,00 e "
            f"economia estimada de R$ {comp['economia_anual_brl']:.2f}/ano (~{comp['desconto_estimado_pct']:.0f}%)"
        )
        print(f"   - Viabilidade/Limitação: {alt2['limitacoes']}")
        print("-" * 76)
        print("Fontes: ANEEL, PROCEL/INMETRO, EPE (Balanço Energético) e MCTI (Fator SIN).")
        print("Aviso : As estimativas acima são referenciais e NÃO constituem resultado garantido.")
        print("        Aviso: este assistente NÃO é um canal oficial.")
        print("=" * 76)
        return dados

    def exibir_tabela_equipamentos(self) -> None:
        """Exibe a tabela de consumo por equipamento carregada do CSV."""
        print("\n" + "=" * 76)
        print("PERFIL DE CONSUMO POR EQUIPAMENTO (RESIDÊNCIA DE REFERÊNCIA — 4 PESSOAS)")
        print("=" * 76)
        for item in self.equipamentos:
            print(
                f"[{item['id_equipamento']}] {item['equipamento']}\n"
                f"    Qtd: {item['quantidade']} | Potência atual: {item['potencia_atual_w']:.0f} W "
                f"| Uso: {item['horas_uso_dia']:.2f} h/dia\n"
                f"    Consumo atual: {item['consumo_atual_kwh_mes']:.1f} kWh/mês -> "
                f"Pós-eficiência: {item['consumo_eficiente_kwh_mes']:.1f} kWh/mês "
                f"(Economia: {item['economia_kwh_mes']:.1f} kWh/mês)\n"
                f"    Ação recomendada: {item['acao_eficiencia']} [{item['fonte_referencia']}]"
            )
        print("=" * 76)

    def executar_menu_interativo(self) -> None:
        """Executa o menu interativo de Energia e Sustentabilidade no terminal."""
        while True:
            print("\n=== Módulo de Energia Sustentável e Transição Fotovoltaica (ERS) ===")
            print("1 - Diagnóstico padrão da família de Aurora (280,0 kWh/mês)")
            print("2 - Simular com o consumo da sua própria conta de luz (kWh/mês)")
            print("3 - Ver tabela detalhada de consumo por equipamento (CSV)")
            print("4 - Consultar fontes verificáveis e limitações técnicas")
            print("0 - Voltar")

            opcao = input("Escolha uma opção (0 para voltar): ").strip()
            if opcao == "0":
                return
            if opcao == "1":
                self.exibir_relatorio_terminal(CONSUMO_BASE_PADRAO_KWH_MES)
            elif opcao == "2":
                entrada = input(
                    "Digite o consumo mensal da sua residência em kWh (ex.: 280): "
                ).strip().replace(",", ".")
                try:
                    valor_kwh = float(entrada)
                    if valor_kwh <= 0:
                        print("Digite um valor de consumo positivo maior que zero.")
                        continue
                    self.exibir_relatorio_terminal(valor_kwh)
                except ValueError:
                    print("Entrada inválida. Digite um número válido em kWh (ex.: 280).")
            elif opcao == "3":
                self.exibir_tabela_equipamentos()
            elif opcao == "4":
                print("\n--- Fontes Técnicas e Normativas Verificadas ---")
                for ref in REFERENCIAS_VERIFICAVEIS:
                    print(f"- {ref['sigla']} ({ref['orgao']}): {ref['documento']} [{ref['url']}]")
                print("\n--- Condições de Uso e Limitações das Estimativas ---")
                for lim in LIMITACOES_E_CONDICOES:
                    print(f"- {lim}")
            else:
                print("Opção fora da faixa. Escolha de 0 a 4.")

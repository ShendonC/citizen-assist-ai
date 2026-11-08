#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Citizen Assist AI — Central do Cidadão de Aurora
Global Solution 2026.2 — Citizen Tech (1º Ano de Ciência da Computação — FIAP)

Ponto de entrada principal (Terminal Interativo + Lançador da Interface Gráfica Unificada).
Integra as 8 disciplinas do semestre em um único ecossistema coeso:
  1. Pensamento Computacional e Automação com Python (PCP)
  2. Prompt and Artificial Intelligence (PAI - Gemini 3.8 Flash + LLM-as-a-Judge)
  3. Soluções em Energias Renováveis e Sustentáveis (ERS)
  4. Data Structures and Algorithms (DSA - Lista Encadeada + Merge Sort + Big-O)
  5. Ciência da Computação (CS - Decisão Booleana, De Morgan e Karnaugh)
  6. Computer Organization and Architecture (COA - Totem IoT Raspberry Pi Pico / Wokwi)
  7. Modelagem Matemática e Computacional (MMC - Frota de 72 Ônibus / Transformação Linear)
  8. Modelagem Linear para Aprendizado de Máquina (MLM - Estatística & Regressão Linear/Logística)
"""

import os
import sys
import webbrowser
from pathlib import Path

from base_conhecimento import BaseConhecimento
from assistente import Assistente


DIRETORIO_RAIZ = Path(__file__).resolve().parent
CAMINHO_BASE_JSON = DIRETORIO_RAIZ / "data" / "base_conhecimento.json"
CAMINHO_WEB_APP = DIRETORIO_RAIZ / "Abrir_Aurora_Cidada.html"


def exibir_cabecalho() -> None:
    print("\n" + "=" * 78)
    print("  CENTRAL DO CIDADÃO DE AURORA — CITIZEN ASSIST AI (GLOBAL SOLUTION 2026.2)")
    print("  Tecnologia Cidadã: Documentos, Direitos, Energia Limpa e Gestão Urbana")
    print("=" * 78)
    print("  [AVISO] Este assistente é um protótipo educacional e NÃO é canal oficial.")
    print("  [LGPD]  Nunca digite números de CPF, RG, telefone, endereço ou e-mail.")
    print("=" * 78)


def abrir_interface_visual() -> None:
    if CAMINHO_WEB_APP.exists():
        url = CAMINHO_WEB_APP.as_uri()
        print(f"\n>> Abrindo a Interface Visual Unificada no navegador:\n   {CAMINHO_WEB_APP}")
        webbrowser.open(url)
    else:
        print("\n[!] Arquivo Abrir_Aurora_Cidada.html ainda não encontrado no diretório raiz.")


def executar_modulo_energia() -> None:
    try:
        from energia_sustentavel import SimuladorEnergiaSustentavel
        simulador = SimuladorEnergiaSustentavel()
        if hasattr(simulador, "executar_menu_interativo"):
            simulador.executar_menu_interativo()
        elif hasattr(simulador, "calcular_comparativo"):
            res = simulador.calcular_comparativo(280.0)
            print("\n=== ANÁLISE DE EFICIÊNCIA ENERGÉTICA E FONTE RENOVÁVEL (ERS) ===")
            for k, v in res.items():
                print(f" - {k}: {v}")
    except Exception as exc:
        print(f"\n[!] Erro ao carregar módulo de Energia Sustentável: {exc}")


def executar_modulo_dsa() -> None:
    try:
        import dsa_lista_encadeada
        if hasattr(dsa_lista_encadeada, "executar_menu_dsa"):
            dsa_lista_encadeada.executar_menu_dsa()
        elif hasattr(dsa_lista_encadeada, "executar_bateria_testes_evidencias"):
            dsa_lista_encadeada.executar_bateria_testes_evidencias()
    except Exception as exc:
        print(f"\n[!] Erro ao carregar módulo DSA (Lista Encadeada): {exc}")


def executar_modulo_cs() -> None:
    try:
        import cs_decisao_booleana
        if hasattr(cs_decisao_booleana, "executar_menu_cs"):
            cs_decisao_booleana.executar_menu_cs()
        elif hasattr(cs_decisao_booleana, "validar_tabela_verdade_completa"):
            cs_decisao_booleana.validar_tabela_verdade_completa()
    except Exception as exc:
        print(f"\n[!] Erro ao carregar módulo de Ciência da Computação: {exc}")


def executar_modulo_pai() -> None:
    try:
        sys.path.insert(0, str(DIRETORIO_RAIZ / "ai_agent"))
        from ai_agent import llm_judge
        if hasattr(llm_judge, "executar_avaliacao_completa"):
            llm_judge.executar_avaliacao_completa()
        elif hasattr(llm_judge, "main"):
            llm_judge.main()
        else:
            print("\n>> Executando avaliação Golden Dataset (26 questões)...")
            os.system(f'"{sys.executable}" "{DIRETORIO_RAIZ / "ai_agent" / "llm_judge.py"}"')
    except Exception as exc:
        print(f"\n[!] Erro ao executar módulo Prompt & AI: {exc}")


def executar_modulo_coa() -> None:
    try:
        caminho_sim = DIRETORIO_RAIZ / "wokwi_iot" / "simulador_totem_pc.py"
        if caminho_sim.exists():
            os.system(f'"{sys.executable}" "{caminho_sim}" --test')
        else:
            print("\n[!] Arquivo wokwi_iot/simulador_totem_pc.py não encontrado.")
    except Exception as exc:
        print(f"\n[!] Erro ao executar simulador IoT Wokwi: {exc}")


def executar_modulo_mmc() -> None:
    try:
        import mobilidade_frota_mmc
        if hasattr(mobilidade_frota_mmc, "main"):
            mobilidade_frota_mmc.main()
        else:
            os.system(f'"{sys.executable}" "{DIRETORIO_RAIZ / "mobilidade_frota_mmc.py"}"')
    except Exception as exc:
        print(f"\n[!] Erro ao executar Modelagem Matemática (72 Ônibus): {exc}")


def executar_modulo_mlm() -> None:
    try:
        import ml_estatistica_cidada
        if hasattr(ml_estatistica_cidada, "main"):
            ml_estatistica_cidada.main()
        else:
            os.system(f'"{sys.executable}" "{DIRETORIO_RAIZ / "ml_estatistica_cidada.py"}"')
    except Exception as exc:
        print(f"\n[!] Erro ao executar Modelagem Linear e Machine Learning: {exc}")


def main() -> None:
    # Instanciação padrão exigida na especificação de PCP:
    base = BaseConhecimento(str(CAMINHO_BASE_JSON))
    base.carregar()
    assistente = Assistente("Citizen Assist AI", base)

    if "--web" in sys.argv:
        abrir_interface_visual()
        return

    while True:
        exibir_cabecalho()
        print("  ESCOLHA UMA OPÇÃO DE ATENDIMENTO OU MÓDULO INTEGRADO:")
        print("  ------------------------------------------------------------------------")
        print("  [1] Fazer uma pergunta em texto livre (Busca Inteligente por Pontos - PCP)")
        print("  [2] Navegar por categorias de serviços e orientações (PCP)")
        print("  [3] Ver indicadores de atendimento e exportar CSV (PCP)")
        print("  [4] Simulador de Consumo Elétrico e Energia Solar Fotovoltaica (ERS)")
        print("  [5] Triagem Lógica Booleana de Atendimento Presencial (Computer Science)")
        print("  [6] Gerenciador de Serviços em Lista Encadeada & Merge Sort (DSA)")
        print("  [7] Agente IA (Gemini 3.8 Flash) & Auditoria Golden Dataset (Prompt & AI)")
        print("  [8] Simulador do Totem Físico IoT - Fila Virtual & Clima (COA / Wokwi)")
        print("  [9] Mobilidade Urbana: Modelo Matricial da Frota de 72 Ônibus (MMC)")
        print("  [10] Observatório Cidadão: Estatística, Regressão & Machine Learning (MLM)")
        print("  [11] Abrir Super Interface Gráfica Unificada no Navegador (UX/UI Web App)")
        print("  [0] Encerrar atendimento e avaliar facilidade de uso")
        print("  ------------------------------------------------------------------------")

        opcao = input("\n  Digite o número da opção desejada: ").strip()

        if opcao == "1":
            assistente.perguntar()
        elif opcao == "2":
            assistente.navegar()
        elif opcao == "3":
            assistente.indicadores()
            assistente.exportar_csv()
        elif opcao == "4":
            executar_modulo_energia()
        elif opcao == "5":
            executar_modulo_cs()
        elif opcao == "6":
            executar_modulo_dsa()
        elif opcao == "7":
            executar_modulo_pai()
        elif opcao == "8":
            executar_modulo_coa()
        elif opcao == "9":
            executar_modulo_mmc()
        elif opcao == "10":
            executar_modulo_mlm()
        elif opcao == "11":
            abrir_interface_visual()
        elif opcao == "0":
            print("\n  Antes de sair, avalie sua experiência na Central do Cidadão de Aurora:")
            while True:
                nota_str = input("  De 1 (muito difícil) a 5 (muito fácil), qual nota você dá para o assistente? (Enter p/ pular): ").strip()
                if not nota_str:
                    break
                if nota_str in {"1", "2", "3", "4", "5"}:
                    if hasattr(assistente, "registrar_avaliacao_final"):
                        assistente.registrar_avaliacao_final(int(nota_str))
                    elif hasattr(assistente, "notas_facilidade"):
                        assistente.notas_facilidade.append(int(nota_str))
                    print(f"  Obrigado pela avaliação (Nota {nota_str}/5)!")
                    break
                print("  [!] Opção inválida. Digite um número inteiro entre 1 e 5.")
            assistente.exportar_csv()
            assistente.indicadores()
            print("\n  Atendimento encerrado. Obrigado por utilizar o Citizen Assist AI!\n")
            break
        else:
            print("\n  [!] Entrada inválida: digite um número válido do menu (0 a 11). O programa continua ativo.")


if __name__ == "__main__":
    main()

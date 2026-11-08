# -*- coding: utf-8 -*-
"""
Simulador Local de Bancada (PC) e Suite de Verificacao Automatizada
Totem Inteligente de Fila Virtual, Acessibilidade e Monitoramento Ambiental
Central do Cidadao de Aurora - Citizen Assist AI (GS 2026.2 - FIAP 1CC)
Disciplina: Computer Organization and Architecture (COA) - Prof. Dr. Marcus Grilo

Uso:
  python wokwi_iot/simulador_totem_pc.py --test   # Executa bateria completa de testes e telemetria
  python wokwi_iot/simulador_totem_pc.py          # Modo interativo de simulacao no terminal
"""

import argparse
import json
from pathlib import Path
import sys

# Garante importacao limpa do modulo main.py mesmo executado da raiz do projeto
DIRETORIO_ATUAL = Path(__file__).resolve().parent
if str(DIRETORIO_ATUAL) not in sys.path:
    sys.path.insert(0, str(DIRETORIO_ATUAL))

import main as totem_fw  # noqa: E402


class HardwareVirtualPC:
    """Mock de hardware da Raspberry Pi Pico para validacao deterministica no PC."""

    def __init__(self):
        self.leds = {"VERDE_GP10": 0, "AMARELO_GP11": 0, "VERMELHO_GP12": 0}
        self.historico_buzzer = []

    def definir_leds(self, verde=False, amarelo=False, vermelho=False):
        self.leds["VERDE_GP10"] = 1 if verde else 0
        self.leds["AMARELO_GP11"] = 1 if amarelo else 0
        self.leds["VERMELHO_GP12"] = 1 if vermelho else 0

    def tocar_buzzer(self, bips=1, freq=880, duracao_ms=100):
        registro = {"bips": bips, "freq_hz": freq, "duracao_ms": duracao_ms}
        self.historico_buzzer.append(registro)
        print(
            "  [ATUADOR BUZZER GP18] Acionado: {} bip(s) @ {} Hz ({} ms)".format(
                bips, freq, duracao_ms
            )
        )


def validar_diagrama_wokwi(caminho_diagrama: Path):
    """Valida a integridade estrutural, pinagem e ausencia de BOM no diagram.json."""
    raw_bytes = caminho_diagrama.read_bytes()
    assert not raw_bytes.startswith(b"\xef\xbb\xbf"), (
        "ERRO: diagram.json nao pode conter UTF-8 BOM."
    )

    dados = json.loads(raw_bytes.decode("utf-8"))
    assert dados.get("version") == 1, "Versao invalida no diagram.json"

    partes_por_id = {p["id"]: p for p in dados.get("parts", [])}
    ids_obrigatorios = {
        "pico": "wokwi-pi-pico",
        "btn_normal": "wokwi-pushbutton",
        "btn_prio": "wokwi-pushbutton",
        "btn_chamar": "wokwi-pushbutton",
        "dht1": "wokwi-dht22",
        "led_verde": "wokwi-led",
        "led_amarelo": "wokwi-led",
        "led_vermelho": "wokwi-led",
        "r_verde": "wokwi-resistor",
        "r_amarelo": "wokwi-resistor",
        "r_vermelho": "wokwi-resistor",
        "bz1": "wokwi-buzzer",
    }
    for comp_id, comp_type in ids_obrigatorios.items():
        assert comp_id in partes_por_id, f"Componente ausente no diagram.json: {comp_id}"
        assert partes_por_id[comp_id]["type"] == comp_type, (
            f"Tipo incorreto para {comp_id}: esperado {comp_type}"
        )

    conexoes_texto = json.dumps(dados.get("connections", []))
    pinos_obrigatorios = [
        "pico:GP14",
        "pico:GP15",
        "pico:GP16",
        "pico:GP22",
        "pico:GP10",
        "pico:GP11",
        "pico:GP12",
        "pico:GP18",
    ]
    for pino in pinos_obrigatorios:
        assert pino in conexoes_texto, f"Pino obrigatorio nao conectado no diagram.json: {pino}"

    return True


def executar_bateria_testes():
    """Executa a simulacao fim-a-fim e valida todas as regras de negocio e hardware."""
    print("========================================================================")
    print(" INICIANDO SIMULACAO E VALIDACAO DO TOTEM IoT - CENTRAL DE AURORA")
    print("========================================================================")

    caminho_diagrama = DIRETORIO_ATUAL / "diagram.json"
    validar_diagrama_wokwi(caminho_diagrama)
    print("[OK] Schema e pinagem do arquivo diagram.json validados (UTF-8 puro, sem BOM).")

    hw = HardwareVirtualPC()
    ctrl = totem_fw.ControladorTotemAurora(hardware=hw)
    ctrl.sincronizar_leds()

    # 1. Estado inicial: Fila livre e conforto termico (24.5 C, 55%)
    assert hw.leds["VERDE_GP10"] == 1 and hw.leds["AMARELO_GP11"] == 0 and hw.leds["VERMELHO_GP12"] == 0
    t_clock = 1000
    ctrl.publicar_telemetria(
        evento="BOOT_SIMULADOR_PC",
        detalhe="Inicializacao em condicoes normais de conforto termico",
        ts_ms=t_clock,
    )

    # 2. Entrada de 2 cidadaos na fila normal (GP14) -> 1 bip cada, LED permanece VERDE
    t_clock += 1500
    p1 = ctrl.registrar_entrada_normal(ts_ms=t_clock)
    assert p1["filas"]["normal"] == 1
    assert p1["previsao_espera"]["formula_base_min"] == 5.0
    assert hw.historico_buzzer[-1]["bips"] == 1
    assert hw.leds["VERDE_GP10"] == 1

    t_clock += 1500
    p2 = ctrl.registrar_entrada_normal(ts_ms=t_clock)
    assert p2["filas"]["normal"] == 2
    assert p2["previsao_espera"]["formula_base_min"] == 10.0
    assert hw.leds["VERDE_GP10"] == 1

    # 3. Entrada de 4 cidadaos na fila prioritaria FC-07 (GP15)
    # Ao atingir 3 pessoas no total -> LED AMARELO (GP11)
    # Ao atingir 6 pessoas no total -> LED VERMELHO (GP12) + 3 bips de superlotacao
    for idx in range(1, 5):
        t_clock += 1200
        ev = ctrl.registrar_entrada_prioritaria(ts_ms=t_clock)
        total_atual = ev["filas"]["total_aguardando"]
        if total_atual < 6:
            assert hw.leds["AMARELO_GP11"] == 1, "Esperado LED Amarelo em fila moderada"
            assert hw.historico_buzzer[-1]["bips"] == 2
        else:
            assert hw.leds["VERMELHO_GP12"] == 1, "Esperado LED Vermelho em superlotacao (>=6)"
            assert hw.historico_buzzer[-1]["bips"] == 3

    # Verifica preditor com 2 normais (2*5=10) + 4 prioritarios (4*7=28) = 38.0 min
    t_base, t_ewma = ctrl.calcular_estimativa_espera()
    assert t_base == 38.0, f"Esperado 38.0 min na formula base, obtido {t_base}"

    # 4. Teste de Chamada no Guiche (GP16): Prioridade Legal FC-07 + Regra Anti-Inanicao (3x1)
    # As 3 primeiras chamadas devem atender P-001, P-002 e P-003 (fila prioritaria)
    senhas_chamadas = []
    for intervalo_real in (6.0, 5.0, 4.5):
        t_clock += 3000
        ev_chamada = ctrl.chamar_proximo_guiche(
            ts_ms=t_clock, intervalo_simulado_min=intervalo_real
        )
        senhas_chamadas.append(ev_chamada["filas"]["ultima_chamada"])

    assert senhas_chamadas == ["P-001", "P-002", "P-003"], (
        f"Falha na prioridade FC-07: {senhas_chamadas}"
    )

    # A 4a chamada consecutiva DEVE acionar a regra Anti-Inanicao (3x1) e chamar N-001
    # mesmo ainda existindo P-004 na fila prioritaria!
    t_clock += 3000
    ev_anti_inanicao = ctrl.chamar_proximo_guiche(ts_ms=t_clock, intervalo_simulado_min=4.8)
    assert ev_anti_inanicao["filas"]["ultima_chamada"] == "N-001", (
        "Falha na regra anti-inanicao: deveria ter chamado N-001 apos 3 prioritarios"
    )
    assert "ANTI_INANICAO_3X1" in ev_anti_inanicao["detalhe"]

    # A 5a chamada volta a priorizar P-004
    t_clock += 3000
    ev_p4 = ctrl.chamar_proximo_guiche(ts_ms=t_clock, intervalo_simulado_min=5.2)
    assert ev_p4["filas"]["ultima_chamada"] == "P-004"

    # 5. Teste do Sensor DHT22 (GP22): Elevacao termica acima de 28 C (ex.: 29.6 C)
    # Mesmo com apenas 1 pessoa na fila (N-002), o alerta termico deve acionar LED VERMELHO e 3 bips
    t_clock += 2500
    ev_clima = ctrl.atualizar_ambiente(temperatura_c=29.6, umidade_pct=64.0, ts_ms=t_clock)
    assert ev_clima is not None and ev_clima["evento"] == "ALERTA_AMBIENTAL_DHT22"
    assert hw.leds["VERMELHO_GP12"] == 1
    assert hw.historico_buzzer[-1]["bips"] == 3

    # 6. Normalizacao climatica (24.0 C, 52.0%) -> Retorna ao LED VERDE e publica evento
    t_clock += 2500
    ev_norm = ctrl.atualizar_ambiente(temperatura_c=24.0, umidade_pct=52.0, ts_ms=t_clock)
    assert ev_norm is not None and ev_norm["evento"] == "NORMALIZACAO_AMBIENTAL_DHT22"
    assert hw.leds["VERDE_GP10"] == 1

    print("========================================================================")
    print(" [SUCESSO] TODOS OS TESTES DE FILA, ANTI-INANICAO, EWMA, DHT22 E LEDS")
    print("           FORAM EXECUTADOS E VALIDADOS COM 100% DE CONFORMIDADE!")
    print("========================================================================")
    return 0


def menu_interativo():
    """Permite operar o Totem manualmente no terminal do PC."""
    hw = HardwareVirtualPC()
    ctrl = totem_fw.ControladorTotemAurora(hardware=hw)
    ctrl.sincronizar_leds()

    while True:
        print("\n=== SIMULADOR TOTEM AURORA (PC) ===")
        print("[1] Pressionar Botao Verde   (GP14) - Nova Senha Fila Normal")
        print("[2] Pressionar Botao Azul    (GP15) - Nova Senha Prioritaria (FC-07)")
        print("[3] Pressionar Botao Amarelo (GP16) - Guiche Chamar Proximo")
        print("[4] Simular Leitura DHT22    (GP22) - Alterar Temperatura/Umidade")
        print("[5] Executar Bateria Automatizada de Testes (--test)")
        print("[0] Sair")
        opcao = input("Escolha uma acao: ").strip()

        if opcao == "1":
            ctrl.registrar_entrada_normal()
        elif opcao == "2":
            ctrl.registrar_entrada_prioritaria()
        elif opcao == "3":
            ctrl.chamar_proximo_guiche()
        elif opcao == "4":
            try:
                t_str = input("Nova Temperatura em C (ex: 29.5): ").strip()
                u_str = input("Nova Umidade em % (ex: 55.0): ").strip()
                ctrl.atualizar_ambiente(float(t_str), float(u_str))
                ctrl.publicar_telemetria(
                    evento="LEITURA_MANUAL_DHT22",
                    detalhe="Leitura ambiental atualizada pelo operador",
                )
            except ValueError:
                print("Valores invalidos. Digite numeros decimais como 25.0 e 60.0.")
        elif opcao == "5":
            executar_bateria_testes()
        elif opcao == "0":
            print("Encerrando simulador do Totem Aurora.")
            break
        else:
            print("Opcao invalida.")


def main():
    parser = argparse.ArgumentParser(
        description="Simulador de Bancada do Totem IoT da Central do Cidadao de Aurora"
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="Executa a bateria automatizada de verificacao e encerra",
    )
    args = parser.parse_args()

    if args.test:
        sys.exit(executar_bateria_testes())
    else:
        menu_interativo()


if __name__ == "__main__":
    main()

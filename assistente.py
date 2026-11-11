"""Módulo da classe Assistente com atendimento, bloqueio LGPD, histórico e CSV."""

from __future__ import annotations

import csv
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Any

from base_conhecimento import BaseConhecimento


MENSAGEM_BLOQUEIO_LGPD = (
    "Atenção: não digite CPF, telefone ou e-mail. Reescreva."
)

COLUNAS_HISTORICO = [
    "data",
    "origem",
    "pergunta",
    "id_orientacao",
    "confianca",
    "encontrou",
    "ajudou",
    "tentativas",
    "tempo_segundos",
    "facilidade",
]


class Assistente:
    """Orquestra o atendimento ao cidadão, proteção LGPD e indicadores."""

    def __init__(
        self,
        nome: str,
        base: BaseConhecimento,
        caminho_historico: str = "data/historico.json",
        caminho_csv: str = "data/atendimentos.csv",
    ) -> None:
        self.nome = str(nome)
        self.base = base
        self.caminho_historico = str(caminho_historico)
        self.caminho_csv = str(caminho_csv)
        self.historico: list[dict[str, Any]] = []
        self._atendimentos_sessao: int = 0
        self._carregar_historico()

    def _carregar_historico(self) -> None:
        """Carrega o histórico prévio do JSON sem interromper a execução."""
        caminho = Path(self.caminho_historico)
        if not caminho.exists():
            self.historico = []
            return
        try:
            with caminho.open("r", encoding="utf-8-sig") as arquivo:
                dados = json.load(arquivo)
            if isinstance(dados, list):
                self.historico = [item for item in dados if isinstance(item, dict)]
            else:
                self.historico = []
        except (json.JSONDecodeError, OSError) as erro:
            print(
                f"Aviso: não foi possível ler '{self.caminho_historico}' ({erro}). "
                "Iniciando histórico vazio."
            )
            self.historico = []

    def _salvar_historico(self) -> bool:
        """Persiste a lista de atendimentos em JSON UTF-8 sem BOM."""
        caminho = Path(self.caminho_historico)
        try:
            caminho.parent.mkdir(parents=True, exist_ok=True)
            with caminho.open("w", encoding="utf-8") as arquivo:
                json.dump(self.historico, arquivo, ensure_ascii=False, indent=2)
            return True
        except OSError as erro:
            print(f"Aviso: falha ao salvar histórico em '{caminho}': {erro}")
            return False

    def contem_dados_pessoais(self, texto: str) -> bool:
        """Verifica se o texto contém '@' (e-mail) ou 8 ou mais dígitos numéricos."""
        if not texto:
            return False
        texto_str = str(texto)
        if "@" in texto_str:
            return True
        total_digitos = sum(1 for caractere in texto_str if caractere.isdigit())
        return total_digitos >= 8

    @staticmethod
    def _ler_confirmacao_sn(mensagem: str) -> bool:
        """Lê confirmação 's' ou 'n' no terminal tratando entradas inválidas."""
        while True:
            resposta = input(mensagem).strip().lower()
            if resposta in ("s", "sim"):
                return True
            if resposta in ("n", "nao", "não"):
                return False
            print("Entrada inválida. Digite apenas 's' para sim ou 'n' para não.")

    @staticmethod
    def _ler_nota_facilidade() -> int:
        """Solicita ao cidadão uma nota de facilidade de uso de 1 a 5."""
        while True:
            entrada = input(
                "De 1 a 5, quão fácil foi usar o assistente neste atendimento? "
            ).strip()
            if entrada.isdigit():
                nota = int(entrada)
                if 1 <= nota <= 5:
                    return nota
            print("Opção fora da faixa. Digite um número inteiro de 1 a 5.")

    def responder_texto(self, pergunta: str) -> dict[str, Any]:
        """Processa uma pergunta de forma programática e retorna o diagnóstico."""
        pergunta_limpa = str(pergunta).strip()
        if not pergunta_limpa:
            return {
                "status": "vazia",
                "bloqueado_lgpd": False,
                "encontrou": False,
                "confianca": "BAIXA",
                "pontos": 0,
                "orientacao": None,
                "alternativas": [],
                "mensagem": "Entrada vazia. Digite sua dúvida.",
            }

        if self.contem_dados_pessoais(pergunta_limpa):
            return {
                "status": "bloqueado_lgpd",
                "bloqueado_lgpd": True,
                "encontrou": False,
                "confianca": "BLOQUEADO",
                "pontos": 0,
                "orientacao": None,
                "alternativas": [],
                "mensagem": MENSAGEM_BLOQUEIO_LGPD,
            }

        resultados = self.base.buscar(pergunta_limpa)
        if not resultados or resultados[0][0] < 3:
            return {
                "status": "nao_encontrada",
                "bloqueado_lgpd": False,
                "encontrou": False,
                "confianca": "NÃO ENCONTRADA",
                "pontos": resultados[0][0] if resultados else 0,
                "orientacao": None,
                "alternativas": [],
                "mensagem": (
                    "Não encontrei orientação com confiança suficiente para essa "
                    "dúvida. Tente usar outras palavras-chave ou consulte as "
                    f"categorias: {', '.join(self.base.categorias())}."
                ),
            }

        melhor_pontos, melhor_orientacao = resultados[0]
        confianca = self.base.classificar_confianca(melhor_pontos)
        alternativas = [
            (pts, ori) for pts, ori in resultados[1:3] if pts >= 3
        ]
        return {
            "status": "encontrada",
            "bloqueado_lgpd": False,
            "encontrou": True,
            "confianca": confianca,
            "pontos": melhor_pontos,
            "orientacao": melhor_orientacao,
            "alternativas": alternativas,
            "mensagem": "Orientação localizada com sucesso.",
        }

    def perguntar(self) -> None:
        """Executa o fluxo interativo de perguntas em texto livre no terminal."""
        print(f"\n=== {self.nome} — Consulta por Pergunta Livre ===")
        inicio = time.time()
        tentativas = 0

        while True:
            pergunta = input("\nDigite sua dúvida (0 para voltar): ").strip()
            if pergunta == "0":
                return

            if not pergunta:
                print("Entrada vazia. Digite uma dúvida válida ou 0 para voltar.")
                continue

            if self.contem_dados_pessoais(pergunta):
                print(MENSAGEM_BLOQUEIO_LGPD)
                continue

            tentativas += 1
            resultados = self.base.buscar(pergunta)

            if not resultados or resultados[0][0] < 3:
                print("\nNão encontrei uma orientação verificada para essa dúvida.")
                categorias_disp = ", ".join(self.base.categorias())
                print(f"Sugestão: tente outras palavras ou navegue por: {categorias_disp}")
                tentar_novamente = self._ler_confirmacao_sn(
                    "Deseja tentar reformular a pergunta? (s/n): "
                )
                if tentar_novamente:
                    continue

                tempo_total = round(time.time() - inicio, 1)
                facilidade = self._ler_nota_facilidade()
                self.registrar(
                    origem="pergunta",
                    pergunta=pergunta,
                    id_orientacao=None,
                    confianca="NÃO ENCONTRADA",
                    encontrou=False,
                    ajudou=False,
                    tentativas=tentativas,
                    tempo_segundos=tempo_total,
                    facilidade=facilidade,
                )
                return

            melhor_pontos, melhor_orientacao = resultados[0]
            confianca = self.base.classificar_confianca(melhor_pontos)
            print()
            melhor_orientacao.exibir(confianca=confianca, pontos=melhor_pontos)

            alternativas = [
                (pts, ori) for pts, ori in resultados[1:3] if pts >= 3
            ]
            if alternativas:
                print("\nOutras orientações relacionadas:")
                for pts_alt, ori_alt in alternativas:
                    print(
                        f"  - [{ori_alt.id}] {ori_alt.titulo} "
                        f"({ori_alt.categoria} — {pts_alt} pontos)"
                    )

            ajudou = self._ler_confirmacao_sn(
                "\nEssa orientação respondeu sua dúvida? (s/n): "
            )
            if not ajudou:
                nova_tentativa = self._ler_confirmacao_sn(
                    "Deseja tentar outra pergunta antes de encerrar? (s/n): "
                )
                if nova_tentativa:
                    continue

            tempo_total = round(time.time() - inicio, 1)
            facilidade = self._ler_nota_facilidade()
            self.registrar(
                origem="pergunta",
                pergunta=pergunta,
                id_orientacao=melhor_orientacao.id,
                confianca=confianca,
                encontrou=True,
                ajudou=ajudou,
                tentativas=tentativas,
                tempo_segundos=tempo_total,
                facilidade=facilidade,
            )
            return

    def navegar(self) -> None:
        """Permite navegar pelas categorias e orientações numeradas."""
        inicio = time.time()
        tentativas = 0

        while True:
            categorias = self.base.categorias()
            if not categorias:
                print("Nenhuma categoria disponível na base de conhecimento.")
                return

            print(f"\n=== {self.nome} — Navegação por Categorias ===")
            for indice, cat in enumerate(categorias, start=1):
                print(f"{indice} - {cat}")
            print("0 - Voltar")

            escolha_cat = input("Escolha uma categoria (0 para voltar): ").strip()
            if escolha_cat == "0":
                return
            if not escolha_cat.isdigit():
                print("Entrada inválida. Digite o número da categoria desejada.")
                continue

            idx_cat = int(escolha_cat)
            if not (1 <= idx_cat <= len(categorias)):
                print("Opção fora da faixa. Escolha uma categoria listada.")
                continue

            categoria_selecionada = categorias[idx_cat - 1]
            orientacoes_cat = self.base.por_categoria(categoria_selecionada)

            while True:
                print(f"\n--- Categoria: {categoria_selecionada} ---")
                for indice_ori, ori in enumerate(orientacoes_cat, start=1):
                    print(f"{indice_ori} - {ori.titulo}")
                print("0 - Voltar")

                escolha_ori = input(
                    "Escolha uma orientação para exibir (0 para voltar): "
                ).strip()
                if escolha_ori == "0":
                    break
                if not escolha_ori.isdigit():
                    print("Entrada inválida. Digite o número da orientação.")
                    continue

                idx_ori = int(escolha_ori)
                if not (1 <= idx_ori <= len(orientacoes_cat)):
                    print("Opção fora da faixa. Escolha uma orientação listada.")
                    continue

                orientacao_escolhida = orientacoes_cat[idx_ori - 1]
                tentativas += 1
                print()
                orientacao_escolhida.exibir(confianca="ALTA (Categoria)")

                ajudou = self._ler_confirmacao_sn(
                    "\nEssa orientação respondeu sua dúvida? (s/n): "
                )
                tempo_total = round(time.time() - inicio, 1)
                facilidade = self._ler_nota_facilidade()
                self.registrar(
                    origem="categoria",
                    pergunta=f"[{categoria_selecionada}] {orientacao_escolhida.titulo}",
                    id_orientacao=orientacao_escolhida.id,
                    confianca="NAVEGAÇÃO",
                    encontrou=True,
                    ajudou=ajudou,
                    tentativas=tentativas,
                    tempo_segundos=tempo_total,
                    facilidade=facilidade,
                )
                return

    def registrar(
        self,
        origem: str | dict[str, Any] = "pergunta",
        pergunta: str = "",
        id_orientacao: int | None = None,
        encontrou: bool = False,
        ajudou: bool = False,
        tentativas: int = 1,
        tempo_segundos: float = 0.0,
        facilidade: int = 5,
        confianca: str | None = None,
        data: str | None = None,
    ) -> dict[str, Any]:
        """Registra um atendimento no histórico em memória e salva em JSON."""
        if isinstance(origem, dict):
            dados_entrada = origem
            texto_pergunta = str(dados_entrada.get("pergunta", "")).strip()
            if self.contem_dados_pessoais(texto_pergunta):
                raise ValueError(MENSAGEM_BLOQUEIO_LGPD)
            registro = {
                "data": str(
                    dados_entrada.get(
                        "data", datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    )
                ),
                "origem": str(dados_entrada.get("origem", "pergunta")),
                "pergunta": texto_pergunta,
                "id_orientacao": dados_entrada.get("id_orientacao"),
                "confianca": str(
                    dados_entrada.get(
                        "confianca",
                        "ALTA" if dados_entrada.get("encontrou") else "NÃO ENCONTRADA",
                    )
                ),
                "encontrou": bool(dados_entrada.get("encontrou", False)),
                "ajudou": bool(dados_entrada.get("ajudou", False)),
                "tentativas": int(dados_entrada.get("tentativas", 1)),
                "tempo_segundos": round(
                    float(
                        dados_entrada.get(
                            "tempo_segundos", dados_entrada.get("tempo", 0.0)
                        )
                    ),
                    1,
                ),
                "facilidade": int(dados_entrada.get("facilidade", 5)),
            }
        else:
            texto_pergunta = str(pergunta).strip()
            if self.contem_dados_pessoais(texto_pergunta):
                raise ValueError(MENSAGEM_BLOQUEIO_LGPD)
            nivel_confianca = confianca or (
                "ALTA" if encontrou else "NÃO ENCONTRADA"
            )
            registro = {
                "data": data or datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "origem": str(origem),
                "pergunta": texto_pergunta,
                "id_orientacao": id_orientacao,
                "confianca": str(nivel_confianca),
                "encontrou": bool(encontrou),
                "ajudou": bool(ajudou),
                "tentativas": int(tentativas),
                "tempo_segundos": round(float(tempo_segundos), 1),
                "facilidade": int(facilidade),
            }

        self.historico.append(registro)
        self._atendimentos_sessao += 1
        self._salvar_historico()
        return registro

    def registrar_avaliacao_final(self, nota: int) -> None:
        """Atualiza a nota de facilidade do último atendimento realizado nesta sessão."""
        if 1 <= int(nota) <= 5 and self._atendimentos_sessao > 0 and self.historico:
            self.historico[-1]["facilidade"] = int(nota)
            self._salvar_historico()

    def indicadores(self) -> dict[str, Any]:
        """Calcula, exibe no terminal e retorna os indicadores de desempenho."""
        total = len(self.historico)
        if total == 0:
            print("\nNenhum atendimento registrado até o momento.")
            return {
                "total_atendimentos": 0,
                "resposta_encontrada_pct": 0.0,
                "taxa_acerto_ajudou_pct": 0.0,
                "tempo_medio_segundos": 0.0,
                "tentativas_por_atendimento": 0.0,
                "facilidade_media": 0.0,
                "duvidas_sem_solucao": [],
            }

        qtd_encontrou = sum(1 for item in self.historico if item.get("encontrou"))
        qtd_ajudou = sum(1 for item in self.historico if item.get("ajudou"))

        resposta_encontrada_pct = round((qtd_encontrou / total) * 100, 1)
        taxa_acerto_ajudou_pct = round((qtd_ajudou / total) * 100, 1)

        tempos = [
            float(item.get("tempo_segundos", item.get("tempo", 0.0)))
            for item in self.historico
        ]
        tempo_medio_segundos = round(sum(tempos) / total, 1)

        tentativas_lista = [
            int(item.get("tentativas", 1)) for item in self.historico
        ]
        tentativas_por_atendimento = round(sum(tentativas_lista) / total, 2)

        notas_facilidade = [
            int(item["facilidade"])
            for item in self.historico
            if item.get("facilidade") is not None
            and str(item.get("facilidade")).strip() != ""
        ]
        facilidade_media = (
            round(sum(notas_facilidade) / len(notas_facilidade), 2)
            if notas_facilidade
            else 0.0
        )

        duvidas_sem_solucao = [
            str(item.get("pergunta", ""))
            for item in self.historico
            if not item.get("encontrou") or not item.get("ajudou")
        ]

        print("\n" + "=" * 62)
        print(f"INDICADORES DE ATENDIMENTO — {self.nome.upper()}")
        print("=" * 62)
        print(f"Total de atendimentos avaliados : {total}")
        print(f"Resposta encontrada (%)         : {resposta_encontrada_pct:.1f}%")
        print(f"Taxa de acerto: ajudou (%)      : {taxa_acerto_ajudou_pct:.1f}%")
        print(f"Tempo médio para encontrar      : {tempo_medio_segundos:.1f} s")
        print(f"Tentativas por atendimento      : {tentativas_por_atendimento:.2f}")
        print(f"Facilidade de uso (1 a 5)       : {facilidade_media:.2f} / 5.00")
        print("Lista de dúvidas sem solução    :")
        if duvidas_sem_solucao:
            for duvida in duvidas_sem_solucao:
                print(f"  - {duvida}")
        else:
            print("  - Nenhuma dúvida pendente.")
        print("=" * 62)

        return {
            "total_atendimentos": total,
            "resposta_encontrada_pct": resposta_encontrada_pct,
            "taxa_acerto_ajudou_pct": taxa_acerto_ajudou_pct,
            "tempo_medio_segundos": tempo_medio_segundos,
            "tentativas_por_atendimento": tentativas_por_atendimento,
            "facilidade_media": facilidade_media,
            "duvidas_sem_solucao": duvidas_sem_solucao,
        }

    def exportar_csv(self, caminho: str | None = None) -> str:
        """Exporta os atendimentos para CSV usando csv.DictWriter (UTF-8 com BOM)."""
        destino = Path(caminho or self.caminho_csv)
        destino.parent.mkdir(parents=True, exist_ok=True)

        with destino.open("w", encoding="utf-8-sig", newline="") as arquivo_csv:
            escritor = csv.DictWriter(
                arquivo_csv,
                fieldnames=COLUNAS_HISTORICO,
                extrasaction="ignore",
            )
            escritor.writeheader()
            for item in self.historico:
                linha = {
                    "data": item.get("data", ""),
                    "origem": item.get("origem", "pergunta"),
                    "pergunta": item.get("pergunta", ""),
                    "id_orientacao": (
                        "" if item.get("id_orientacao") is None else item.get("id_orientacao")
                    ),
                    "confianca": item.get("confianca", ""),
                    "encontrou": bool(item.get("encontrou", False)),
                    "ajudou": bool(item.get("ajudou", False)),
                    "tentativas": int(item.get("tentativas", 1)),
                    "tempo_segundos": round(
                        float(item.get("tempo_segundos", item.get("tempo", 0.0))), 1
                    ),
                    "facilidade": item.get("facilidade", ""),
                }
                escritor.writerow(linha)

        return str(destino)

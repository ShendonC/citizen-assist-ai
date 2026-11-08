"""Módulo da classe BaseConhecimento e busca por pontuação (PCP)."""

from __future__ import annotations

import json
from pathlib import Path

from orientacao import Orientacao


ACENTOS: dict[str, str] = {
    "á": "a",
    "à": "a",
    "ã": "a",
    "â": "a",
    "é": "e",
    "ê": "e",
    "í": "i",
    "ó": "o",
    "õ": "o",
    "ô": "o",
    "ú": "u",
    "ç": "c",
}


def normalizar(texto: str) -> str:
    """Normaliza um texto removendo acentos, pontuação e espaços extras."""
    texto = str(texto).lower().strip()
    for letra, troca in ACENTOS.items():
        texto = texto.replace(letra, troca)
    for sinal in "?!.,;:()":
        texto = texto.replace(sinal, " ")
    return " " + " ".join(texto.split()) + " "


class BaseConhecimento:
    """Gerencia o conjunto de orientações verificadas e a busca por regras."""

    def __init__(self, caminho: str = "data/base_conhecimento.json") -> None:
        self.caminho = str(caminho)
        self.orientacoes: list[Orientacao] = []

    def normalizar(self, texto: str) -> str:
        """Método utilitário que delega para a função de normalização."""
        return normalizar(texto)

    def carregar(self) -> bool:
        """Lê o arquivo JSON e popula a lista de objetos Orientacao sem travar."""
        caminho_arquivo = Path(self.caminho)
        try:
            with caminho_arquivo.open("r", encoding="utf-8-sig") as arquivo:
                dados = json.load(arquivo)

            if not isinstance(dados, list):
                print(
                    f"Aviso: formato inválido em '{self.caminho}'. "
                    "Esperava uma lista de orientações."
                )
                self.orientacoes = []
                return False

            orientacoes_carregadas: list[Orientacao] = []
            for item in dados:
                if isinstance(item, dict):
                    orientacoes_carregadas.append(Orientacao.from_dict(item))

            self.orientacoes = orientacoes_carregadas
            return True
        except FileNotFoundError:
            print(
                f"Aviso: arquivo de base de conhecimento não encontrado em "
                f"'{self.caminho}'. O sistema iniciará com base vazia."
            )
            self.orientacoes = []
            return False
        except json.JSONDecodeError as erro:
            print(
                f"Aviso: arquivo JSON corrompido em '{self.caminho}' ({erro}). "
                "O sistema iniciará com base vazia."
            )
            self.orientacoes = []
            return False
        except (KeyError, TypeError, ValueError, OSError) as erro:
            print(
                f"Aviso: erro ao processar '{self.caminho}' ({erro}). "
                "O sistema iniciará com base vazia."
            )
            self.orientacoes = []
            return False

    def categorias(self) -> list[str]:
        """Retorna a lista ordenada de categorias únicas disponíveis na base."""
        categorias_unicas = {orientacao.categoria for orientacao in self.orientacoes}
        return sorted(categorias_unicas)

    def por_categoria(self, categoria: str) -> list[Orientacao]:
        """Retorna todas as orientações pertencentes à categoria informada."""
        alvo_norm = normalizar(categoria).strip()
        filtradas = [
            orientacao
            for orientacao in self.orientacoes
            if normalizar(orientacao.categoria).strip() == alvo_norm
        ]
        return sorted(filtradas, key=lambda o: o.id)

    def pontuar(self, pergunta: str, orientacao: Orientacao) -> int:
        """Calcula a pontuação de relevância de uma orientação para a pergunta.

        Regras (Seção 6.2 do enunciado de PCP):
        - +3 pontos para cada palavra-chave da orientação presente na pergunta;
        - +1 ponto para cada palavra da pergunta (4 letras ou mais) no título.
        """
        pergunta_norm = normalizar(pergunta)
        titulo_norm = normalizar(orientacao.titulo)

        if not pergunta_norm.strip():
            return 0

        pontos = 0
        for chave in orientacao.palavras_chave:
            chave_norm = normalizar(chave)
            if chave_norm.strip() and chave_norm in pergunta_norm:
                pontos += 3

        palavras_contabilizadas: set[str] = set()
        for palavra in pergunta_norm.split():
            if len(palavra) >= 4 and palavra not in palavras_contabilizadas:
                palavras_contabilizadas.add(palavra)
                if f" {palavra} " in titulo_norm or palavra in titulo_norm:
                    pontos += 1

        return pontos

    @staticmethod
    def classificar_confianca(pontos: int) -> str:
        """Retorna o nível de confiança ('ALTA', 'MÉDIA' ou 'BAIXA')."""
        if pontos >= 6:
            return "ALTA"
        if pontos >= 3:
            return "MÉDIA"
        return "BAIXA"

    def buscar(self, pergunta: str) -> list[tuple[int, Orientacao]]:
        """Retorna lista de tuplas (pontos, orientacao) da maior para a menor."""
        if not self.orientacoes:
            return []

        avaliadas: list[tuple[int, Orientacao]] = []
        for orientacao in self.orientacoes:
            pontos = self.pontuar(pergunta, orientacao)
            if pontos > 0:
                avaliadas.append((pontos, orientacao))

        avaliadas.sort(key=lambda item: (-item[0], item[1].id))
        return avaliadas

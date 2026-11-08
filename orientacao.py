"""Módulo da classe Orientacao do sistema Citizen Assist AI (PCP)."""

from __future__ import annotations

from typing import Any


AVISO_CANAL_NAO_OFICIAL = "Aviso: este assistente NÃO é um canal oficial."


class Orientacao:
    """Representa um registro verificado de orientação ao cidadão."""

    def __init__(
        self,
        id: int,
        categoria: str,
        titulo: str,
        palavras_chave: list[str],
        resposta: str,
        documentos: list[str],
        onde: str,
        fonte: str,
        verificado_em: str,
    ) -> None:
        self.id = int(id)
        self.categoria = str(categoria).strip()
        self.titulo = str(titulo).strip()
        self.palavras_chave = [str(p).strip() for p in palavras_chave]
        self.resposta = str(resposta).strip()
        self.documentos = [str(d).strip() for d in documentos]
        self.onde = str(onde).strip()
        self.fonte = str(fonte).strip()
        self.verificado_em = str(verificado_em).strip()

    def exibir(
        self,
        confianca: str | None = None,
        pontos: int | None = None,
    ) -> str:
        """Exibe a orientação formatada no terminal e retorna o texto gerado."""
        linhas: list[str] = []
        if confianca is not None and pontos is not None:
            linhas.append(f"Confiança da resposta: {confianca} ({pontos} pontos)")
            linhas.append("")
        elif confianca is not None:
            linhas.append(f"Confiança da resposta: {confianca}")
            linhas.append("")

        linhas.append(f">> {self.titulo} [{self.categoria}]")
        linhas.append(self.resposta)

        if self.documentos:
            linhas.append("Documentos necessários:")
            for doc in self.documentos:
                linhas.append(f"  - {doc}")

        linhas.append(f"Onde: {self.onde}")
        linhas.append(f"Fonte: {self.fonte} (verificado em {self.verificado_em})")
        linhas.append(AVISO_CANAL_NAO_OFICIAL)

        bloco = "\n".join(linhas)
        print(bloco)
        return bloco

    def to_dict(self) -> dict[str, Any]:
        """Converte o objeto Orientacao em dicionário serializável."""
        return {
            "id": self.id,
            "categoria": self.categoria,
            "titulo": self.titulo,
            "palavras_chave": list(self.palavras_chave),
            "resposta": self.resposta,
            "documentos": list(self.documentos),
            "onde": self.onde,
            "fonte": self.fonte,
            "verificado_em": self.verificado_em,
        }

    @classmethod
    def from_dict(cls, dados: dict[str, Any]) -> "Orientacao":
        """Instancia uma Orientacao a partir de um dicionário do JSON."""
        return cls(
            id=dados["id"],
            categoria=dados["categoria"],
            titulo=dados["titulo"],
            palavras_chave=dados.get("palavras_chave", []),
            resposta=dados["resposta"],
            documentos=dados.get("documentos", []),
            onde=dados["onde"],
            fonte=dados["fonte"],
            verificado_em=dados["verificado_em"],
        )

    def __repr__(self) -> str:
        return (
            f"Orientacao(id={self.id}, categoria={self.categoria!r}, "
            f"titulo={self.titulo!r})"
        )

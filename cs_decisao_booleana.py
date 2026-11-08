# -*- coding: utf-8 -*-
"""Computer Science: motor de decisão booleana do Citizen Assist AI.

Lê a lógica FEITA À MÃO pelo grupo em cs_regras.json (mintermos da tabela-verdade e a
expressão simplificada). Este arquivo não contém a tabela, o mapa de Karnaugh nem o circuito.

    python cs_decisao_booleana.py            # menu: consultar e validar
    python cs_decisao_booleana.py --validar  # só a validação das 2^n combinações
"""
import itertools
import json
import re
import sys
from pathlib import Path

REGRAS = Path(__file__).with_name("cs_regras.json")
AVISO = ("Protótipo educacional: não é um canal oficial e não confirma a concessão de serviços "
         "ou direitos. Nenhum dado pessoal é pedido ou guardado. Confirme no canal oficial.")
FALTA = ("A lógica ainda não foi cadastrada. Faça à mão a tabela-verdade, a simplificação e o "
         "Karnaugh (roteiro: CS_ROTEIRO_FEITO_A_MAO.pdf) e preencha "
         "'mintermos' e 'expr_simplificada' em cs_regras.json.")
SIM = {"1", "s", "sim"}
NAO = {"0", "n", "nao", "não"}


def carregar():
    r = json.loads(REGRAS.read_text(encoding="utf-8-sig"))
    r["nomes"] = [v["nome"] for v in r["variaveis"]]
    return r


def pronto(r):
    return r.get("mintermos") is not None and bool(r.get("expr_simplificada"))


def avaliar(expr, nomes, valores):
    """Avalia 'A and B and (C or D)' só com variáveis, and/or/not e parênteses."""
    ok = set(nomes) | {"and", "or", "not"}
    if any(t not in ok for t in re.findall(r"[A-Za-z_]\w*", expr)) or re.search(r"[^\w\s()]", expr):
        raise ValueError(f"Expressão inválida (use só {', '.join(nomes)}, and, or, not e parênteses): {expr!r}")
    return bool(eval(expr, {"__builtins__": {}}, dict(zip(nomes, map(bool, valores)))))


def decidir(r, valores):
    s = avaliar(r["expr_simplificada"], r["nomes"], valores)
    return s, r["saida"]["orientacao_1" if s else "orientacao_0"]


def validar(r, imprimir=True):
    """Item 8: regra original (mintermos) x expressão simplificada x resultado executado."""
    n, tudo_ok = len(r["nomes"]), True
    if imprimir:
        print(" i | " + " ".join(r["nomes"]) + " | original | simplif. | executado | ok")
    for i, v in enumerate(itertools.product((0, 1), repeat=n)):
        original = i in r["mintermos"]
        simpl = avaliar(r["expr_simplificada"], r["nomes"], v)
        exec_ = decidir(r, v)[0]
        ok = original == simpl == exec_
        if r.get("expr_de_morgan"):
            ok = ok and avaliar(r["expr_de_morgan"], r["nomes"], v) == original
        tudo_ok &= ok
        if imprimir:
            print(f"{i:2d} | " + " ".join(map(str, v)) + f" |    {int(original)}     |    {int(simpl)}     |     {int(exec_)}     | {'OK' if ok else 'FALHOU'}")
    if imprimir:
        print(f"\n{2 ** n} combinações: " + ("todas equivalentes." if tudo_ok else "HÁ DIVERGÊNCIA entre a tabela-verdade, a expressão e o programa."))
    return tudo_ok


def ler_bit(v):
    while True:
        try:
            t = input(f"  {v['nome']} ({v['descricao']}): 1 = {v['significado_1']}; 0 = {v['significado_0']}\n  > ").strip().lower()
        except EOFError:
            return None
        if t in SIM | NAO:
            return int(t in SIM)
        print("  Resposta inválida. Digite 1 (sim) ou 0 (não). Não digite dados pessoais.")


def consultar(r):
    print(f"\n{r['situacao']}\n")
    vals = [ler_bit(v) for v in r["variaveis"]]
    if None in vals:
        return
    s, texto = decidir(r, vals)
    print(f"\n{r['saida']['nome']} = {int(s)}\n{texto}\n{AVISO}")


def executar_menu_cs():
    r = carregar()
    print("\n=== Ciência da Computação: decisão booleana ===")
    if not pronto(r):
        print(FALTA)
        return
    while True:
        try:
            op = input("\n[1] Consultar orientação  [2] Validar as combinações  [0] Voltar\n> ").strip()
        except EOFError:
            return
        if op == "1":
            consultar(r)
        elif op == "2":
            validar(r)
        elif op == "0":
            return
        else:
            print("Opção inválida.")


if __name__ == "__main__":
    regras = carregar()
    if "--validar" in sys.argv:
        if not pronto(regras):
            sys.exit(FALTA)
        sys.exit(0 if validar(regras) else 1)
    executar_menu_cs()

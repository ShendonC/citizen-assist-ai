"""Fecha os testes com usuarios (PCP, ERS e PAI) a partir dos registros reais.

Uso (na pasta do projeto):
    python testes_usuarios/resumo_testes.py --pessoas 4 --melhoria "Adicionamos a palavra-chave X"

Le data/historico.json (gerado pelo main.py) e testes_usuarios/folha_pai.csv.
Atualiza o bloco de testes do README.md e cria testes_usuarios/PAI_resultados.md.
"""
import argparse, csv, json, re, sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
INI, FIM = "<!-- TESTES:INICIO -->", "<!-- TESTES:FIM -->"


def v(x, n=1): return f"{x:.{n}f}".replace(".", ",")


def pcp(pessoas, melhoria):
    h = json.loads((RAIZ / "data/historico.json").read_text(encoding="utf-8-sig"))
    n = len(h)
    if n < 10 or pessoas < 3:
        sys.exit(f"PCP exige 10+ atendimentos e 3+ pessoas de fora. Tem {n} atendimentos e {pessoas} pessoas.")
    achou = sum(bool(i.get("encontrou")) for i in h); ajudou = sum(bool(i.get("ajudou")) for i in h)
    tempo = sum(float(i.get("tempo_segundos", 0)) for i in h) / n
    tent = sum(int(i.get("tentativas", 1)) for i in h) / n
    nf = [int(i["facilidade"]) for i in h if str(i.get("facilidade", "")).strip() != ""]
    sem = [i.get("pergunta", "") for i in h if not i.get("encontrou") or not i.get("ajudou")]
    base = json.loads((RAIZ / "data/base_conhecimento.json").read_text(encoding="utf-8-sig"))
    base = base if isinstance(base, list) else next(x for x in base.values() if isinstance(x, list))
    ener = {o["id"] for o in base if str(o.get("categoria", "")).startswith("Energia")}
    n_ener = sum(i.get("id_orientacao") in ener for i in h)
    bloco = [
        INI,
        f"* **Amostra:** {pessoas} pessoas de fora da equipe, {n} atendimentos registrados em `data/historico.json` e exportados em `data/atendimentos.csv`.",
        f"* **Atendimentos sobre energia (ERS):** {n_ener} de {n}",
        f"* **Resposta encontrada (%):** {v(achou / n * 100)}%",
        f"* **Taxa de acerto (ajudou, %):** {v(ajudou / n * 100)}%",
        f"* **Tempo médio para encontrar:** {v(tempo)} segundos",
        f"* **Tentativas por atendimento:** {v(tent, 2)}",
        f"* **Facilidade de uso (1 a 5):** {v(sum(nf) / len(nf), 2) if nf else 'sem notas'}",
        "* **Dúvidas sem solução:** " + ("; ".join(f'"{p}"' for p in sem) if sem else "nenhuma"),
        f"* **Melhoria feita a partir do teste:** {melhoria}",
        FIM,
    ]
    p = RAIZ / "README.md"; t = p.read_text(encoding="utf-8-sig")
    t, k = re.subn(re.escape(INI) + r".*?" + re.escape(FIM), "\n".join(bloco).replace("\\", "\\\\"), t, flags=re.S)
    if k != 1: sys.exit("Marcadores de teste nao encontrados no README.md")
    p.write_text(t, encoding="utf-8-sig"); print(f"README atualizado ({n} atendimentos, {pessoas} pessoas).")


def pai():
    f = RAIZ / "testes_usuarios/folha_pai.csv"
    rows = list(csv.DictReader(f.open(encoding="utf-8-sig")))
    if len(rows) < 5: sys.exit(f"PAI exige 5+ pessoas cronometradas. A folha tem {len(rows)}.")
    L = ["| Participante | Tarefa 1 (s) | Tarefa 2 (s) | Tarefa 3 (s) | Tempo médio (s) | Tarefas concluídas | Nota de facilidade (1 a 5) |", "|---|---:|---:|---:|---:|---:|---:|"]
    T, ok, notas = [[], [], []], 0, []
    for r in rows:
        t = [float(r[f"tarefa{i}_s"].replace(",", ".")) for i in (1, 2, 3)]
        c = sum(r[f"tarefa{i}_ok"].strip().lower() in ("s", "sim", "1") for i in (1, 2, 3))
        q = [int(r[f"q{i}"]) for i in range(1, 6)]
        assert all(1 <= x <= 5 for x in q), f"nota fora de 1-5 em {r['participante']}"
        for i in range(3): T[i].append(t[i])
        ok += c; notas.append(sum(q) / 5)
        L.append(f"| {r['participante']} | {v(t[0])} | {v(t[1])} | {v(t[2])} | {v(sum(t) / 3)} | {c}/3 | {v(sum(q) / 5, 2)} |")
    m = [sum(x) / len(x) for x in T]; n = len(rows)
    L.append(f"| **Média** | {v(m[0])} | {v(m[1])} | {v(m[2])} | {v(sum(m) / 3)} | {ok}/{3 * n} ({v(ok / (3 * n) * 100, 0)}%) | {v(sum(notas) / n, 2)} |")
    L += ["", f"- **Tempo para encontrar a informação:** média de {v(sum(m) / 3)} s por tarefa, com {n} pessoas de fora do grupo.",
          f"- **Facilidade de utilização:** média de {v(sum(notas) / n, 2)} de 5,00 no questionário de 5 perguntas."]
    (RAIZ / "testes_usuarios/PAI_resultados.md").write_text("\n".join(L) + "\n", encoding="utf-8-sig")
    print("\n".join(L))


if __name__ == "__main__":
    a = argparse.ArgumentParser(); a.add_argument("--pessoas", type=int, required=True); a.add_argument("--melhoria", required=True)
    g = a.parse_args(); pcp(g.pessoas, g.melhoria); pai()

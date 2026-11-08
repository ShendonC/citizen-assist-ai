"""
Modelagem Linear para Aprendizado de Maquina - Global Solution 2026.2 (FIAP)
Tema: CitizenTech - inclusao digital e acesso a servicos publicos por assistente digital.

Base: dados reais do IBGE (Censo 2022 e PIB dos Municipios 2022) para os 5.570 municipios.
Arquivo: data/base_municipios_ibge.csv (fontes e data da consulta em data/fontes_base_municipios_ibge.txt).

Como executar (na pasta do projeto):  python ml_estatistica_cidada.py
Gera: 7 graficos em relatorios/graficos_ml/ e data/ml_resultados.json
"""
import json
import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.metrics import confusion_matrix, accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

BASE = Path(__file__).resolve().parent
GRAF = BASE / "relatorios" / "graficos_ml"
GRAF.mkdir(parents=True, exist_ok=True)

Y_COL, Y_NOME = "pct_internet", "Domicílios com internet (%)"
X_NOMES = {
    "taxa_alfabetizacao_15mais_pct": "Alfabetização 15+ (%)",
    "pib_pc_mil": "PIB per capita (mil R$)",
    "idade_mediana_anos": "Idade mediana (anos)",
    "media_moradores_por_domicilio": "Moradores por domicílio",
}
X1 = "taxa_alfabetizacao_15mais_pct"
LIMIAR_ALTA = 80.0  # "alta conectividade": pelo menos 8 em cada 10 domicilios com internet
plt.rcParams.update({"font.size": 10, "axes.spines.top": False, "axes.spines.right": False})
AZUL, LARANJA, CINZA = "#1f4e79", "#c8731a", "#6b6b6b"
R = {}  # resultados para o relatorio


def carregar():
    CSV = BASE / "data" / "base_municipios_ibge.csv"
    if not CSV.exists():  # entrega solta no Portal: CSV ao lado do .py
        CSV = BASE / "base_municipios_ibge.csv"
    d = pd.read_csv(CSV, encoding="utf-8-sig", dtype={"cod_ibge": str})
    d[Y_COL] = d.domicilios_com_internet / d.domicilios_ocupados * 100
    d["pib_pc_mil"] = d.pib_2022_mil_reais / d.populacao_2022  # mil R$ por habitante
    d["regiao"] = d.cod_ibge.str[0].map({"1": "Norte", "2": "Nordeste", "3": "Sudeste", "4": "Sul", "5": "Centro-Oeste"})
    assert len(d) == 5570 and d.isna().sum().sum() == 0, "base incompleta"
    return d


def classificar(p):
    if p <= 1e-9: return "evento impossível (P = 0%)"
    if p >= 1 - 1e-9: return "evento certo (P = 100%)"
    if abs(p - 0.5) < 1e-4: return "evento equiprovável (P = 50%)"
    if p >= 0.75: return "evento muito provável (P acima de 75%)"
    if p > 0.5: return "evento provável (P acima de 50%)"
    if p > 0.25: return "evento menos provável que o seu contrário (P abaixo de 50%)"
    return "evento improvável (P abaixo de 25%)"


def salvar(nome):
    plt.tight_layout(); plt.savefig(GRAF / nome, dpi=150); plt.close()


# ---------------------------------------------------------------- item 01
def item01(d):
    cols = [Y_COL] + list(X_NOMES)
    R["n"] = len(d)
    R["descritiva"] = d[cols].describe().T[["mean", "std", "min", "50%", "max"]].round(4).to_dict("index")
    R["brasil_pct_internet"] = d.domicilios_com_internet.sum() / d.domicilios_ocupados.sum() * 100
    R["regiao"] = (d.groupby("regiao").agg(municipios=(Y_COL, "size"), media=(Y_COL, "mean"),
                   abaixo70=(Y_COL, lambda s: (s < 70).mean() * 100)).round(2).to_dict("index"))
    R["abaixo70_n"] = int((d[Y_COL] < 70).sum())
    R["pop_abaixo70"] = int(d.loc[d[Y_COL] < 70, "populacao_2022"].sum())
    R["pop_total"] = int(d.populacao_2022.sum())
    R["uf_menor"] = d.groupby("uf")[Y_COL].mean().sort_values().head(3).round(2).to_dict()
    R["uf_maior"] = d.groupby("uf")[Y_COL].mean().sort_values().tail(3).round(2).to_dict()


# ---------------------------------------------------------------- item 02
def item02(d):
    y = d[Y_COL]
    mu, sd, med = y.mean(), y.std(ddof=0), y.median()
    pa = stats.norm.cdf(mu, mu, sd)           # P(Y < media)
    pb = 1 - stats.norm.cdf(med, mu, sd)      # P(Y > mediana)
    R["i02"] = dict(media=mu, desvio_pop=sd, mediana=med, pa=pa, pb=pb, ca=classificar(pa), cb=classificar(pb))
    fig, ax = plt.subplots(figsize=(8, 4.2))
    ax.hist(y, bins=40, density=True, color=AZUL, alpha=.75, label="Municípios (histograma)")
    xs = np.linspace(y.min(), y.max(), 300)
    ax.plot(xs, stats.norm.pdf(xs, mu, sd), color=LARANJA, lw=2, label="Normal(μ, σ)")
    ax.axvline(mu, color="k", ls="--", lw=1, label=f"Média = {mu:.2f}")
    ax.axvline(med, color=CINZA, ls=":", lw=1.5, label=f"Mediana = {med:.2f}")
    ax.set(title="Domicílios com internet nos municípios brasileiros (Censo 2022)", xlabel=Y_NOME, ylabel="Densidade")
    ax.legend(frameon=False); salvar("item02_distribuicao_normal.png")


# ---------------------------------------------------------------- item 03
def ztest(d, regiao, n, alfa, cauda, seed):
    y = d[Y_COL]; mu0, sd = y.mean(), y.std(ddof=0)
    amostra = d[d.regiao == regiao].sample(n, random_state=seed)[Y_COL]
    xb = amostra.mean(); z = (xb - mu0) / (sd / np.sqrt(n))
    if cauda == "esq":
        zc = stats.norm.ppf(alfa); p = stats.norm.cdf(z); rej = z < zc
    else:
        zc = stats.norm.ppf(1 - alfa); p = 1 - stats.norm.cdf(z); rej = z > zc
    return dict(regiao=regiao, n=n, alfa=alfa, cauda=cauda, seed=seed, mu0=mu0, sigma=sd, xbarra=xb, z=z, zcrit=zc, p=p, rejeita=bool(rej))


def item03(d):
    a = ztest(d, "Norte", 20, 0.06, "esq", 2026)
    b = ztest(d, "Sul", 25, 0.09, "dir", 2026)
    R["i03"] = dict(a=a, b=b)
    fig, axs = plt.subplots(1, 2, figsize=(10, 3.8))
    for ax, t, tit in [(axs[0], a, "(a) H1: μ < μ0 | α = 6% | n = 20 (Norte)"), (axs[1], b, "(b) H1: μ > μ0 | α = 9% | n = 25 (Sul)")]:
        xs = np.linspace(-4.5, 4.5, 400); ax.plot(xs, stats.norm.pdf(xs), color=AZUL)
        m = xs <= t["zcrit"] if t["cauda"] == "esq" else xs >= t["zcrit"]
        ax.fill_between(xs[m], stats.norm.pdf(xs[m]), color=LARANJA, alpha=.5, label="Região de rejeição")
        ax.axvline(t["z"], color="k", ls="--", label=f"Z calculado = {t['z']:.2f}")
        ax.set(title=tit, xlabel="Z", ylabel="Densidade"); ax.legend(frameon=False, fontsize=8)
    salvar("item03_testes_hipotese.png")


# ---------------------------------------------------------------- OLS (numpy)
def ols(X, y, nomes):
    n, k = X.shape
    A = np.column_stack([np.ones(n), X]); beta = np.linalg.lstsq(A, y, rcond=None)[0]
    res = y - A @ beta; sse = res @ res; sst = ((y - y.mean()) ** 2).sum(); ssr = sst - sse
    r2 = ssr / sst; r2aj = 1 - (1 - r2) * (n - 1) / (n - k - 1)
    F = (ssr / k) / (sse / (n - k - 1)); pF = 1 - stats.f.cdf(F, k, n - k - 1)
    se = np.sqrt(np.diag(sse / (n - k - 1) * np.linalg.inv(A.T @ A))); t = beta / se
    p = 2 * (1 - stats.t.cdf(np.abs(t), n - k - 1))
    return dict(beta=dict(zip(["const"] + nomes, beta)), r2=r2, r2aj=r2aj, F=F, pF=pF, gl=(k, n - k - 1),
                t=dict(zip(["const"] + nomes, t)), p=dict(zip(["const"] + nomes, p)), erro_padrao_residuo=float(np.sqrt(sse / (n - k - 1))))


# ---------------------------------------------------------------- item 04
def item04(d):
    x, y = d[X1].values, d[Y_COL].values
    cov = np.cov(x, y, ddof=1)[0, 1]; r, pr = stats.pearsonr(x, y)
    m = ols(x.reshape(-1, 1), y, [X1])
    x0 = 90.0; y0 = m["beta"]["const"] + m["beta"][X1] * x0
    R["i04"] = dict(cov=cov, r=r, p_r=pr, modelo=m, x0=x0, y0=y0)
    # (a)+(d) dispersao com reta
    fig, ax = plt.subplots(figsize=(7.5, 5))
    ax.scatter(x, y, s=7, alpha=.25, color=AZUL, edgecolors="none")
    xs = np.linspace(x.min(), x.max(), 100)
    ax.plot(xs, m["beta"]["const"] + m["beta"][X1] * xs, color=LARANJA, lw=2.2,
            label=f"ŷ = {m['beta']['const']:.2f} + {m['beta'][X1]:.3f}·x   (R² = {m['r2']:.3f})")
    ax.set(title="Internet nos domicílios x alfabetização dos municípios", xlabel=X_NOMES[X1], ylabel=Y_NOME)
    ax.legend(frameon=False); salvar("item04_dispersao_regressao.png")
    # (c) correlacao (mapa de calor 2x2 com r)
    fig, ax = plt.subplots(figsize=(4.6, 4))
    M = np.array([[1, r], [r, 1]]); im = ax.imshow(M, cmap="RdBu_r", vmin=-1, vmax=1)
    lab = ["Alfabetização", "Internet"]; ax.set_xticks([0, 1], lab); ax.set_yticks([0, 1], lab)
    for i in range(2):
        for j in range(2): ax.text(j, i, f"{M[i, j]:.3f}", ha="center", va="center", color="w" if abs(M[i, j]) > .6 else "k", fontsize=13)
    ax.set_title("Correlação linear de Pearson"); plt.colorbar(im, fraction=.046); salvar("item04_correlacao.png")


# ---------------------------------------------------------------- item 05
def item05(d):
    xs = list(X_NOMES); X = d[xs].values; y = d[Y_COL].values
    m = ols(X, y, xs)
    sk = LinearRegression().fit(X, y)
    assert np.allclose(sk.coef_, [m["beta"][c] for c in xs]) and np.isclose(sk.intercept_, m["beta"]["const"]), "OLS diverge do sklearn"
    cols = [Y_COL] + xs
    cov, cor = d[cols].cov(), d[cols].corr()
    exemplo = {"taxa_alfabetizacao_15mais_pct": 90.0, "pib_pc_mil": 25.0, "idade_mediana_anos": 35.0, "media_moradores_por_domicilio": 2.8}
    yhat = m["beta"]["const"] + sum(m["beta"][c] * exemplo[c] for c in xs)
    R["i05"] = dict(modelo=m, cov=cov.round(4).to_dict(), cor=cor.round(4).to_dict(), exemplo=exemplo, yhat=yhat)
    curto = ["Internet", "Alfabet.", "PIB pc", "Idade med.", "Moradores"]
    # (a) matriz de dispersao (amostra de 1500 municipios para legibilidade)
    s = d[cols].sample(1500, random_state=1); fig, axs = plt.subplots(5, 5, figsize=(10, 10))
    for i, ci in enumerate(cols):
        for j, cj in enumerate(cols):
            ax = axs[i, j]
            if i == j: ax.hist(s[ci], bins=25, color=AZUL, alpha=.8)
            else: ax.scatter(s[cj], s[ci], s=4, alpha=.3, color=AZUL, edgecolors="none")
            ax.set_xticks([]); ax.set_yticks([])
            if j == 0: ax.set_ylabel(curto[i], fontsize=9)
            if i == 4: ax.set_xlabel(curto[j], fontsize=9)
    fig.suptitle("Matriz de dispersão (amostra aleatória de 1.500 municípios)", y=.995); salvar("item05_dispersao_multivariada.png")
    # (c) mapa de calor de Pearson
    fig, ax = plt.subplots(figsize=(6.2, 5.2)); C = cor.values
    im = ax.imshow(C, cmap="RdBu_r", vmin=-1, vmax=1); ax.set_xticks(range(5), curto, rotation=30); ax.set_yticks(range(5), curto)
    for i in range(5):
        for j in range(5): ax.text(j, i, f"{C[i, j]:.2f}", ha="center", va="center", color="w" if abs(C[i, j]) > .6 else "k", fontsize=10)
    ax.set_title("Correlação linear de Pearson (5.570 municípios)"); plt.colorbar(im, fraction=.046); salvar("item05_heatmap_pearson.png")


# ---------------------------------------------------------------- item 06
def item06(d):
    xs = list(X_NOMES); X = d[xs].values; y = (d[Y_COL] >= LIMIAR_ALTA).astype(int).values
    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=.2, random_state=42, stratify=y)
    sc = StandardScaler().fit(Xtr)
    lg = LogisticRegression(max_iter=5000).fit(sc.transform(Xtr), ytr)  # L2 padrao (C=1); n grande: efeito desprezivel
    coef = lg.coef_[0] / sc.scale_; b0 = lg.intercept_[0] - (lg.coef_[0] * sc.mean_ / sc.scale_).sum()
    pred = lg.predict(sc.transform(Xte)); cm = confusion_matrix(yte, pred)
    exemplo = {"taxa_alfabetizacao_15mais_pct": 90.0, "pib_pc_mil": 25.0, "idade_mediana_anos": 35.0, "media_moradores_por_domicilio": 2.8}
    z = b0 + sum(c * exemplo[k] for c, k in zip(coef, xs)); p = 1 / (1 + np.exp(-z))
    R["i06"] = dict(limiar=LIMIAR_ALTA, prevalencia=float(y.mean()), b0=float(b0), coef=dict(zip(xs, map(float, coef))),
                    cm=cm.tolist(), acc_teste=float(accuracy_score(yte, pred)), acc_treino=float(accuracy_score(ytr, lg.predict(sc.transform(Xtr)))),
                    n_treino=len(ytr), n_teste=len(yte), exemplo=exemplo, p_exemplo=float(p), classe_exemplo=int(p >= .5))
    fig, ax = plt.subplots(figsize=(4.8, 4.2)); ax.imshow(cm, cmap="Blues")
    ax.set_xticks([0, 1], ["Prevista: baixa", "Prevista: alta"]); ax.set_yticks([0, 1], ["Real: baixa", "Real: alta"])
    for i in range(2):
        for j in range(2): ax.text(j, i, cm[i, j], ha="center", va="center", fontsize=16, color="w" if cm[i, j] > cm.max() / 2 else "k")
    ax.set_title(f"Matriz de confusão (teste, n = {len(yte)})\nAcurácia = {R['i06']['acc_teste']:.1%}"); salvar("item06_matriz_confusao.png")


def main():
    d = carregar()
    for f in (item01, item02, item03, item04, item05, item06): f(d)
    (BASE / "data").mkdir(exist_ok=True)
    (BASE / "data" / "ml_resultados.json").write_text(json.dumps(R, ensure_ascii=False, indent=1, default=float), encoding="utf-8")
    i = R["i02"]; a, b = R["i03"]["a"], R["i03"]["b"]; m4 = R["i04"]["modelo"]; m5 = R["i05"]["modelo"]; l = R["i06"]
    print(f"[01] {R['n']} municipios | Y = {Y_NOME}: media {i['media']:.2f}, desvio {i['desvio_pop']:.2f}, mediana {i['mediana']:.2f}")
    print(f"[02] P(Y<media) = {i['pa']:.4f} ({i['ca']}) | P(Y>mediana) = {i['pb']:.4f} ({i['cb']})")
    for k, t in (("a", a), ("b", b)):
        print(f"[03{k}] {t['regiao']} n={t['n']} alfa={t['alfa']:.0%}: x̄={t['xbarra']:.2f} mu0={t['mu0']:.2f} Z={t['z']:.3f} Zcrit={t['zcrit']:.3f} p={t['p']:.4f} -> {'rejeita' if t['rejeita'] else 'nao rejeita'} H0")
    print(f"[04] cov={R['i04']['cov']:.3f} r={R['i04']['r']:.4f} | y = {m4['beta']['const']:.3f} + {m4['beta'][X1]:.4f} x | R2={m4['r2']:.4f} F={m4['F']:.1f} (p={m4['pF']:.2e}) | x=90 -> {R['i04']['y0']:.2f}")
    print(f"[05] R2={m5['r2']:.4f} R2aj={m5['r2aj']:.4f} F={m5['F']:.1f} | " + " ".join(f"{k}={v:.4f}" for k, v in m5['beta'].items()) + f" | previsao = {R['i05']['yhat']:.2f}")
    print(f"[06] limiar {l['limiar']:.0f}% | acc teste {l['acc_teste']:.4f} (treino {l['acc_treino']:.4f}) | cm {l['cm']} | exemplo p={l['p_exemplo']:.3f} -> classe {l['classe_exemplo']}")
    print("Graficos em", GRAF, "| resultados em data/ml_resultados.json")


if __name__ == "__main__":
    main()

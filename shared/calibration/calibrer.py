#!/usr/bin/env python3
"""
calibrer.py : recalibre les poids de hookscore_fr.py sur TES reels.

C'est le script qui a produit hookscore_fr_poids.json. Les données de
calibration ne sont pas dans le repo (ce sont des transcripts privés), mais la
méthode l'est : tu peux la refaire sur ton propre compte.

Entrée : un fichier TSV avec une ligne d'en-tête et au moins deux colonnes.
    hook    perf
    J'ai perdu 18 000 € sur un seul contrat.    3.2
`hook` = la première phrase dite dans le reel (transcription, pas la légende).
`perf` = vues du reel / médiane des vues des reels publiés autour de lui
(25 avant, 25 après). Un « hit » = perf >= 2. Une colonne `annee` facultative
active le test « appris sur le passé, testé sur la suite ».

Méthode :
  1. hookscore_fr.features() sur chaque hook : 5 mesures (0 à 1) et 3 pièges (0 ou 1).
  2. Régression logistique (hit ou pas), pénalité L2, variables centrées-réduites.
  3. Contrainte de sens : une mesure ne peut que faire monter le score, un piège
     que le faire baisser. Si les données veulent l'inverse, la variable sort du
     modèle (poids 0) et le rapport le dit.
  4. AUC en validation croisée 5 blocs, répétée 20 fois, contrainte comprise.
     AUC 0,50 = pile ou face, 1,00 = parfait.
  5. Modèle final ajusté sur tout le corpus. Le score affiché par
     hookscore_fr.py est le rang du hook parmi ceux du corpus (centiles).

Aucune donnée brute n'est écrite dans le fichier de poids : des coefficients,
des centiles et des agrégats.

Méthode adaptée de celle décrite dans instagram-agent-skill (Jake Schincariol, MIT).

Usage
  python3 calibrer.py corpus.tsv --out ../hookscore_fr_poids.json
  python3 calibrer.py corpus.tsv             # rapport seul, rien d'écrit
"""

import argparse
import datetime
import json
import math
import os
import random
import statistics
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
import hookscore_fr as hs  # noqa: E402

TRAPS = [p["mesure"] for p in hs.PIEGES if "mesure" in p]
KEYS = hs.FEATURE_KEYS + TRAPS
SIGN = {k: (-1 if k in TRAPS else 1) for k in KEYS}
L2 = 10.0         # pénalité, sur variables centrées-réduites
HIT = 2.0         # perf à partir de laquelle un reel compte comme un hit


def read_tsv(path):
    lines = [l.rstrip("\n") for l in open(path, encoding="utf-8") if l.strip()]
    head = [c.strip().lower() for c in lines[0].split("\t")]
    rows = []
    for line in lines[1:]:
        cells = dict(zip(head, line.split("\t")))
        try:
            perf = float(cells["perf"].replace(",", "."))
        except (KeyError, ValueError):
            continue
        if cells.get("hook", "").strip():
            rows.append({"hook": cells["hook"].strip(), "perf": perf,
                         "hit": int(perf >= HIT), "annee": cells.get("annee", "").strip()})
    return rows


def auc(scores, labels):
    """Probabilité qu'un hit pris au hasard soit mieux noté qu'un raté pris au hasard."""
    pairs = sorted(zip(scores, labels))
    n1 = sum(labels)
    n0 = len(labels) - n1
    if not n1 or not n0:
        return float("nan")
    rank_sum, i = 0.0, 0
    while i < len(pairs):
        j = i
        while j < len(pairs) and pairs[j][0] == pairs[i][0]:
            j += 1
        rank_sum += (i + j + 1) / 2 * sum(l for _, l in pairs[i:j])   # rang moyen des ex aequo
        i = j
    return (rank_sum - n1 * (n1 + 1) / 2) / (n1 * n0)


def solve(A, b):
    """Élimination de Gauss avec pivot partiel. A est petite : une ligne par variable."""
    n = len(b)
    M = [row[:] + [v] for row, v in zip(A, b)]
    for c in range(n):
        p = max(range(c, n), key=lambda r: abs(M[r][c]))
        M[c], M[p] = M[p], M[c]
        for r in range(c + 1, n):
            f = M[r][c] / M[c][c]
            for j in range(c, n + 1):
                M[r][j] -= f * M[c][j]
    x = [0.0] * n
    for r in range(n - 1, -1, -1):
        x[r] = (M[r][n] - sum(M[r][j] * x[j] for j in range(r + 1, n))) / M[r][r]
    return x


def fit_logistic(X, y, l2=L2, iters=25):
    """Régression logistique pénalisée (Newton). Retourne (b0, betas) en unités d'origine."""
    cols = list(zip(*X))
    mu = [statistics.mean(c) for c in cols]
    sd = [statistics.pstdev(c) or 1.0 for c in cols]
    Z = [[1.0] + [(v - m) / s for v, m, s in zip(row, mu, sd)] for row in X]
    k = len(Z[0])
    w = [0.0] * k
    for _ in range(iters):
        g = [0.0] * k
        H = [[0.0] * k for _ in range(k)]
        for row, t in zip(Z, y):
            z = sum(wi * xi for wi, xi in zip(w, row))
            p = 1 / (1 + math.exp(-max(-30.0, min(30.0, z))))
            e, v = p - t, p * (1 - p)
            for i in range(k):
                g[i] += e * row[i]
                vi, Hi = v * row[i], H[i]
                for j in range(k):
                    Hi[j] += vi * row[j]
        for i in range(1, k):                      # pas de pénalité sur l'intercept
            g[i] += l2 * w[i]
            H[i][i] += l2
        step = solve(H, g)
        w = [wi - si for wi, si in zip(w, step)]
        if max(abs(s) for s in step) < 1e-8:
            break
    betas = [wi / s for wi, s in zip(w[1:], sd)]
    b0 = w[0] - sum(wi * m / s for wi, m, s in zip(w[1:], mu, sd))
    return b0, betas


def fit(X, y, keys=KEYS):
    """Ajuste, retire la variable la plus à contresens, recommence. Retourne (b0, {clé: beta}, retirées)."""
    active = list(keys)
    dropped = []
    while active:
        idx = [keys.index(k) for k in active]
        b0, betas = fit_logistic([[row[i] for i in idx] for row in X], y)
        wrong = [(b * SIGN[k], k) for k, b in zip(active, betas) if b * SIGN[k] < 0]
        if not wrong:
            coefs = {k: 0.0 for k in keys}
            coefs.update(dict(zip(active, betas)))
            return b0, coefs, dropped
        worst = min(wrong)[1]
        active.remove(worst)
        dropped.append(worst)
    return math.log(sum(y) / (len(y) - sum(y))), {k: 0.0 for k in keys}, dropped


def predict(b0, coefs, X, keys=KEYS):
    return [b0 + sum(coefs[k] * row[i] for i, k in enumerate(keys)) for row in X]


def folds(y, k, seed):
    rnd = random.Random(seed)
    pos = [i for i, t in enumerate(y) if t]
    neg = [i for i, t in enumerate(y) if not t]
    rnd.shuffle(pos)
    rnd.shuffle(neg)
    out = [[] for _ in range(k)]
    for n, i in enumerate(pos + neg):
        out[n % k].append(i)
    return out


def cross_validate(X, y, k=5, repeats=20):
    aucs, first = [], None
    for rep in range(repeats):
        z_all = [0.0] * len(y)
        for test in folds(y, k, seed=rep):
            ts = set(test)
            tr = [i for i in range(len(y)) if i not in ts]
            b0, coefs, _ = fit([X[i] for i in tr], [y[i] for i in tr])
            for i, z in zip(test, predict(b0, coefs, [X[i] for i in test])):
                z_all[i] = z
        aucs.append(auc(z_all, y))
        first = first or z_all
    return aucs, first


def terciles(z, y):
    order = sorted(range(len(y)), key=lambda i: z[i])
    n = len(order)
    cuts = [order[: n // 3], order[n // 3: 2 * n // 3], order[2 * n // 3:]]
    return [(len(c), sum(y[i] for i in c) / len(c)) for c in cuts]


def centiles(values):
    s = sorted(values)
    out = []
    for p in range(101):
        pos = p / 100 * (len(s) - 1)
        lo, hi = int(math.floor(pos)), int(math.ceil(pos))
        out.append(round(s[lo] + (s[hi] - s[lo]) * (pos - lo), 5))
    return out


def jake_formula(results):
    scores = [results[c][0] for c in hs.CHECKS]
    return statistics.mean(scores) * 0.6 + min(scores) * 0.4


def main():
    ap = argparse.ArgumentParser(description="Recalibre hookscore_fr sur un corpus de reels.")
    ap.add_argument("corpus", help="TSV avec les colonnes hook et perf (annee facultative)")
    ap.add_argument("--out", help="où écrire le fichier de poids (sinon : rapport seul)")
    ap.add_argument("--nom", default="corpus privé", help="nom du corpus dans le fichier de poids")
    args = ap.parse_args()

    rows = read_tsv(args.corpus)
    if len(rows) < 100:
        print(f"{len(rows)} reels seulement. En dessous de 100, l'AUC ne veut rien dire.", file=sys.stderr)
        sys.exit(2)
    y = [r["hit"] for r in rows]
    feats = [hs.features(r["hook"]) for r in rows]
    X = [[f[1][k] for k in KEYS] for f in feats]
    base = sum(y) / len(y)

    print(f"\nCORPUS  {len(rows)} reels, {sum(y)} hits (perf >= {HIT}), taux de base {base:.1%}")
    print("=" * 70)

    print("\nCHAQUE VARIABLE SEULE (AUC sur tout le corpus ; un piège bien vu est sous 0,50)")
    single = {}
    for j, k in enumerate(KEYS):
        single[k] = round(auc([row[j] for row in X], y), 3)
        print(f"  {k:<18} {single[k]:.3f}")

    print("\nPIÈGES (taux de hits quand le piège est là, contre quand il n'y est pas)")
    pieges = {}
    for p in hs.PIEGES:
        if "mesure" not in p:
            continue
        j = KEYS.index(p["mesure"])
        hit_in = [t for row, t in zip(X, y) if row[j]]
        hit_out = [t for row, t in zip(X, y) if not row[j]]
        if hit_in:
            pieges[p["id"]] = {"n": len(hit_in), "taux_hits": round(sum(hit_in) / len(hit_in), 3),
                               "taux_hits_sans": round(sum(hit_out) / len(hit_out), 3)}
            print(f"  {p['id']:<12} n={len(hit_in):<4} {sum(hit_in) / len(hit_in):.1%} de hits "
                  f"contre {sum(hit_out) / len(hit_out):.1%}")

    a_jake = auc([jake_formula(f[0]) for f in feats], y)
    print(f"\nFORMULE D'ORIGINE (moyenne 60 % + pire mesure 40 %, sans calibration) : AUC {a_jake:.3f}")

    aucs, pooled = cross_validate(X, y)
    m, lo, hi = statistics.mean(aucs), min(aucs), max(aucs)
    print(f"RECALIBRÉE, validation croisée 5 blocs x 20 : AUC {m:.3f} (de {lo:.3f} à {hi:.3f})")
    tiers = terciles(pooled, y)
    print("  taux de hits par tiers de score, hors apprentissage : "
          + " / ".join(f"{t:.1%}" for _, t in tiers) + "  (bas / milieu / haut)")

    temporal = None
    years = sorted({r["annee"] for r in rows if r["annee"]})
    if len(years) >= 3:
        cut = next(yr for yr in years
                   if sum(1 for r in rows if r["annee"] and r["annee"] <= yr) / len(rows) >= 0.6)
        tr = [i for i, r in enumerate(rows) if r["annee"] and r["annee"] <= cut]
        te = [i for i, r in enumerate(rows) if r["annee"] and r["annee"] > cut]
        if len(te) >= 50 and sum(y[i] for i in te) >= 10:
            b0, coefs, _ = fit([X[i] for i in tr], [y[i] for i in tr])
            a_t = auc(predict(b0, coefs, [X[i] for i in te]), [y[i] for i in te])
            temporal = {"appris_jusqu_a": cut, "n_test": len(te), "auc": round(a_t, 3)}
            print(f"PASSÉ -> FUTUR (appris jusqu'à {cut}, testé sur les {len(te)} reels d'après) : AUC {a_t:.3f}")

    b0, coefs, dropped = fit(X, y)
    z = predict(b0, coefs, X)
    print("\nMODÈLE FINAL (log-odds pour une mesure qui passe de 0 à 1, ou un piège présent)")
    for k in KEYS:
        tag = "  retirée : les données la voulaient à contresens" if k in dropped else ""
        print(f"  {k:<18} {coefs[k]:+.3f}{tag}")
    print(f"  {'intercept':<18} {b0:+.3f}\n")

    if not args.out:
        return
    poids = {
        "version": 1,
        "note": ("Poids de hookscore_fr.py, produits par calibration/calibrer.py. Régression "
                 "logistique pénalisée (L2) sur la première phrase parlée ; hit = vues >= 2 x la "
                 "médiane des 50 reels voisins. Une mesure ne peut que monter le score, un piège "
                 "que le baisser ; à contresens, elle est retirée (poids 0). Le score affiché = "
                 "rang du hook parmi ceux du corpus (centiles_z). Aucune donnée brute ici."),
        "corpus": {"nom": args.nom, "reels": len(rows), "hits": sum(y), "taux_base": round(base, 3),
                   "definition_hit": f"perf >= {HIT}, perf = vues / médiane des 50 reels voisins",
                   "hook": "première phrase de la transcription, 30 mots max"},
        "mesure": {"auc_cv_moyenne": round(m, 3), "auc_cv_min": round(lo, 3), "auc_cv_max": round(hi, 3),
                   "methode_cv": "5 blocs stratifiés, 20 répétitions, contrainte de sens comprise",
                   "auc_formule_origine": round(a_jake, 3), "auc_par_variable": single,
                   "pieges": pieges, "passe_futur": temporal,
                   "taux_hits_par_tiers_cv": [round(t, 3) for _, t in tiers]},
        "retirees": dropped,
        "coefficients": {k: round(v, 4) for k, v in coefs.items()},
        "intercept": round(b0, 4),
        "centiles_z": centiles(z),
        "seuils": {"fort": 67, "faible": 33},
        "date": datetime.date.today().isoformat(),
    }
    with open(args.out, "w", encoding="utf-8") as fh:
        json.dump(poids, fh, indent=1, ensure_ascii=False)
        fh.write("\n")
    print(f"écrit : {args.out}", file=sys.stderr)


if __name__ == "__main__":
    main()

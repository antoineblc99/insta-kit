#!/usr/bin/env python3
"""
stats.py : classe tes posts au multiple (vues / ta médiane) et aux partages,
pas aux vues brutes, et sort le meilleur reel du mois par réseau.

Construit pour insta-kit à partir de la méthode du skill ig-audit
d'instagram-agent-skill (Jake Schincariol, MIT).

Les vues brutes dépendent surtout du nombre de gens qui te suivent déjà. Le
multiple dit si un post a vraiment percé ou si c'était un jour normal. Les
partages par portée sont le signal le plus fort qu'on puisse gagner : quelqu'un
met son nom dessus en l'envoyant.

Entrée : un TSV avec une ligne d'en-tête. Seules `vues` et `titre` (ou `hook`)
sont obligatoires ; le reste rend l'analyse meilleure.

    date        reseau     titre                              vues   portee  partages  enregistrements  abonnes  formule
    2026-10-02  instagram  J'ai perdu 18 000 € sur un contrat  41200  38000   310       420              95       1

Usage
  python3 stats.py posts.tsv
  python3 stats.py posts.tsv --json
"""

import argparse
import json
import statistics
import sys

ALIASES = {"hook": "titre", "title": "titre", "views": "vues", "reach": "portee", "portée": "portee",
           "shares": "partages", "saves": "enregistrements", "follows": "abonnes",
           "abonnés": "abonnes", "platform": "reseau", "réseau": "reseau"}
NUMERIC = ("vues", "portee", "partages", "enregistrements", "abonnes", "retention3s")


def num(cell):
    cell = (cell or "").strip().replace(" ", "").replace("\u202f", "").replace("%", "")
    if not cell:
        return None
    try:
        return float(cell.replace(",", "."))
    except ValueError:
        return None


def read_rows(path):
    raw = sys.stdin.read() if path == "-" else open(path, encoding="utf-8").read()
    lines = [l for l in raw.splitlines() if l.strip() and not l.lstrip().startswith("#")]
    if not lines:
        return []
    head = [ALIASES.get(c.strip().lower(), c.strip().lower()) for c in lines[0].split("\t")]
    rows = []
    for line in lines[1:]:
        cells = dict(zip(head, [c.strip() for c in line.split("\t")]))
        r = {k: cells.get(k, "") for k in head}
        for k in NUMERIC:
            r[k] = num(cells.get(k))
        r["reseau"] = (cells.get("reseau") or "instagram").lower()
        if r["vues"] and r.get("titre"):
            rows.append(r)
    return rows


def ratio(a, b):
    return a / b if a is not None and b else None


def analyse(rows):
    out = {}
    for net in sorted({r["reseau"] for r in rows}):
        posts = [r for r in rows if r["reseau"] == net]
        med = statistics.median(r["vues"] for r in posts)
        for r in posts:
            r["multiple"] = round(r["vues"] / med, 2) if med else None
            r["partages_portee"] = ratio(r.get("partages"), r.get("portee"))
            r["abonnes_portee"] = ratio(r.get("abonnes"), r.get("portee"))
        ranked = sorted(posts, key=lambda r: (-(r["multiple"] or 0), -(r["partages_portee"] or 0)))
        notes = []
        n = len(ranked)
        if n < 10:
            notes.append(f"{n} posts seulement : regarde les chiffres, ne conclus rien.")
        best = ranked[0]
        # « Des vues sans abonnés, c'est un problème de bio, pas de hook. »
        with_follow = [r for r in posts if r["abonnes_portee"] is not None]
        if len(with_follow) >= 5:
            med_follow = statistics.median(r["abonnes_portee"] for r in with_follow)
            leaky = [r for r in with_follow if (r["multiple"] or 0) >= 2 and r["abonnes_portee"] < med_follow / 2]
            if leaky:
                notes.append(f"{len(leaky)} post(s) à 2x ou plus avec deux fois moins d'abonnés par portée que "
                             "d'habitude : l'attention arrive et repart. C'est la bio et le profil, pas le hook.")
        formulas = {}
        for r in posts:
            f = (r.get("formule") or "").strip()
            if f:
                formulas.setdefault(f, []).append(r["multiple"] or 0)
        by_formula = sorted(((f, round(statistics.median(v), 2), len(v)) for f, v in formulas.items()
                             if len(v) >= 2), key=lambda t: -t[1])
        if formulas and not by_formula:
            notes.append("Formules notées, mais aucune utilisée deux fois : pas de comparaison possible.")
        out[net] = {
            "posts": n, "mediane_vues": med, "classement": ranked,
            "meilleur": best, "top": ranked[:5], "flop": ranked[-5:][::-1] if n > 5 else [],
            "par_formule": by_formula, "notes": notes,
        }
    return out


def fmt_row(r):
    bits = [f"{r['multiple']:>5.1f}x", f"{int(r['vues']):>9,} vues".replace(",", " ")]
    if r["partages_portee"] is not None:
        bits.append(f"{r['partages_portee'] * 1000:5.1f} partages / 1000 portée")
    if r.get("retention3s") is not None:
        bits.append(f"rétention 3 s {r['retention3s']:.0f} %")
    title = r["titre"] if len(r["titre"]) <= 50 else r["titre"][:47] + "..."
    return "  ".join(bits) + f"  « {title} »"


def render(a, out=sys.stdout):
    for net, d in a.items():
        head = f"STATS {net.upper()}  ·  {d['posts']} posts  ·  médiane {int(d['mediane_vues']):,} vues".replace(",", " ")
        print("\n" + head, file=out)
        print("=" * max(len(head), 78), file=out)
        b = d["meilleur"]
        print("  MEILLEUR REEL DU MOIS", file=out)
        print("  " + fmt_row(b), file=out)
        if b.get("date"):
            print(f"  publié le {b['date']}", file=out)
        print("\n  TOP 5 AU MULTIPLE", file=out)
        for r in d["top"]:
            print("  " + fmt_row(r), file=out)
        if d["flop"]:
            print("\n  FLOP 5", file=out)
            for r in d["flop"]:
                print("  " + fmt_row(r), file=out)
        if d["par_formule"]:
            print("\n  PAR FORMULE DE HOOK (multiple médian, au moins 2 posts)", file=out)
            for f, m, n in d["par_formule"]:
                print(f"    #{f:<4} {m:>5.2f}x  (n={n})", file=out)
        for n in d["notes"]:
            print(f"\n  - {n}", file=out)
        print("", file=out)


def main():
    ap = argparse.ArgumentParser(description="Classe des posts au multiple et aux partages.")
    ap.add_argument("input", nargs="?", default="-", help="fichier TSV, ou -")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    rows = read_rows(args.input)
    if not rows:
        print("aucune ligne utilisable. Il faut au moins les colonnes vues et titre.", file=sys.stderr)
        sys.exit(2)
    a = analyse(rows)
    if args.json:
        print(json.dumps(a, indent=2, ensure_ascii=False, default=str))
    else:
        render(a)


if __name__ == "__main__":
    main()

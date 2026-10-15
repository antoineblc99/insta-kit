#!/usr/bin/env python3
"""
swipe.py : classe les reels que tu as relevés selon combien ils ont battu leur
propre compte, nomme la formule de hook de chacun, et écrit le fichier swipe.

Adapté de instagram-agent-skill (skills/ig-viral/swipe.py), Jake Schincariol,
licence MIT. Version française : formules et regex en français, accents gérés,
colonnes en français ou en anglais, score de hook recalibré (hookscore_fr).

L'idée du script tient en une correction : les vues brutes ne prouvent rien.
Un compte à 2 000 000 d'abonnés qui fait 400 000 vues a eu un mardi calme. Un
compte à 4 000 abonnés qui fait 400 000 vues a trouvé quelque chose. On classe
donc au multiple : vues du reel / médiane des vues du compte.

Entrée : un fichier TSV rempli pendant que tu regardes, un reel par ligne, avec
une ligne d'en-tête :

    compte    abonnes   mediane   vues     hook
    @compte_a 48000     11000     412000   personne ne te dit que tes 30 premiers reels vont flopper

`mediane` = les vues habituelles du compte (prends le milieu des 12 derniers
reels). C'est la meilleure base. Sans elle, le script se rabat sur les abonnés
et le dit. `hook` = la première phrase du reel, dite ou écrite, dans leurs mots.
Les en-têtes anglais de l'original (account, followers, median, views) marchent aussi.

Usage
  python3 swipe.py releve.tsv
  python3 swipe.py releve.tsv --out ~/.claude/insta-kit/swipe.md
  python3 swipe.py releve.tsv --json
"""

import argparse
import json
import os
import re
import statistics
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REEL = os.path.join(HERE, "..", "insta-reel")
HOOKS = os.path.join(REEL, "hooks.json")
WORD_RE = re.compile(r"[\w€$%]+(?:['’-][\w€$%]+)*")
ALIASES = {"account": "compte", "followers": "abonnes", "abonnés": "abonnes",
           "median": "mediane", "médiane": "mediane", "views": "vues"}

try:                                              # facultatif : noter les hooks aussi
    sys.path.insert(0, REEL)
    from hookscore_fr import run as score_hook    # noqa: E402
except Exception:                                 # insta-viral copié tout seul
    score_hook = None


def load_formulas(path):
    try:
        d = json.load(open(path, encoding="utf-8"))
    except Exception:
        return None
    by_id = {h["id"]: h for h in d["hooks"]}
    order = d.get("classify_order") or sorted(by_id)
    return [(by_id[i]["id"], by_id[i]["nom"], bool(by_id[i].get("piege")),
             re.compile(by_id[i]["match"], re.IGNORECASE)) for i in order if i in by_id]


def classify(hook, formulas):
    if not formulas:
        return None, "non classé", False
    text = hook.replace("’", "'")
    for fid, name, trap, pattern in formulas:
        if pattern.search(text):
            return fid, name, trap
    return None, "non classé", False


def read_rows(path):
    raw = sys.stdin.read() if path == "-" else open(path, encoding="utf-8").read()
    lines = [l for l in raw.splitlines() if l.strip() and not l.lstrip().startswith("#")]
    if not lines:
        return []
    head = [ALIASES.get(c.strip().lower(), c.strip().lower()) for c in lines[0].split("\t")]
    if "vues" in head and "hook" in head:
        cols, body = head, lines[1:]
    else:
        cols, body = ["compte", "abonnes", "vues", "hook"], lines
    rows = []
    for line in body:
        cells = line.split("\t")
        if len(cells) < len(cols):
            cells += [""] * (len(cols) - len(cells))
        r = dict(zip(cols, [c.strip() for c in cells]))
        r["vues"] = int(re.sub(r"[^\d]", "", r.get("vues", "")) or 0)
        for k in ("abonnes", "mediane"):
            digits = re.sub(r"[^\d]", "", r.get(k, "") or "")
            r[k] = int(digits) if digits else None
        if r["vues"] and r.get("hook"):
            rows.append(r)
    return rows


def analyse(rows, formulas):
    used_median = any(r.get("mediane") for r in rows)
    for r in rows:
        base = r.get("mediane") or r.get("abonnes") or 0
        r["base"] = base
        r["multiple"] = round(r["vues"] / base, 2) if base else None
        r["formule_id"], r["formule"], r["piege"] = classify(r["hook"], formulas)
        r["mots"] = len(WORD_RE.findall(r["hook"]))
        if score_hook:
            _, score, verdict, _ = score_hook(r["hook"])
            r["score_hook"], r["verdict_hook"] = round(score, 1), verdict
        else:
            r["score_hook"], r["verdict_hook"] = None, None
    ranked = sorted(rows, key=lambda r: -(r["multiple"] or 0))
    third = max(1, len(ranked) // 3)
    top, bottom = ranked[:third], ranked[-third:]

    def med(items, key):
        vals = [i[key] for i in items if i.get(key) is not None]
        return round(statistics.median(vals), 1) if vals else None

    counts, counts_bottom = {}, {}
    for r in top:
        counts[r["formule"]] = counts.get(r["formule"], 0) + 1
    for r in bottom:
        counts_bottom[r["formule"]] = counts_bottom.get(r["formule"], 0) + 1
    return {
        "base": "médiane du compte" if used_median else "nombre d'abonnés",
        "n": len(ranked),
        "comptes": len({r.get("compte", "") for r in ranked}),
        "reels": ranked,
        "formules_haut": sorted(counts.items(), key=lambda kv: -kv[1]),
        "formules_bas": sorted(counts_bottom.items(), key=lambda kv: -kv[1]),
        "score_hook_haut": med(top, "score_hook"),
        "score_hook_bas": med(bottom, "score_hook"),
        "mots_haut": med(top, "mots"),
        "mots_bas": med(bottom, "mots"),
        "non_classes": sum(1 for r in ranked if r["formule"] == "non classé"),
    }


def render(a, out=sys.stdout):
    head = (f"FICHIER SWIPE  ·  {a['n']} reels  ·  {a['comptes']} comptes  ·  "
            f"base : {a['base']}")
    print("\n" + head, file=out)
    print("=" * max(len(head), 78), file=out)
    for r in a["reels"]:
        mult = f"{r['multiple']:.1f}x" if r["multiple"] else "   ?"
        score = f"{r['score_hook']:.0f}" if r["score_hook"] is not None else " -"
        fid = f"#{r['formule_id']:<2}" if r["formule_id"] else "-  "
        trap = " (piège)" if r["piege"] else ""
        vues = f"{r['vues']:,}".replace(",", " ")
        print(f"  {mult:>7}  hook {score:>3}  {fid} {(r['formule'] + trap)[:26]:<26} "
              f"{r.get('compte', '')[:16]:<16} {vues:>9}", file=out)
        print(f"           « {r['hook'][:96]} »", file=out)
    print("-" * max(len(head), 78), file=out)
    print("CE QUI MARCHE DANS CE LOT", file=out)
    if a["formules_haut"]:
        print("  tiers du haut (multiple) : "
              + ", ".join(f"{n} x{c}" for n, c in a["formules_haut"][:4]), file=out)
    if a["formules_bas"]:
        print("  tiers du bas :             "
              + ", ".join(f"{n} x{c}" for n, c in a["formules_bas"][:4]), file=out)
    if a["score_hook_haut"] is not None:
        print(f"  score de hook médian :     haut {a['score_hook_haut']:.0f}  "
              f"contre bas {a['score_hook_bas']:.0f}", file=out)
    print(f"  longueur médiane du hook : haut {a['mots_haut']:g} mots  "
          f"contre bas {a['mots_bas']:g} mots", file=out)
    print(f"  non classés :              {a['non_classes']} sur {a['n']}. Lis-les à la main : "
          "c'est là que se cache une formule que tu n'as pas encore.", file=out)
    print("\n  Un relevé à la main, c'est un indice, pas une preuve. Douze reels ne montrent rien ;"
          "\n  quarante sur six comptes montrent quelque chose. Relève plus avant d'y croire.\n",
          file=out)


def to_markdown(a):
    lines = ["# Fichier swipe", "",
             f"{a['n']} reels sur {a['comptes']} comptes, classés au multiple sur la {a['base']}.", ""]
    for r in a["reels"]:
        mult = f"{r['multiple']:.1f}x" if r["multiple"] else "?"
        trap = " (piège)" if r["piege"] else ""
        lines += [f"## {mult}  {r['formule']}{trap}  ({r.get('compte', '')})",
                  f"- vues : {r['vues']:,}  base : {r['base']:,}".replace(",", " "),
                  f"- score du hook : {r['score_hook']}  mots : {r['mots']}",
                  f"- hook : « {r['hook']} »", ""]
    return "\n".join(lines) + "\n"


def main():
    ap = argparse.ArgumentParser(description="Classe des reels relevés au multiple sur leur compte.")
    ap.add_argument("input", nargs="?", default="-", help="fichier TSV, ou -")
    ap.add_argument("--hooks", default=HOOKS, help="chemin de insta-reel/hooks.json")
    ap.add_argument("--out", help="écrire aussi le fichier swipe en markdown ici")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    rows = read_rows(args.input)
    if not rows:
        print("aucune ligne utilisable. Il faut un TSV avec au moins les colonnes vues et hook.",
              file=sys.stderr)
        sys.exit(2)
    formulas = load_formulas(args.hooks)
    a = analyse(rows, formulas)
    if not formulas:
        print("note : hooks.json introuvable, formules non nommées. Passe --hooks.", file=sys.stderr)
    if score_hook is None:
        print("note : hookscore_fr.py introuvable, scores de hook ignorés.", file=sys.stderr)

    if args.json:
        print(json.dumps(a, indent=2, ensure_ascii=False))
    else:
        render(a)
    if args.out:
        path = os.path.expanduser(args.out)
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        open(path, "w", encoding="utf-8").write(to_markdown(a))
        print(f"écrit : {path}", file=sys.stderr)


if __name__ == "__main__":
    main()

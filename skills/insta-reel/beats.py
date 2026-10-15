#!/usr/bin/env python3
"""
beats.py : transforme le script d'un reel en conducteur minuté, avant le tournage.

Adapté de instagram-agent-skill (skills/ig-reel/beats.py), Jake Schincariol,
licence MIT. Version française : accents gérés (« déjà » = un mot), mots
vides français pour repérer la boucle, nombres dits en toutes lettres comptés
comme concrets, débit par défaut mesuré sur de vrais reels français.

Estime le temps de chaque ligne, les empile en timecodes, et signale les quatre
choses qui tuent un reel au montage : un hook qui dépasse les trois secondes, un
temps assez long pour que le spectateur parte, une suite de lignes sans rien de
concret, et pas de boucle vers la première ligne.

Les durées sont une estimation à partir du nombre de mots et d'un débit. Assez
proche pour préparer un montage, pas un substitut à l'enregistrement. Le débit
par défaut, 230 mots par minute, est le débit médian de 618 reels français
montés (silences coupés). Une voix posée tourne plutôt autour de 180 : chronomètre-toi
une fois et passe --wpm.

Usage
  python3 beats.py script.txt
  python3 beats.py script.txt --target 30
  python3 beats.py script.txt --wpm 180 --target 45
  pbpaste | python3 beats.py -
  python3 beats.py script.txt --json
"""

import argparse
import json
import re
import sys

WORD_RE = re.compile(r"[\w€$%]+(?:['’-][\w€$%]+)*")
SENT_RE = re.compile(r"[^.!?]+[.!?]*")
CONCRETE_RE = re.compile(
    r"\d|€|(?<!^)(?<![.!?] )\b[A-ZÀ-ÖØ-Ý][a-zà-öø-ÿ]{2,}"
    r"|\b(?:deux|trois|quatre|cinq|six|sept|huit|neuf|dix|onze|douze|quinze|vingt|trente|"
    r"quarante|cinquante|soixante|cent|cents|mille|million|millions|milliard|milliards)\b",
    re.MULTILINE | re.IGNORECASE)
STOPWORDS = {
    "le", "la", "les", "un", "une", "des", "de", "du", "d", "et", "ou", "mais", "si",
    "à", "a", "au", "aux", "en", "dans", "sur", "pour", "par", "avec", "sans", "que",
    "qui", "quoi", "ce", "cet", "cette", "ces", "ça", "c", "est", "sont", "été", "être",
    "tu", "te", "t", "toi", "ton", "ta", "tes", "je", "j", "me", "m", "moi", "mon", "ma",
    "mes", "on", "nous", "vous", "votre", "vos", "il", "elle", "ils", "elles", "lui",
    "leur", "y", "ne", "n", "pas", "plus", "très", "tout", "tous", "fait", "faire",
    "ai", "as", "avez", "ont", "va", "vais", "juste", "alors", "donc", "comme", "l", "s",
}

HOOK_WINDOW = 3.0        # secondes. Au-delà, le pouce a déjà décidé.
MAX_BEAT = 4.0           # secondes sur une seule idée sans changement à l'écran.
ABSTRACT_RUN = 3         # temps d'affilée sans rien de vérifiable.


def normalise(text):
    text = text.replace("’", "'")
    text = re.sub(r"[\u00a0\u202f]", " ", text)
    # « 18 000 € » se dit en un seul nombre, donc il compte pour un mot.
    return re.sub(r"(?<=\d)[ .,](?=\d{3}\b)", "", text)


def words(text):
    return WORD_RE.findall(normalise(text))


def loop_words(text):
    out = set()
    for w in words(text):
        for part in re.split(r"['-]", w.lower()):
            if part and part not in STOPWORDS:
                out.add(part)
    return out


def tc(seconds):
    m, s = divmod(seconds, 60)
    return f"{int(m)}:{s:04.1f}"


def split_beats(raw, wps):
    """Une ligne = un temps, sauf si la ligne est trop longue pour en être un."""
    beats = []
    for line in [l.strip() for l in raw.splitlines()]:
        if not line:
            continue
        if len(words(line)) / wps <= MAX_BEAT * 1.5:
            beats.append(line)
            continue
        # Paragraphe long : on coupe aux fins de phrase pour que les durées
        # veuillent dire quelque chose.
        parts = [p.strip() for p in SENT_RE.findall(line) if p.strip()]
        buf = ""
        for part in parts:
            candidate = (buf + " " + part).strip()
            if buf and len(words(candidate)) / wps > MAX_BEAT:
                beats.append(buf)
                buf = part
            else:
                buf = candidate
        if buf:
            beats.append(buf)
    return beats


def analyse(raw, wpm=230, target=None):
    wps = wpm / 60.0
    beats = split_beats(raw, wps)
    if not beats:
        return None

    rows, clock = [], 0.0
    for i, text in enumerate(beats):
        n = len(words(text))
        dur = n / wps
        rows.append({
            "n": i + 1,
            "start": round(clock, 2),
            "dur": round(dur, 2),
            "words": n,
            "text": text,
            "concrete": len(CONCRETE_RE.findall(normalise(text))),
            "label": "",
            "flags": [],
        })
        clock += dur
    total = clock

    for r in rows:
        if r["n"] == 1 or r["start"] + r["dur"] <= HOOK_WINDOW:
            r["label"] = "HOOK"
    rows[-1]["label"] = "CTA" if rows[-1]["label"] != "HOOK" else "HOOK/CTA"
    half = total / 2
    for r in rows:
        if not r["label"] and r["start"] <= half < r["start"] + r["dur"]:
            r["label"] = "MILIEU"

    notes = []
    if rows[0]["dur"] > HOOK_WINDOW:
        rows[0]["flags"].append(f"le hook dure {rows[0]['dur']:.1f} s, au-delà des {HOOK_WINDOW:.0f} s")
        notes.append(f"Le temps 1 prend {rows[0]['dur']:.1f} s à dire. Descends à "
                     f"{int(HOOK_WINDOW * wps)} mots ou moins, sinon le hook arrive après "
                     "que la décision a été prise.")
    if rows[0]["concrete"] == 0:
        notes.append("Le temps 1 n'a ni chiffre ni nom. Les hooks sans rien de vérifiable "
                     "sont ceux qu'on scrolle.")

    for r in rows:
        if r["dur"] > MAX_BEAT:
            r["flags"].append(f"{r['dur']:.1f} s sur un seul temps")
    long_beats = [r["n"] for r in rows if r["dur"] > MAX_BEAT]
    if long_beats:
        notes.append(f"Temps {', '.join(map(str, long_beats))} : plus de {MAX_BEAT:.0f} s. "
                     "Coupe la ligne en deux ou change ce qu'il y a à l'écran pendant. "
                     "Un plan fixe, c'est là que les gens partent.")

    run, start = 0, None
    for r in rows:
        if r["concrete"] == 0:
            run += 1
            start = start if start is not None else r["n"]
            if run == ABSTRACT_RUN:
                notes.append(f"Temps {start} à {r['n']} : rien de concret. "
                             "Mets un chiffre, un nom ou un prix dans l'un d'eux.")
        else:
            run, start = 0, None

    loop = sorted(loop_words(rows[0]["text"]) & loop_words(rows[-1]["text"]))
    if loop:
        notes.append(f"Boucle : le dernier temps reprend « {', '.join(loop[:3])} » du hook. "
                     "Les revisionnages, c'est de la portée gratuite.")
    else:
        notes.append("Pas de boucle. Le dernier temps ne partage aucun mot avec le hook, la vidéo "
                     "finit à plat. Reprendre un mot du temps 1, c'est le revisionnage le moins cher.")

    if target:
        delta = total - target
        if abs(delta) <= target * 0.1:
            notes.append(f"Durée dans la cible ({total:.1f} s pour {target:g} s).")
        elif delta > 0:
            notes.append(f"{delta:.1f} s de trop. Coupe environ {int(delta * wps)} mots.")
        else:
            notes.append(f"{-delta:.1f} s sous la cible. Ajoute {int(-delta * wps)} mots ou "
                         "tourne-le court. Court, c'est souvent mieux.")

    return {
        "wpm": wpm, "target": target,
        "total_seconds": round(total, 2),
        "total_words": sum(r["words"] for r in rows),
        "beats": rows,
        "notes": notes,
    }


def render(a, out=sys.stdout):
    head = (f"CONDUCTEUR  ·  {a['total_words']} mots  ·  ~{a['total_seconds']:.1f} s "
            f"à {a['wpm']:g} mots/min" + (f"  ·  cible {a['target']:g} s" if a["target"] else ""))
    print("\n" + head, file=out)
    print("=" * max(len(head), 72), file=out)
    for r in a["beats"]:
        label = f"{r['label']:<8}" if r["label"] else " " * 8
        print(f"  {tc(r['start'])}  {r['dur']:4.1f}s  {label}{r['text']}", file=out)
        for f in r["flags"]:
            print(f"  {'':>6}  {'':>5}  {'':<8}^ {f}", file=out)
    print("-" * max(len(head), 72), file=out)
    for n in a["notes"]:
        print(f"  - {n}", file=out)
    print("", file=out)


def main():
    ap = argparse.ArgumentParser(description="Minute le script d'un reel.")
    ap.add_argument("input", nargs="?", default="-", help="fichier du script, ou -")
    ap.add_argument("--wpm", type=float, default=230, help="débit en mots par minute (230 par défaut)")
    ap.add_argument("--target", type=float, help="durée visée en secondes")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    raw = sys.stdin.read() if args.input == "-" else open(args.input, encoding="utf-8").read()
    a = analyse(raw, wpm=args.wpm, target=args.target)
    if not a:
        print("script vide", file=sys.stderr)
        sys.exit(2)
    if args.json:
        print(json.dumps(a, indent=2, ensure_ascii=False))
    else:
        render(a)
    sys.exit(0)


if __name__ == "__main__":
    main()

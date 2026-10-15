#!/usr/bin/env python3
"""
detect.py : cinq mesures qui notent à quel point un brouillon en français
sonne écrit par une machine.

Adapté de instagram-agent-skill (skills/ig-human/detect.py), Jake Schincariol,
licence MIT. Version française : les accents comptent comme des lettres,
la VOIX lit l'oral français (« c'est pas », « t'as », « du coup ») au lieu des
contractions anglaises, et l'apostrophe ’ et les guillemets « » ne comptent
plus comme une empreinte : c'est la typographie normale du français.

Ce que c'est : cinq heuristiques locales, calquées sur ce que mesurent les
détecteurs publics : la variation de longueur des phrases, le concret, le
vocabulaire tout fait, l'empreinte typographique, la voix. Tout est calculé sur
ta machine, rien n'est envoyé.

Ce que ce n'est pas : GPTZero, Originality, Copyleaks, Winston ou Turnitin. Il
n'appelle pas leurs API et ne peut pas promettre leur verdict.

Chaque mesure rend un score HUMAIN de 0 à 100. Plus c'est haut, mieux c'est.

Usage
  python3 detect.py brouillon.txt
  pbpaste | python3 detect.py -
  python3 detect.py brouillon.txt --json
  python3 detect.py avant.txt apres.txt      # comparer deux versions
"""

import argparse
import json
import os
import re
import statistics
import sys
import unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
LEX = os.path.join(HERE, "slop-fr.json")

EM_DASH = "\N{EM DASH}"
SENT_RE = re.compile(r"[^.!?\n]+[.!?]*")
WORD_RE = re.compile(r"[^\W\d_]+(?:['’-][^\W\d_]+)*")
# L'oral français écrit : la négation sans « ne », les élisions familières, les
# mots de liaison qu'on dit et qu'on n'écrit pas dans un rapport.
ORAL = re.compile(
    r"(?i)\b(?:c['’]est|j['’]ai|t['’]as|t['’]es|on a|y a|il y a|j['’]sais|je sais|j['’]suis|"
    r"je suis|ça|il est|elle est|on est|j['’]avais|t['’]avais|j['’]peux|je peux|tu peux|j['’]vais)"
    r" pas\b"
    r"|(?<![\w])(?:t['’](?:as|es|étais|avais|inquiète)|y['’]a|j['’](?:sais|suis|vais|peux))\b"
    r"|\b(?:ouais|du coup|en vrai|genre|bref|grave|carrément|franchement|perso|bah|ben|hein|"
    r"trop bien|trop fort|tranquille|un truc|des trucs)\b")
PRONOUNS = re.compile(
    r"(?i)(?<![\w])(?:j|m|t)['’]"
    r"|\b(?:je|me|moi|mon|ma|mes|nous|on|notre|nos|tu|te|toi|ton|ta|tes|vous|votre|vos)\b")
NUMBERS = re.compile(r"\b\d[\d\s,.]*%?|\d\s?€|€\s?\d|\$\d")
PROPER = re.compile(r"(?<![.!?]\s)(?<!^)\b[A-ZÀ-ÖØ-Ý][a-zà-öø-ÿ]{2,}\b", re.MULTILINE)


def clamp(n):
    return max(0.0, min(100.0, n))


def scale(value, human, machine):
    """Ramène value sur 0-100, `human` -> 100 et `machine` -> 0."""
    if human == machine:
        return 50.0
    return clamp((value - machine) / (human - machine) * 100)


def sentences(text):
    return [s.strip() for s in SENT_RE.findall(text) if len(s.split()) > 2]


def words(text):
    return WORD_RE.findall(text)


def lex_pattern(find):
    body = re.escape(find).replace(r"\ ", r"\s+").replace("'", "['’]")
    return re.compile(r"(?<![\w])" + body + r"(?![\w])", re.IGNORECASE)


def check_burstiness(text):
    """Un humain varie fort la longueur de ses phrases. La machine écrit régulier."""
    lens = [len(s.split()) for s in sentences(text)]
    if len(lens) < 4:
        return 50.0, "trop court pour juger"
    mean = statistics.mean(lens)
    cv = statistics.pstdev(lens) / mean if mean else 0
    return scale(cv, human=0.70, machine=0.22), \
        f"variation {cv:.2f} sur {len(lens)} phrases (idéal : 0,55 et plus)"


def check_specificity(text):
    """Des chiffres, des noms, du concret. Le texte machine est abstrait."""
    w = words(text)
    if len(w) < 25:
        return 50.0, "trop court pour juger"
    hits = len(NUMBERS.findall(text)) + len(set(PROPER.findall(text)))
    density = hits * 100 / len(w)
    return scale(density, human=6.0, machine=0.5), \
        f"{hits} élément(s) concret(s), {density:.1f} pour 100 mots (idéal : 4 et plus)"


def check_slop(text, lex):
    """Densité de vocabulaire tout fait, d'après le lexique."""
    w = words(text)
    if not w:
        return 50.0, "vide"
    hits, found, rest = 0, [], text
    # Les plus longues d'abord, et on efface ce qui a été compté : « abonne-toi pour
    # plus de contenu » ne compte pas une deuxième fois comme « abonne-toi pour plus ».
    for entry in sorted(lex["words"] + lex["phrases"], key=lambda e: -len(e["find"])):
        pattern = lex_pattern(entry["find"])
        n = len(pattern.findall(rest))
        if n:
            hits += n
            found.append(entry["find"])
            rest = pattern.sub(" ", rest)
    density = hits * 100 / len(w)
    detail = f"{hits} tic(s), {density:.1f} pour 100 mots"
    if found:
        detail += " (" + ", ".join(sorted(found)[:4]) + (", ..." if len(found) > 4 else "") + ")"
    return scale(density, human=0.0, machine=4.0), detail


def check_fingerprint(text):
    """Les caractères qu'un clavier de téléphone ne produit pas.

    Pas comptés : l'apostrophe ’ et les guillemets « », que les claviers
    français tapent tout seuls et que tout bon texte français utilise.
    """
    invisible = sum(1 for c in text if unicodedata.category(c) == "Cf")
    em = text.count(EM_DASH)
    curly = sum(text.count(c) for c in "‘“”")
    ellip = text.count("…")
    nbsp = sum(text.count(c) for c in "\u00a0\u2007\u202f")
    total = invisible * 4 + em * 2 + curly + ellip + nbsp
    per1k = total * 1000 / max(len(text), 1)
    detail = (f"{invisible} invisible(s), {em} tiret(s) cadratin(s), {curly} guillemet(s) anglais, "
              f"{ellip} caractère(s) …, {nbsp} espace(s) insécable(s)")
    return scale(per1k, human=0.0, machine=12.0), detail


def check_voice(text, lex):
    """L'oral, les personnes, et les formes que la machine prend par défaut."""
    w = words(text)
    if len(w) < 25:
        return 50.0, "trop court pour juger"
    per100 = 100 / len(w)
    oral = len(ORAL.findall(text)) * per100
    person = len(PRONOUNS.findall(text)) * per100
    tells, names = 0, []
    for s in lex["structures"]:
        try:
            n = len(re.compile(s["regex"], re.MULTILINE).findall(text))
        except re.error:
            continue
        if n:
            tells += n
            names.append(s["id"])
    bullets = [len(b.split()) for b in re.findall(r"(?m)^\s*[-*•]\s+(.+)$", text)]
    uniform = len(bullets) >= 3 and statistics.pstdev(bullets) < 1.6
    score = (scale(oral, human=2.5, machine=0.0) * 0.35
             + scale(person, human=8.0, machine=1.0) * 0.35
             + clamp(100 - tells * 22) * 0.30)
    if uniform:
        score -= 12
        names.append("puces-uniformes")
    detail = (f"{oral:.1f} marque(s) d'oral, {person:.1f} pronom(s) personnel(s) "
              f"pour 100 mots, {tells} structure(s) repérée(s)")
    if names:
        detail += " [" + ", ".join(names[:4]) + "]"
    return clamp(score), detail


CHECKS = ["RYTHME", "PRÉCISION", "LEXIQUE IA", "EMPREINTE", "VOIX"]


def run(text, lex):
    results = {
        "RYTHME": check_burstiness(text),
        "PRÉCISION": check_specificity(text),
        "LEXIQUE IA": check_slop(text, lex),
        "EMPREINTE": check_fingerprint(text),
        "VOIX": check_voice(text, lex),
    }
    scores = [results[c][0] for c in CHECKS]
    # La pire mesure pèse lourd : un détecteur n'a besoin que d'un signal.
    overall = statistics.mean(scores) * 0.6 + min(scores) * 0.4
    verdict = "PASSE" if overall >= 70 and min(scores) >= 55 else (
        "À REVOIR" if overall >= 50 else "SIGNALÉ")
    return results, overall, verdict


def bar(score, width=24):
    filled = round(score / 100 * width)
    return "#" * filled + "." * (width - filled)


def render(results, overall, verdict, label=None, out=sys.stdout):
    title = "PANNEAU DE DÉTECTION" + (f"  :  {label}" if label else "")
    print("\n" + title, file=out)
    print("=" * max(len(title), 62), file=out)
    for name in CHECKS:
        score, detail = results[name]
        print(f"  {name:<12} {bar(score)} {score:5.1f}", file=out)
        print(f"  {'':<12} {detail}", file=out)
    print("-" * 62, file=out)
    print(f"  {'SCORE HUMAIN':<12} {bar(overall)} {overall:5.1f}   {verdict}", file=out)
    if verdict != "PASSE":
        weakest = min(CHECKS, key=lambda c: results[c][0])
        print(f"\n  Signal le plus faible : {weakest}. Corrige-le d'abord.", file=out)
    print("", file=out)


def main():
    ap = argparse.ArgumentParser(description="Note à quel point un brouillon sonne machine.")
    ap.add_argument("input", nargs="?", default="-", help="fichier, ou - pour l'entrée standard")
    ap.add_argument("compare", nargs="?", help="second fichier, pour un avant / après")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--lexicon", default=LEX)
    args = ap.parse_args()

    lex = json.load(open(args.lexicon, encoding="utf-8"))
    read = lambda p: sys.stdin.read() if p == "-" else open(p, encoding="utf-8").read()

    targets = [(args.input, read(args.input))]
    if args.compare:
        targets.append((args.compare, read(args.compare)))

    payload = []
    for name, text in targets:
        results, overall, verdict = run(text, lex)
        payload.append({
            "source": name,
            "checks": {k: {"score": round(v[0], 1), "detail": v[1]} for k, v in results.items()},
            "human_score": round(overall, 1),
            "verdict": verdict,
        })

    if args.json:
        print(json.dumps(payload if args.compare else payload[0], indent=2, ensure_ascii=False))
        return

    for (name, text), p in zip(targets, payload):
        results, overall, verdict = run(text, lex)
        render(results, overall, verdict, label=os.path.basename(name) if args.compare else None)
    if args.compare:
        a, b = payload
        delta = b["human_score"] - a["human_score"]
        print(f"  {a['human_score']:.1f} {a['verdict']}  ->  "
              f"{b['human_score']:.1f} {b['verdict']}   ({delta:+.1f})\n")

    sys.exit(0 if payload[-1]["verdict"] == "PASSE" else 1)


if __name__ == "__main__":
    main()

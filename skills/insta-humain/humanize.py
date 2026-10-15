#!/usr/bin/env python3
"""
humanize.py : retire l'empreinte machine d'un brouillon en français.

Adapté de instagram-agent-skill (skills/ig-human/humanize.py), Jake Schincariol,
licence MIT. Lexique réécrit en français (slop-fr.json), accents gérés,
apostrophes droites et typographiques traitées pareil, ponctuation française
respectée (l'espace avant ? ! : ; reste là).

Trois passes, dans cet ordre :

  1. INVISIBLES    supprime ou normalise ce qu'un clavier ne tape jamais :
                   espaces de largeur nulle, joints, tirets conditionnels,
                   BOM, caractères d'étiquette Unicode, espaces insécables.
  2. TYPOGRAPHIE   tiret cadratin -> virgule, demi-cadratin -> trait d'union,
                   guillemets anglais -> droits, … -> trois points. Les
                   guillemets français « » et l'apostrophe ’ ne bougent pas.
  3. LEXIQUE       remplace les tics du lexique slop-fr.json par des mots
                   simples, garde les majuscules, ne touche pas aux liens.

Les structures (« Ce n'est pas X, c'est Y », triades, préambules) sont
SIGNALÉES, jamais réécrites : changer la forme d'une phrase demande du
jugement. C'est le travail du modèle, pas d'une regex.

Usage
  python3 humanize.py brouillon.txt
  python3 humanize.py brouillon.txt --report
  pbpaste | python3 humanize.py - --report
  python3 humanize.py brouillon.txt --json
  python3 humanize.py brouillon.txt -o propre.txt
"""

import argparse
import json
import os
import re
import sys
import unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
LEX = os.path.join(HERE, "slop-fr.json")

EM_DASH = "\N{EM DASH}"
EN_DASH = "\N{EN DASH}"
URL_RE = re.compile(r"https?://\S+|www\.\S+|\S+@\S+\.\S+")
SENT_RE = re.compile(r"[^.!?\n]+[.!?]*")
LETTER = r"[^\W\d_]"


def load_lexicon(path=LEX):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def _cp(spec):
    """'U+200B' -> 0x200b ; 'U+E0000-U+E007F' -> (début, fin)."""
    if "-" in spec:
        a, b = spec.split("-")
        return (int(a[2:], 16), int(b[2:], 16))
    return int(spec[2:], 16)


def protect_urls(text):
    """Remplace les liens par des repères pour qu'aucune passe ne les modifie."""
    found = []

    def stash(m):
        found.append(m.group(0))
        return f"\x00URL{len(found) - 1}\x00"

    return URL_RE.sub(stash, text), found


def restore_urls(text, found):
    for i, url in enumerate(found):
        text = text.replace(f"\x00URL{i}\x00", url)
    return text


def lex_pattern(find):
    """Motif d'une entrée du lexique : insensible à la casse, ' et ’ équivalents."""
    body = re.escape(find).replace(r"\ ", r"\s+").replace("'", "['’]")
    return re.compile(r"(?<![\w])" + body + r"(?![\w])", re.IGNORECASE)


def pass_invisible(text, lex):
    hits = []
    for entry in lex["invisible"]:
        cp = _cp(entry["cp"])
        if isinstance(cp, tuple):
            pattern = "[" + re.escape(chr(cp[0])) + "-" + re.escape(chr(cp[1])) + "]"
        else:
            pattern = re.escape(chr(cp))
        n = len(re.findall(pattern, text))
        if n:
            hits.append({"name": entry["cp"] + " " + entry["name"], "count": n,
                         "action": entry["action"]})
            text = re.sub(pattern, "" if entry["action"] == "delete" else " ", text)
    # Tout caractère de format (catégorie Cf) restant est invisible par définition.
    stray = [c for c in text if unicodedata.category(c) == "Cf"]
    if stray:
        hits.append({"name": "autres caractères de format invisibles", "count": len(stray),
                     "action": "delete"})
        text = "".join(c for c in text if unicodedata.category(c) != "Cf")
    return text, hits


def pass_typographic(text, lex):
    hits = []
    for entry in lex["typographic"]:
        ch = entry["from"]
        n = text.count(ch)
        if not n:
            continue
        hits.append({"name": f"{ch} {entry['name']}", "count": n,
                     "to": entry["to"].strip() or "(espace)"})
        if ch == EM_DASH:
            # Avec ou sans espaces autour, le cadratin devient « , ».
            text = re.sub(r"\s*" + EM_DASH + r"\s*", ", ", text)
        elif ch == EN_DASH:
            text = re.sub(r"\s*" + EN_DASH + r"\s*(?=\d)", "-", text)   # entre deux chiffres : trait d'union
            text = re.sub(r"\s+" + EN_DASH + r"\s+", ", ", text)         # employé comme cadratin
            text = text.replace(EN_DASH, "-")
        else:
            text = text.replace(ch, entry["to"])
    # Une virgule ajoutée juste avant une autre ponctuation se lit mal.
    text = re.sub(r",\s*([,.;:!?])", r"\1", text)
    text = re.sub(r",\s*\n", "\n", text)
    text = re.sub(r"(?m)^\s*,\s*", "", text)
    return text, hits


def _match_case(src, repl):
    if not repl:
        return repl
    if src.isupper() and len(src) > 1:
        return repl.upper()
    if src[0].isupper():
        return repl[0].upper() + repl[1:]
    return repl


def pass_lexical(text, lex):
    """Remplace les tics, les plus longs d'abord pour que les expressions gagnent."""
    hits = []
    entries = sorted(lex["phrases"] + lex["words"], key=lambda e: len(e["find"]), reverse=True)
    for entry in entries:
        pattern = lex_pattern(entry["find"])
        found = pattern.findall(text)
        if not found:
            continue
        hits.append({"find": entry["find"], "replace": entry["replace"] or "(supprimé)",
                     "count": len(found), "family": entry["family"]})
        text = pattern.sub(lambda m: _match_case(m.group(0), entry["replace"]), text)
    # Le ménage après les suppressions. Retirer une expression laisse de la
    # ponctuation orpheline (« système. . » ou une ligne qui commence par une
    # virgule), et ça se lit plus mal que le tic.
    text = re.sub(r"[ \t]{2,}", " ", text)
    text = re.sub(r"(?m)^[ \t]*(?:[,.;:]+[ \t]*)+", "", text)
    text = re.sub(r"(?m)^[ \t](?=\S)", "", text)       # une espace laissée par une suppression
    text = re.sub(r"[ \t]+([,.])", r"\1", text)        # pas d'espace avant , et . ; on garde
                                                       # celle avant ? ! : ; (règle française)
    text = re.sub(r",\s*([,.;:!?])", r"\1", text)
    text = re.sub(r"([.!?])[ \t]*,[ \t]*", r"\1 ", text)
    text = re.sub(r"([.!?])[ \t]+[!?;:]+(?=\s|$)", r"\1", text)   # « penses. ! » après une suppression
    text = re.sub(r"\(\s*\)", "", text)
    text = text.replace("...", "\x00ELL\x00")          # protège les vrais points de suspension
    text = re.sub(r"\.\s*\.+", ".", text)
    text = re.sub(r"([!?])\s*\.", r"\1", text)
    text = text.replace("\x00ELL\x00", "...")
    text = re.sub(r"(?m)^[ \t]+$", "", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    # Un cadratin devenu virgule suivi d'un connecteur fait une phrase soudée
    # (« c'est important, donc, c'est la preuve »). On le transforme en point.
    text = re.sub(r",\s*(aussi|donc|bref|au final|en plus|mais)\s*,\s*",
                  lambda m: ". " + m.group(1)[0].upper() + m.group(1)[1:] + ", ", text)
    return text, hits


def scan_structures(text, lex):
    flags = []
    for s in lex["structures"]:
        try:
            pattern = re.compile(s["regex"], re.MULTILINE)
        except re.error:
            continue
        found = pattern.findall(text)
        if found:
            flags.append({"name": s["name"], "count": len(found), "fix": s["fix"]})
    # Des phrases toutes de la même longueur, c'est aussi une structure.
    lens = [len(s.split()) for s in SENT_RE.findall(text) if len(s.split()) > 2]
    if len(lens) >= 4:
        mean = sum(lens) / len(lens)
        var = sum((n - mean) ** 2 for n in lens) / len(lens)
        cv = (var ** 0.5) / mean if mean else 0
        if cv < 0.35:
            flags.append({
                "name": f"Phrases de longueur uniforme (variation {cv:.2f})",
                "count": len(lens),
                "fix": "Coupe une phrase en deux. Laisses-en une autre s'étirer. La machine écrit régulier.",
            })
    return flags


def restore_capitals(original, text):
    """Supprimer une ouverture laisse le mot suivant en minuscule.

    On ne corrige que pour les gens qui mettent des majuscules en début de
    phrase : une voix tout en minuscules est un style, pas un artefact.
    """
    starts = re.findall(r"(?:^|[.!?]\s+|\n)\s*(" + LETTER + ")", original)
    if not starts or sum(1 for c in starts if c.isupper()) * 2 < len(starts):
        return text
    return re.sub(r"(?:^|(?<=[.!?] )|(?<=[.!?]\n)|(?<=\n))(\s*)(" + LETTER + ")",
                  lambda m: m.group(1) + m.group(2).upper(), text)


def humanize(text, lex):
    raw_for_case = text
    text, urls = protect_urls(text)
    text, inv = pass_invisible(text, lex)
    text, typo = pass_typographic(text, lex)
    text, lexi = pass_lexical(text, lex)
    text = restore_capitals(raw_for_case, text)
    text = restore_urls(text, urls)
    return text.strip() + "\n", {
        "invisible": inv,
        "typographic": typo,
        "lexical": lexi,
        "structures": scan_structures(text, lex),
    }


def render_report(report, out=sys.stderr):
    def head(title):
        print(f"\n{title}\n" + "-" * len(title), file=out)

    total = sum(h["count"] for h in report["invisible"]) \
        + sum(h["count"] for h in report["typographic"]) \
        + sum(h["count"] for h in report["lexical"])

    head("RAPPORT HUMAIN")
    print(f"{total} artefact(s) machine retiré(s), "
          f"{len(report['structures'])} structure(s) signalée(s) à réécrire", file=out)

    if report["invisible"]:
        head("1. CARACTÈRES INVISIBLES")
        for h in report["invisible"]:
            print(f"  {h['count']:>3}x  {h['name']}  -> {h['action']}", file=out)
    if report["typographic"]:
        head("2. TYPOGRAPHIE")
        for h in report["typographic"]:
            print(f"  {h['count']:>3}x  {h['name']}  -> {h['to']}", file=out)
    if report["lexical"]:
        head("3. LEXIQUE IA")
        for h in report["lexical"]:
            print(f"  {h['count']:>3}x  {h['find']}  -> {h['replace']}   [{h['family']}]", file=out)
    if report["structures"]:
        head("4. STRUCTURES  (pas corrigées automatiquement : réécris-les toi-même)")
        for h in report["structures"]:
            print(f"  {h['count']:>3}x  {h['name']}\n        {h['fix']}", file=out)
    if not any(report.values()):
        head("PROPRE")
        print("  Rien à retirer.", file=out)
    print("", file=out)


def main():
    ap = argparse.ArgumentParser(description="Retire l'empreinte machine d'un brouillon en français.")
    ap.add_argument("input", nargs="?", default="-", help="fichier, ou - pour l'entrée standard")
    ap.add_argument("-o", "--out", help="écrire le texte nettoyé ici plutôt qu'à l'écran")
    ap.add_argument("--report", action="store_true", help="afficher ce qui a changé (sur stderr)")
    ap.add_argument("--json", action="store_true", help="sortie {text, report} en JSON")
    ap.add_argument("--lexicon", default=LEX, help="chemin du lexique (slop-fr.json)")
    args = ap.parse_args()

    raw = sys.stdin.read() if args.input == "-" else open(args.input, encoding="utf-8").read()
    lex = load_lexicon(args.lexicon)
    clean, report = humanize(raw, lex)

    if args.json:
        print(json.dumps({"text": clean, "report": report}, indent=2, ensure_ascii=False))
        return
    if args.out:
        with open(args.out, "w", encoding="utf-8") as fh:
            fh.write(clean)
        print(f"écrit : {args.out}", file=sys.stderr)
    else:
        sys.stdout.write(clean)
    if args.report:
        render_report(report)


if __name__ == "__main__":
    main()

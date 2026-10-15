#!/usr/bin/env python3
"""
hookscore_fr.py : note la première phrase d'un reel (le hook parlé) et classe
plusieurs hooks entre eux. En français.

Adapté de instagram-agent-skill (skills/ig-reel/hookscore.py), Jake Schincariol,
licence MIT. Listes réécrites pour le français, accents gérés, poids recalibrés
sur 623 reels français réels (voir hookscore_fr_poids.json et le README).

Ce que c'est : cinq mesures locales calculées sur le texte seul, plus trois
pièges repérés. LONGUEUR (assez court pour tenir en 3 secondes), PRÉCISION (un
chiffre, un nom, un montant), ENJEU (quelque chose à perdre ou à gagner),
ATTAQUE (le mot fort au début, pas en neuvième position), ADRESSE (on parle à
quelqu'un). Les poids qui les combinent viennent d'une régression logistique
sur des reels mesurés, pas d'une intuition. Sur ce corpus, ATTAQUE et ADRESSE
allaient à contresens : leur poids est 0, elles s'affichent sans compter.

Ce que ce n'est pas : un prédicteur de vues. Sur le corpus de calibration, le
score sépare les reels qui ont cartonné des autres un peu mieux qu'une pièce
(AUC en validation croisée dans le fichier de poids). Il sert à tuer les hooks
faibles avant le tournage. Il ne choisit pas entre deux bons hooks : ça, c'est
ton visage, ton montage, ton son et l'audience à qui Instagram le montre.

Le score va de 0 à 100 : c'est le rang du hook parmi les premières phrases du
corpus. 70 = il fait mieux que 70 % d'entre elles, d'après le modèle.

Usage
  python3 hookscore_fr.py hooks.txt               # un hook par ligne, classés
  python3 hookscore_fr.py --hook "J'ai perdu 18 000 € à cause d'un contrat."
  pbpaste | python3 hookscore_fr.py -
  python3 hookscore_fr.py hooks.txt --json
  python3 hookscore_fr.py --hook "..." --poids autre_fichier.json
"""

import argparse
import bisect
import json
import os
import re
import statistics
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
POIDS = os.path.join(HERE, "hookscore_fr_poids.json")

# Un mot = des lettres (accents compris), des chiffres, €, $ ou %, avec les
# apostrophes et traits d'union internes. « déjà » est un mot, pas deux.
WORD_RE = re.compile(r"[\w€$%]+(?:['-][\w€$%]+)*")
ELISION_RE = re.compile(r"\b(jusqu|lorsqu|puisqu|quoiqu|qu|l|d|j|m|t|s|c|n)'", re.IGNORECASE)
NUMBER_RE = re.compile(
    r"\d+(?:[.,]\d+)?\s?(?:%|€|\$|k€|k\b|x\b|h\b|min\b|heures?\b|minutes?\b|secondes?\b"
    r"|jours?\b|semaines?\b|mois\b|ans\b|années?\b|kilos?\b|kg\b)?",
    re.IGNORECASE)
PROPER_RE = re.compile(r"(?<!^)(?<![.!?] )\b[A-ZÀ-ÖØ-Ý][a-zà-öø-ÿ]{2,}")
HASHTAG_RE = re.compile(r"(?:^|\s)#\w+")
EMOJI_RE = re.compile(r"[\U0001F300-\U0001FAFF☀-➿]")

# Les nombres dits à voix haute. « Dix-huit mille euros » est aussi concret
# que « 18 000 € ». « Un », « une » et « premier » n'y sont pas : ce sont des
# articles bien plus souvent que des quantités.
SPOKEN_NUMBERS = {
    "zéro", "deux", "trois", "quatre", "cinq", "six", "sept", "huit", "neuf",
    "dix", "onze", "douze", "treize", "quatorze", "quinze", "seize", "vingt",
    "vingts", "trente", "quarante", "cinquante", "soixante", "cent", "cents",
    "mille", "million", "millions", "milliard", "milliards", "douzaine",
    "dizaine", "dizaines", "centaine", "centaines", "moitié", "double", "triple",
}
MONEY_WORDS = {
    "euros", "euro", "balles", "dollars", "dollar", "pourcent", "pourcents",
    "salaire", "smic", "loyer", "prix", "bénéfice", "bénéfices", "revenus",
    "millionnaire", "millionnaires", "milliardaire", "milliardaires",
}

# Ce qui met quelque chose en jeu : une perte, un coût, une négation, un
# interdit. Une phrase sans aucun de ces mots est un constat.
STAKES = {
    "jamais", "arrête", "arrêter", "arrêtez", "arrêté", "stop", "erreur", "erreurs",
    "faux", "fausse", "perdu", "perdue", "perdre", "perds", "perd", "perte", "pertes",
    "coûté", "coûte", "coûtent", "coûter", "raté", "rater", "rate", "échec", "échoué",
    "personne", "rien", "pas", "plus", "non", "sans", "viré", "virée", "quitté",
    "quitter", "quitte", "démission", "supprimé", "supprime", "supprimer", "tué",
    "tue", "tuer", "remplacé", "remplace", "remplacer", "remplacent", "battu",
    "gratuit", "gratuite", "gratuitement", "payé", "payer", "paie", "facturé",
    "embauché", "sauvé", "économisé", "interdit", "interdite", "illégal", "pire",
    "déteste", "détesté", "gâché", "gaspillé", "arnaque", "mensonge", "menti",
    "ment", "mentent", "vérité", "secret", "secrets", "caché", "cachée", "volé",
    "voler", "avant", "jusqu", "lieu", "sauf", "problème", "risque", "danger",
    "attention", "regret", "regrette", "aurais", "devrais", "encore", "déjà",
    "seul", "seule", "seulement", "uniquement", "contre", "versus", "vs",
    "vraiment", "mort", "meurt", "mourir", "faillite", "dette", "dettes", "fauché",
    "ruiné", "peur", "obligé", "inutile", "inutiles", "nul", "nulle",
}

# Les ouvertures qui dépensent la première seconde à ne rien dire.
WEAK_OPENERS = [
    "salut", "hello", "coucou", "bonjour", "bonsoir", "hey", "yo", "wesh", "ok",
    "okay", "alors", "donc", "bon", "bah", "ben", "euh", "aujourd'hui",
    "en fait", "honnêtement", "écoute", "écoutez", "juste", "bref", "je vais",
    "on va", "j'ai envie", "je voulais", "je veux", "dans cette", "dans la vidéo",
    "il y a", "il existe", "est-ce que", "tu sais", "vous savez", "peut-être",
    "petit", "petite", "comme vous", "comme tu", "quand on", "je pense",
    "je sais pas", "je ne sais pas",
]

# Les impératifs qui méritent la première place.
IMPERATIVES = {
    "arrête", "arrêtez", "vole", "volez", "copie", "copiez", "supprime",
    "supprimez", "essaie", "essaye", "essayez", "regarde", "regardez", "lis",
    "lisez", "garde", "gardez", "utilise", "utilisez", "construis", "fais",
    "faites", "écris", "écrivez", "envoie", "envoyez", "prends", "prenez",
    "commence", "commencez", "quitte", "quittez", "mets", "mettez", "teste",
    "testez", "évite", "évitez", "oublie", "oubliez", "ne", "n'", "stop",
}

ADDRESS = {"tu", "t'", "toi", "te", "ton", "ta", "tes", "vous", "votre", "vos"}
FIRST_PERSON = {"je", "j'", "moi", "me", "m'", "mon", "ma", "mes", "nous", "on", "notre", "nos"}

# Les pièges. `mesure` = la clé du poids appris sur le corpus. Ceux sans
# `mesure` n'apparaissent presque jamais dans un hook parlé, donc le corpus ne
# dit rien sur eux : leur pénalité est fixée à la main, et c'est écrit.
PIEGES = [
    {"id": "si_tu", "mesure": "piege_si_tu",
     "re": re.compile(r"(?i)^\s*(?:et |mais |alors )?si (?:tu|t'|vous)\b"),
     "texte": "Ouvre sur « Si tu… ». Sur 623 reels mesurés, ces hooks font 7 % de hits "
              "contre 19 % pour les autres. Dis la chose au lieu de poser la condition."},
    {"id": "salutation", "mesure": "piege_salutation",
     "re": re.compile(r"(?i)^\s*(?:salut|hello|coucou|bonjour|bonsoir|hey|yo|wesh)\b"
                      r"|^\s*(?:c'est|ici) [A-ZÀ-Ý][a-zà-ÿ]+\s*[,.!]"),
     "texte": "Salutation. Personne n'est venu sur le fil pour qu'on lui dise bonjour."},
    {"id": "preambule", "mesure": "piege_preambule",
     "re": re.compile(r"(?i)\b(?:dans (?:cette|la) vidéo|dans ce reel|je vais (?:te|vous) "
                      r"(?:montrer|expliquer|donner|parler)|aujourd'hui,? (?:je|on) va|"
                      r"on va (?:voir|parler)|laisse-moi (?:te|vous))\b"),
     "texte": "Préambule. Supprime-le et commence par ce que tu allais annoncer."},
    {"id": "scroll", "penalite": 15,
     "re": re.compile(r"(?i)^\s*(?:arrête|arrêtez|stop|ne)\W+(?:de\s+)?(?:scroller|scrolle|défiler)"),
     "texte": "Ouvre sur « Arrête de scroller ». Demander l'attention prouve que tu ne l'as pas gagnée."},
    {"id": "hashtag", "penalite": 15, "re": HASHTAG_RE,
     "texte": "Hashtag dans le hook. Les hashtags vont en bas de la légende, s'ils vont quelque part."},
    {"id": "emoji", "penalite": 15, "re": EMOJI_RE,
     "texte": "Emoji dans le hook. À la taille d'un texte d'accroche, il y a la place pour des mots ou pour un emoji, pas les deux."},
]

CHECKS = ["LONGUEUR", "PRÉCISION", "ENJEU", "ATTAQUE", "ADRESSE"]
FEATURE_KEYS = ["longueur", "precision", "enjeu", "attaque", "adresse"]


def clamp(n):
    return max(0.0, min(100.0, n))


def normalise(text):
    text = text.replace("’", "'").replace("‘", "'")
    text = re.sub(r"[\u00a0\u202f\u2009]", " ", text)
    # « 18 000 », « 18.000 » ou « 18,000 » se disent en un seul nombre.
    return re.sub(r"(?<=\d)[ .,](?=\d{3}\b)", "", text)


def words(text):
    """Les mots tels qu'on les dit : « j'ai » et « aujourd'hui » comptent pour un."""
    return WORD_RE.findall(normalise(text))


def tokens(word):
    """Découpe l'élision pour comparer aux listes : « t'as » -> « t' », « as »."""
    low = word.lower()
    m = ELISION_RE.match(low)
    if m and len(low) > len(m.group(0)):
        return [m.group(0), low[len(m.group(0)):]]
    return [low]


def flat_tokens(text):
    out = []
    for w in words(text):
        out.extend(tokens(w))
    return out


def is_number_word(tok):
    return tok in SPOKEN_NUMBERS or any(p in SPOKEN_NUMBERS for p in tok.split("-"))


def check_length(text):
    """Un hook doit tomber avant que le pouce bouge. Environ deux secondes."""
    n = len(words(text))
    chars = len(text.strip())
    secs = n / (230 / 60)                # 230 mots par minute : débit médian mesuré sur 618 reels montés
    if 5 <= n <= 12:
        score = 100.0
    elif n < 5:
        score = clamp(100 - (5 - n) * 20)
    else:
        score = clamp(100 - (n - 12) * 11)
    if chars > 70:                       # deux lignes de gros texte à l'écran
        score -= 12
    return clamp(score), f"{n} mots, {chars} caractères, ~{secs:.1f} s à l'oral (idéal : 5 à 12 mots)"


def check_specificity(text):
    """Une chose concrète bat trois choses abstraites."""
    norm = normalise(text)
    nums = [n.strip() for n in NUMBER_RE.findall(norm) if n.strip()]
    propers = set(PROPER_RE.findall(norm))
    spoken = [t for t in flat_tokens(text) if is_number_word(t) or t in MONEY_WORDS]
    hits = len(nums) + len(propers) + len(spoken)
    score = 15.0 if hits == 0 else clamp(45 + hits * 30)
    found = ", ".join(nums[:2] + sorted(propers)[:2] + spoken[:2])
    return score, (f"{hits} élément(s) concret(s)" + (f" : {found}" if found else
                   ", ni chiffre, ni nom, rien de vérifiable"))


def check_stakes(text):
    """Une tension, un coût, une négation. Quelque chose qu'on peut perdre."""
    toks = flat_tokens(text)
    markers = sorted({t for t in toks if t in STAKES})
    if re.search(r"\d\s?(?:€|k€)|€\s?\d|\$\s?\d", normalise(text)):
        markers.append("un prix")
    n = len(markers)
    score = {0: 20.0, 1: 70.0}.get(n, 100.0)
    detail = f"{n} marqueur(s) de tension" + (f" : {', '.join(markers[:4])}" if markers else
                                               ", rien n'est en jeu dans cette phrase")
    return clamp(score), detail


def check_frontload(text):
    """Le mot fort ne peut pas être en neuvième position."""
    w = words(text)
    if not w:
        return 0.0, "vide"
    low = " ".join(x.lower() for x in w)
    penalty, hit_opener = 0, None
    for weak in WEAK_OPENERS:
        if low == weak or low.startswith(weak + " ") or low.startswith(weak + "'"):
            penalty, hit_opener = 30, weak
            break
    payload = None
    for i, word in enumerate(w):
        toks = tokens(word)
        if (any(t in STAKES or is_number_word(t) or t in MONEY_WORDS for t in toks)
                or NUMBER_RE.match(word) or (i and PROPER_RE.match(word))):
            payload = i
            break
    if payload is None:
        base, where = 30.0, "aucun mot fort dans la phrase"
    elif payload <= 3:
        base, where = 100.0, f"mot fort en position {payload + 1}"
    elif payload <= 6:
        base, where = 70.0, f"mot fort en position {payload + 1}, peut avancer"
    else:
        base, where = 40.0, f"mot fort en position {payload + 1}, trop tard"
    detail = where + (f" ; ouverture faible « {hit_opener} »" if hit_opener else "")
    return clamp(base - penalty), detail


def check_address(text):
    """Visé sur une personne, ou lancé dans le vide."""
    toks = flat_tokens(text)
    if any(t in ADDRESS for t in toks):
        return 100.0, "parle au spectateur"
    if toks and toks[0] in IMPERATIVES:
        return 90.0, f"ouvre sur un impératif (« {toks[0]} »)"
    if any(t in FIRST_PERSON for t in toks):
        return 70.0, "première personne, personne n'est visé"
    return 35.0, "troisième personne, personne dans la pièce"


def features(text):
    """Les valeurs que le modèle lit : cinq mesures entre 0 et 1, trois pièges à 0 ou 1."""
    results = {
        "LONGUEUR": check_length(text),
        "PRÉCISION": check_specificity(text),
        "ENJEU": check_stakes(text),
        "ATTAQUE": check_frontload(text),
        "ADRESSE": check_address(text),
    }
    x = {k: results[c][0] / 100 for k, c in zip(FEATURE_KEYS, CHECKS)}
    pieges = [p for p in PIEGES if p["re"].search(normalise(text))]
    for p in PIEGES:
        if "mesure" in p:
            x[p["mesure"]] = 1.0 if p in pieges else 0.0
    return results, x, pieges


def load_poids(path=POIDS):
    try:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    except (OSError, ValueError):
        return None


def linear(x, poids):
    z = poids["intercept"]
    for k, beta in poids["coefficients"].items():
        z += beta * x.get(k, 0.0)
    return z


def rank(z, poids):
    """Rang de z parmi les hooks du corpus, de 0 à 100, interpolé entre centiles."""
    q = poids["centiles_z"]
    if z <= q[0]:
        return 0.0
    if z >= q[-1]:
        return 100.0
    i = bisect.bisect_right(q, z)
    lo, hi = q[i - 1], q[i]
    frac = 0.0 if hi == lo else (z - lo) / (hi - lo)
    return clamp((i - 1 + frac) * 100 / (len(q) - 1))


def run(text, poids=None):
    """Retourne (mesures, score, verdict, pièges). Même forme que l'original de Jake."""
    poids = poids if poids is not None else _POIDS
    results, x, pieges = features(text)
    if poids:
        z = linear(x, poids)
        score = rank(z, poids)
    else:                                # fichier de poids absent : formule d'origine
        scores = [results[c][0] for c in CHECKS]
        score = clamp(statistics.mean(scores) * 0.6 + min(scores) * 0.4)
    score = clamp(score - sum(p.get("penalite", 0) for p in pieges))
    seuils = (poids or {}).get("seuils", {"fort": 67, "faible": 33})
    if score >= seuils["fort"] and not pieges:
        verdict = "FORT"
    elif score >= seuils["faible"]:
        verdict = "MOYEN"
    else:
        verdict = "FAIBLE"
    return results, score, verdict, [p["texte"] for p in pieges]


_POIDS = load_poids()


def bar(score, width=24):
    filled = round(score / 100 * width)
    return "#" * filled + "." * (width - filled)


def counted(poids=None):
    """Les mesures qui pèsent dans le score. Une mesure à poids 0 s'affiche, sans compter."""
    poids = poids if poids is not None else _POIDS
    if not poids:
        return list(CHECKS)
    return [c for c, k in zip(CHECKS, FEATURE_KEYS) if poids["coefficients"].get(k, 0) > 0]


def weakest(results, poids=None):
    pool = counted(poids) or list(CHECKS)
    return min(pool, key=lambda c: results[c][0])


def render_one(text, results, score, verdict, flags, poids=None, out=sys.stdout):
    print("\nSCORE DU HOOK", file=out)
    print("=" * 62, file=out)
    print(f"  « {text.strip()} »\n", file=out)
    live = counted(poids)
    for name in CHECKS:
        s, detail = results[name]
        tag = "" if name in live else "   (ne compte pas : poids 0 sur le corpus)"
        print(f"  {name:<11} {bar(s)} {s:5.1f}{tag}", file=out)
        print(f"  {'':<11} {detail}", file=out)
    print("-" * 62, file=out)
    print(f"  {'SCORE':<11} {bar(score)} {score:5.1f}   {verdict}", file=out)
    for f in flags:
        print(f"\n  PIÈGE  {f}", file=out)
    if verdict != "FORT":
        print(f"\n  Point faible : {weakest(results, poids)}. Corrige celui-là et relance.", file=out)
    print("", file=out)


def render_table(rows, out=sys.stdout):
    print("\nCLASSEMENT DES HOOKS\n" + "=" * 78, file=out)
    for i, r in enumerate(rows, 1):
        mark = "->" if i == 1 else "  "
        hook = r["hook"] if len(r["hook"]) <= 60 else r["hook"][:57] + "..."
        print(f"{mark} {r['score']:5.1f} {r['verdict']:<7} {hook}", file=out)
        print(f"        point faible : {r['point_faible']} ({r['mesures'][r['point_faible']]['score']:.0f})",
              file=out)
        for f in r["pieges"]:
            print(f"        piège : {f}", file=out)
    print("\nTourne le premier. Si le premier est sous 50, aucun de ces hooks n'est le bon.\n",
          file=out)


def main():
    ap = argparse.ArgumentParser(description="Note un hook de reel en français.")
    ap.add_argument("input", nargs="?", default="-", help="fichier, un hook par ligne, ou -")
    ap.add_argument("--hook", help="noter un seul hook passé en argument")
    ap.add_argument("--poids", default=POIDS, help="fichier de poids (hookscore_fr_poids.json)")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    poids = load_poids(args.poids)
    if poids is None:
        print("note : fichier de poids introuvable, formule d'origine non calibrée.", file=sys.stderr)
    if args.hook:
        lines = [args.hook]
    else:
        raw = sys.stdin.read() if args.input == "-" else open(args.input, encoding="utf-8").read()
        lines = [l.strip() for l in raw.splitlines() if l.strip()]
    if not lines:
        print("rien à noter", file=sys.stderr)
        sys.exit(2)

    payload = []
    for line in lines:
        results, score, verdict, flags = run(line, poids)
        payload.append({
            "hook": line,
            "mesures": {k: {"score": round(v[0], 1), "detail": v[1]} for k, v in results.items()},
            "point_faible": weakest(results, poids),
            "pieges": flags,
            "score": round(score, 1),
            "verdict": verdict,
        })

    if args.json:
        print(json.dumps(payload if len(payload) > 1 else payload[0], indent=2, ensure_ascii=False))
    elif len(payload) == 1:
        results, score, verdict, flags = run(lines[0], poids)
        render_one(lines[0], results, score, verdict, flags, poids)
    else:
        render_table(sorted(payload, key=lambda r: -r["score"]))

    sys.exit(0 if max(p["score"] for p in payload) >= 50 else 1)


if __name__ == "__main__":
    main()

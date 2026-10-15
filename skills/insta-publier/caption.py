#!/usr/bin/env python3
"""
caption.py : vérifie une légende et montre exactement ce que le fil affiche
avant le « ... plus ».

Adapté de instagram-agent-skill (skills/ig-caption/caption.py), Jake Schincariol,
licence MIT. Version française : demandes repérées en français, hashtags
accentués comptés en entier (#réseauxsociaux est un seul tag), et --plateforme
pour les limites de chaque réseau.

Instagram montre environ 125 caractères d'une légende dans le fil et cache le
reste derrière un tap. Presque toutes les légendes qui ratent, ratent là. Le
script affiche donc cette fenêtre dans une boîte, comme la lit un inconnu qui
scrolle, puis fait les vérifications qui valent la peine.

Les fenêtres visibles sont des approximations : elles bougent avec l'appareil,
la taille du texte et les retours à la ligne. Garde une marge plutôt que
d'écrire pile au caractère près. --truncate pour tester une autre coupe.

Usage
  python3 caption.py legende.txt
  python3 caption.py legende.txt --mots-cles "contrat freelance,prix client"
  python3 caption.py legende.txt --plateforme linkedin
  pbpaste | python3 caption.py -
  python3 caption.py legende.txt --json
"""

import argparse
import json
import re
import sys
import textwrap

# limite = caractères acceptés ; visible = caractères montrés avant la coupure
# (None : pas de coupure fiable connue) ; hashtags = plafond (None : pas de plafond) ;
# mot_cle = l'automation « commente MOT -> DM » existe sur ce réseau ;
# lien = ce qu'un lien dans le corps produit.
PLATEFORMES = {
    "instagram": {"limite": 2200, "visible": 125, "hashtags": 5, "mot_cle": True,
                  "lien": "pas cliquable dans une légende : mets-le en bio ou dans le DM"},
    "facebook": {"limite": 63206, "visible": None, "hashtags": None, "mot_cle": True,
                 "lien": "cliquable, mais un lien dans le corps freine la portée : mets-le en premier commentaire"},
    "tiktok": {"limite": 4000, "visible": None, "hashtags": None, "mot_cle": False,
               "lien": "pas cliquable dans une légende TikTok"},
    "youtube": {"limite": 5000, "visible": None, "hashtags": None, "mot_cle": False, "lien": None},
    "x": {"limite": 280, "visible": None, "hashtags": None, "mot_cle": False,
          "lien": "un lien dans le corps freine la portée : mets-le en réponse"},
    "linkedin": {"limite": 3000, "visible": 140, "hashtags": None, "mot_cle": False,
                 "lien": "un lien dans le corps freine la portée : mets-le en premier commentaire"},
    "threads": {"limite": 500, "visible": None, "hashtags": 1, "mot_cle": False,
                "lien": "un lien dans le corps freine la portée : mets-le en réponse"},
    "bluesky": {"limite": 300, "visible": None, "hashtags": None, "mot_cle": False, "lien": None},
}
# Plafond Instagram depuis le 18 décembre 2025 (annonce du compte @creators) :
# « using fewer (up to 5) more targeted hashtags, rather than many generic
# ones, can improve both your content's performance and people's experience ».

HASHTAG_RE = re.compile(r"(?:^|\s)(#\w+)")
MENTION_RE = re.compile(r"(?:^|\s)(@[\w.]+)")
LINK_RE = re.compile(r"https?://\S+|\bwww\.\S+|\b[a-z0-9-]+\.(?:com|co|io|net|org|ai|app|fr|be|ch)/\S*",
                     re.IGNORECASE)
EMOJI_RE = re.compile(r"[\U0001F300-\U0001FAFF☀-➿←-⇿️]")
CONCRETE_RE = re.compile(
    r"\d|€|(?<!^)(?<![.!?] )\b[A-ZÀ-ÖØ-Ý][a-zà-öø-ÿ]{2,}"
    r"|\b(?i:deux|trois|quatre|cinq|six|sept|huit|neuf|dix|vingt|trente|cent|mille|million)\b",
    re.MULTILINE)
KEYWORD_ASK = re.compile(r"(?i:\bcommente[sz]?\b)\s+(?:(?i:le mot)\s+)?[«\"]?\s*([A-ZÀ-Ý0-9]{2,})\b")

ASKS = [
    (KEYWORD_ASK, "commenter un mot-clé"),
    (re.compile(r"(?i)\b(?:écris-moi|écrivez-moi|envoie-moi un (?:dm|message)|envoyez-moi un (?:dm|message)|dm-moi)\b"),
     "écrire en DM"),
    (re.compile(r"(?i)\b(?:enregistre|enregistrez|sauvegarde|sauvegardez)\b"), "enregistrer"),
    (re.compile(r"(?i)\b(?:partage|partagez)[- ](?:ce|cette|le|la|à|avec|-le|-la)"), "partager"),
    (re.compile(r"(?i)\b(?:abonne-toi|abonnez-vous|suis-moi|suivez-moi)\b"), "s'abonner"),
    (re.compile(r"(?i)\blien (?:en|dans (?:ma|la)) bio\b"), "lien en bio"),
    (re.compile(r"(?i)\b(?:swipe|fais défiler|faites défiler|glisse vers)\b"), "faire défiler"),
    (re.compile(r"(?i)\b(?:dis-moi|dites-moi|tu préfères|vous préférez|laquelle|lequel)\b"), "répondre à une question"),
]

FILLER_TAGS = {"#viral", "#fyp", "#pourtoi", "#explore", "#explorepage", "#foryou", "#foryoupage",
               "#trending", "#instagood", "#love", "#follow", "#like4like", "#reels",
               "#reelsinstagram", "#viralreels", "#instadaily", "#abonnetoi", "#france", "#tendance"}


def visible_window(text, cut):
    """Ce que montre le fil. Instagram coupe au milieu d'un mot, le script aussi."""
    flat = text.strip()
    return flat if cut is None or len(flat) <= cut else flat[:cut]


def render_box(window, truncated, out=sys.stdout, width=52):
    print("\n  CE QUE VOIT LE FIL", file=out)
    print("  +" + "-" * (width + 2) + "+", file=out)
    lines = []
    for raw in window.split("\n"):
        lines.extend(textwrap.wrap(raw, width) or [""])
    for line in lines[:8]:
        print(f"  | {line:<{width}} |", file=out)
    tail = "... plus" if truncated else "(la légende tient en entier)"
    print("  +" + "-" * (width + 2 - len(tail) - 2) + f" {tail} " + "+", file=out)


def analyse(text, plateforme="instagram", cut=None, keywords=None):
    p = PLATEFORMES[plateforme]
    cut = cut if cut is not None else p["visible"]
    stripped = text.strip()
    chars = len(stripped)
    first_line = stripped.split("\n")[0].strip() if stripped else ""
    tags = HASHTAG_RE.findall(stripped)
    mentions = MENTION_RE.findall(stripped)
    links = LINK_RE.findall(stripped)
    emoji = EMOJI_RE.findall(stripped)
    window = visible_window(stripped, cut)
    truncated = cut is not None and chars > cut
    asks = [name for pattern, name in ASKS if pattern.search(stripped)]
    keyword = KEYWORD_ASK.search(stripped)
    filler = [t for t in tags if t.lower() in FILLER_TAGS]
    keywords = [k.strip() for k in (keywords or []) if k.strip()]

    checks = []

    def add(name, status, detail):
        checks.append({"check": name, "status": status, "detail": detail})

    add("LONGUEUR", "ÉCHEC" if chars > p["limite"] else "OK",
        f"{chars} / {p['limite']} caractères" + (f", {chars - p['limite']} de trop"
                                                 if chars > p["limite"] else ""))

    if not first_line:
        add("PREMIÈRE LIGNE", "ÉCHEC", "la légende commence par une ligne vide")
    elif first_line.startswith("#") or first_line.startswith("@"):
        add("PREMIÈRE LIGNE", "ÉCHEC",
            "commence par un hashtag ou une mention, la seule place qui mérite une phrase")
    elif cut is not None and len(first_line) > cut:
        add("PREMIÈRE LIGNE", "À VOIR",
            f"{len(first_line)} caractères, coupée à {cut} en pleine idée. "
            "Bien si la coupe est un suspense, mauvais si c'est une subordonnée")
    else:
        add("PREMIÈRE LIGNE", "OK", f"{len(first_line)} caractères, passe en entier")

    concrete = CONCRETE_RE.findall(window)
    add("HOOK CONCRET", "OK" if concrete else "À VOIR",
        f"{len(concrete)} chiffre(s) ou nom(s) dans la partie visible"
        + ("" if concrete else ", rien de vérifiable avant le tap"))

    cap = p["hashtags"]
    if cap is not None and len(tags) > cap:
        add("HASHTAGS", "ÉCHEC", f"{len(tags)} tags, au-delà du plafond de {cap} sur {plateforme}. "
                                "Les tags en trop ne comptent pas et le bloc fait daté")
    elif cap is not None and len(tags) == cap and filler:
        add("HASHTAGS", "À VOIR", f"{len(tags)} tags, au plafond, dont {len(filler)} génériques. "
                                "Dépense-les sur des sujets")
    elif filler:
        add("HASHTAGS", "À VOIR", f"{len(tags)} tags, dont {len(filler)} génériques "
                                f"({', '.join(filler[:3])}). Ils ne décrivent rien")
    else:
        add("HASHTAGS", "OK", f"{len(tags)} tag(s)" + (f" : {' '.join(tags)}" if tags else ""))

    if not tags:
        add("PLACEMENT DES TAGS", "OK", "aucun tag à placer")
    elif cut is not None and any(re.search(r"(?:^|\s)" + re.escape(t) + r"\b", window) for t in tags):
        add("PLACEMENT DES TAGS", "À VOIR", "un hashtag est dans la partie visible, "
                                          "de la place du fil dépensée sur une étiquette")
    else:
        add("PLACEMENT DES TAGS", "OK", "les tags sont sous la coupure")

    if links and p["lien"]:
        add("LIENS", "À VOIR", f"{len(links)} lien(s) dans le corps : {p['lien']}")
    else:
        add("LIENS", "OK", "pas de lien mort dans le corps" if not links else f"{len(links)} lien(s), ok ici")

    if len(asks) == 1:
        add("UNE DEMANDE", "OK", f"une seule demande : {asks[0]}")
    elif not asks:
        add("UNE DEMANDE", "À VOIR", "aucune demande. Décide à quoi sert ce post")
    else:
        add("UNE DEMANDE", "À VOIR", f"{len(asks)} demandes ({', '.join(asks)}). "
                                   "Deux demandes, c'est comme aucune")

    if keyword and not p["mot_cle"]:
        add("MOT-CLÉ", "ÉCHEC", f"« commente {keyword.group(1)} » sur {plateforme} : l'envoi "
                               "automatique en DM n'existe que sur Instagram et Facebook. "
                               "Retire la demande ou change-la pour ce réseau")
    elif keyword:
        add("MOT-CLÉ", "OK", f"mot-clé {keyword.group(1)} : vérifie que l'automation existe "
                               "AVANT la publication")

    density = len(emoji) * 100 / max(chars, 1)
    add("EMOJI", "À VOIR" if density > 4 else "OK",
        f"{len(emoji)} emoji, {density:.1f} pour 100 caractères"
        + (", ça fait décoration" if density > 4 else ""))

    if keywords:
        low = stripped.lower()
        found = [k for k in keywords if k.lower() in low]
        missing = [k for k in keywords if k.lower() not in low]
        in_window = [k for k in found if k.lower() in window.lower()]
        status = "OK" if not missing else ("À VOIR" if found else "ÉCHEC")
        add("RECHERCHE", status,
            f"{len(found)}/{len(keywords)} présents"
            + (f", dont {len(in_window)} dans la partie visible" if found else "")
            + (f". Manquants : {', '.join(missing)}" if missing else ""))

    fails = sum(1 for c in checks if c["status"] == "ÉCHEC")
    warns = sum(1 for c in checks if c["status"] == "À VOIR")
    verdict = "À CORRIGER" if fails else ("À REVOIR" if warns else "PRÊTE")

    return {
        "plateforme": plateforme, "characters": chars, "limit": p["limite"], "truncate_at": cut,
        "visible": window, "truncated": truncated,
        "first_line_chars": len(first_line),
        "hashtags": tags, "mentions": mentions, "links": links,
        "emoji": len(emoji), "asks": asks, "keyword": keyword.group(1) if keyword else None,
        "checks": checks, "verdict": verdict,
    }


def render(a, out=sys.stdout):
    head = (f"LÉGENDE {a['plateforme'].upper()}  ·  {a['characters']} / {a['limit']} car.  ·  "
            f"{len(a['hashtags'])} hashtag(s)  ·  {len(a['asks'])} demande(s)")
    print("\n" + head, file=out)
    print("=" * max(len(head), 62), file=out)
    render_box(a["visible"], a["truncated"], out=out)
    print("", file=out)
    for c in a["checks"]:
        print(f"  {c['status']:<6} {c['check']:<19} {c['detail']}", file=out)
    print("-" * max(len(head), 62), file=out)
    print(f"  VERDICT  {a['verdict']}\n", file=out)


def main():
    ap = argparse.ArgumentParser(description="Vérifie une légende avant publication.")
    ap.add_argument("input", nargs="?", default="-", help="fichier de la légende, ou -")
    ap.add_argument("--plateforme", default="instagram", choices=sorted(PLATEFORMES))
    ap.add_argument("--truncate", type=int, help="caractères visibles avant « ... plus »")
    ap.add_argument("--mots-cles", "--keywords", dest="keywords", default="",
                    help="termes de recherche, séparés par des virgules")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    raw = sys.stdin.read() if args.input == "-" else open(args.input, encoding="utf-8").read()
    a = analyse(raw, plateforme=args.plateforme, cut=args.truncate, keywords=args.keywords.split(","))
    if args.json:
        print(json.dumps(a, indent=2, ensure_ascii=False))
    else:
        render(a)
    sys.exit(0 if a["verdict"] == "PRÊTE" else 1)


if __name__ == "__main__":
    main()

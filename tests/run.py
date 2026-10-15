#!/usr/bin/env python3
"""
Tests d'insta-kit : les scripts tournent sur des exemples français, les accents
ne cassent plus le comptage, les copies de shared/ sont à jour, aucun tiret
cadratin dans le repo, et chaque SKILL.md ne cite que des outils PlugKit réels.

    python3 tests/run.py
"""

import json
import os
import re
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EX = os.path.join(ROOT, "tests", "exemples")
SK = os.path.join(ROOT, "skills")
FAILS = []

# Les outils PlugKit qu'un skill a le droit de citer.
ALLOWED = {
    "whoami", "list_accounts", "list_media", "upload_media", "create_media_upload",
    "check_media_upload", "get_publish_options", "create_post", "list_posts", "update_post",
    "create_comment_automation", "list_comment_automations", "update_comment_automation",
    "get_comments", "reply_to_comment", "hide_comment", "list_engagement", "reply_to_engagement",
    "get_post_analytics", "get_top_posts", "get_analytics_summary", "get_analytics_timeseries",
    "get_best_times_to_post", "get_follower_stats", "get_account_media", "reel_guide",
    "reel_create", "reel_status", "reel_preview", "reel_render", "reel_revise", "reel_hooks",
    "reel_reference",
}
# Les autres outils du serveur PlugKit : ils existent, mais aucun skill ne doit les citer.
OTHERS = {
    "boost_post", "cancel_broadcast", "create_ad", "create_ad_set", "create_broadcast",
    "create_campaign", "create_conversation", "create_profile", "create_sequence",
    "delete_broadcast", "delete_comment", "delete_comment_automation", "delete_media",
    "delete_post", "delete_profile", "delete_sequence", "disconnect_account",
    "enroll_in_sequence", "get_account", "get_account_audience", "get_ad_account",
    "get_ads_insights", "get_analytics_by_account", "get_broadcast_recipients",
    "get_comment_automation_runs", "get_connect_url", "get_conversation",
    "get_engagement_summary", "get_playbook", "get_post", "get_profile",
    "get_sequence_enrollments", "get_shopping_status", "get_subscription", "get_usage",
    "install_playbook", "list_ad_sets", "list_ads", "list_broadcasts", "list_campaigns",
    "list_conversations", "list_integration_tools", "list_integrations",
    "list_message_templates", "list_messages", "list_places", "list_playbook_installs",
    "list_playbooks", "list_profiles", "list_sequences", "mark_engagement_handled",
    "open_media_uploader", "preview_broadcast_audience", "publish_post", "query_integration",
    "reel_add_asset", "reel_buy_credits", "reel_cancel", "reel_credits", "reel_cut",
    "reel_list", "reel_list_files", "reel_mix", "reel_read_file", "reel_snapshot",
    "reel_style", "reel_style_save", "reel_taste", "reel_taste_add", "reel_view",
    "reel_write_file", "remove_playbook_install", "run_integration_action",
    "search_shop_products", "send_broadcast", "send_dm", "send_message", "set_x_billing",
    "subscribe_facebook_webhooks", "subscribe_instagram_webhooks", "sync_analytics",
    "sync_conversations", "sync_engagement", "tag_products_on_post", "unpublish_post",
    "update_ad", "update_ad_set", "update_campaign", "update_profile", "update_sequence",
}


def check(name, ok, detail=""):
    print(("  ok    " if ok else "  ÉCHEC ") + name + (f"  ({detail})" if detail and not ok else ""))
    if not ok:
        FAILS.append(name)


def run(args, stdin=None):
    p = subprocess.run([sys.executable] + args, input=stdin, capture_output=True, text=True, cwd=ROOT)
    return p.returncode, p.stdout, p.stderr


def script(skill, name):
    return os.path.join(SK, skill, name)


def main():
    print("\nCOPIES DE shared/")
    for src, dst in [("shared/hookscore_fr.py", "skills/insta-reel/hookscore_fr.py"),
                     ("shared/hookscore_fr_poids.json", "skills/insta-reel/hookscore_fr_poids.json"),
                     ("shared/slop-fr.json", "skills/insta-humain/slop-fr.json")]:
        same = open(os.path.join(ROOT, src), "rb").read() == open(os.path.join(ROOT, dst), "rb").read()
        check(f"{dst} identique à {src}", same, "lance scripts/sync-shared.sh")

    print("\nACCENTS")
    sys.path.insert(0, os.path.join(ROOT, "shared"))
    import hookscore_fr as hs
    check("hookscore : « déjà » compte pour un mot", len(hs.words("déjà vu")) == 2)
    check("hookscore : « aujourd'hui » et « j'ai » comptent pour un", len(hs.words("aujourd'hui j'ai")) == 2)
    check("hookscore : « 18 000 € » est un seul nombre", "18000" in "".join(hs.words("18 000 €")))
    sys.path.insert(0, os.path.join(SK, "insta-reel"))
    import beats
    check("beats : « Été, déjà, très » = 3 mots", len(beats.words("Été, déjà, très")) == 3)
    sys.path.insert(0, os.path.join(SK, "insta-humain"))
    import detect
    check("detect : « Ça été génial » = 3 mots", len(detect.words("Ça été génial")) == 3)
    sys.path.insert(0, os.path.join(SK, "insta-publier"))
    import caption
    a = caption.analyse("Une légende.\n\n#réseauxsociaux #été")
    check("caption : #réseauxsociaux reste un seul tag", a["hashtags"] == ["#réseauxsociaux", "#été"],
          str(a["hashtags"]))

    print("\nHOOKS (shared/hookscore_fr.py)")
    code, out, err = run([os.path.join(ROOT, "shared", "hookscore_fr.py"), os.path.join(EX, "hooks.txt"), "--json"])
    rows = json.loads(out)
    by = {r["hook"][:12]: r for r in rows}
    check("tourne sur hooks.txt", code in (0, 1) and len(rows) == 6, err)
    check("« J'ai perdu 18 000 € » est FORT", by["J'ai perdu 1"]["verdict"] == "FORT")
    check("« Si tu veux grandir » est pris dans le piège « Si tu »",
          any("Si tu" in f for f in by["Si tu veux g"]["pieges"]) and by["Si tu veux g"]["verdict"] != "FORT")
    check("la salutation finit dernière", min(rows, key=lambda r: r["score"])["hook"].startswith("Salut"))
    check("le point faible n'est jamais une mesure à poids 0",
          all(r["point_faible"] in hs.counted() for r in rows))

    print("\nHUMANISEUR (insta-humain)")
    raw = open(os.path.join(EX, "brouillon-ia.txt"), encoding="utf-8").read()
    raw = raw.replace("{CADRATIN}", "\u2014").replace("{INSECABLE}", "\u202f").replace("{ZWSP}", "\u200b")
    with tempfile.TemporaryDirectory() as tmp:
        before = os.path.join(tmp, "avant.txt")
        after = os.path.join(tmp, "apres.txt")
        open(before, "w", encoding="utf-8").write(raw)
        code, out, err = run([script("insta-humain", "humanize.py"), before, "-o", after, "--report"])
        clean = open(after, encoding="utf-8").read()
        check("humanize tourne", code == 0, err)
        check("plus de tiret cadratin", "\u2014" not in clean)
        check("plus d'invisibles", "\u200b" not in clean and "\u202f" not in clean)
        check("« booster » et « game changer » remplacés", "booster" not in clean and "game changer" not in clean.lower())
        check("l'espace avant « ! » est gardée (ponctuation française)", "régularité !" in clean, clean[:200])
        check("« Ce n'est pas X, c'est Y » signalé", "Ce n'est pas X" in err)
        check("« Le résultat ? » signalé", "Ligne-question" in err)
        code, out, err = run([script("insta-humain", "detect.py"), before, after, "--json"])
        a, b = json.loads(out)
        check("detect : le score monte après nettoyage", b["human_score"] > a["human_score"],
              f"{a['human_score']} -> {b['human_score']}")
        guill = "« C'est l'été », dit-il. J'ai déjà vu ça, t'as pas idée. " * 4
        r, _, _ = detect.run(guill, json.load(open(script("insta-humain", "slop-fr.json"), encoding="utf-8")))
        check("detect : ni ’ ni « » comptés comme empreinte", r["EMPREINTE"][0] == 100.0, r["EMPREINTE"][1])
        check("detect : « t'as pas », « c'est » lus comme de l'oral", not r["VOIX"][1].startswith("0.0 marque"), r["VOIX"][1])

    print("\nCONDUCTEUR (insta-reel/beats.py)")
    code, out, err = run([script("insta-reel", "beats.py"), os.path.join(EX, "script.txt"), "--target", "30", "--json"])
    a = json.loads(out)
    check("tourne sur script.txt", code == 0, err)
    check("boucle repérée (« vingt », « heures »...)", any(n.startswith("Boucle") for n in a["notes"]), str(a["notes"]))
    check("hook sous 3 s", a["beats"][0]["dur"] <= 3.0, str(a["beats"][0]["dur"]))

    print("\nLÉGENDE (insta-publier/caption.py)")
    code, out, err = run([script("insta-publier", "caption.py"), os.path.join(EX, "legende.txt"), "--json",
                          "--mots-cles", "contrats freelance,devis"])
    a = json.loads(out)
    check("tourne sur legende.txt", code in (0, 1), err)
    check("mot-clé DEVIS repéré", a["keyword"] == "DEVIS")
    check("une seule demande", len(a["asks"]) == 1, str(a["asks"]))
    code, out, err = run([script("insta-publier", "caption.py"), os.path.join(EX, "legende.txt"), "--json",
                          "--plateforme", "linkedin"])
    a = json.loads(out)
    check("« commente » refusé sur LinkedIn", any(c["check"] == "MOT-CLÉ" and c["status"] == "ÉCHEC" for c in a["checks"]))

    print("\nSWIPE (insta-viral/swipe.py)")
    code, out, err = run([script("insta-viral", "swipe.py"), os.path.join(EX, "releve.tsv"), "--json"])
    a = json.loads(out)
    check("tourne sur releve.tsv", code == 0, err)
    order = [r["compte"] for r in a["reels"]]
    check("classé au multiple, pas aux vues", a["reels"][0]["hook"].startswith("Vole")
          and order.index("@grand_compte") > 3, str(order))
    named = {r["hook"][:10]: r["formule_id"] for r in a["reels"]}
    check("« Personne ne te dit » = formule 3", named["Personne n"] == 3, str(named))
    check("« La motivation ne sert à rien » = contre-pied (22)", named["La motivat"] == 22, str(named))
    check("« Si tu veux plus de vues » = formule 10, marquée piège",
          any(r["formule_id"] == 10 and r["piege"] for r in a["reels"]))

    print("\nSTATS (insta-stats/stats.py)")
    code, out, err = run([script("insta-stats", "stats.py"), os.path.join(EX, "posts.tsv"), "--json"])
    a = json.loads(out)
    check("tourne sur posts.tsv", code == 0, err)
    check("un classement par réseau", set(a) == {"instagram", "tiktok"}, str(list(a)))
    check("meilleur reel Instagram = le plus gros multiple", a["instagram"]["meilleur"]["titre"].startswith("Mes devis"))
    check("vues sans abonnés repérées", any("bio" in n for n in a["instagram"]["notes"]), str(a["instagram"]["notes"]))

    print("\nREPO")
    dash_files = []
    for base, dirs, files in os.walk(ROOT):
        dirs[:] = [d for d in dirs if d not in (".git", "__pycache__")]
        for f in files:
            path = os.path.join(base, f)
            try:
                if "\u2014" in open(path, encoding="utf-8").read():
                    dash_files.append(os.path.relpath(path, ROOT))
            except (UnicodeDecodeError, OSError):
                pass
    check("aucun tiret cadratin dans le repo", not dash_files, ", ".join(dash_files))
    known = ALLOWED | OTHERS
    for doc in ("README.md", "CLAUDE.md"):
        text = open(os.path.join(ROOT, doc), encoding="utf-8").read()
        bad = sorted((set(re.findall(r"\b[a-z]+(?:_[a-z]+)+\b", text)) & known) - ALLOWED)
        check(f"{doc} : outils PlugKit tous dans la liste", not bad, ", ".join(bad))
    for skill in sorted(os.listdir(SK)):
        path = os.path.join(SK, skill, "SKILL.md")
        if not os.path.exists(path):
            check(f"{skill}/SKILL.md existe", False)
            continue
        text = open(path, encoding="utf-8").read()
        cited = set(re.findall(r"\b[a-z]+(?:_[a-z]+)+\b", text)) & known
        bad = sorted(cited - ALLOWED)
        check(f"{skill} : outils PlugKit tous dans la liste ({len(cited)} cités)", not bad, ", ".join(bad))
        check(f"{skill} : lien PlugKit avec UTM",
              skill == "insta-humain" or "plugkit.co/fr?utm_source=github&utm_campaign=insta-kit" in text)

    print(f"\n{'TOUT PASSE' if not FAILS else str(len(FAILS)) + ' ÉCHEC(S)'}\n")
    sys.exit(1 if FAILS else 0)


if __name__ == "__main__":
    main()

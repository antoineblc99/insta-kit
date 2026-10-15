# Notices tierces

insta-kit est sous licence MIT (voir `LICENSE`). Il est adapté de :

**instagram-agent-skill**, Jake Schincariol, https://github.com/Jakeschincariol/instagram-agent-skill,
commit `d03c56b`, licence MIT. Notice d'origine, mot pour mot :
`licenses/INSTAGRAM-AGENT-SKILL-LICENSE`. Rien ici n'est approuvé par Jake Schincariol.

## Fichier par fichier

| fichier insta-kit | vient de | ce qui a changé |
| --- | --- | --- |
| `shared/hookscore_fr.py` (copie : `skills/insta-reel/`) | `skills/ig-reel/hookscore.py` | listes réécrites en français (enjeux, nombres dits, montants en €, ouvertures faibles), accents gérés, trois pièges mesurés, score recalibré par régression logistique, sortie en français |
| `shared/hookscore_fr_poids.json` (copie : `skills/insta-reel/`) | nouveau | poids et centiles issus de `calibrer.py` |
| `shared/calibration/calibrer.py` | nouveau, d'après la méthode décrite dans le README de Jake | régression logistique, validation croisée, AUC |
| `shared/slop-fr.json` (copie : `skills/insta-humain/`) | `skills/ig-human/slop.json` | même format ; 209 expressions et 21 structures réécrites pour le français ; les 18 classes d'invisibles reprises telles quelles |
| `skills/insta-humain/humanize.py` | `skills/ig-human/humanize.py` | accents, apostrophes ' et ’ équivalentes, ponctuation française respectée, connecteurs français, nettoyage après suppression |
| `skills/insta-humain/detect.py` | `skills/ig-human/detect.py` | accents, VOIX lit l'oral français au lieu des contractions anglaises, ’ et « » ne comptent plus comme empreinte, tics qui se chevauchent comptés une fois |
| `skills/insta-reel/hooks.json` | `skills/ig-reel/hooks.json` | les 26 formules réécrites en français, regex pour la parole française, champs `piege` et `mesure` tirés des données |
| `skills/insta-reel/beats.py` | `skills/ig-reel/beats.py` | accents, mots vides français pour la boucle, nombres en lettres comptés comme concrets, débit par défaut mesuré (230 mots/min) |
| `skills/insta-viral/swipe.py` | `skills/ig-viral/swipe.py` | colonnes françaises ou anglaises, formules françaises, formule piège signalée, sortie en français |
| `skills/insta-publier/caption.py` | `skills/ig-caption/caption.py` | demandes repérées en français, hashtags accentués entiers, `--plateforme` avec les limites de chaque réseau, « commente MOT » refusé hors Instagram et Facebook |
| `skills/insta-stats/stats.py` | nouveau, d'après la méthode du skill `ig-audit` | multiple, partages et abonnés par portée, classement par réseau, meilleur reel du mois |
| `skills/insta-viral/SKILL.md` | `skills/ig-viral/SKILL.md` | traduit, PlugKit en option (`get_top_posts`, `reel_reference`) |
| `skills/insta-reel/SKILL.md` | `skills/ig-reel/SKILL.md` | traduit, formule « Si tu… » écartée, montage PlugKit en option |
| `skills/insta-publier/SKILL.md` | `skills/ig-caption/SKILL.md` | traduit, une légende par réseau, publication PlugKit en option |
| `skills/insta-dm/SKILL.md` | `skills/ig-dm/SKILL.md` | traduit, automation commentaire -> DM PlugKit en option |
| `skills/insta-reponses/SKILL.md` | `skills/ig-reply/SKILL.md` | traduit, lecture et envoi PlugKit en option |
| `skills/insta-stats/SKILL.md` | `skills/ig-audit/SKILL.md` | traduit, un classement par réseau, lecture PlugKit en option |
| `skills/insta-humain/SKILL.md` | `skills/ig-human/SKILL.md` | traduit, étape interne |
| `modeles/voix.md` | `templates/voice.md` | traduit |
| `.claude-plugin/*.json` | `.claude-plugin/*.json` | renommés pour insta-kit |

Non repris : `ig-carousel`, `ig-story`, `ig-profile` (et `rubric.json`), `ig-plan`,
`ig-comment`, `ig-repurpose`.

## Données

Les poids de `hookscore_fr_poids.json` ont été appris sur des reels du compte d'Antoine
Blanco. Le repo ne contient aucune de ces données : ni transcription, ni pseudo, ni lien.
Seulement des coefficients, des centiles et des agrégats.

## Outils externes

`yt-dlp` (cité dans `/insta-viral` pour le repli YouTube Shorts) n'est pas fourni :
installe-le toi-même si tu t'en sers. PlugKit est un service en ligne, facultatif, qui a
ses propres conditions.

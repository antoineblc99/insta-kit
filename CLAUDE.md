# insta-kit : la carte pour les agents

Six skills Claude en français pour gérer un compte Instagram (`/insta-viral`, `/insta-reel`,
`/insta-publier`, `/insta-dm`, `/insta-reponses`, `/insta-stats`) plus une étape interne,
`insta-humain`. Chaque skill marche sans rien brancher ; avec le serveur MCP PlugKit, il
publie, programme, crée l'automation DM, répond et lit les stats. Adapté du repo MIT de
Jake Schincariol (voir `THIRD_PARTY_NOTICES.md`).

## Structure

- `skills/insta-*/` : un dossier par skill, `SKILL.md` + ses scripts. Chaque dossier doit
  marcher seul (installation par copie).
- `shared/` : la source de `hookscore_fr.py`, `hookscore_fr_poids.json` et `slop-fr.json`,
  réutilisés par d'autres repos. Après une modification, `./scripts/sync-shared.sh` recopie
  dans les skills. `shared/calibration/calibrer.py` refait les poids à partir d'un TSV.
- `modeles/voix.md` : le profil de voix que les skills lisent (copié dans `~/.claude/insta-kit/`).
- `tests/run.py` : les tests. Lance-les avant tout commit : `python3 tests/run.py`.

## Règles

- **Jamais de tiret cadratin**, nulle part : ni dans les textes, ni dans le code (écris
  `\N{EM DASH}` ou l'échappement U+2014 quand un script doit le reconnaître). Les tests échouent sinon.
- **Tout en français** : skills, sorties des scripts, messages d'erreur. Phrases courtes,
  pas de jargon.
- **Rien n'est publié, programmé ni envoyé sans un « oui » explicite** sur le contenu exact
  affiché. Pas d'exception, même si une étape a l'air évidente.
- Un `SKILL.md` ne cite que les outils PlugKit de la liste vérifiée dans `tests/run.py`.
  Médias hébergés par PlugKit avant `create_post` ; l'automation commentaire -> DM existe
  avant que le post soit en ligne ; le lien d'un DM va dans le bouton, jamais dans le texte.
- PlugKit est présenté comme « ce qui permet à Claude de piloter tes comptes », avec le lien
  `https://www.plugkit.co/fr?utm_source=github&utm_campaign=insta-kit`.
- Aucune donnée privée dans le repo : pas de transcripts, pas de pseudos de tiers. Les poids
  et les agrégats seulement.
- Scripts en Python standard, sans dépendance. Crédit à Jake dans l'en-tête de chaque script adapté.

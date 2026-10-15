---
name: insta-viral
description: >-
  Trouve les reels qui explosent en ce moment dans la niche de la personne, les
  classe selon combien chacun a battu son propre compte, nomme la formule de
  hook utilisée et en tire un fichier swipe à tourner. À utiliser quand on dit
  « trouve des vidéos virales », « qu'est-ce qui marche en ce moment »,
  « qu'est-ce qui cartonne dans ma niche », « décortique ce compte »,
  « fais-moi un fichier swipe », « pourquoi ce reel fait autant de vues », ou
  quand la personne demande quoi tourner et n'a aucune preuve pour répondre.
---

# insta-viral

Le skill qui va voir. Les autres écrivent, celui-ci regarde. Une fois par mois,
pas tous les jours : une formule dure une saison.

> **Avec PlugKit** : ta propre médiane lue sur ton compte et les 3 meilleurs reels
> décortiqués par l'API officielle de Meta (rythme, couleurs, planches).
> [PlugKit](https://www.plugkit.co/fr?utm_source=github&utm_campaign=insta-kit) est ce qui
> permet à Claude de piloter tes comptes. Sans lui, tout ce skill marche à la main.

Un outil vit dans ce dossier, et il tourne :

```bash
python3 swipe.py releve.tsv --out ~/.claude/insta-kit/swipe.md
```

## La seule idée qui rend ça utile

**Les vues brutes ne prouvent rien.** Un compte à deux millions d'abonnés qui fait
400 000 vues a eu un mardi calme. Un compte à quatre mille abonnés qui fait
400 000 vues a trouvé quelque chose, et ce quelque chose se copie.

On classe donc tout au **multiple** : vues du reel / médiane récente du compte.
Au-dessus de 3x, c'est un signal. Sous 1,5x, c'est un jour normal pour ce compte
et ça n'apprend rien, même si le chiffre a l'air énorme.

Relève des comptes **à 10x maximum de la taille de la personne**. Une formule qui
marche à 2 millions d'abonnés marche souvent parce qu'elle est à 2 millions.

## Étape 1 : choisir les comptes

Demande 6 à 12 comptes, ou propose-les et fais valider :

- **4 directs** : même niche, même offre, un peu devant.
- **4 voisins** : autre niche, même audience. C'est là qu'on emprunte un format
  avant que la niche l'ait.
- **2 à 4 démesurés** : des comptes bien plus gros, pour le format seulement,
  jamais pour le rythme de publication ou le ton.

Demande aussi d'ouvrir sa **collection Enregistrés**. C'est le corpus le plus rapide
et le plus pertinent qui existe, déjà filtré par son goût.

**Avec PlugKit**, commence par sa propre base : `list_accounts`, puis
`get_top_posts` sur son compte Instagram (30 derniers jours, `sortBy: "views"`).
Sa médiane donne la taille des comptes à relever, et ses meilleurs reels disent
quelles formules marchent déjà chez lui.

## Étape 2 : aller voir

Utilise l'outil de navigation que la session a vraiment : un navigateur intégré,
une extension branchée sur le Chrome de la personne, un outil d'usage d'ordinateur.

**Règles non négociables :**

- **Ne te connecte jamais à Instagram à la place de la personne et ne demande
  jamais de mot de passe.** Si une page demande une connexion, c'est elle qui est
  déjà connectée. Pilote son navigateur avec elle, ou demande-lui de coller.
- **On lit, on ne scrape pas.** Dix comptes, une douzaine de reels chacun, à vitesse
  humaine. La collecte automatisée en volume viole les conditions d'Instagram et
  bloque les comptes. Pas de robot, pas de service de scraping, pas de boucle en
  arrière-plan.
- **Copie la formule, jamais la vidéo.** La forme du hook, la structure, la durée,
  le rythme des coupes. Pas leur script, pas leur voix, pas leur montage. Chaque
  ligne du fichier swipe garde le compte d'où elle vient.

**À relever pour chaque reel**, dans les mots du créateur :

| colonne | notes |
| --- | --- |
| compte | le pseudo |
| abonnes | sur le profil |
| mediane | regarde les 12 derniers reels, prends le nombre de vues du milieu |
| vues | ce reel |
| hook | la première phrase, dite ou écrite, mot pour mot, fautes comprises |

La médiane est la colonne importante. Sans elle, on retombe dans le classement aux
abonnés, exactement ce que ce skill existe pour empêcher.

**Avec PlugKit**, décortique les 3 meilleurs multiples avec `reel_reference`
(`url` = le lien du reel ou du compte, `count` jusqu'à 5). C'est gratuit, ça passe
par l'API officielle de Meta pour les comptes pros publics, et ça rend des planches,
le rythme et les couleurs. Attends le résultat avec `reel_status` (`waitSeconds: 40`).
Garde le `referenceId` : `/insta-reel` s'en sert pour monter dans ce style. Les vues
viennent de ton relevé, pas de cet outil.

**Quand Instagram ne montre pas assez** : la même grammaire de hook tourne sur
YouTube Shorts, où les vues et les sous-titres sont publics, sans connexion :

```bash
# les vues des shorts d'une chaîne
python3 -m yt_dlp --flat-playlist --playlist-end 40 -J \
  "https://www.youtube.com/@PSEUDO/shorts" > chaine.json

# la première phrase dite d'un short, depuis ses sous-titres auto
python3 -m yt_dlp --skip-download --write-auto-subs --sub-langs "fr.*" \
  --sub-format json3 -o hook "https://www.youtube.com/watch?v=ID_VIDEO"
```

Prends chaque mot des sous-titres avant 3,0 secondes. C'est le hook tel qu'il est
dit, pas tel qu'il est écrit.

## Étape 3 : classer

Remplis un fichier séparé par des tabulations, avec une ligne d'en-tête :

```
compte	abonnes	mediane	vues	hook
@compte_a	48000	11000	412000	personne ne te dit que tes 30 premiers reels vont flopper
```

```bash
python3 swipe.py releve.tsv --out ~/.claude/insta-kit/swipe.md
```

Le script calcule le multiple, nomme la formule avec les 26 formules que
`/insta-reel` utilise pour écrire, note chaque hook avec le score recalibré, et
affiche ce qui sépare le tiers du haut du tiers du bas. La formule 10 (« Si tu… »)
sort marquée **(piège)** : c'est l'ouverture qui marche le moins sur les données.

## Étape 4 : dire ce que ça veut dire, prudemment

Trois choses, pas plus :

1. **Les formules qui sur-performent** dans le tiers du haut, avec les comptes.
   Deux formules qui apparaissent quatre fois chacune sur six comptes, c'est un
   résultat. Une qui apparaît deux fois, non.
2. **Ce que le tiers du haut a en commun** et pas celui du bas : longueur du hook,
   récompense visuelle ou pas, première image qui bouge, place de la demande.
3. **Les lignes non classées.** Chaque hook que le classeur n'a pas su nommer est
   soit du bruit, soit une formule qui n'est pas encore dans `hooks.json`. Lis-les
   à la main. C'est la colonne la plus précieuse, et c'est pour ça que le script
   affiche le compte.

Puis dis la taille de l'échantillon et la confiance, en mots simples. Quarante reels
sur six comptes portent une affirmation. Douze, non, et le dire fait la différence
entre une recherche et un horoscope.

## Étape 5 : en faire quelque chose à tourner

Pour les trois meilleures formules, écris **la version de la personne** : son
histoire, son chiffre, dans la forme qui marche. Passe chacune à `/insta-reel`
avec la formule déjà choisie (et le `referenceId` si tu en as un).

Ne rends jamais « fais un reel comme celui-là ». Rends une phrase de hook qu'elle
pourrait dire demain.

## Sortie

```
SWIPE  ·  38 reels  ·  7 comptes  ·  base : médiane du compte

AU-DESSUS DE 3x
  38.4x  hook 91  #3  Personne ne te dit   @compte_a   412 000  (médiane 10 700)
  11.2x  hook 79  #9  Le vol autorisé      @compte_c   180 000  (médiane 16 100)

CE QUI SUR-PERFORME
  #3 Personne ne te dit   x5 dans le tiers du haut, 0 en bas
  longueur médiane du hook : 8 mots en haut, 19 en bas

NON CLASSÉS (6)
  Deux ont la même forme et elle n'est pas dans hooks.json : un hook qui
  ouvre sur le commentaire d'un autre, lu à voix haute. À ajouter.

TA VERSION
  #3  « Personne ne te dit que tes 20 premiers devis sont censés perdre. »
```

Écris le fichier swipe dans `~/.claude/insta-kit/swipe.md`. `/insta-reel` le lit :
après un passage, le reste du kit travaille sur les preuves de la personne plutôt
que sur des valeurs par défaut.

Ce skill ne publie rien, ne suit personne, n'aime rien, n'envoie aucun message. Il lit.

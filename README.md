# insta-kit

Six skills Claude, gratuits, en français, pour gérer ton Instagram.

Le premier trouve les reels qui explosent dans ta niche et les classe selon combien chacun
a battu son propre compte. Le deuxième t'écrit le tien à partir de ce qui marche, avec un
hook noté sur 623 vrais reels avant que tu tournes. Les autres écrivent la légende, mettent
en place le DM mot-clé, répondent à tes commentaires, et lisent tes stats pour sortir ton
meilleur reel du mois.

Tout marche sans rien brancher. Branche [PlugKit](https://www.plugkit.co/fr?utm_source=github&utm_campaign=insta-kit),
ce qui permet à Claude de piloter tes comptes, et le même kit publie et programme tes reels
sur sept réseaux d'un coup, envoie ton lien en DM quand on commente ton mot-clé, répond à
tes commentaires et lit tes stats tout seul.

**Rien n'est publié, programmé ni envoyé sans ton « oui ».** Sur le contenu exact affiché, à
chaque fois.

## Installer

Colle ça dans Claude :

```
https://github.com/antoineblc99/insta-kit

Installe ce kit, puis vérifie que /insta-reel marche.
```

Ou en plugin, dans Claude Code :

```
/plugin install insta-kit --marketplace antoineblc99/insta-kit
```

Sur une version plus ancienne de Claude Code, en deux temps :

```
/plugin marketplace add antoineblc99/insta-kit
/plugin install insta-kit
```

Ou à la main :

```bash
git clone https://github.com/antoineblc99/insta-kit.git
cp -r insta-kit/skills/insta-* ~/.claude/skills/
```

Pour un seul projet plutôt que partout : copie les mêmes dossiers dans le `.claude/skills/`
du projet. Pas de Claude Code du tout ? Colle un `SKILL.md` en haut d'une conversation et il
tourne comme un mode. Tu perds les scripts, qui sont l'essentiel de `/insta-reel` et de
l'humaniseur, mais le reste marche.

Ensuite, dix minutes sur `modeles/voix.md`. Copie-le dans `~/.claude/insta-kit/voix.md` et
remplis-le, ou envoie trois de tes reels à Claude et dis « écris mon voix.md à partir de
ça ». Tous les skills le lisent. Ça compte plus ici qu'ailleurs : ces mots, tu vas les dire
à voix haute.

### Brancher PlugKit (facultatif)

PlugKit est un serveur MCP : Claude s'y connecte et pilote tes comptes par les API
officielles (Instagram, Facebook, TikTok, YouTube, X, LinkedIn, Threads, Bluesky).
7 jours gratuits.

- **Claude (web ou appli)** : Personnaliser > Connecteurs > Ajouter un connecteur
  personnalisé, colle `https://api.plugkit.co/mcp`, puis Autoriser.
- **Claude Code** : `claude mcp add --transport http plugkit https://api.plugkit.co/mcp`,
  puis `/mcp` pour te connecter.
- **ChatGPT et les autres** : dans PlugKit, Comptes > PlugKit dans mon IA, choisis ton
  application et suis les étapes.

Puis connecte tes réseaux dans PlugKit. Chaque skill le détecte et dit en une ligne ce que
ça ajoute.

## Les six

| commande | sans rien brancher | avec PlugKit |
| --- | --- | --- |
| `/insta-viral` | Tu relèves 6 à 12 comptes, il classe leurs reels au multiple (vues / médiane du compte), nomme la formule de hook et écrit ton fichier swipe. | Ta médiane lue sur ton compte, les 3 meilleurs reels décortiqués par l'API de Meta (rythme, couleurs). |
| `/insta-reel` | Trois hooks tirés de [26 formules](skills/insta-reel/hooks.json), notés, puis le script, le texte à l'écran et un conducteur minuté. | Le rush monté sur les serveurs PlugKit (Express par défaut, Studio sur devis), les hooks battus en ouvertures alternatives. |
| `/insta-publier` | La légende, une par réseau, vérifiée : ce que le fil montre avant le « ... plus », une seule demande, cinq hashtags au plus. | Programmé sur tous tes réseaux au meilleur créneau, après ton « oui ». |
| `/insta-dm` | La livraison du mot-clé, le premier message, la proposition de collab, deux relances. | L'automation : chaque commentaire avec ton mot-clé reçoit ton lien en DM, dans un bouton, sur Instagram et ta Page Facebook. |
| `/insta-reponses` | Tu colles tes commentaires, il les trie en six seaux et écrit les réponses qui valent la peine. | Les commentaires en attente lus sur tous tes posts, les réponses envoyées après un « oui » sur le lot. |
| `/insta-stats` | Tu colles tes stats, il classe au multiple et aux partages, pas aux vues, et sort ton meilleur reel du mois. | Les stats de tous tes réseaux lues directement, un classement par réseau. |

Et une étape interne, `insta-humain`, que les quatre skills qui écrivent appellent avant de
te montrer un texte : elle retire les tirets cadratins, les tics de l'IA en français et les
caractères invisibles, puis note ce qui reste.

## Les outils qui tournent

Python standard, sans dépendance, rien n'est envoyé nulle part. Ils tournent sur ta machine,
sur ton texte.

### Le hook

```bash
python3 hookscore_fr.py hooks.txt              # classe tes hooks
python3 beats.py script.txt --target 30        # minute le script avant de tourner
```

```
CLASSEMENT DES HOOKS
==============================================================================
->  99.0 FORT    J'ai perdu 18 000 € à cause d'une seule clause dans un co...
        point faible : PRÉCISION (75)
    96.9 FORT    Mes devis me prenaient cinq heures. Maintenant, vingt min...
        point faible : ENJEU (20)
    91.0 FORT    Personne ne te dit que tes 30 premiers reels sont censés ...
        point faible : LONGUEUR (66)
    69.6 MOYEN   Arrête de scroller si tu veux percer sur Instagram en 2026 🔥
        piège : Ouvre sur « Arrête de scroller ». Demander l'attention prouve que tu ne l'as pas gagnée.
    16.6 FAIBLE  Si tu veux grandir sur Instagram, regarde cette vidéo jus...
        piège : Ouvre sur « Si tu… ». Sur 623 reels mesurés, ces hooks font 7 % de hits contre 19 % pour les autres.
     0.0 FAIBLE  Salut c'est Marie, aujourd'hui je vais te parler de strat...
        piège : Salutation. Personne n'est venu sur le fil pour qu'on lui dise bonjour.
```

Le score va de 0 à 100 : c'est le rang du hook parmi les premières phrases de 623 reels
réels. 91 = mieux que 91 % d'entre elles, d'après le modèle. Ce que ça vaut vraiment est
plus bas, dans « Ce que j'ai mesuré ».

`beats.py` estime le temps de chaque ligne, les empile en timecodes et signale les quatre
choses qui tuent un reel au montage : un hook qui dépasse trois secondes, un temps assez long
pour qu'on parte, une suite de lignes sans rien de concret, et pas de boucle vers la
première ligne.

```
CONDUCTEUR  ·  86 mots  ·  ~22.4 s à 230 mots/min  ·  cible 30 s
========================================================================
  0:00.0   2.4s  HOOK    Mes devis me prenaient cinq heures. Maintenant, vingt minutes.
  0:02.4   3.1s          Le problème, ce n'était pas la rédaction. C'était la mise en page.
  0:05.5   4.2s          Je recopiais les mêmes blocs à la main, client après client, et je perdais le fil.
                         ^ 4.2 s sur un seul temps
  ...
  0:19.3   3.1s  CTA     Commente DEVIS et je t'envoie le modèle. Vingt minutes, pas cinq heures.
------------------------------------------------------------------------
  - Boucle : le dernier temps reprend « cinq, devis, heures » du hook. Les revisionnages, c'est de la portée gratuite.
  - 7.6 s sous la cible. Ajoute 29 mots ou tourne-le court. Court, c'est souvent mieux.
```

Le débit par défaut, 230 mots par minute, est le débit médian mesuré sur 618 reels français
montés. Une voix posée tourne plutôt autour de 180 : `--wpm` pour le tien.

### La légende

```bash
python3 caption.py legende.txt --mots-cles "devis freelance,contrat"
python3 caption.py legende.txt --plateforme tiktok
```

Instagram montre environ 125 caractères d'une légende et cache le reste derrière un tap.
Presque toutes les légendes qui ratent, ratent là. Le script affiche cette fenêtre comme la
lit un inconnu qui scrolle :

```
  CE QUE VOIT LE FIL
  +------------------------------------------------------+
  | Cinq heures par devis, c'était mon quotidien il y a  |
  | un an. Aujourd'hui j'en envoie un en vingt minutes,  |
  | et voici le modèle ex                                |
  +-------------------------------------------- ... plus +

  À VOIR PREMIÈRE LIGNE      129 caractères, coupée à 125 en pleine idée
  OK     HOOK CONCRET        2 chiffre(s) ou nom(s) dans la partie visible
  OK     HASHTAGS            3 tag(s) : #freelance #devis #independant
  OK     UNE DEMANDE         une seule demande : commenter un mot-clé
  OK     MOT-CLÉ             mot-clé DEVIS : vérifie que l'automation existe AVANT la publication
```

Il applique le plafond actuel, **cinq hashtags par post** (Instagram l'a fixé le
18 décembre 2025), compte `#réseauxsociaux` comme un seul tag, et refuse un « commente MOT »
sur un réseau où l'envoi automatique en DM n'existe pas.

### L'humaniseur

```bash
python3 humanize.py brouillon.txt --report     # nettoie, montre chaque changement
python3 detect.py brouillon.txt                 # note, cinq mesures
python3 detect.py avant.txt apres.txt           # prouve l'écart
```

**Ce qui part tout seul :** les caractères invisibles, les tirets cadratins, les guillemets
anglais, et 209 tics de l'IA en français avec leur remplacement simple (« booster », « il est
crucial de », « tirer parti de », « un véritable game changer », « dans un monde en
constante évolution »), plus le bloc Instagram (« arrête de scroller », « abonne-toi pour
plus », « l'algorithme adore »). Tout est dans [`slop-fr.json`](shared/slop-fr.json), fait
pour être modifié.

**Ce qui ne bouge pas :** les guillemets « », l'apostrophe ’ et l'espace avant ? ! : ;.
C'est la typographie normale du français, pas une empreinte.

**Ce qui est signalé, pas corrigé :** « Ce n'est pas X, c'est Y », « Non seulement… mais
aussi », les triades, « Le résultat ? », « Et si je te disais que », « N'hésite pas à »,
« Que tu sois débutant ou expert », les puces en emoji, les murs de hashtags. Changer la
forme d'une phrase demande du jugement.

Sur une légende écrite pour être la pire possible : 9,7 SIGNALÉ avant, 40,5 après le
nettoyage automatique, structures pas encore réécrites. La réécriture des lignes signalées
fait le reste.

### Le fichier swipe et les stats

```bash
python3 swipe.py releve.tsv --out ~/.claude/insta-kit/swipe.md
python3 stats.py posts.tsv
```

Les vues brutes ne prouvent rien. Un compte à 2 millions d'abonnés qui fait 400 000 vues a
eu un mardi calme. Un compte à 4 000 abonnés qui fait 400 000 vues a trouvé quelque chose.
Les deux scripts classent au multiple sur la médiane du compte, et `stats.py` ajoute les
partages et les abonnés par portée : des vues sans abonnés, c'est un problème de bio, pas
de hook.

## Ce que j'ai mesuré, la partie qui vaut la peine d'être lue

Je ne voulais pas publier un score de hook sur la foi qu'il « a l'air juste ». Jake
Schincariol, dont ce kit est adapté, avait testé le sien sur 74 hooks de YouTube Shorts en
anglais. J'ai refait l'exercice en français, sur mes propres reels.

**Le corpus.** Mes 1 900 reels Instagram publiés entre 2020 et 2026 (101 millions de vues,
lus par l'API officielle), dont 1 842 transcrits mot à mot. 961 sont parlés ; 623 sont parlés en
français, les autres sont des extraits en anglais ou de la musique. Pour chaque reel, le
hook = la première phrase dite (30 mots au plus). Un « hit » = un reel qui fait au moins
2 fois la médiane des 50 reels publiés autour de lui (25 avant, 25 après), ce qui corrige
l'effet d'époque : 18 % des reels sont des hits.

**La méthode.** Les cinq mesures du score (LONGUEUR, PRÉCISION, ENJEU, ATTAQUE, ADRESSE)
plus trois pièges (« Si tu… », salutation, préambule), combinés par une régression
logistique. Une contrainte : une mesure ne peut que faire monter le score, un piège que le
faire baisser ; si les données veulent l'inverse, la mesure sort du modèle. Mesure :
l'AUC, la probabilité qu'un hit pris au hasard soit mieux noté qu'un raté pris au hasard.
0,50 = pile ou face, 1,00 = parfait. En validation croisée (5 blocs, 20 fois), donc sur des
reels que le modèle n'a pas vus. Le script est dans le repo : [`calibrer.py`](shared/calibration/calibrer.py).
Les données, non : ce sont des transcriptions privées.

**Quatre résultats, dont deux qui ne font pas plaisir :**

**1. Le score sépare un peu mieux qu'une pièce, pas beaucoup plus.** AUC **0,59** (de 0,58
à 0,61 selon le découpage). La formule de Jake avec mes listes françaises, sans calibration :
0,57. Son script anglais tel quel sur mes phrases françaises : 0,565. Concrètement, le tiers
des hooks les mieux notés fait 22 % de hits, le tiers du milieu 19 %, le tiers du bas 13 %.
Les hooks du haut cartonnent 1,75 fois plus souvent que ceux du bas. C'est réel et c'est
modeste.

**2. « Si tu… » est un piège, et c'est le résultat le plus net.** Les reels qui ouvrent sur
« Si tu… » font **7 % de hits** (43 reels) contre 19 % pour les autres. Avec une définition
plus large (« si tu », « tu es », « quand tu », étiquetage automatique sur les 961 reels
parlés) : 8 % sur 137 reels, contre 18 % de base, le pire des huit types d'ouverture. Le
meilleur : l'affirmation contre-intuitive, 24 % sur 220 reels. Les salutations (« Salut,
c'est… ») : 0 hit sur 16. Le préambule (« je vais te montrer ») : 9 % sur 11, trop peu pour
conclure mais dans le même sens. La formule « Si tu… » de Jake (sa n°10) est donc marquée
piège dans [`hooks.json`](skills/insta-reel/hooks.json), et `/insta-reel` ne la propose plus.

**3. Deux mesures de Jake ne tiennent pas sur mes reels.** ATTAQUE (le mot fort en début de
phrase) et ADRESSE (parler au spectateur) vont à contresens : les hooks qui disent « tu »
font même un peu moins de hits (AUC 0,44 seule), et ce n'est pas un effet de sujet, on le
retrouve en fitness, en mindset et sur l'IA. Le modèle leur donne un poids nul ; le script
les affiche quand même, marquées « ne compte pas ». PRÉCISION reste la mesure la plus utile
(0,56 seule), comme chez Jake : un chiffre, un nom, un montant.

**4. Le passé ne prédit pas bien le futur.** Appris sur mes reels jusqu'en 2023 (fitness,
mindset), testé sur les 146 reels d'après (surtout l'IA et le business) : AUC 0,52, presque pile ou face. Ce
qui marchait dans une niche ne se transporte pas tel quel dans une autre.

Et le classeur de formules : les regex anglaises de Jake nomment 1 % de mes premières
phrases françaises. Réécrites pour la parole française, elles en nomment **33 %** (207 sur
623). Le reste n'a pas de formule, et c'est normal : beaucoup de reels n'en ont pas.

**L'usage honnête, donc :** tuer les hooks évidemment faibles avant de tourner (salutation,
« Si tu… », préambule, rien de concret), puis croire ta courbe de rétention. Rien qui lit
du texte ne peut dire lequel de deux bons hooks va percer : c'est ton visage, ton montage,
ton son et les gens à qui Instagram le montre.

**Les limites, écrites ici plutôt qu'enterrées :** un seul créateur, un seul compte, le mien,
avec ses sujets et son époque. Le hit dépend de choses que le texte ne voit pas. L'étiquetage
« si tu / contre-intuitif » est automatique. Le seuil de 2x est un choix. Si tu as tes
propres reels transcrits, refais la calibration avec `calibrer.py` : si tu trouves autre
chose, je préfère le savoir.

## Les petites lignes, la partie honnête

**Ces skills publient, mais seulement par les API officielles, et seulement après ton
« oui ».** Sans PlugKit, ils écrivent et tu publies. Avec PlugKit, la publication, les DM et
les réponses passent par les API officielles des plateformes, jamais par un navigateur
automatisé : c'est ce qui fait bloquer les comptes. Chaque action publique s'arrête sur une
porte où tu vois le contenu exact.

**L'automation DM ne répond qu'à quelqu'un qui a commenté.** Jamais de DM à froid automatisé.
Elle est créée avant que le post soit en ligne, sinon les premiers commentaires ne reçoivent
jamais leur message, et le lien part dans un bouton, pas dans le texte.

**`/insta-viral` lit, il ne scrape pas.** Dix comptes, une douzaine de reels chacun, à vitesse
humaine, avec toi qui pilotes ton navigateur. Il ne demande jamais ton mot de passe.

**Les cinq mesures de l'humaniseur sont des heuristiques locales**, pas GPTZero, Originality,
Copyleaks, Winston ou Turnitin. Elles n'appellent pas leurs API et ne promettent pas leur
verdict. Personne ne peut honnêtement vendre de l'« indétectable ».

**Rien n'est inventé.** Aucun chiffre, client ou résultat sous ton nom. Si un brouillon a
besoin d'un chiffre que tu n'as pas donné, il revient avec `{{ton chiffre}}` dedans.

**Les règles des plateformes changent.** Le plafond de hashtags est passé de 30 à 5 en
décembre 2025. Si quelque chose ici contredit ce que fait Instagram quand tu le lis,
Instagram a raison.

## Fichiers

```
skills/insta-reel/hooks.json          26 formules de hook : modèle, exemple, version écran,
                                      à quoi elle sert, comment on la rate, regex, pièges mesurés
skills/insta-reel/beats.py            script -> conducteur minuté
skills/insta-publier/caption.py       la fenêtre du fil et la vérification, par réseau
skills/insta-humain/humanize.py       les trois passes de nettoyage
skills/insta-humain/detect.py         les cinq mesures
skills/insta-viral/swipe.py           classement au multiple et nom des formules
skills/insta-stats/stats.py           multiple, partages, meilleur reel du mois
shared/hookscore_fr.py                le score de hook (copié dans skills/insta-reel/)
shared/hookscore_fr_poids.json        les poids calibrés, sans aucune donnée brute
shared/slop-fr.json                   le lexique anti-IA français (copié dans skills/insta-humain/)
shared/calibration/calibrer.py        refaire la calibration sur tes reels
modeles/voix.md                       ton profil de voix. À remplir en premier.
tests/run.py                          les tests, sur des exemples en français
```

`shared/` est la source ; chaque dossier de skill garde sa copie pour marcher seul.
`scripts/sync-shared.sh` les remet à jour, et les tests échouent si une copie a dérivé.

## Crédits

Adapté de [instagram-agent-skill](https://github.com/Jakeschincariol/instagram-agent-skill)
de **Jake Schincariol** ([opusjake.ai](https://opusjake.ai)), sous licence MIT. Sa méthode,
sa structure, ses scripts et ses 26 formules sont la base de ce kit ; la version française,
la recalibration sur des reels français, les branchements PlugKit et les deux scripts
nouveaux (`stats.py`, `calibrer.py`) sont ajoutés ici. Sa notice MIT est conservée dans
`LICENSE` et `licenses/INSTAGRAM-AGENT-SKILL-LICENSE`, le détail fichier par fichier dans
`THIRD_PARTY_NOTICES.md`. Rien ici n'est approuvé par Jake.

## Licence

MIT. Prends-le, change-le, publie-le.

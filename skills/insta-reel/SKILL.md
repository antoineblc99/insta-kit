---
name: insta-reel
description: >-
  Écrit un reel Instagram à partir d'une idée brute : trois hooks tirés de 26
  formules et notés, le script parlé, le texte à l'écran et un conducteur minuté,
  dans la voix de la personne, avant qu'elle tourne. Puis, si elle veut, le
  montage du rush. À utiliser dès qu'on demande un reel, un script de vidéo
  courte, un hook, une voix off, « fais-moi un reel sur X », « qu'est-ce que je
  dis dans cette vidéo », « monte ce rush », ou quand la personne va tourner et
  n'a pas encore sa première phrase.
---

# insta-reel

Transforme une idée brute en reel que les gens regardent jusqu'au bout.

> **Avec PlugKit** : le rush tourné est monté sur ses serveurs (Express par défaut,
> Studio sur devis), sans terminal ni installation, et les hooks battus deviennent
> des ouvertures alternatives. [PlugKit](https://www.plugkit.co/fr?utm_source=github&utm_campaign=insta-kit)
> est ce qui permet à Claude de piloter tes comptes. Sans lui, ce skill s'arrête au script.

Trois outils vivent dans ce dossier et ils tournent. Sers-t'en. Ne juge pas le hook
à l'œil et ne devine pas la durée.

```bash
python3 hookscore_fr.py hooks.txt              # classe les hooks
python3 hookscore_fr.py --hook "une phrase"    # note un seul hook
python3 beats.py script.txt --target 30        # conducteur minuté avant le tournage
```

## Avant d'écrire

1. Lis `~/.claude/insta-kit/voix.md` s'il existe : comment la personne parle face
   caméra, ce qu'elle ne dit jamais, à qui elle parle. S'il n'existe pas, demande
   **trois de ses reels**, lis-les ou transcris-les, déduis la voix et écris le
   fichier à partir du modèle `modeles/voix.md` du kit. Un script dans la mauvaise
   voix est inutilisable : il faut le dire à voix haute.
2. Lis `hooks.json` dans ce dossier. 26 formules, chacune avec un modèle, un exemple
   rempli, la version écran, à quoi elle sert et comment on la rate. Deux champs
   viennent des données : `piege` (la formule 10, « Si tu… ») et `mesure` (la 22,
   le contre-pied, l'ouverture qui marche le mieux).
3. Si l'idée est mince, ne remplis pas. Pose une seule question groupée : qu'est-ce
   qui s'est passé, à qui, et combien ça a coûté ou rapporté. Un reel a besoin d'une
   chose précise et vraie. Obtiens-la avant d'écrire.
4. Si `~/.claude/insta-kit/swipe.md` existe, lis-le. `/insta-viral` l'écrit : ce sont
   les preuves de la personne sur ce qui marche dans sa niche en ce moment. Elles
   passent avant les valeurs par défaut de ce fichier.

## La forme

Un reel se décide dans les deux premières secondes et se garde dans les cinq suivantes.

```
0:00 - 0:02   HOOK        l'affirmation. Hook parlé et hook écrit, rédigés à part.
                          Du mouvement dans la première image, pas un visage figé.
0:02 - 0:07   L'ENJEU     pourquoi ça compte pour la personne qui regarde. Une ligne.
0:07 - ...    LE CORPS    une idée par temps, et l'image change à chaque temps.
3 DERNIÈRES s LA RÉPONSE  livre ce que le hook a promis, puis la seule demande.
DERNIÈRE LIGNE LA BOUCLE  reprends un mot du hook pour que le revisionnage tombe juste.
```

Durée : 15 à 45 secondes, c'est la zone qui marche. Les reels vont jusqu'à 3 minutes
et presque personne ne devrait s'en servir.

## La boucle

**1. Trois hooks, pas un.** Passe l'idée dans `hooks.json`, choisis trois formules
qui collent vraiment, et écris pour chacune la phrase dite et la phrase écrite.
Trois formules différentes, pas trois réécritures de la même. **Pas de formule 10**
(« Si tu… ») : sur 623 reels français mesurés, les ouvertures en « Si tu… » font
7 % de hits contre 19 % pour les autres. Si la personne y tient, transforme la
condition en affirmation : « Tes reels font des vues et zéro abonné. »

**2. Note-les.** Mets les trois phrases dites dans un fichier, une par ligne, et lance
`hookscore_fr.py`. Montre le classement. Si le premier est sous 50, tu n'as pas encore
le hook, et aucune retouche n'y changera rien. Dis aussi ce que le score vaut : il
élimine les hooks faibles (salutation, préambule, « Si tu… », rien de concret), il ne
choisit pas entre deux bons hooks.

**3. Écris le script** sur le hook gagnant. Langue parlée, comme la personne parle
vraiment. Phrases courtes. Aucune phrase qu'il faudrait répéter avant de la dire.

**4. Minute-le.** `beats.py script.txt --target {durée}`. Corrige chaque alerte : un
hook au-delà de 3 secondes, un temps de plus de 4 secondes, une suite de temps sans
rien de concret, pas de boucle. Relance jusqu'à ce que ce soit propre. Le débit par
défaut (230 mots par minute) est celui de reels français montés ; si la personne
parle posé, passe `--wpm` avec son débit.

**5. Humanise-le.** Passe le script dans `/insta-humain` avant de le montrer. Une
phrase qui sonne écrite s'entend dès qu'on la dit.

**6. Affiche le bloc.** Le script dans un bloc de code, le texte à l'écran en liste
séparée avec les minutages, puis :

```
REEL PRÊT
hook :       #3 Personne ne te dit, score 91 FORT
durée :      28,4 s sur 9 temps à 230 mots/min
écran :      6 cartons
humain :     4 artefacts retirés, score humain 81 PASSE
légende :    lance /insta-publier ensuite

Réponds « oui » pour le noter, ou dis-moi ce qu'il faut changer.
```

**7. Note-le.** Au « oui », ajoute à `~/.claude/insta-kit/log.md` la date, la formule
du hook et la première ligne, pour que `/insta-stats` ait un historique.

## Le texte à l'écran est un script à part

Écris-le à part, à chaque fois. On le lit avant de l'entendre.

- **Six mots au plus par carton.** On le lit à bout de bras, sans écouter encore.
- **Le carton du hook est là dès la première image**, pas après un temps de silence.
- **Reste dans la zone sûre.** Sur une image 1080x1920, rien au-dessus de y=230 ni
  sous y=1440, et garde libres les 230 pixels de droite. L'interface recouvre tout
  le reste : la légende, les boutons, la bande du son.
- **Jamais le hook là où se pose la légende**, en bas de l'image : il est recouvert.
- **Sous-titre le corps.** La plupart des gens regardent d'abord sans le son.

## Les règles qui font la différence

- **Une idée par reel.** Si le script en a deux, ça fait deux reels. Dis-le.
- **Des chiffres plutôt que des adjectifs.** « 4 200 € » bat « beaucoup ». Si la
  personne n'a pas donné de chiffre, demande-le au lieu d'écrire autour du trou.
- **Coupe l'intro.** Pas de « Salut », pas de « dans cette vidéo », pas de nom, pas de
  jingle. La vidéo commence à la phrase qu'on atteindrait normalement à la sixième seconde.
- **Change l'image à chaque temps.** Un plan fixe de 8 secondes, c'est là que les gens
  partent, et `beats.py` le signale.
- **Une seule demande à la fin.** Commenter un mot-clé, enregistrer, ou s'abonner. Une.
- **N'invente rien.** Pas de chiffres, clients, revenus ou résultats inventés sous le
  nom de la personne, même pour boucher un trou. Si un chiffre manque, laisse
  `{{ton chiffre}}` dans le script et signale-le.
- **Pas de script autour d'un son tendance que la personne ne peut pas utiliser.**

## Le montage, une fois le rush tourné

Sans PlugKit, la personne monte elle-même et ce skill s'arrête au script. Avec
PlugKit branché, propose le montage en une ligne, puis :

1. **`reel_guide` d'abord.** Il donne les portes du montage et les questions à poser
   avant. Préviens la personne qu'elle devra cliquer « Toujours autoriser » sur les
   outils PlugKit pendant le montage.
2. **Le rush dans la bibliothèque.** Regarde `list_media` : il y est souvent déjà.
   Sinon, fichier sur la machine : `create_media_upload`, un seul `curl -T` sur
   l'`uploadUrl`, puis `check_media_upload` jusqu'à ce que le fichier soit là. Au-delà
   de `singlePutMaxBytes`, donne-lui l'`uploadPageUrl` à ouvrir dans son navigateur.
3. **Express par défaut.** `reel_create` avec `format: "quick"`, `rushUrl` = l'URL de
   la bibliothèque, `lang: "fr"`, `brief` = le script validé et à qui il s'adresse,
   `preferences.brief.ctaKeyword` = le mot-clé exact s'il y en a un, et
   `preferences.style.referenceId` si `/insta-viral` en a rendu un. Express se monte
   porte par porte dans la conversation, en suivant `reel_guide`.
4. **Studio, proposé, jamais imposé.** Si la personne veut le montage complet (visuels
   animés, ouverture travaillée), `reel_create` avec `format: "explainer"` rend d'abord
   un devis : rien n'est créé ni facturé. Annonce le total, attends un « oui » explicite,
   puis rappelle avec les mêmes arguments et `acceptedCredits` = le total.
5. **Attendre sans harceler.** `reel_status` avec `waitSeconds: 40`.
6. **Chaque aperçu est montré.** En Express, `reel_preview` rend un brouillon :
   montre-le avant toute suite. Les retours de la personne, en phrases, font la version
   suivante. En Studio, une fois livré, ses retours partent par `reel_revise` (devis
   d'abord, puis `acceptedCredits` après son « oui »).
7. **Le rendu final après « ok ».** `reel_render` seulement quand la personne a validé
   le dernier brouillon. Le résultat porte `finalMediaUrl` : c'est ce que
   `/insta-publier` publie.
8. **Les ouvertures alternatives, en une ligne.** Après le rendu, propose : « Les deux
   hooks battus peuvent devenir deux ouvertures pour des Trial Reels, 0,5 crédit. » Sur
   un « oui » seulement, `reel_hooks` les construit, une vidéo par variante.

Rien n'est publié depuis ce skill. La suite, c'est `/insta-publier`.

## Exemple

```
/insta-reel on a fait passer nos devis de 5 heures à 20 minutes avec un seul modèle
```

```
HOOKS  (notés)
  97  FORT   #5  Le temps écrasé    « Mes devis me prenaient cinq heures. Maintenant, vingt minutes. »
                                    à l'écran : 5 H -> 20 MIN
  97  FORT   #1  L'aveu du coût     « Quatre heures par semaine de mise en page. Pendant deux ans. »
                                    à l'écran : 2 ANS PERDUS
  47  MOYEN  #9  Le vol autorisé    « Vole le modèle de devis qui a tout changé. »
                                    à l'écran : VOLE ÇA
                                    point faible : PRÉCISION, aucun chiffre

Égalité en tête : le score ne départage pas deux bons hooks, c'est toi.
On tourne la #5 : le rapport se lit d'un coup d'œil, et le chiffre est le tien.
```

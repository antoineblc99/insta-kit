---
name: insta-humain
description: >-
  Étape interne du kit, appelée par /insta-reel, /insta-publier, /insta-dm et
  /insta-reponses avant de montrer un texte : retire l'empreinte machine d'un
  brouillon en français (tirets cadratins, tics de l'IA, caractères invisibles)
  et le note sur cinq mesures. À utiliser aussi quand on dit « humanise »,
  « ça sonne IA ? », « enlève les tirets », « ça fait ChatGPT ».
---

# insta-humain

L'étape qui rend le reste utilisable. Les autres skills du kit l'appellent avant de te
montrer un script, une légende, un DM ou une réponse. Tu n'as pas besoin de la lancer.

Deux outils vivent dans ce dossier et ils tournent. Sers-t'en, ne juge pas à l'œil.

```bash
python3 humanize.py brouillon.txt --report       # nettoie, montre ce qui a changé
python3 detect.py brouillon.txt                   # note, cinq mesures
python3 detect.py avant.txt apres.txt             # prouve l'écart
```

Les deux lisent `slop-fr.json` : plus de 200 expressions toutes faites avec leur
remplacement simple, 18 familles de caractères invisibles, 10 substitutions
typographiques et 21 structures repérées. Le dernier bloc (famille « instagram ») est la
langue des légendes et des voix off : « arrête de scroller », « abonne-toi pour plus »,
« l'algorithme adore ». Le fichier est fait pour être modifié : si la personne a un mot
à elle que le lexique retire, enlève-le du fichier.

## Pourquoi ça compte plus sur Instagram qu'il n'y paraît

Les légendes sont courtes et les scripts se disent à voix haute. Une phrase qui sonne
écrite pèse plus dans 600 caractères que dans un essai, et une voix off que personne ne
dirait comme ça s'entend à la première prise. Le vrai signal, ce n'est pas un détecteur
qui signale le post. C'est quelqu'un qui scrolle devant un texte qui sonne comme une
marque, ou un créateur qui bute sur son propre script.

## Ce qui est corrigé tout seul

**1. Les caractères invisibles.** Espaces de largeur nulle, joints, tirets conditionnels,
BOM, caractères d'étiquette Unicode, espaces insécables. Un clavier de téléphone ne les
tape pas, ils survivent au copier-coller et sont invisibles partout.

**2. La typographie.** Tiret cadratin -> virgule (c'est la passe qui compte), demi-cadratin
-> trait d'union, guillemets anglais -> droits, caractère « … » -> trois points, puce ->
tiret. Ce qui ne bouge pas : les guillemets français « », l'apostrophe ’ et l'espace avant
? ! : ; qui sont la typographie normale du français.

**3. Le lexique.** « booster », « crucial », « tirer parti de », « un véritable game
changer », « dans un monde en constante évolution », « il est important de noter que »,
plus le bloc Instagram. Chaque tic est remplacé par un mot simple ou supprimé, les
majuscules sont gardées et les liens ne sont pas touchés.

## Ce qui n'est PAS corrigé tout seul

Les structures sont **signalées, pas réécrites** : changer la forme d'une phrase demande
du jugement.

- « Ce n'est pas X, c'est Y » et « Non seulement X, mais aussi Y »
- Les triades (trois éléments, une virgule, un « et »)
- Les lignes-questions rhétoriques : « Le résultat ? »
- Le préambule vidéo : « Dans cette vidéo, je vais te montrer »
- « Et si je te disais que », « N'hésite pas à », « Que tu sois débutant ou expert »
- Les listes à puces en emoji, trois mots en majuscules d'affilée, les murs de hashtags
- Les appâts : « abonne-toi pour », « identifie un pote qui », « double tape si »

Ça, c'est ton travail. Réécris chaque ligne signalée à la main, en gardant le sens, puis
relance `detect.py`. C'est ce qui fait passer le score de À REVOIR à PASSE, et c'est la
partie qu'un script ne sait pas faire.

## Les cinq mesures

`detect.py` note cinq signaux de 0 à 100, plus haut = plus humain :

| mesure | ce qu'elle mesure | à quoi ressemble la machine |
| --- | --- | --- |
| RYTHME | la variation de longueur des phrases | toutes les phrases de la même longueur |
| PRÉCISION | chiffres, noms, éléments concrets pour 100 mots | des noms abstraits, aucun chiffre |
| LEXIQUE IA | tics du lexique pour 100 mots | du vocabulaire tout fait |
| EMPREINTE | invisibles, cadratins, guillemets anglais pour 1 000 caractères | une typographie trop parfaite |
| VOIX | l'oral (« c'est pas », « t'as », « du coup »), les personnes, les structures | pas d'oral, des révélations mises en scène |

Le verdict pèse la moyenne à 60 % et la **pire mesure** à 40 %, parce qu'un seul signal
suffit. PASSE demande 70 ou plus, sans mesure sous 55.

## À dire honnêtement

Ce sont cinq heuristiques locales, calquées sur ce que regardent les détecteurs publics.
Tout tourne sur la machine de la personne, rien n'est envoyé. Ce **n'est pas** GPTZero,
Originality, Copyleaks, Winston ou Turnitin : le script n'appelle pas leurs API et ne
peut pas promettre leur verdict. Corriger ce qu'il mesure fait souvent bouger leurs
chiffres, parce qu'ils mesurent les mêmes choses. C'est tout ce qu'on affirme. Ne dis
jamais à quelqu'un que son texte est indétectable.

## L'ordre

1. `humanize.py brouillon.txt -o propre.txt --report`
2. Lis les structures signalées. Réécris ces lignes toi-même.
3. `detect.py brouillon.txt propre.txt` pour l'avant / après.
4. Si le verdict n'est pas PASSE, corrige la mesure la plus faible et recommence. Deux
   tours, c'est normal. Cinq, c'est que le brouillon a été écrit à la formule : la
   solution est un autre brouillon, pas plus de passes.
5. Montre le texte nettoyé et le score. Jamais le score seul.

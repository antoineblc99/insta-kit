---
name: insta-stats
description: >-
  Lit les stats de ce que la personne a déjà publié et sort son meilleur reel du
  mois, ce qui a vraiment marché, pourquoi, et ce qu'il faut arrêter de faire, un
  classement par réseau. À utiliser quand on colle ses statistiques Instagram ou
  ses anciens posts, ou qu'on dit « qu'est-ce qui marche », « pourquoi ce reel a
  fait un flop », « lis mes stats », « fais le point sur mon contenu », « c'est
  quoi mon meilleur reel du mois ».
---

# insta-stats

La seule source honnête de ce qui marche pour un compte, c'est ce compte. Chaque règle de
chaque guide Instagram, celles de ce kit comprises, est un a priori. Les 30 derniers posts
de la personne sont la preuve.

> **Avec PlugKit** : les stats de tous tes réseaux sont lues directement, un classement
> par réseau et ton meilleur reel du mois, sans capture d'écran.
> [PlugKit](https://www.plugkit.co/fr?utm_source=github&utm_campaign=insta-kit) est ce qui
> permet à Claude de piloter tes comptes. Sans lui, colle tes statistiques.

Un outil vit dans ce dossier, et il tourne :

```bash
python3 stats.py posts.tsv
```

## L'entrée

**Sans PlugKit**, demande ce que la personne a :

- les statistiques par post : vues, portée, interactions, durée de visionnage,
  enregistrements, partages, abonnés gagnés. Les captures marchent ;
- ou la courbe de rétention de son meilleur et de son pire reel récents. Cette capture
  vaut plus que tout le reste ;
- ou juste les posts et leurs vues, assez pour un premier passage.

**Avec PlugKit**, tout est lu, rien n'est modifié :

1. `get_analytics_summary` sur 30 jours : la vue d'ensemble, tous comptes confondus.
2. `get_top_posts` par réseau (`platform`, `from` = il y a 30 jours, `sortBy: "views"`,
   `limit: 50`) : les posts avec leurs métriques, y compris ceux publiés directement
   sur la plateforme.
3. `get_post_analytics` sur les cinq premiers et les cinq derniers si une métrique manque
   (partages, enregistrements).
4. `get_follower_stats` : les abonnés gagnés sur la période.
5. `get_analytics_timeseries` si la personne demande une tendance.

La rétention à 3 secondes ne sort pas par l'API. Si elle compte pour la conclusion,
demande deux captures : la courbe du meilleur et celle du pire.

Lis aussi `~/.claude/insta-kit/log.md` s'il existe : il donne la formule de hook de
chaque reel écrit avec `/insta-reel`. Mets-la dans la colonne `formule`.

Puis remplis le TSV (une ligne par post, colonnes `date`, `reseau`, `titre`, `vues`,
`portee`, `partages`, `enregistrements`, `abonnes`, `formule`, `retention3s` quand tu
l'as) et lance `stats.py`.

## Ce qu'on mesure vraiment

Les vues brutes sont le chiffre le moins utile de la page : elles dépendent surtout du
nombre de gens qui suivent déjà. On calcule plutôt, en montrant le calcul :

| mesure | calcul | ce qu'elle dit |
| --- | --- | --- |
| **Multiple** | vues / médiane des vues du compte | un vrai succès, ou un jour normal |
| **Partages par portée** | partages / portée | le signal le plus fort qu'on puisse gagner : quelqu'un met son nom dessus |
| **Abonnés par portée** | abonnés gagnés / portée | le profil a-t-il converti l'attention |
| **Rétention à 3 s** | spectateurs encore là à 3 s / ceux qui ont commencé | la note du hook |
| **Durée moyenne** | dans les statistiques | le milieu a-t-il tenu |

On classe au multiple, puis aux partages, jamais aux vues. Un reel à 4 000 vues et 90
partages a battu celui à 60 000 vues et 11 partages.

**Le meilleur reel du mois = le plus gros multiple du réseau sur 30 jours.** Un
classement par réseau : Instagram, TikTok, YouTube et les autres ne se mélangent pas.

## Puis trouver le motif

Avec le top 5 et le flop 5 côte à côte, cherche ce qui les sépare, et accepte une
conclusion qui ne plaira pas :

- **La rétention à 3 secondes.** Si le haut et le bas diffèrent là, c'est le hook et rien
  d'autre, le reste est une distraction.
- **La formule de hook.** Quels numéros de `insta-reel/hooks.json` sont dans le top 5 ?
  Une formule 10 (« Si tu… ») dans le flop confirme ce que disent les données du kit.
- **Le format.** Reel, carrousel, image seule.
- **La durée.** Moins de 15 s, 15 à 30 s, 30 à 60 s, plus de 60 s.
- **Le sujet.**
- **Si la personne a répondu aux commentaires dans la première heure.**
- **Le jour et l'heure.** En **dernier**, et seulement si le reste ne montre rien.
  Ce n'est presque jamais la cause, et c'est là que tout le monde voudrait qu'elle soit.

Formule la conclusion comme une affirmation avec sa preuve, et dis à quel point elle est
sûre. Avec 30 posts, on voit un motif. Avec 6, non, et le dire vaut mieux qu'en inventer un.

## La distinction qui fait gagner des mois

**Un reel qui fait des vues et pas d'abonnés n'est pas un reel raté, c'est un problème
de profil.** Un reel sans vues, c'est un problème de hook. Sépare les deux avant de
recommander quoi que ce soit. Si le multiple est haut et les abonnés par portée bas,
arrête de réécrire les hooks : c'est la bio, la photo, le nom. `stats.py` le signale.

## Sortie

```
STATS INSTAGRAM  ·  31 posts  ·  12/09 - 12/10  ·  médiane 4 100 vues

MEILLEUR REEL DU MOIS
  18.2x   74 600 vues   17.2 partages / 1000 portée   « Personne ne te dit combien coûte un client »
  formule #3, publié le 02/10

TOP 5 AU MULTIPLE
  18.2x  #3   74 600 vues   rétention 3 s 71 %   128 partages
   6.4x  #1   26 300 vues   rétention 3 s 64 %    71 partages

FLOP 5
   0.3x  #10   1 200 vues   rétention 3 s 31 %     2 partages

CE QUE DISENT LES DONNÉES
1. La rétention à 3 secondes fait tout. Top 5 : 66 % en moyenne, flop 5 : 33 %.
2. Les reels où c'est toi qui as l'air bête : 8,1x en moyenne contre 0,9x. n=5.
3. Les listes d'outils font des vues et rien d'autre. Trois du flop 5.
4. Le jour de la semaine ne montre rien. Arrête de l'optimiser.

ARRÊTE : les listes d'outils.
FAIS PLUS : les reels avec un coût que tu as payé et un chiffre dessus.
```

Puis passe les conclusions à `/insta-viral`, pour filtrer le prochain fichier swipe sur
les formules qui marchent pour ce compte, et à `/insta-reel` pour le prochain hook.

Ce skill lit. Il ne publie, ne supprime et ne modifie rien.

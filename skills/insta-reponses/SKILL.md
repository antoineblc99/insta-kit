---
name: insta-reponses
description: >-
  Gère les commentaires sous les reels et les posts de la personne : les trie,
  écrit les réponses à ceux qui en valent la peine, dans l'ordre de ce qu'ils
  valent, et les envoie après un « oui ». À utiliser quand la personne colle ses
  commentaires, dit « réponds à mes commentaires », « gère mes commentaires »,
  « quelqu'un a écrit X sous mon reel », ou fait face à un critique, un troll ou
  un prospect dans les commentaires.
---

# insta-reponses

Le fil de commentaires sous ton post, c'est là que la portée se décide. Chaque réponse
est une interaction de plus, celles de la première heure font l'essentiel du travail, et
sur Instagram une réponse peut aussi être un reel, le geste le plus sous-utilisé de la
plateforme.

Mais tous les commentaires ne se valent pas, donc ce skill trie avant d'écrire.

> **Avec PlugKit** : les commentaires qui attendent sont lus sur tous tes posts, et
> les réponses partent une par une après ton « oui » sur le lot.
> [PlugKit](https://www.plugkit.co/fr?utm_source=github&utm_campaign=insta-kit) est ce qui
> permet à Claude de piloter tes comptes. Sans lui, colle tes commentaires et repars
> avec les réponses prêtes.

## L'entrée

**Sans PlugKit** : la personne colle les commentaires, avec les pseudos si possible.
Les captures d'écran marchent. Ne scrape pas le fil avec un navigateur.

**Avec PlugKit** : `list_engagement` rend tout ce qui attend une réponse, sur tous les
posts et tous les comptes, chaque ligne avec le post en dessous duquel elle est. Pour un
seul post précis : `get_account_media` pour son `mediaId`, puis `get_comments`.

## Trier d'abord

Range chaque commentaire dans un des six seaux et annonce les comptes à voix haute :

| seau | ce que c'est | ce qu'il reçoit |
| --- | --- | --- |
| **MOT-CLÉ** | le mot que tu as demandé de commenter | la chose promise, par l'automation ou à la main |
| **PROSPECT** | quelqu'un qui décrit le problème que tu règles | une vraie réponse en public, puis une porte |
| **FOND** | apporte une donnée, n'est pas d'accord, prolonge | la réponse la plus longue du fil |
| **QUESTION** | une question que beaucoup de gens se posent | elle devient un reel, pas juste une réponse |
| **SOUTIEN** | « 🔥 », « trop bien », une identification | un like, et 3 à 8 mots au plus |
| **BRUIT** | pub, spam, mauvaise foi, provocation | rien, ou une ligne et basta |

Écris dans cet ordre et arrête-toi quand la valeur s'arrête.

## Le geste que presque tout le monde rate

Si une question en commentaire est une question que trente autres personnes se posent,
**réponds-y par un reel**. Instagram accroche le commentaire à la nouvelle vidéo comme un
autocollant, la personne qui a demandé est prévenue, et une question avec une vraie
demande derrière devient un post dont le hook est déjà écrit. Signale chaque QUESTION qui
s'y prête et passe-la à `/insta-reel` comme formule 16, « La question telle quelle ».

## Comment répondre

- **Réponds à la vraie question.** Si on demande comment, dis comment, dans la réponse.
  N'envoie pas en DM une réponse qu'on aurait pu avoir en public.
- **Le prénom une fois**, au début, sans point d'exclamation.
- **À la longueur du commentaire.** Un commentaire de quatre mots n'appelle pas quatre lignes.
- **Tutoiement ou vouvoiement** : comme dans `~/.claude/insta-kit/voix.md`. Par défaut,
  comme la personne qui commente.
- **À un critique** : concède d'abord ce qui est vrai, dans ses mots, puis tiens ta
  position. Jamais supprimer, jamais se défendre, jamais deux réponses sur le même fil.
- **À un troll** : rien. Une réponse, c'est de la portée, et c'est ce qu'il est venu chercher.
  Masque le commentaire s'il est injurieux : les outils de modération existent, s'en
  servir n'est pas perdre.
- **À un prospect** : réponds en entier, en public. La porte tient en une phrase à la
  fin, c'est une offre d'aide, pas un argumentaire. La réponse publique est ce qui fait
  écrire la personne suivante.

## Les commentaires mot-clé

Si le post demandait un mot-clé, ces commentaires sont tout l'intérêt du post. Chacun
est une main levée. **Avec PlugKit**, l'automation envoie le DM toute seule ;
`list_comment_automations` dit combien de DM chaque règle a déjà envoyés, compare au
nombre de commentaires mot-clé et signale l'écart. Pas de réponse publique identique
sous chacun : le texte répété est un signal de spam. Un mot de remerciement varié sur
quelques-uns suffit. **Sans automation**, les réponses se font à la main, et c'est
très bien à ce volume. Ne DM jamais en masse des gens qui n'ont pas commenté.

## Sortie

Un bloc, groupé par seau, chaque réponse numérotée, prête à copier et déjà passée dans
`/insta-humain` :

```
RÉPONSES  ·  84 commentaires  ·  41 MOT-CLÉ, 2 PROSPECT, 3 FOND, 2 QUESTION, 34 SOUTIEN, 2 BRUIT

MOT-CLÉ  (41)  l'automation DEVIS a envoyé 39 DM. 2 commentaires avant sa création :
               à envoyer à la main, brouillon ci-dessous.

PROSPECT
 1. @pseudo : « on a eu exactement ce souci en juin »
    > Ce qui a tout réglé chez nous, c'est de sortir le paiement de la validation.
    > Je t'envoie la formulation si ça t'aide.

QUESTION -> REEL
    @pseudo : « tu fais quoi s'ils refusent de signer ? »
    34 j'aime sur ce commentaire. C'est un reel, pas une réponse. Formule 16.

BRUIT  (2)  ignorés. Leur répondre, c'est leur donner de la portée.
 2. @pseudo : injurieux, à masquer.

Réponds « oui » pour tout envoyer, ou « oui sauf 2 ».
```

## Envoyer avec PlugKit

Un « oui » vaut pour le lot affiché, pas pour la suite. « Oui sauf 4 » retire la réponse 4.
Puis, une réponse à la fois :

- commentaire venu de `list_engagement` : `reply_to_engagement` avec son `_id` et le texte
  validé. L'élément passe en traité ;
- commentaire venu de `get_comments` : `reply_to_comment` avec son `commentId` ;
- commentaire injurieux validé pour être masqué : `hide_comment`. Réversible, l'auteur
  n'est pas prévenu.

Les plateformes ne permettent pas de modifier une réponse publiée : le texte envoyé est
exactement le texte validé. Rien ne part sans « oui ».

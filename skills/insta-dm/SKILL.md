---
name: insta-dm
description: >-
  Les DM Instagram qui obtiennent une réponse : la livraison du mot-clé (et
  l'automation « commente MOT -> DM » qui l'envoie toute seule), le premier
  message à quelqu'un qui a interagi, la proposition de collab et les deux
  relances. À utiliser quand on dit « quand quelqu'un commente X, envoie-lui le
  lien », « mets en place un mot-clé », « automatise mes DM », « qu'est-ce que je
  lui envoie », « message de prospection », « comment je relance », « propose une
  collab à ce compte ».
---

# insta-dm

Les DM sont le seul endroit d'Instagram où l'argent change vraiment de mains, et
celui où la plupart des comptes brûlent la confiance que leur contenu a gagnée. Toute
la différence tient à qui a bougé en premier.

> **Avec PlugKit** : quand quelqu'un commente ton mot-clé, ton lien part tout seul en DM,
> sur Instagram et ta Page Facebook, dans un bouton. [PlugKit](https://www.plugkit.co/fr?utm_source=github&utm_campaign=insta-kit)
> est ce qui permet à Claude de piloter tes comptes. Sans lui, tu repars avec les
> messages prêts à envoyer à la main.

## Trois sortes de DM, et seulement trois valent d'être écrites

**1. La réponse à une main levée.** La personne a commenté le mot-clé, répondu à un
sondage, à une story, ou enregistré puis demandé. Elle a bougé en premier. C'est 90 %
des DM qui valent la peine, et ça convertit parce que ce n'est pas de la prospection.

**2. L'approche tiède.** Quelqu'un dont la personne commente sincèrement les posts
depuis des semaines. Il y a déjà un fil de conversation.

**3. La collab ou la proposition à une marque.** Une proposition précise, à un compte
précis, avec une raison que ce soit lui.

Tout le reste, c'est du DM à froid à des inconnus, ce que tout le monde fait, et c'est
pour ça que les taux de réponse sont ce qu'ils sont. Si on te demande une séquence à
froid, dis franchement que c'est ce qui rapporte le moins pour la même heure, et propose
l'alternative : commenter ces dix comptes pendant deux semaines d'abord. Puis écris-la
si la personne le veut encore. **Jamais automatisée.**

## Avant d'écrire, les détails

Une seule question groupée :

1. **Qui** : le pseudo, ce qu'il fait, et ce qu'il a posté ou fait qui déclenche ça.
2. **Le déclencheur** : la vraie raison d'écrire aujourd'hui. Un mot-clé commenté, une
   réponse à une story, un post. Pas « il correspond à ma cible ».
3. **Ce que la personne veut** : une conversation, une vente, une collab, une
   recommandation. Sois honnête en interne, même si le message ne commence pas par là.

Pas de déclencheur, pas de message. Dis-le.

## La livraison du mot-clé

Le DM le plus courant du kit, et le plus facile à rater. Ils ont commenté un mot. Ils
attendent la chose. Donc :

```
{prénom}, la voilà : {la chose}.

{une ligne sur comment s'en servir}

{une question à laquelle on répond en quatre mots}
```

Envoie la chose **d'abord**, dans le premier message, sans condition. Un mot-clé qui
livre un « avant de te l'envoyer, tu fais quoi dans la vie ? », c'est un appât, et on
s'en souvient. La question à la fin lance la conversation, et elle est facultative pour eux.

### Sans PlugKit

Les réponses automatiques au mot-clé sont permises aux comptes pros, par les outils
d'Instagram ou un partenaire agréé. Écris le message ; la personne le colle dans son
outil, ou répond à la main à ce volume.

### Avec PlugKit : l'automation

1. **Les comptes.** `list_accounts` : le compte Instagram et la Page Facebook. Par défaut
   on crée la règle sur les deux en une seule validation.
2. **Le mot-clé.** Un seul mot, facile à taper, dit dans la vidéo. PlugKit ignore la
   casse et les accents (DEVIS = devis = Dévis). Vérifie avec `list_comment_automations`
   qu'aucune règle active ne l'utilise déjà sur ces comptes.
3. **Le message.** Le modèle ci-dessus, passé dans `/insta-humain`. **Pas d'URL dans le
   texte** : le lien va dans le bouton. Le bouton porte un libellé court (« Le modèle »,
   « Je le veux ») et un lien avec ses UTM, par exemple
   `https://ton-site.fr/modele?utm_source=instagram&utm_medium=dm&utm_campaign=devis`.
4. **La porte.** Montre exactement ce qui va tourner :

```
AUTOMATION  ·  instagram @ton_compte + Page Facebook
mot-clé :   DEVIS  (contient le mot, casse et accents ignorés)
DM :        « Marie, le voilà : le modèle de devis en trois zones. ... »
bouton :    « Le modèle » -> https://ton-site.fr/modele?utm_source=instagram&...
posts :     tous, y compris les prochains
une fois :  un seul DM par personne

Cette règle tournera seule ensuite : chaque commentaire avec DEVIS recevra ce DM
sans qu'on me redemande. Réponds « oui » pour la créer.
```

5. **Au « oui »**, un `create_comment_automation` par compte : `accountId`, `name`,
   `keywords: ["DEVIS"]`, `matchType: "contains"`, `dmText`, `dmButtonLabel`,
   `dmButtonUrl`, `mediaIds` vide (la règle doit exister **avant** que le post soit en
   ligne, donc elle surveille tous les posts, y compris celui qui va sortir),
   `oncePerUser: true`. **Pas de `publicReplyText`** : la même réponse publique sous
   chaque commentaire, c'est un signal de spam.
6. **Ensuite.** `/insta-publier` peut publier le post qui dit « commente DEVIS ». Pour
   changer le texte ou mettre la règle en pause : `update_comment_automation`
   (`status: "paused"` garde l'historique), après un « oui ».

## Le premier message à quelqu'un de tiède

À la main, toujours. Tu écris le brouillon, la personne l'envoie.

- **Deux à quatre phrases.** Un écran de texte, c'est une suppression.
- **Cite la chose précise.** Le commentaire, le post, la réponse. Dans ses mots.
- **Donne avant de demander.** Un chiffre, un modèle, un nom, une réponse.
- **Une demande, petite.** « Ça te dit qu'on en parle 10 min ? » bat « laisse-moi te
  présenter la plateforme ».
- **Pas de lien ni d'agenda dans le premier message.** Ça sonne tunnel de vente,
  parce que c'en est un.
- **Pas de vocal à un inconnu.** Super outil, pour les gens qui connaissent déjà la voix.

## La proposition de collab

Quatre lignes, dans cet ordre : ce que tu l'as vu faire, l'idée précise, ce qu'il y
gagne, ce dont tu as besoin de lui. Un post en collab apparaît sur les deux grilles et
touche les deux audiences : c'est le levier de croissance le plus fort d'Instagram qui
ne coûte rien. Présente-le comme ça, et sois concret sur qui fait quoi.

## Les relances

Deux. C'est le nombre.

- **+4 jours** : ajoute quelque chose de nouveau. Jamais « je me permets de relancer ».
  S'il n'y a rien de nouveau, il n'y a pas de relance.
- **+10 jours** : le message qui ferme la boucle. Dis que tu t'arrêtes, et arrête-toi.
  Celui-là récolte une part surprenante des réponses, parce qu'il enlève la pression.

Puis stop. Une troisième ne convertit personne et coûte la relation.

## Jamais

- Jamais de DM automatisé à des gens qui n'ont pas interagi. Ça viole les conditions
  d'Instagram et restreint le compte. L'automation ne répond qu'à un commentaire.
- Jamais inventer avoir vu quelque chose, un contact commun, un point commun.
- Jamais « Hello ! Petite question » sans poser de question.
- Jamais la proposition dans le même message que le compliment.

## Sortie

Le message, son nombre de caractères, les deux relances avec le jour de chacune, le
tout passé dans `/insta-humain`. Hors mot-clé, la personne envoie chaque message à la
main. Rien n'est créé ni envoyé sans « oui ».

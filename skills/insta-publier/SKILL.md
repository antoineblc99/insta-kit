---
name: insta-publier
description: >-
  Écrit la légende (la ligne qui survit à la coupure « ... plus », le corps, la
  seule demande, les termes de recherche, cinq hashtags au plus), la vérifie,
  puis programme le reel sur tous les réseaux branchés au meilleur créneau, après
  un « oui ». À utiliser quand on dit « écris la légende », « mets une légende »,
  « qu'est-ce que je mets en description », « publie ce reel », « programme-le
  partout », « poste-le sur TikTok et YouTube aussi », ou quand on parle de hashtags.
---

# insta-publier

> **Avec PlugKit** : le reel part sur sept réseaux d'un coup, une légende adaptée à
> chacun, programmé au meilleur créneau de ton compte, après ton « oui ».
> [PlugKit](https://www.plugkit.co/fr?utm_source=github&utm_campaign=insta-kit) est ce qui
> permet à Claude de piloter tes comptes. Sans lui, tu repars avec la légende prête
> à coller.

Un outil vit dans ce dossier, et il tourne :

```bash
python3 caption.py legende.txt
python3 caption.py legende.txt --mots-cles "devis freelance,prix client"
python3 caption.py legende.txt --plateforme tiktok
```

Il affiche la légende comme le fil l'affiche : les 125 premiers caractères dans une
boîte, le reste derrière le tap. Lis cette boîte avant tout le reste.

## D'abord : quel est le travail de cette légende

C'est la décision qui ruine les légendes quand on la saute.

**Travail A : la vidéo a déjà accroché.** Un reel porte son hook dans les deux
premières secondes, dit et écrit. La légende n'est pas un deuxième hook, et
concurrencer la vidéo fait perdre les deux. Son travail : la demande, le contexte qui
rend la demande logique, et les mots que les gens cherchent.

**Travail B : la légende est le contenu.** Une photo, une image seule, une couverture
de carrousel. Ici la première ligne est le hook et marche exactement comme un hook de
reel : concrète, courte, coupée sur un suspense plutôt qu'au milieu d'une subordonnée.

Dis lequel tu écris. Pour un reel avec un bon hook, écris A et dis pourquoi.

## La forme

```
Ligne 1     125 caractères visibles. Travail A : la demande, simplement.
            Travail B : le hook. Jamais une salutation, jamais un hashtag,
            jamais un emoji en premier caractère.
Corps       paragraphes courts, une ligne vide entre chacun. Deux à six.
            C'est là que vivent les termes de recherche.
La demande  une seule. Commenter un mot-clé, enregistrer, ou écrire en DM. Une.
Hashtags    cinq au plus, sur leur propre ligne en bas, ou aucun.
```

La limite est de 2 200 caractères et presque rien n'en a besoin. Une légende qui
gagne le tap puis livre 600 caractères bat celle qui en livre 1 800.

## Hashtags, honnêtement

Les hashtags ne sont plus un levier de portée, et la plateforme l'a dit par un
changement de produit : **Instagram a plafonné les hashtags à cinq par post le
18 décembre 2025**, contre trente avant. Adam Mosseri avait déjà dit en février 2025
qu'ils ne servent pas à augmenter la portée : c'est une étiquette.

Donc cinq au plus, précis, comme étiquettes de sujet. `#viral`, `#fyp`, `#pourtoi`,
`#explore` ne décrivent rien. Coupe-les.

## Les termes de recherche comptent plus que les hashtags

La recherche Instagram lit le texte de la légende. L'expression pour laquelle la
personne veut être trouvée va dans la légende comme un humain la taperait, dans une
phrase normale. « Devis freelance » en mots, ligne trois, pas `#devisfreelance` en bas.

Demande deux ou trois de ces termes et passe-les au vérificateur avec `--mots-cles`.

## Une légende par réseau

Écris une version par réseau, pas une partout :

- **Instagram et Facebook** : la version complète. « Commente MOT » n'existe que là,
  parce que l'envoi automatique en DM n'existe que là.
- **TikTok, YouTube Shorts, X, Threads, LinkedIn, Bluesky** : pas de « commente MOT ».
  Remplace par la demande qui marche sur ce réseau (s'abonner, une question, le lien
  là où il est cliquable). Respecte les limites : 280 caractères sur X, 300 sur
  Bluesky, 500 sur Threads.

Vérifie chaque version avec `caption.py --plateforme <réseau>` : il refuse un
« commente MOT » hors Instagram et Facebook et applique la bonne limite.

## Les règles

- **Pas de lien dans une légende Instagram.** Elle n'est pas cliquable. Bio ou DM.
- **Une seule demande.** Deux demandes, c'est comme aucune. `caption.py` les compte.
- **Le mot-clé doit pouvoir se taper.** Un mot, sans espace, sans emoji, et dit aussi
  dans la vidéo. `Commente DEVIS` marche. `Commente « le modèle de devis »`, non.
- **Emoji en ponctuation, pas en décoration.** Le vérificateur signale plus de 4 pour
  100 caractères.

## La boucle

1. Décide A ou B et dis lequel.
2. Rédige, une version par réseau.
3. Passe-les dans `/insta-humain`. Les légendes sont courtes, le ton IA s'y entend plus
   qu'ailleurs.
4. Lance `caption.py` sur chaque version avec les termes de recherche. Corrige chaque
   ÉCHEC. Tranche chaque À VOIR à voix haute plutôt qu'en silence.
5. Affiche les blocs prêts à copier, puis le reçu :

```
LÉGENDE PRÊTE
travail :     A, le reel porte le hook
visible :     118 caractères sur 125 avant la coupure
demande :     une, commenter DEVIS
hashtags :    3
recherche :   « devis freelance » ligne 3
vérification : PRÊTE
```

Sans PlugKit, c'est fini : la personne colle la légende et publie.

## Publier avec PlugKit

1. **Les comptes.** `list_accounts` (ou `whoami`) : quels réseaux sont branchés, avec
   leur `accountId`.
2. **Le média, hébergé par PlugKit avant tout.** Le `finalMediaUrl` de `/insta-reel`
   y est déjà. Sinon regarde `list_media` (le fichier y est souvent), `upload_media` si
   tu as l'URL directe du fichier, ou `create_media_upload` + `curl -T` +
   `check_media_upload` pour un fichier sur la machine. Jamais un lien de partage qui
   ouvre une page web : la publication échouerait.
3. **Le mot-clé, vérifié avant.** Si une légende dit « commente MOT », lance
   `list_comment_automations`. Pas de règle active pour ce mot sur ce compte ? **On
   ne publie pas** : envoie vers `/insta-dm`, l'automation doit exister avant que le
   post soit en ligne, sinon les premiers commentaires ne reçoivent jamais leur DM.
4. **TikTok** : `get_publish_options` sur le compte, et la personne choisit la
   visibilité. Ne la suppose pas.
5. **Le créneau.** `get_best_times_to_post` sur le compte, dans son fuseau. Une case
   appuyée sur deux posts, c'est du bruit : dis-le et prends l'heure habituelle de la
   personne.
6. **La porte.** Un tableau, une ligne par réseau :

```
RÉSEAU      LÉGENDE (début)                          MÉDIA          DATE
instagram   Cinq heures par devis, c'était mon...    reel-devis.mp4 jeu. 17/10 12:30
facebook    Cinq heures par devis, c'était mon...    reel-devis.mp4 jeu. 17/10 12:30
tiktok      Mes devis me prenaient 5 h. Voilà le...  reel-devis.mp4 jeu. 17/10 12:30  (public)
youtube     Devis : de 5 heures à 20 minutes         reel-devis.mp4 jeu. 17/10 12:30

Réponds « oui » pour programmer, ou dis-moi ce qu'il faut changer.
```

7. **Au « oui », et seulement là.** Un `create_post` par légende : `accountIds` des
   réseaux qui partagent ce texte, `content`, `mediaIds` (ou `mediaUrls`), `scheduledFor`
   et `timezone`. Par défaut, programmé au créneau ; tout de suite seulement si la
   personne le demande. Un lien utile va dans `firstComment` (Instagram, Facebook,
   Threads), pas dans la légende.
8. **Vérifie et note.** `list_posts` pour confirmer le statut. Ajoute l'id du post à
   `~/.claude/insta-kit/log.md`, sur la ligne du reel. Un changement de texte ou de date
   avant la mise en ligne passe par `update_post`, après un nouveau « oui ».

Rien ne part sans « oui » sur le contenu exact affiché.

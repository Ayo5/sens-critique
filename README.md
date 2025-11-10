# System Design

BDD -> API -> Interface

|          | MongoDB                                                                                                           | FastAPI                                                                                                                                                                                       | Next.js                                                                                       |
| -------- | ----------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------- |
| Avantage | Systeme de collection pertinent avec le type de données traité et simple d'utilisation (un film = une collection) | Framework API REST efficace qui peut generer la doc et qui gere le async, on utiliserais uniquement des méthodes get (pour la récuperation de données et le traitements de la recommandation) | L'un des meilleur framework de devweb selon moi car beau, optimisé permet de gerer le ssr ... |

Cas d'usage

- Le user clique sur un film vois un commentaire, il clique sur celui-ci. Le user envoie donc une requete api contenant le film et le commentaire selectionné. L'API traite ces infos et analysant les mots utilisé dans le commentaire et renvoie une liste de commentaire recommander qui contient ses mots qui seront affiché dans la partie commentaire similaire de l'interface.

# Comment le code fonctionne

## Endpoints principaux (exemples)

- GET /collections  
  Retourne la liste des collections (titres de films).

- GET /{collection_name}?limit=100  
  Retourne les documents d'une collection (limit, pagination).

- GET /{collection_name}/{id_review}  
  Retourne la review dont le champ `id` vaut id_review.

- GET /{collection_name}/{id_review}/recommendations?limit=100&min_common=20  
  Retourne des reviews similaires : mêmes mots‑clés (au moins `min_common`) et rating identique ou proche.  
  Paramètres : limit (nombre max de résultats), min_common (nombre minimum de mots‑clés partagés).

## Fonctionnement résumé

- Extraction de mots‑clés : split du texte, garder les mots de longueur > 4, normaliser en minuscules.
- Requête de pré‑filtre : recherche par mots‑clés (regex échappés) + rating similaire, exclure l'id courant.
- Filtre final : calcul de l'intersection des mots‑clés et garder les documents avec au moins `min_common` mots en commun.

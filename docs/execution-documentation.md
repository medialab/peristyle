# Documentation pour l'exécution du projet
Sont documentés ici tous les éléments nécessaires à la réalihttps://github.com/medialab/peristylesation de la méthodologie du projet Péristyle. 
Le projet Péristyle nécessite des éléments de plusieurs types, notamment des scripts de code python, des fichiers json et scripts jupyter pour la visualisation et finalement des fichies csv avec les résultats. Tous ces éléments sont rangés en fonction de leur type dans un dossier nommé "Péristyle". Cette documentation explicite ce classement ainsi que les protocoles d'utilisation des différents éléments, afin de rendre les résultats reproductibles.
Il ne s'agit pas du détail des scripts, ni la justification de la méthodologie mais le protocole réalisé pour ce projet. Pour permettre la reproduction des résultats obtenus, cette documentation se découpe en trois parties:
  - [Organisation du dossier "Péristyle"](#organisation-dossier)
  - [Ordre d'exécution des scripts et desriptiond des scripts](#ordre-script)
  - [Les résultats](#resultats)
## Organisation du dossier "Péristyle"<a name="organisation-dossier"></a>
### Les scripts: l'exécution 
Les scripts principaux pour réaliser les résultats du projet Péristyle se trouvent à la racine du dossier. Ils sont écrits en python. Chaque script exécute une tâche spécifique et il faut les réaliser dans un ordre précis. Les descriptions de ces derniers sont précisées dans la section [Ordre d'exécution des scripts et descriptions des scripts](#ordre-script).
### Sample: les données initiales
Sample contient approximativement 100 000 fichiers texts issus de médiacloud. Ce sont les stories étudiées tout au long du projet, les données brutes. Ainsi, certains de ces fichiers sont imparfaits à cause de problèmes d'importation depuis le serveur médiacloud ou d'extraction des contenus texts. Pour y remédier, ces fichiers text sont ensuite filtrés et nettoyés.
Le nom de chaque fichier correspond à son identifiant. 
### Les résultats
Les résultats du projet prennent plusieurs formes de visualisation. D'une part une partie est uniquement manuscrite sous forme de tableau CSV, d'autres parts il y a des résultats qui prennent des formes plus visuels avec notamment des graphes et des nuages de points.
  Note nomenclature: le projet fonctionne pour une réduction en 3 ou 2 dimensions. Ainsi, presque tous les fichiers résultats sont en double, une version avec "_2D" à la fin du nom pour indiquer que ce sont les résultats pour une réduction en 2 dimensions et l'autre avec "_3D" à la fin du nom pour une réduction en 3 dimensions.
#### Tables: les résultats manuscrits en tableau
Le sous-dossier tables contient tous les fichiers CSV produits par le projet. La description de chaque table est détaillée dans la section [Les tables](#les-tables) 
#### Visualisation: les résultats visualisables
Cette partie des résultats est à exécuter avec un notebook jupyter. En effet, cela permet de donner de nouvelles formes aux résultats et de les rendre interractifs. La description de chaque visualisation est détaillée dans la section [Avec jupyter](#avec-jupyter)
##### Data
Ce sous dossier contient tous les fichiers json avec les données nécessaires pour exécuter les scripts jupyter.  
##### Views
Ce dossier est vide mais sert 
### Texts: extractions pour la vérification
### Autres 
#### Extra
#### Extra stories
#### Database pour cortext

## Ordre d'exécution des scripts et descriptions des scripts<a name="ordre-script"></a>

## Les résultats<a name="resultats"></a>
### Les tables<a name="les-tables"></a>
### Les visualisations
#### Avec jupyter<a name="avec-jupyter"></a>
#### Avec Cortext

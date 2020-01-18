# Péristyle
Bienvenue sur le repository contenant le code du projet "Péristyle".
Le projet Péristyle est un projet de recherche cherchant à trouver un moyen algorithmique de mesurer le style rédactionnel d'un article de presse. 

## Installation

Pour installer les dépendances qui permettent de réaliser le projet, exécutez:

    pip install -r requirements.txt

De plus veillez à bien avoir le ressources nlp du repository <a href="https://github.com/medialab/nlp">NLP</a> à la racine du projet.


## Explication de la documentation

Dans le dossier [**docs**](https://github.com/medialab/peristyle/tree/master/docs) se trouvent tous les éléments de documentations suivant: 

- [execution-documentation.md](https://github.com/medialab/peristyle/blob/master/docs/execution-documentation.md): ce document explique comment reproduire tous les résultats du projet;  
- [features-documentation.md](https://github.com/medialab/peristyle/blob/master/docs/features-documentation.md): ce document explique comment sont calculées toutes les features du projet;
- [features-list.md](https://github.com/medialab/peristyle/blob/master/docs/features-list.md): ce document résume toutes les features du projet;
- [features-extraction.md](https://github.com/medialab/peristyle/blob/master/docs/features-extraction.md): ce document recense toutes les directions de recherches potentielles;
- [notes.md](https://github.com/medialab/peristyle/blob/master/docs/notes.md): document de notes.

## Application

Lien vers l'interface d'exploration de l'espace stylistique: <a href="https://medialab.github.io/peristyle/">https://medialab.github.io/peristyle/</a>. Le code de celle-ci se trouve dans le dossier [**Application**](#Application)
Cette application est une représentation de l'espace stylistique dans lequel les articles et médias sont projetés. 
- les petits points sont les articles;
- les gros points sont les médias;
- les gros points roses nommés de "un" à "huit" sont les barycentres des quartiles.


Les couleurs quant à elles, correspondent aux médias dont sont issus les articles.<br>
Sur la droite de l'écran, les paramètres d'affichage permettent d'ajencer la visualisation de l'espace en choisissant les dimensions voulues sur les axes. En dessous, une boite présente des informations sur l'élément séléctionné, notamment les liens vers les articles.

## Le drive Péristyle

Lien vers le dossier drive Péristyle: <a href="https://drive.google.com/drive/u/1/folders/1TY3JOAV3XOnz4k4IV9UV0eNSQXp_bBuL">drive Péristyle</a>.
Celui-ci contient en particulier deux google slides qui décrivent l'espace stylistique élaboré.
  - Péristyle est le dernier espace stylistique obtenu;
  - Péristyle historique est l'historique des différentes étapes pour arriver à ce résultat.
  
## Remerciements
Le projet Péristyle est financé par le DIM <a href="http://www.dim-humanites-numeriques.fr">STCN</a>

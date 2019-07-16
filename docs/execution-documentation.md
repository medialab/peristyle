# Documentation pour l'exécution du projet
Sont documentés ici tous les éléments nécessaires à la réalisation de la méthodologie du projet Péristyle. 
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
#### Notebooks: les résultats visualisables
Cette partie des résultats est à exécuter avec un notebook jupyter. En effet, les notebooks permettent d'utiliser VegaLite et donc de donner de nouvelles formes aux résultats et de les rendre interractifs. La description de chaque visualisation est détaillée dans la section [Avec jupyter](#avec-jupyter).
##### Data
Ce sous dossier contient tous les fichiers json avec les données nécessaires pour exécuter les scripts jupyter.
##### Views
Ce dossier est vide mais sert à enregistrer les vues générées avec VegaLite. 
### Texts: extractions pour la vérification
Ce fichier contient des fichiers textes avec des textes de stories. Celles-ci ont été lues pour aider à donner une interprétation de l'espace stylistique produit avec la PCA. Le nom des sous dossiers de texts est composé de la façon suivante: numéro de **V**ersion + nombre de **D**imensions. Les versions dépendent des nouvelles features ajoutées.
### Autres
Dans ces dossiers se trouvent tous les scripts et éléments inachevés. 
#### Extra
Les scripts qui se trouvent dans ce sous-dossier font diverses tâches, de plus certains ne sont pas achevés. Certains ne marchent pas.
  - regression_dim_median_tsne.py et regression_dim_media_umap.py réalisent respectivement les algorithmes tsne et umap sur les données; 
  - update_source.py a servi à remettre les informations des sources à jour avec la roue des médias;
  - regression_dim.py est la première version du script utilisé pour faire la réduction de dimension;
  - sample_language_level.py et wiki_word.py ont servi pour produire le dictionaire de niveau de langage;
  - ARI_using_nltk.py est un script d'entrainement pour apprendre à utiliser nltk.
  
#### Extra stories
Ce sont des stories supplémentaires qu'il faudrait projeter dans l'espace stylistique pour voir si ce dernier est prévisible. 
#### Database pour cortext
Ce dossier contient la visualisation topic mdoeling faite avec cortext ainsi que les fichiers texts des stories non filtrée pour faire la database de cortext. 

## Ordre d'exécution des scripts et descriptions des scripts<a name="ordre-script"></a>
  **1. calcul_stories.py**
  
  Ce script est le plus important, il extrait toutes les features des données
  liste des features extraites :
    
    ["ARI","nb_sent","nb_word","nb_char","mean_cw","mean_ws","median_cw","median_ws","shortwords_prop","longwords_prop","max_len_word","dictwords_prop","proper_noun_prop","negation_prop1","negation_prop2","subjectivity_prop1","subjectivity_prop2","interpellation_prop1","interpellation_prop2","nous_prop1","nous_prop2","verb_prop","past_verb_cardinality","pres_verb_cardinality","fut_verb_cardinality","imp_verb_cardinality","other_verb_cardinality","past_verb_prop","pres_verb_prop","fut_verb_prop","imp_verb_prop","plur_verb_prop","sing_verb_prop","tenses_diversity","conditional_prop","question_prop","exclamative_prop","quote_prop","bracket_prop","noun_prop","cconj_prop","sconj_prop","pronp_prop","adj_prop","adv_prop","a","e","i","l","n","o","sttr","comma_prop","numbers_prop","level0_prop","level1_prop","level2_prop","autre_prop","ner_prop","person_prop","norp_prop","fac_prop","org_prop","gpe_prop","loc_prop","product_prop","event_prop"] 
    
(cf l'autre partie de la documentation pour plus d'explications)

***Il nécessite d'avoir le repo NLP à sa racine pour pouvoir être exécuté correctement.***


  **2. filter_sample.py**
  
  Ce script filtre les stories en fonction de différents critères dont une partie se base sur les valeurs de quelques features calculée précedemment. Les stories qui ne répondent pas aux critères sont taggées comme "filtered" et sont par la suite ignorée.
  Liste des critères de filtration:
            - story issue d'un media paywallé;
            - story issue d'un media partiellement paywallé mais fait moins de 1000 charactères;
            - story écrite dans une autre langue;
            - story ayant une valeur pour la feature ARI incohérente, c'est-à-dire négative ou plus que 20;
            - story ne contennant pas de mots;
            - story à moins de 4 phrases;
            - story à moins 250 mots ou plus de 1500 mots pour normaliser la longueur des texts étudiés;
            - story issue d'un média pas suffisement représenté dans les données, c'est à dire d'un média qui comptabilise moins de 20 stories au total.
            
  **3. join_media_features.py**
  
  Ce script calcule une valeur pour pouvoir avoir une position moyenne de toutes les stories pour chaque média et ainsi avoir une position pour les médias. Pour réaliser ce calcul, les valeurs des features de toutes les stories sont d'abord *scalées* avec la fonction scale de sklearn puis on calcule la moyenne de ces dernières pour chaque média. On obtient ainsi des vecteurs pour les médias.  
  
  **4. regression_dim_media.py**
  
  Ce script réalise la PCA sur les vecteurs des stories et des médias. L'espace stylistique est créé à partir des vecteurs des médias (fonction fit transform de sklearn) puis les vecteurs des story sont projeté dans celui-ci (fonction fit de sklearn). 
  
  **5. filter_studies.py**
  
  Ce script a plusieurs fonction pour étudier l'espace obtenu, c'est notamment celui-ci qui détermine les barycentres des quartiles, la distribution des stories et des médias dans les 8 ou 4 quartiers de l'espace en 3 ou 2 dimensions, enfin il pemet de calculer la distance entre les stories/les médias et le barycentre de leur quartile.
  
  **6. topic_distribution.py**
  
  Ce script calcul la distribution dans l'espace stylistique des stories d'un topic donné.
  
  **6.bis extract_articles.py**
  
  Ce script extrait des texts de stories dans un document text.

## Les résultats<a name="resultats"></a>
Dans cette section vous trouverez les détails des différents fichiers contenant des résultats. 

### Les tables<a name="les-tables"></a>
  - sources.csv & paywall.csv: méta-informations sur les médias;
  - sources_update.csv & wheel_tuned_full.csv: méta-informations sur les médias mises à jour avec la roue des médias;
  - sample_normalized_sorted.csv: méta-informations sur toutes les stories;
  - sample_with_features.csv: stories avec toutes les valeurs des features calculées; 
  - sample_filtered_with_features.csv: même chose que au dessus mais avec un tag "filtered" en plus; 
  - media_with_mean_features.csv: résultat des valeurs des features pour les médias renvoyé par le script join_media_features.py;
  - medias_with_distance_to_barycenters_(3D/2D).csv: distribution des médias dans l'espace stylistique ainsi que leur distance au barycentre de leur quartile;
  - stories_with_distances_to_barycenters_(3D/2D).csv: distribution des stories dans l'espace stylistique ainsi que leur distance au barycentre de leur quartile;
  - text_near_barycenters_extraction_(3D/2D).csv: extraction des textes les plus proches des barycentres;
  - topic_distribution.csv & topic_stories_examples.csv: distribution des topics dans l'espace stylistique ainsi que des exemples de stories pour chaqe topic;
  - media_clustered_3D.csv: résultat du clustering umap;
  - bloc_stories_distribution.csv: distribution des bloc dans l'espace stylistique.

### Les visualisations
#### Avec jupyter<a name="avec-jupyter"></a>
  - Features distances.ipynb cette visualisation donne des informations sur les variables, en particulier la projection des variables sue les axes x, y et z;
  - Show PCA 3D.ipynb & show PCA mean media 3D.ipynb ces visualisations sont différentes dispositionns pour montrer l'espace stylisqtique aec les médias et les stories;
  - Topic distribution.ipynb cette visualisation montre la distribution des articles des différents types de médias dans les huit quartiles. 
#### Avec Cortext
Un topic modeling a été réalisé sur les texts des articles ayant passé le filtre avec cortext.
#### Application
Enfin, sur ce lien https://medialab.github.io/peristyle/ ammène sur une application qui projette les articles et les médias dans l'espace stylistique.  
Les articles sont les petits points, les médias les gros points et les gros points roses nommés de "un" à "huit" sont les barycentres. Les couleurs quant à elles, correspondent aux médias dont sont issus les articles. Sur la droite de l'écran, les paramètres d'affichage permettent d'ajencer la visualisation de l'espace en choisissant les dimensions voulues sur les axes. En dessous, une boite présente des informations sur l'élément séléctionné, nottament les liens vers les articles.
Le code de cette application est dans le sous dossier application.

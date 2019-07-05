# Documentation features

Voici la documentation de toutes les features calculées pour le projet [Péristyle](https://github.com/medialab/peristyle). Dans ce cadre, celles-ci doivent se rapporter au style rédactionnel et non au sujet des écrits traités, elles sont donc essentiellement grammaticales.
Il y a plusieurs types de features qui ont été calculées grâce à différents outils de tal: les regex ainsi que les librairies python [Spacy](https://spacy.io/) et [NLTL](http://www.nltk.org/), elles sont expliquées ainsi que leur méthode de calcul ci-dessous. 

# Les différentes normalisations
Les features prennent la plupart du temps la forme de proportion, c'est-à-dire que les features sont comptées dans les textes puis le résultat est normalisé. Cette normalisation peut prendre plusieurs formes:
  * normalisation par le nombre de mots calculé par le wordtokenizer de NLTK;
  * normalisation par le nombre de phrases calculé par le senttokenizer de NLTK;
  * normalisation par le nombre de tokens calculé par le tokenizer de Spacy;
  * normalisation par le nombre de verbes calculé par le pos-tagging de Spacy.

La tokenization de Spacy moins performante et plus lente que celle de NLTK lorsqu'il s'agit de découper le texte en phrase. Or, cette mesure est nécessaire pour calculer certaines features (en particulier l'ARI, mais aussi la proportion de phrases exclamatives par exemple), d'où la cohabitation de ces deux outils au sein de ce projet.

# Features calculées avec des regex
## Explications
Les **regex**, ou *expressions régulières*, permettent de calculer des features qui sont plus abstraites que du pos-tagging. En effet, le pos-tagging permet d'extraire des features en se basant uniquement sur la nature grammaticale des mots alors que les regex peuvent se baser sur des mots de natures différentes mais qui recouvrent la même notion comme la subjectivité.
Cependant, on ne peut relever que les **traces explicites** de ces notions car les regex se basent sur une liste de mots prédéfinie.

Ces features sont calculées de deux manières différentes, c'est pourquoi elles sont dupliquées en version 1 et en version 2, negation_prop1 et negation_prop2 par exemple. En effet, le version 1 correspond toujours à une 
normalisation par le nombre de mots et la version 2 par le nombre de phrases. Celle selectionnée pour la PCA est la version 1.
## Features calculées
### *negation_prop*
Cette calcule la proportion de **negation explicite** 

### *subjectivity_prop*
### *interpellation_prop*
### *nous_prop*

# Features calculées avec NLTK
## Features utilisant la tokenisation de nltk
### *nb_sent*
### *nb_char*
### *mean_cw/ws*
### *median_cw/ws*
### *max_len_word*
### *shortwords_prop*
### *longwords_prop*
    
## Métrique de lisibilité *ARI*
### Explication
### Formule

# Features calculées avec Spacy
## Pos-tagging
### Features verbales
#### *verb_prop*
#### *past_verb_prop*
#### *pres_verb_prop*
#### *futur_verb_prop*
#### *imp_verb_prop*
#### *plur_verb_prop*
#### *sing_verb_prop*
#### *conditional_prop*

### Features de ponctuation
#### *question_prop*
#### *exclamative_prop*
#### *quote_prop*
#### *bracket_prop*
#### *comma_prop*

### Features grammaticales
#### *numbers_prop*
#### *adv_prop*
#### *adj_prop*
#### *noun_prop*
#### *cconj_prop*
#### *sconj_prop*

### Features d'entitées nommées
#### *ner_prop*
#### *person_prop*
#### *norp_prop*
#### *fac_prop*
#### *org_prop*
#### *gpe_prop*
#### *loc_prop*
#### *product_prop*
#### *event_prop*


# Features calculées grâce à d'autres ressources NLP
## Le repo NLP
## Exceptions noms propres
### *propernoun_prop*
## Dictionnaire français
### *dictwords_prop*
## Dictionaire de stopwords
### *stopwords_prop*
## wikitinary.csv
### *level0_prop*
### *level1_prop*
### *level2_prop*
### *autre_prop*

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
Cette feature calcule la proportion de **negation explicite** grâce à la formule suivante:
    
    NEGATION = re.compile(r"\bne\b|\bn'\b|\bnon\b", re.I)

### *subjectivity_prop*
Cette feature calcule la proportion de **subjectivité explicite** grâce à la formule suivante:

    SUBJ = re.compile(r"\bje\b|\bma\b|\bme\b|\bmon\b|\bmes\b|\bj'\b|\bm'\b|\bmien\b|\bmienne\b|\bmiens\b|\bmiennes\b", re.I)

### *interpellation_prop*
Cette feature calcule la proportion de **interpellation explicite** (incluant tout les tutoiements et vouvoiements) grâce à la formule suivante:

    INTERPEL = re.compile(r"\btu\b|\bt'\b|\bte\b|\btes\b|\bton\b|\bta\b|\btien\b|\btiens\b|\btienne\b|\btiennes\b|\bvous\b|\bvos\b|\bvotre\b|\bvôtre\b|\bvôtres\b", re.I)

### *nous_prop*
Cette feature calcule la proportion de **nounoiement explicite** grâce à la formule suivante:

    NOUS = re.compile(r"\bnous\b|\bnos\b|\bnotre\b|\bnrôte\b|\bnôtres\b", re.I)

# Features calculées avec NLTK
Les prochaines features utilisent la bibliothèque python **[NLTK](http://www.nltk.org/)**. Grâce au tokenizer de phrases et de mots, cet outil permet en particulier de capturer la longueur des articles.

## Features utilisant la tokenisation de nltk
### *nb_sent*
Cette feature comptabilise le **nombre de phrases** grâce à la fonction sent_tokenize de NLTK. Ne sont considérées comme phrases valides et ne sont comptabilisées que les phrases avec une longueur censée comprise **entre 3 et 300 mots**.
### *nb_char*
Cette feature comptabilise la somme du **nombre de charactères** des mots de plus de trois charactères.
### *mean_cw/mean_ws*
Ces features sont la **moyenne du nombre de charactères par mot** et la **moyenne du nombre de mots par phrase**.  
### *median_cw/median_ws*
Ces features sont la **médiane du nombre de charactères par mot** et la **médiane du nombre de mots par phrase**.  
### *max_len_word*
Cette feature est la **longueur du mot le plus long** du texte. 
### *shortwords_prop*
Cette feature est la proportion de **mots courts**. Ne sont considérés comme mots courts que les mots de **moins de 5 charactères** et le résultats est divisé par le nombre de mots total. La limite a été fixée à 5 charactères car c'est la moyenne du nombre de charactères par mot en français.
### *longwords_prop*
Cette feature est la proportion de **mots longs**. Ne sont considérés comme mots longs que les mots de **plus de 5 charactères** et le résultats est divisé par le nombre de mots total. La limite a été fixée à 5 charactères car c'est la moyenne du nombre de charactères par mot en français. 
## Métrique de lisibilité *ARI*
### Explication
ARI, ou [**Automated Readability Index**](http://www.readabilityformulas.com/automated-readability-index.php) est une **métrique de lisibilité** comprise entre 0 et 14 (mais entre 0 et 30 pour le projet car adapté au français). LE résultat renvoyé donne une estimation de la complexité du texte et de sa difficulté à être lu. Cette métrique a été choisie car elle ne dépend pas du nombre de syllabes comme la plupart des autres métriques de lisibilité. En effet, contrairement à l'anglais où il sufffit de compter le nombre de voyelles pour estimer le nombre de syllabes, en français les syllabes sont souvent formées de plusieurs voyelles.
C'est pour calculer cette formule que le tokenizer de phrase est nécessaire.
### Formule
             ARI = 4.71 * (moyenne de charactères par mot) + 0.5 * (moyenne de mots par phrase) - 21.43

# Features calculées avec Spacy
## Pos-tagging
[Spacy](https://spacy.io/) offre un grand nombre d'opérations de nlp. La fonctionnalité d'[étiquetage morpho-syntaxique](https://fr.wikipedia.org/wiki/%C3%89tiquetage_morpho-syntaxique), ou en anglais **pos-tagging** ([Part-Of-Speech tagging](https://en.wikipedia.org/wiki/Part-of-speech_tagging)) est largement utilisée tout au long de ce projet. En utilisant le modèle *fr_core_news_sm*, tous les texts sont étiquetés puis cet étiquetage est triés, comptabilisé, normalisé. [Lien vers la documentation des tags de Spacy](https://github.com/explosion/spaCy/blob/master/spacy/lang/fr/tag_map.py).  
On appelle *tokens* les entités morpho-syntaxique en lesquels le texte est découpés.  
## Features calculées
### Features verbales
Le pos-tagging de Spacy donne des informations très poussées pour ce qui concerne les verbes, avec notamment le temps, le mode et la personne. Ces informations sont contenues dans une chaîne de charactère d'un attribut *tag_* des tokens, qu'il faut par la suite trier pour extraire les informations. (Tous les verbes sont taggé *"VERB"*.)
#### *verb_prop*
Cette feature comptabilise le nombre de **verbes total** divisé par le nombre de total de tokens. 
#### *past_verb_prop*
Cette feature comptabilise le nombre de **verbes au passé** divisé par le nombre de total de verbes.
#### *pres_verb_prop*
Cette feature comptabilise le nombre de **verbes au présent** divisé par le nombre de total de verbes.
#### *futur_verb_prop*
Cette feature comptabilise le nombre de **verbes au futur** divisé par le nombre de total de verbes.
#### *imp_verb_prop*
Cette feature comptabilise le nombre de **verbes à l'imparfait** divisé par le nombre de total de verbes.
#### *plur_verb_prop*
Cette feature comptabilise le nombre de **verbes conjugué au pluriel** divisé par le nombre de total de verbes.
#### *sing_verb_prop*
Cette feature comptabilise le nombre de **verbes conjugué au singulier** divisé par le nombre de total de verbes.
#### *conditional_prop*
Cette feature comptabilise le nombre de **verbes au conditionnel** divisé par le nombre de total de verbes.
### Features de ponctuation
Le nom de l'un des tag de Spacy est *"PUNCT"* pour ponctuation. Le texte de tous les tokens étiquetés ainsi sont stockés dans une variable, puis chaque forme de ponctuation est reconnue grâce à une regex, enfin ces variables sont normalisées par le nombre de phrases dans le texte.  
#### *question_prop*
Cette feature comptabilise le nombre de **points d'interrogation** divisé par le nombre total de phrases.
#### *exclamative_prop*
Cette feature comptabilise le nombre de points d'**exclamation divisé** par le nombre total de phrases.
#### *quote_prop*
Cette feature comptabilise le nombre de **guillemets** divisé par 2 avant d'être normalisé par le nombre total de phrases. 
#### *bracket_prop*
Cette feature comptabilise le nombre de **parenthèses** divisé par 2 avant d'être normalisé par le nombre total de phrases.
#### *comma_prop*
Cette feature comptabilise le nombre de **virgules** divisé par le nombre total de phrases.

### Features grammaticales
#### *numbers_prop*
Cette feature comptabilise le nombre de nombres (tag *"NUM"*) divisé par le nombre total de tokens. 
#### *adv_prop*
Cette feature comptabilise le nombre d'**adverbes** divisé par le nombre total de tokens.
#### *adj_prop*
Cette feature comptabilise le nombre d'**adjectifs** divisé par le nombre total de tokens.
#### *noun_prop*
Cette feature comptabilise le nombre de **noms** divisé par le nombre total de tokens.
#### *cconj_prop*
Cette feature comptabilise le nombre de **conjonctions de coordinations** divisé par le nombre total de tokens.
#### *sconj_prop*
Cette feature comptabilise le nombre de **conjonctions de subordination** divisé par le nombre total de tokens.

### Features d'entitées nommées
Les Spacy identifie également les entités nommées (ou ner). Celles-ci sont identiées par le modèle de tokenization puis elles sont accessibles au travers de l'attribut ents du texte tokenizé. Chaque entité identifiée possède un attribut de label indiquant le type de l'entité. [Lien vers la documentation des entités nommées de Spacy.](https://spacy.io/api/annotation/)
#### *ner_prop*
Cette feature comptabilise le nombre total d'**entités nommées** divisé par le nombre total de tokens.
#### *person_prop*
Cette feature comptabilise le nombre d'entités nommées **personnes** identifiées divisé par le nombre total de tokens. (label: *"PERSON"*)
#### *norp_prop*
Cette feature comptabilise le nombre d'entités nommées **conjonctions de subordination** divisé par le nombre total de tokens. (label: *"NORP"*)
#### *fac_prop*
Cette feature comptabilise le nombre d'entités nommées **de construction** (monuments, aéroports, autoroutes, ponts etc.) divisé par le nombre total de tokens. (label: *"FAC"*)
#### *org_prop*
Cette feature comptabilise le nombre d'entités nommées **organisation** (ONG, entreprises, agences, institutions etc.) divisé par le nombre total de tokens. (label: *"ORG"*)
#### *gpe_prop*
Cette feature comptabilise le nombre d'entités nommées **éléments géopolitiques** (pays, villes, états etc.) divisé par le nombre total de tokens. (label: *"GPE"*)
#### *loc_prop*
Cette feature comptabilise le nombre d'entités nommées **éléments de localisation naturels** (chaînes de montagnes, étendues d'eau etc.) divisé par le nombre total de tokens. (label: *"LOC"*)
#### *product_prop*
Cette feature comptabilise le nombre d'entités nommées **produits** (objets, véhicules, aliments etc.) divisé par le nombre total de tokens. (label: *"PRODUCT"*)
#### *event_prop*
Cette feature comptabilise le nombre d'entités nommées **événements** (noms d'ouragan, batailles, guerres, événements sportifs etc.) divisé par le nombre total de tokens. (label: *"EVENT"*)

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

# Features biais
## Explications
## Méthode de calcul
## Features biais
### *e*, *l*, *a*, *o*, *u*, *i*, *n*

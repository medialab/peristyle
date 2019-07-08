# Documentation features
## Sommaire
 - [1. Introduction](#introduction)
 - [2. Les différentes normalisations](#les-différentes-normalisations)
 - [3. Features calculées avec des regex](#features-calculées-avec-des-regex)
  - [3.1. Explications](#explications)
  - [3.2. Features calculées](#features-calculées)
    - [negation_prop](#negation_prop)
    - [subjectivity_prop](#subjectivity_prop)
    - [interpellation_prop](#interpellation_prop)
    - [nous_prop](#nous_prop)
 - [4. Features calculées avec NLTK ](#features-calculées-avec-nltk)
    - [4.1 Features utilisant la tokenisation de nltk](#features-utilisant-la-tokenisation-de-nltk)
      - [nb_sent](#nb_sent)
      - [nb_char](#nb_char)
      - [mean_cw/mean_ws](#mean)
      - [median_cw/median_ws](#median)
      - [max_len_word](#max_len_word)
      - [shortwords_prop](#shortwords_prop)
      - [longwords_prop](#longwords_prop)
   - [4.2. Métrique de lisibilité ARI](#ari)
      - [Explication](#explications-ari)
      - [Formule](#formule-ari)
   - [4.3. Métrique de richesse de vocabulaire sttr](#sttr)
      - [Explications](#explications-sttr)
 - [5. Features calculées avec Spacy](#features-calculées-avec-spacy)
   - [5.1. Pos-tagging](#pos-tagging)
   - [5.2. Features calculées](#features-calculées-spacy)
      - [5.2.1. Features verbales](#features-verbales)
         - [verb_prop](#verb_prop)
         - [past_verb_prop](#past_verb_prop)
         - [pres_verb_prop](#pres_verb_prop)
         - [futur_verb_prop](#futur_verb_prop)
         - [imp_verb_prop](#imp_verb_prop)
         - [plur_verb_prop](#plur_verb_prop)
         - [sing_verb_prop](#sing_verb_prop)
         - [conditional_prop](#conditional_prop)
      - [5.2.2. Features de ponctuation](#punct-features)
         - [question_prop](#question_prop)
         - [exclamative_prop](#exclamative_prop)
         - [quote_prop](#quote_prop)
         - [bracket_prop](#bracket_prop)
         - [comma_prop](#comma_prop)
      - [5.2.3. Features grammaticales](#gram_features)
         - [numbers_prop](#numbres_prop)
         - [adv_prop](#adv_prop)
         - [adj_prop](#adj_prop)
         - [noun_prop](#noun_prop)
         - [cconj_prop](#cconj_porp)
         - [sconj_prop](#sconj_prop)
         - [pronp_prop](#pronp_p)
      - [5.2.4. Features d'entitées nommées](#ner-features)
         - [ner_prop](#ner_prop)
         - [person_prop](#person_prop)
         - [norp_prop](#norp_prop)
         - [fac_prop](#fac_prop)
         - [org_prop](#org_prop)
         - [gpe_prop](#gpe_prop)
         - [loc_prop](#loc_prop)
         - [product_prop](#product_prop)
         - [event_prop](#event_prop)
 - [6. Features calculées avec d'autres ressources de NLP](#nlp-features)
   - [6.1. Le repo NLP](#repo-nlp)
   - [6.2. Exceptions noms propres](#nom-propres)
      - [propernoun_prop](#propernoun_prop)
   - [6.3. Dictionnaire français](#français)
      - [dictwords_prop](#dictwords_prop)
   - [6.4. Dictionaire de stopwords](#stopwords)
      - [stopwords_prop](#stopwords_prop)
   - [6.5. wikitionary.csv](#wikitionary)
      - [level0_prop](#level0_porp)
      - [level2_prop](#level2_prop)
      - [autre_prop](#autre_prop)
      - [level1_prop](#level1_prop)
 - [7. Features biais](#features-biais)
   - [7.1. Explications](#explications-biais)
   - [7.2. Méthode de calcul](#biais-calcul)

## 1. Introduction <a name="introduction"></a>
Voici la documentation de toutes les features calculées pour le projet [Péristyle](https://github.com/medialab/peristyle). Dans ce cadre, celles-ci doivent se rapporter au style rédactionnel et non au sujet des écrits traités, elles sont donc essentiellement grammaticales.
Il y a plusieurs types de features qui ont été calculées grâce à différents outils de tal: les regex ainsi que les librairies python [Spacy](https://spacy.io/) et [NLTL](http://www.nltk.org/), elles sont expliquées ainsi que leur méthode de calcul ci-dessous. 


## 2. Les différentes normalisations<a name="les-différentes-normalisations"></a>
Les features prennent la plupart du temps la forme de proportion, c'est-à-dire que les features sont comptées dans les textes puis le résultat est normalisé. Cette normalisation peut prendre plusieurs formes:
  * normalisation par le nombre de mots calculé par le wordtokenizer de NLTK;
  * normalisation par le nombre de phrases calculé par le senttokenizer de NLTK;
  * normalisation par le nombre de tokens calculé par le tokenizer de Spacy;
  * normalisation par le nombre de verbes calculé par le pos-tagging de Spacy.

La tokenization de Spacy moins performante et plus lente que celle de NLTK lorsqu'il s'agit de découper le texte en phrase. Or, cette mesure est nécessaire pour calculer certaines features (en particulier l'ARI, mais aussi la proportion de phrases exclamatives par exemple), d'où la cohabitation de ces deux outils au sein de ce projet.

## 3. Features calculées avec des regex<a name="features-calculées-avec-des-regex"></a>
### 3.1. Explications<a name="explications"></a>
Les **regex**, ou *expressions régulières*, permettent de calculer des features qui sont plus abstraites que du pos-tagging. En effet, le pos-tagging permet d'extraire des features en se basant uniquement sur la nature grammaticale des mots alors que les regex peuvent se baser sur des mots de natures différentes mais qui recouvrent la même notion comme la subjectivité.
Cependant, on ne peut relever que les **traces explicites** de ces notions car les regex se basent sur une liste de mots prédéfinie.

Ces features sont calculées de deux manières différentes, c'est pourquoi elles sont dupliquées en version 1 et en version 2, negation_prop1 et negation_prop2 par exemple. En effet, le version 1 correspond toujours à une 
normalisation par le nombre de mots et la version 2 par le nombre de phrases. Celle selectionnée pour la PCA est la version 1.
### 3.2. Features calculées<a name="features-calculées"></a>
#### *negation_prop*<a name="negation_prop"></a>
Cette feature calcule la proportion de **negation explicite** grâce à la formule suivante:
    
    NEGATION = re.compile(r"\bne\b|\bn'\b|\bnon\b", re.I)

#### *subjectivity_prop*<a name="subjectivity_prop"></a>
Cette feature calcule la proportion de **subjectivité explicite** grâce à la formule suivante:

    SUBJ = re.compile(r"\bje\b|\bma\b|\bme\b|\bmon\b|\bmes\b|\bj'\b|\bm'\b|\bmien\b|\bmienne\b|\bmiens\b|\bmiennes\b", re.I)

#### *interpellation_prop*<a name="interpellation_prop"></a>
Cette feature calcule la proportion de **interpellation explicite** (incluant tout les tutoiements et vouvoiements) grâce à la formule suivante:

    INTERPEL = re.compile(r"\btu\b|\bt'\b|\bte\b|\btes\b|\bton\b|\bta\b|\btien\b|\btiens\b|\btienne\b|\btiennes\b|\bvous\b|\bvos\b|\bvotre\b|\bvôtre\b|\bvôtres\b", re.I)

#### *nous_prop*<a name="nous_prop"></a>
Cette feature calcule la proportion de **nounoiement explicite** grâce à la formule suivante:

    NOUS = re.compile(r"\bnous\b|\bnos\b|\bnotre\b|\bnrôte\b|\bnôtres\b", re.I)

## 4. Features calculées avec NLTK<a name="features-calculées-avec-NLTK"></a>
Les prochaines features utilisent la bibliothèque python **[NLTK](http://www.nltk.org/)**. Grâce au tokenizer de phrases et de mots, cet outil permet en particulier de capturer la longueur des articles.

### 4.1. Features utilisant la tokenisation de nltk<a name="features-utilisant-la-tokenisation-de-nltk"></a>
#### *nb_sent*<a name="nb_sent"></a>
Cette feature comptabilise le **nombre de phrases** grâce à la fonction sent_tokenize de NLTK. Ne sont considérées comme phrases valides et ne sont comptabilisées que les phrases avec une longueur censée comprise **entre 3 et 300 mots**.
#### *nb_char*<a name="nb_char"></a>
Cette feature comptabilise la somme du **nombre de charactères** des mots de plus de trois charactères.
#### *mean_cw/mean_ws*<a name="mean"></a>
Ces features sont la **moyenne du nombre de charactères par mot** et la **moyenne du nombre de mots par phrase**.  
#### *median_cw/median_ws*<a name="median"></a>
Ces features sont la **médiane du nombre de charactères par mot** et la **médiane du nombre de mots par phrase**.  
#### *max_len_word*<a name="max_len_word"></a>
Cette feature est la **longueur du mot le plus long** du texte. 
#### *shortwords_prop*<a name="shortwords_prop"></a>
Cette feature est la proportion de **mots courts**. Ne sont considérés comme mots courts que les mots de **moins de 5 charactères** et le résultats est divisé par le nombre de mots total. La limite a été fixée à 5 charactères car c'est la moyenne du nombre de charactères par mot en français.
#### *longwords_prop*<a name="longwords_prop"></a>
Cette feature est la proportion de **mots longs**. Ne sont considérés comme mots longs que les mots de **plus de 5 charactères** et le résultats est divisé par le nombre de mots total. La limite a été fixée à 5 charactères car c'est la moyenne du nombre de charactères par mot en français. 
### 4.2. Métrique de lisibilité *ARI*<a name="ari"></a>
#### 4.2.1. Explication<a name="explications-ari"></a>
ARI, ou [**Automated Readability Index**](http://www.readabilityformulas.com/automated-readability-index.php) est une **métrique de lisibilité** comprise entre 0 et 14 (mais entre 0 et 30 pour le projet car adapté au français). Le résultat renvoyé donne une estimation de la complexité du texte et de sa difficulté à être lu. Cette métrique a été choisie car elle ne dépend pas du nombre de syllabes comme la plupart des autres métriques de lisibilité. En effet, contrairement à l'anglais où il sufffit de compter le nombre de voyelles pour estimer le nombre de syllabes, en français les syllabes sont souvent formées de plusieurs voyelles.
C'est pour calculer cette formule que le tokenizer de phrase est nécessaire.
#### 4.2.2. Formule<a name="formule-ari"></a>
             ARI = 4.71 * (moyenne de charactères par mot) + 0.5 * (moyenne de mots par phrase) - 21.43

### 4.3. Métrique de richesse de vocabulaire *sttr*<a name="sttr"></a>
#### 4.3.1. Explications<a name="explications-sttr"></a>
STTR, ou [**Standarised Types/Tokens Ration**](https://lexically.net/downloads/version7/HTML/type_token_ratio_proc.html) est une **métrique de richesse du vocabulaire**. Le résultat renvoyé donne une estimation de la diversité du vocabulaire d'un texte, et permet ainsi de comparer les textes entre eux. Issue de la TTR (Types/Tokens Ratio) qui calcule le rapport entre le nombre de mots différents employés et nombres de mots total, la STTR adapte ce calcul à des textes de longueurs différente. En effet, la TTR est particulièrement liées au nombre de mots du texte, or le projet Péristyle traite des articles de longueurs variées. Ainsi, la STTR calcule la TTR sur toutes les franges de 100 mots, puis tous ces résultats de TTR sont moyennés.  
## 5. Features calculées avec Spacy<a name="features-calculées-avec-spacy"></a>
### 5.1. Pos-tagging<a name="pos-tagging"></a>
[Spacy](https://spacy.io/) offre un grand nombre d'opérations de nlp. La fonctionnalité d'[étiquetage morpho-syntaxique](https://fr.wikipedia.org/wiki/%C3%89tiquetage_morpho-syntaxique), ou en anglais **pos-tagging** ([Part-Of-Speech tagging](https://en.wikipedia.org/wiki/Part-of-speech_tagging)) est largement utilisée tout au long de ce projet. En utilisant le modèle *fr_core_news_sm*, tous les texts sont étiquetés puis cet étiquetage est triés, comptabilisé, normalisé. [Lien vers la documentation des tags de Spacy](https://github.com/explosion/spaCy/blob/master/spacy/lang/fr/tag_map.py).  
On appelle *tokens* les entités morpho-syntaxique en lesquels le texte est découpés.  
### 5.2. Features calculées<a name="features-calculées-spacy"></a>
#### 5.2.1. Features verbales<a name="features-verbales"></a>
Le pos-tagging de Spacy donne des informations très poussées pour ce qui concerne les verbes, avec notamment le temps, le mode et la personne. Ces informations sont contenues dans une chaîne de charactère d'un attribut *tag_* des tokens, qu'il faut par la suite trier pour extraire les informations. (Tous les verbes sont taggé *"VERB"*.)
##### *verb_prop*<a name="verb_prop"></a>
Cette feature comptabilise le nombre de **verbes total** divisé par le nombre de total de tokens. 
##### *past_verb_prop*<a name="past_verb_prop"></a>
Cette feature comptabilise le nombre de **verbes au passé** divisé par le nombre de total de verbes.
##### *pres_verb_prop*<a name="pres_verb_prop"></a>
Cette feature comptabilise le nombre de **verbes au présent** divisé par le nombre de total de verbes.
##### *futur_verb_prop*<a name="futur_verb_prop"></a>
Cette feature comptabilise le nombre de **verbes au futur** divisé par le nombre de total de verbes.
##### *imp_verb_prop*<a name="imp_verb_prop"></a>
Cette feature comptabilise le nombre de **verbes à l'imparfait** divisé par le nombre de total de verbes.
##### *plur_verb_prop*<a name="plur_verb_prop"></a>
Cette feature comptabilise le nombre de **verbes conjugué au pluriel** divisé par le nombre de total de verbes.
##### *sing_verb_prop*<a name="sing_verb_prop"></a>
Cette feature comptabilise le nombre de **verbes conjugué au singulier** divisé par le nombre de total de verbes.
##### *conditional_prop*<a name="conditional_prop"></a>
Cette feature comptabilise le nombre de **verbes au conditionnel** divisé par le nombre de total de verbes.
#### 5.2.2. Features de ponctuation<a name="punct-features"></a>
Le nom de l'un des tag de Spacy est *"PUNCT"* pour ponctuation. Le texte de tous les tokens étiquetés ainsi sont stockés dans une variable, puis chaque forme de ponctuation est reconnue grâce à une regex, enfin ces variables sont normalisées par le nombre de phrases dans le texte.  
##### *question_prop*<a name="question_prop"></a>
Cette feature comptabilise le nombre de **points d'interrogation** divisé par le nombre total de phrases.
##### *exclamative_prop*<a name="exclamative_prop"></a>
Cette feature comptabilise le nombre de points d'**exclamation divisé** par le nombre total de phrases.
##### *quote_prop*<a name="quote_prop"></a>
Cette feature comptabilise le nombre de **guillemets** divisé par 2 avant d'être normalisé par le nombre total de phrases. 
##### *bracket_prop*<a name="bracket_prop"></a>
Cette feature comptabilise le nombre de **parenthèses** divisé par 2 avant d'être normalisé par le nombre total de phrases.
##### *comma_prop*<a name="comma_prop"></a>
Cette feature comptabilise le nombre de **virgules** divisé par le nombre total de phrases.

#### 5.2.3. Features grammaticales<a name="gram_features"></a>
##### *numbers_prop*<a name="numbres_prop"></a>
Cette feature comptabilise le nombre de nombres (tag *"NUM"*) divisé par le nombre total de tokens. 
##### *adv_prop*<a name="adv_prop"></a>
Cette feature comptabilise le nombre d'**adverbes** divisé par le nombre total de tokens.
##### *adj_prop*<a name="adj_prop"></a>
Cette feature comptabilise le nombre d'**adjectifs** divisé par le nombre total de tokens.
##### *noun_prop*<a name="noun_prop"></a>
Cette feature comptabilise le nombre de **noms** divisé par le nombre total de tokens.
##### *cconj_prop*<a name="cconj_porp"></a>
Cette feature comptabilise le nombre de **conjonctions de coordinations** divisé par le nombre total de tokens.
##### *sconj_prop*<a name="sconj_prop"></a>
Cette feature comptabilise le nombre de **conjonctions de subordination** divisé par le nombre total de tokens.
##### *pronp_prop*<a name="pronp_p"></a>
Cette feature comptabilise le nombre de **pronoms personnels** divisé par le nombre total de tokens.

#### 5.2.4. Features d'entitées nommées<a name="ner-features"></a>
Les Spacy identifie également les entités nommées (ou ner). Celles-ci sont identiées par le modèle de tokenization puis elles sont accessibles au travers de l'attribut ents du texte tokenizé. Chaque entité identifiée possède un attribut de label indiquant le type de l'entité. [Lien vers la documentation des entités nommées de Spacy.](https://spacy.io/api/annotation/)
##### *ner_prop*<a name="ner_prop"></a>
Cette feature comptabilise le nombre total d'**entités nommées** divisé par le nombre total de tokens.
##### *person_prop*<a name="person_prop"></a>
Cette feature comptabilise le nombre d'entités nommées **personnes** identifiées divisé par le nombre total de tokens. (label: *"PERSON"*)
##### *norp_prop*<a name="norp_prop"></a>
Cette feature comptabilise le nombre d'entités nommées **conjonctions de subordination** divisé par le nombre total de tokens. (label: *"NORP"*)
##### *fac_prop*<a name="fac_prop"></a>
Cette feature comptabilise le nombre d'entités nommées **de construction** (monuments, aéroports, autoroutes, ponts etc.) divisé par le nombre total de tokens. (label: *"FAC"*)
##### *org_prop*<a name="org_prop"></a>
Cette feature comptabilise le nombre d'entités nommées **organisation** (ONG, entreprises, agences, institutions etc.) divisé par le nombre total de tokens. (label: *"ORG"*)
##### *gpe_prop*<a name="gpe_prop"></a>
Cette feature comptabilise le nombre d'entités nommées **éléments géopolitiques** (pays, villes, états etc.) divisé par le nombre total de tokens. (label: *"GPE"*)
##### *loc_prop*<a name="loc_prop"></a>
Cette feature comptabilise le nombre d'entités nommées **éléments de localisation naturels** (chaînes de montagnes, étendues d'eau etc.) divisé par le nombre total de tokens. (label: *"LOC"*)
##### *product_prop*<a name="product_prop"></a>
Cette feature comptabilise le nombre d'entités nommées **produits** (objets, véhicules, aliments etc.) divisé par le nombre total de tokens. (label: *"PRODUCT"*)
##### *event_prop*<a name="event_prop"></a>
Cette feature comptabilise le nombre d'entités nommées **événements** (noms d'ouragan, batailles, guerres, événements sportifs etc.) divisé par le nombre total de tokens. (label: *"EVENT"*)

## 6. Features calculées grâce à d'autres ressources NLP<a name="nlp-features"></a>
### 6.1. Le repo NLP<a name="repo-nlp"></a>
Pour calculer d'autres features il a fallu établir de nouvelles ressources qui prennent souvent la forme de dictionnaire. Ces dernières et les scripts pour les générer se trouvent dans le repo [NLP](https://github.com/medialab/nlp) du [médialab](https://github.com/medialab). 
### 6.2. Exceptions noms propres<a name="nom-propres"></a>
Ce fichier texte contient une liste de noms propres français qui sont homonymes avec des mots courants de la langues française. En effet, pour cette feature, on considère comme nom propres les mots capitalisés qui ne sont pas dans le dictionnaire sauf s'ils sont dans cette liste de homonymes.
#### *propernoun_prop*<a name="propernoun_prop"></a>
Cette feature comptabilise le nombre de noms propres divisé par le nombre total de mots.
### 6.3. Dictionnaire français<a name="français"></a>
Ce fichier texte contient la liste de tous les mots du dictionaire français. Cependant, celle-ci est issue du dictionnaire français de linux qui n'est pas exhaustif. Ainsi, il y a plusieurs moyens d'améliorer cette ressource, à partir du wiktionaire par exemple.
#### *dictwords_prop*<a name="dictwords_prop"></a>
Cette feature comptabilise le nombre de mots du dictionaire divisé par le nombre total de mots.
### 6.4. Dictionaire de stopwords<a name="stopwords"></a>
Ce fichier texte contient une liste des [mots vides](https://fr.wikipedia.org/wiki/Mot_vide), ou [stopwords](https://en.wikipedia.org/wiki/Stop_words), français la plus exhaustive possible. 
#### *stopwords_prop*<a name="stopwords_prop"></a>
Cette feature comptabilise le nombre de mots de stop words divisé par le nombre total de mots.
### 6.5. wikitionary.csv<a name="wikitionary"></a>
À partir d'un dump du wiktionaire, le niveau de language de chaque mot du dictionnaire a été extrait. En effet, chaque définition du wiktionaire comporte un tag correspondant au niveau de language du mot. Les mots dont les différentes définitions n'ont pas le même niveau de laguage, comme "baiser", ont été étiqueté d'après le tag de niveau de language qui apparaît le plus souvent dans toutes leurs définitions.
#### *level0_prop*<a name="level0_porp"></a>
Cette feature comptabilise le nombre de mots du registre familier divisé par le nombre de mots total. Les mots sont considérés comme "familier" lorsque leur définition du wiktionaire comporte l'un des tags suivants:
- populaire
- injurieux
- très familier
- vulgaire
- familier
- argot
- verlan

#### *level2_prop*<a name="level2_prop"></a>
Cette feature comptabilise le nombre de mots du registre soutenu divisé par le nombre de mots total. Les mots sont considérés comme "soutenu" lorsque leur définition du wiktionaire comporte l'un des tags suivants:
- littéraire
- poétique
- soutenu

#### *autre_prop*<a name="autre_prop"></a>
Cette feature comptabilise le nombre de mots de registres particuliers divisé par le nombre de mots total. Les mots sont considérés comme issus de registre "particulier" lorsque leur définition du wiktionaire comporte l'un des tags suivants:
- plaisanterie
- ironique
- péjoratif
- euphémisme
- enfantin
- informel

#### *level1_prop*<a name="level1_prop"></a>
Cette feature comptabilise le nombre de mots du registre courant, c'est-à-dire ni familier, ni soutenu, ni de la catégorie "autre", divisé par le nombre de mots total. Les mots sont considérés du registre "courant" lorsque leur définition du wiktionaire ne comporte pas de tag indiquant le niveau de langage.
## 7. Features biais<a name="features-biais"></a>
### 7.1. Explications<a name="explications-biais"></a>
Enfin, les features biais sont des features qui ne dépendent pas du style rédactionnel des articles. Celles-ci servent à vérifier que l'algorithme renvoit effectivement des résultats sur le style rédactionnel donc sur toutes les features sauf celles-ci. En effet, "elles ne servent à rien" dans la mesure où le but est qu'elles ne transparaissent pas dans les résultats finaux. Ainsi, les distributions des lettres *e*, *l*, *a*, *o*, *u*, *i* et *n*, qui sont les lettres les plus récurrentes de la langue française, ont été choisies comme features biais. Effectivement, la distribution de ces lettres ne devrait pas dépendre du style rédactionnel, du moins dans le cadre d'articles de presse.
### 7.2. Méthode de calcul<a name="biais-calcul"></a>
Pour ne pas rendre cette mesure trop dépendante de la longueur des texts, la distribution des lettres n'a été calculée sur seulement les 100 premiers charactères des textes. 

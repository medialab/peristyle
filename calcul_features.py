import statistics
import csv
import json
import re
import nltk
import ural
import spacy
import numpy
import os
from nltk.tokenize import sent_tokenize
from ural import LRUTrie
from statistics import median
from statistics import mean
from statistics import stdev
from collections import defaultdict
from timeit import default_timer as timer
from multiprocessing import Pool


class Timer(object):
    def __init__(self, name="Timer"):
        self.name = name

    def __enter__(self):
        self.start = timer()

    def __exit__(self, *args):
        self.end = timer()
        self.duration = self.end - self.start
        print("%s:" % self.name, self.duration)


with Timer("load nlp"):
    nlp = spacy.load("fr_core_news_sm", disable=["textcat", "parser"])

csv.field_size_limit(100000000)



# =============================================================================
# Features Calculation Script (1)
# =============================================================================
# This script is the first one to run, it calculates all the different features in the stories in the sample file.
# For each article, the scrip returns an array with the numerical result for each features, then those data are used to train an A.I algorithm.
# Below are the features calculated by this script and they are further explained in the documentation:
#       ["ARI", "nb_sent", "nb_word", "nb_char", "mean_cw", "mean_ws", "median_cw", "median_ws", "shortwords_prop" , "longwords_prop" ,"max_len_word", "dictwords_prop", "proper_noun_prop", "negation_prop1", "negation_prop2", "subjectivity_prop1", "subjectivity_prop2", "interpellation_prop1", "interpellation_prop2", "nous_prop1", "nous_prop2", "verb_prop", "past_verb_cardinality", "pres_verb_cardinality", "fut_verb_cardinality", "imp_verb_cardinality", "other_verb_cardinality","past_verb_prop", "pres_verb_prop", "fut_verb_prop","imp_verb_prop", "plur_verb_prop","sing_verb_prop","verbs_diversity", "conditional_prop","question_prop","exclamative_prop","quote_prop","bracket_prop","noun_prop","cconj_prop", "sconj_prop", "pronp_prop", "adj_prop","adv_prop", "a", "e", "i", "l", "n", "o", "sttr", "comma_prop", "numbers_prop", "level0_prop", "level1_prop", "level2_prop", "autre_prop", "ner_prop", "person_prop", "norp_prop", "fac_prop", "org_prop", "gpe_prop", "loc_prop", "product_prop", "event_prop" ]
# In fact, there are a lot of different types of features so to calculate them different tools are used. Mainly it uses Spacy, NLTK and regular expressions.
#
# As the A.I algorithm requires a lot of data to be trained and the tools using maching learning such as Spacy are pretty slow to execute, this scrip is really time demanding.
# To compensate this time problem, this script uses multiprocessing to be faster. With a 4 PCU computer, this script takes almost 2 hours to execute.
#
# => Explanation of the functions:
#
# At the end of the script there are two main functions : add_info() and add_other_stories() :
#
# - add_info() : is the function to run to extract all the features from the articles in the sample file, contains all the operations to do the multiprocessing and writes the result into a csv file (sample_with_features.csv).
#              The multiprocessing iterates through a file containing all the stories id and uses the function calcul_features(path) to calculate the features for each of them.
#              - calcul_features(path) : is the function which call all the other function to calculate the features and returns an array with all the information in it.
#                                        All the subfunctions calculates one proper type of features with one specific tools:
#                                       - clean_from_html(txt) : is a function to clean the text from potential remainder of HTML;
#                                       - pos_tagging(txt) : is the function which used spacy and its pos tagging to calculate the following features : ["dictwords_prop", "proper_noun_prop", "nb_word", "numbers_prop", "pronp_prop", "level0_prop", "level1_prop", "level2_prop", "autre_prop"];
#                                       - calcul_ARI(txt) : this function is mainly dedicated to calculate the ARI. However this readability metrics needs to split the text into sentences and the sentence tokenizer of spacy is really time demanding, that's why it uses NLTK.
#                                                           It calculates the following features : ["ARI", "nb_sent", "nb_char", "mean_cw", "mean_ws", "median_cw", "median_ws", "max_len_word", "shortwords_prop", "longwords_prop"];
#                                       - count_'something'(txt, nb_word, nb_sent) : those functions all have the same model. They use a specific regex to count its occurence in the text.
#                                                           It returns always to versions of the same result, indeed to get a proportion like the others features the regex match result is divided either by the number of sentences or by the number of words in the text.
#                                                           It calculates the following features : ["'something'_prop2", "'something'_prop1"];
#                                       -> for futher explanation for each of these, have a look to the code below.
# - add_other_stories() : is a function to extract the features from stories which are not in the sample file but in the testing stories file. It permits to calculate the features on a story from outside the sample to test the algorithm.
#


#####                   PREPARATION PART                    #####

# --------------------------------------
# REGEX initialization section
# --------------------------------------

# Those regex are used to clean the text to make sure that the NLTK an spacy tokenizer works correctly on text and not HTML for instance.
HTML = re.compile(r"<[^>]*>")
USELESS = re.compile(r"[\"’`\- ]+")
NOT_CHAR = re.compile(r"[.!?,;:\"\-\s\n\r_()\[\]«»’`/\"0-9]+")

# Those regex are used in the calcul_punct function (in the pos_tagging function) to recognize the type of the punctuations found by spacy.
POINT = re.compile(r"[!?.]+")
QUOTE = re.compile(r"[\"«»]")
BRACKET = re.compile(r"[(){}\[\]]")
COMMA = re.compile(r",")

# Those regex are used in the count_'something' functions.
NEGATION = re.compile(r"\bne\b|\bn'\b|\bnon\b", re.I)
SUBJ = re.compile(r"\bje\b|\bma\b|\bme\b|\bmon\b|\bmes\b|\bj'\b|\bm'\b|\bmien\b|\bmienne\b|\bmiens\b|\bmiennes\b", re.I)
INTERPEL = re.compile(r"\btu\b|\bt'\b|\bte\b|\btes\b|\bton\b|\bta\b|\btien\b|\btiens\b|\btienne\b|\btiennes\b|\bvous\b|\bvos\b|\bvotre\b|\bvôtre\b|\bvôtres\b", re.I)
NOUS = re.compile(r"\bnous\b|\bnos\b|\bnotre\b|\bnrôte\b|\bnôtres\b", re.I)

# This function catches the person (the gender, number and person) in a spacy verb tag.
PERSON = re.compile(r"Gender=[A-z]+\||Number=[A-z]+\||Person=.\|")


# --------------------------------------
# Generate DICTIONARIES section
# --------------------------------------
#
# This section generates different kind of dictionaries for different kind of word from the nlp file.
# This allows to calculate how many words of the stories match one of those kinds of words.
#

# Those dictionaries are made from simple word list, so they are made on the same model.

def generate_stopwords():
    with open("../nlp/stopwords_français.txt", "r") as f:
        stopwords = {word.strip() for word in f.readlines()}
    return stopwords

def generate_dictionary():
    with open("../nlp/french.txt", "r") as f:
        dictionary = {word.strip() for word in f.readlines()}
    return dictionary

def generate_proper_noun_exceptions():
    with open("../nlp/propernoun_exceptions.txt", "r") as f:
        propernoun_exceptions = {name.strip() for name in f.readlines()}
    return propernoun_exceptions

# This one is made to detect the langange level of the words, each word of the dictionary are tag either level0, level1 or level2 depending on there language level.
# That creates a dictionary with 3 levels.
def generate_language_level():

    wiktionaire = defaultdict(set)
    with open("../nlp/wikitionary.csv", "r") as f:
        reader = csv.DictReader(f)

        for row in reader:
            language_level = row["language_level"]
            word = row["word"]
            if language_level != "":
                wiktionaire[language_level].add(word)

    return wiktionaire

# This function is to get the language level corresponding to a word and update the language level counter of the story processed.
# It takes 3 arguments:
#               - language_level is a dict used to count how many words of each language level the story contains;
#               - word1 and word2 are the same word but the first one lemmatized and not the second.
# word1 and word2 are tested in the same condition to don't have duplicates and maximize the chance to match correctly the words of the language level dictionary.

def get_language_level(language_level, word1, word2):

    for level in language_level.keys():

        if word1 in LANGUAGE_LEVEL[level] or word2 in LANGUAGE_LEVEL[level]:
            language_level[level] += 1
            return language_level

        else:
            language_level["level1"] += 1
            return language_level

# Declaring the dictionaries as global variable to make them accesible throughout the text.
STOPWORDS = generate_stopwords()
DICTIONARY = generate_dictionary()
LANGUAGE_LEVEL = generate_language_level()
PROPER_NOUN_EXCEPTIONS = generate_proper_noun_exceptions()


# --------------------------------------
# CLEANING functions
# --------------------------------------
#
# These functions are using to clear the text using the regex described in the regex initialisation section.
#
def is_char(word):
    return not bool(NOT_CHAR.search(word))

# This one is to make sure that the NLTK tokenizer works correctly.
def squeeze(txt):

    txt = re.sub(r"[.]+", ".", txt)
    txt = re.sub(USELESS, " ", txt)

    return txt

def clean_from_html(txt):

    txt = re.sub(HTML, " ", txt)
    txt.strip()

    return txt



#####                   FUNCTIONS TO CALCULATES THE FEATURES PART                        #####


# --------------------------------------
# Functions using REGEX
# --------------------------------------
#
# These functions are using te regex explained above to count there corresponding features.
# They are all made on the same model: they call the re.findall() method with there corresponding REGEX.
# They always return two feature results, the first one is the normalization of the findall result by the number of words and the second by the number of sentence
#
def count_interpellation(txt, nb_word, nb_sent) :

    interpellations = re.findall(INTERPEL, txt)

    interpellation_prop1 = 0
    interpellation_prop2 = 0

    if nb_word > 0 and nb_sent > 0:
        interpellation_prop1 = len(interpellations)/nb_word
        interpellation_prop2 = len(interpellations)/nb_sent

    return {"interpellation_prop1":interpellation_prop1, "interpellation_prop2":interpellation_prop2}

def count_nous(txt, nb_word, nb_sent) :

    nous = re.findall(NOUS, txt)

    nous_prop1 = 0
    nous_prop2 = 0
    if nb_word > 0 and nb_sent > 0:
        nous_prop1 = len(nous)/nb_word
        nous_prop2 = len(nous)/nb_sent

    return {"nous_prop1":nous_prop1, "nous_prop2":nous_prop2}

def count_subjectivity(txt, nb_word, nb_sent):

    subjectivities = re.findall(SUBJ, txt)

    subjectivity_prop1 = 0
    subjectivity_prop2 = 0
    if nb_word > 0 and nb_sent > 0:
        subjectivity_prop1 = len(subjectivities)/nb_word
        subjectivity_prop2 = len(subjectivities)/nb_sent

    return {"subjectivity_prop1":subjectivity_prop1, "subjectivity_prop2":subjectivity_prop2}

def count_negation(txt, nb_word, nb_sent):

    negations = re.findall(NEGATION, txt)

    negation_prop1 = 0
    negation_prop2 = 0
    if nb_word > 0 and nb_sent > 0:
        negation_prop1 = len(negations)/nb_word
        negation_prop2 = len(negations)/nb_sent

    return {"negation_prop1":negation_prop1, "negation_prop2":negation_prop2}


# --------------------------------------
# Functions for the POS TAGGING function
# --------------------------------------
#
# At the end of this section, there is the pos_tagging() function wich is the main function using spacy.
# It calculates all the following features : ["nb_word", "dictwords_prop", "proper_noun_prop", "pronp_prop", "numbers_prop", "level0_prop", "level1_prop", "level2_prop", "autre_prop"]
# But also some features more precise such as the different type of punctuation, verbs, pos, ner and the vocabulary diversity (sttr).
# To do this it goes through all the tokens of the text and counts how many words are corresponding to each features.
# Moreover, for the more complicate features, it calls other functions:
#
#           - calcul_verb(verbs, nb_verbs): the pos_tagging function puts all "VERB" tag in a dict (verbs) and this function permits to have a thinner typology of the verbs in the text.
#                      -> calculated features: ["past_verb_cardinality", "pres_verb_cardinality", "fut_verb_cardinality", "imp_verb_cardinality", "other_verb_cardinality", "past_verb_prop", "pres_verb_prop", "fut_verb_prop", "imp_verb_prop", "conditional_prop", "plur_verb_prop", "sing_verb_prop", ["verbs_diversity"]
#           - calcul_punct(punctuations, nb_punct, nb_token): does nearly the same but with the punctuation.
#                      -> calculated features: ["question_prop", "exclamative_prop", "quote_prop", "bracket_prop", "comma_prop"]
#           - calcul_pos(pos_counting, nb_token): same for pos tagging.
#                      -> calculated features: ["noun_prop", "cconj_prop", "sconj_prop", "adj_prop", "verb_prop", "adv_prop"]
#           - calcul_ner(txt, nb_token): same for named entities
#                      -> calculated features: ["ner_prop", "person_prop", "norp_prop", "fac_prop", "org_prop", "gpe_prop", "loc_prop", "product_prop", "event_prop"]
#           - calcul_sttr(voc_mean): calculates the vocabulary diversity.
#



# This function calculates different kinds of verbs proportions in the stories.
# The pos_tagging() function puts all the tag corresponding to a verb token in the verbs dict and this function goes through this list to record the different features.
# Spacy verb tags is a long string containing a lot of information such as the mood, the person (which covers the number, the person and the gender), the tense, the voice, the verb form etc.
#
def calcul_verb(verbs, nb_verb):
    result = {}

    # These are the tenses recorded.
    nb_past_verb = 0
    nb_fut_verb = 0
    nb_pres_verb = 0
    nb_imp_verb = 0
    nb_conditional = 0
    nb_other_verb = 0
    tenses_diversity = set()


    # Those dict will be to count the tenses and persons diversity in all the verbs.
    tenses = defaultdict(set)
    persons = defaultdict(int)


    for verb in verbs:

        if "Plur" in verb:
            persons["plur"] += 1
        elif "Sing" in verb:
            persons["sing"] += 1

        if "Mood=Cnd" in verb:
            nb_conditional += 1

    # To work only with the tense, the verb is striped from it person.
        tense=re.sub(PERSON, "", verb)

        tenses_diversity.add(tense)
        if "Pres" in tense:
            tenses["pres"].add(tense)
            nb_pres_verb += 1
        elif "Past" in tense:
            tenses["past"].add(tense)
            nb_past_verb += 1
        elif "Fut" in tense:
            tenses["fut"].add(tense)
            nb_fut_verb += 1
        elif "Imp" in tense:
            tenses["imp"].add(tense)
            nb_imp_verb += 1
        else:
            tenses["others"].add(tense)
            nb_other_verb += 1

    # Result contains all the new features values and that's what is returned by the function.
    result = {}

    tenses_diversity = len(tenses_diversity)

    if nb_verb>0:

        result["past_verb_cardinality"] = (len(tenses["past"])/tenses_diversity)
        result["pres_verb_cardinality"] = (len(tenses["pres"])/tenses_diversity)
        result["fut_verb_cardinality"] = (len(tenses["fut"])/tenses_diversity)
        result["imp_verb_cardinality"] = (len(tenses["imp"])/tenses_diversity)
        result["other_verb_cardinality"] = (len(tenses["others"])/tenses_diversity)

        result["past_verb_prop"] = (nb_past_verb/nb_verb)
        result["pres_verb_prop"] = (nb_pres_verb/nb_verb)
        result["fut_verb_prop"] = (nb_fut_verb/nb_verb)
        result["imp_verb_prop"] = (nb_imp_verb/nb_verb)

        result["plur_verb_prop"] = (persons["plur"]/nb_verb)
        result["sing_verb_prop"] = (persons["sing"]/nb_verb)

        result["conditional_prop"] = nb_conditional/nb_verb
        result["tenses_diversity"] = (tenses_diversity/nb_verb)


    else:
        result["past_verb_cardinality"] = 0
        result["pres_verb_cardinality"] = 0
        result["fut_verb_cardinality"] = 0
        result["imp_verb_cardinality"] = 0
        result["other_verb_cardinality"] = 0

        result["past_verb_prop"] = 0
        result["pres_verb_prop"] = 0
        result["fut_verb_prop"] = 0
        result["imp_verb_prop"] = 0
        result["conditional_prop"] = 0


        result["plur_verb_prop"] = 0
        result["sing_verb_prop"] = 0

        result["tenses_diversity"] = 0

    return result


# This function calculates different kinds of punctuation proportions in the stories.
# The pos_tagging() function puts all the token tagged 'PUNCT' (punctuation) by spacy in the punctuations dict and this function goes through this list to record the different features.
# The pos_tagging() puts directly the token text in the dict so this function uses regex to recognize the type of each punctuation.
#
def calcul_punct(punctuations, nb_punct, nb_token):

    # These are the punctuation types recorded.
    nb_sent = 0
    nb_quote = 0
    nb_bracket = 0
    nb_comma = 0

    # Iteration through the list to recognize the type of each punctuation.
    for punct in punctuations.keys():
        if POINT.match(punct):
            nb_sent += punctuations[punct]
        elif QUOTE.match(punct):
            nb_quote += punctuations[punct]
        elif BRACKET.match(punct):
            nb_bracket += punctuations[punct]
        elif COMMA.search(punct):
            nb_comma += punctuations[punct]

    # As the quotes and brackets are pair punctuations, their results is devided by 2.
    if nb_quote%2 != 0 or nb_bracket%2 != 0:
        if nb_quote%2 != 0:
            nb_quote += 1
        else:
            nb_bracket += 1
    else:
        nb_quote = nb_quote/2
        nb_bracket = nb_bracket/2

    # Result contains all the new features values and that's what is returned by the function.
    result = {}

    # Initialization of different prop.
    question_prop = 0
    exclamative_prop = 0
    quote_prop = 0
    bracket_prop = 0
    comma_prop = 0

    # Except for comma, all the proportion are normalized by the number of sentences.
    # Even though that's not the finest way to calculate the quote_prop and bracket_prop.
    if nb_sent > 0:
        question_prop = (punctuations["?"]/nb_sent)
        exclamative_prop = (punctuations["!"]/nb_sent)
        quote_prop = (nb_quote/nb_sent)
        bracket_prop = (nb_bracket/nb_sent)
        comma_prop = (nb_comma/nb_token)

    result["question_prop"] = question_prop
    result["exclamative_prop"] = exclamative_prop
    result["quote_prop"] = quote_prop
    result["bracket_prop"] = bracket_prop
    result["comma_prop"] = comma_prop

    return result


# This function calculates different kinds of pos (part of peach) proportions in the stories.
# The pos_tagging() counts all the wanted pos, the counts are in the pos_counting dict.
# All of them is normalized by the number of tokens.
#
def calcul_pos(pos_counting, nb_token):

    # Result contains all the new features values and that's what is returned by the function.
    result={}

    if nb_token>0:
        result["noun_prop"] = pos_counting["NOUN"]/nb_token
        result["cconj_prop"] = pos_counting["CCONJ"]/nb_token
        result["adj_prop"] = pos_counting["ADJ"]/nb_token
        result["sconj_prop"] = pos_counting["SCONJ"]/nb_token
        result["verb_prop"] = (pos_counting["VERB"]+pos_counting["AUX"])/nb_token
        result["adv_prop"] = pos_counting["ADV"]/nb_token
    else:
        result["noun_prop"] = 0
        result["cconj_prop"] = 0
        result["sconj_prop"] = 0
        result["adj_prop"] = 0
        result["verb_prop"] = 0
        result["adv_prop"] = 0

    return result


# This function calculates different kinds of named entities (ner) proportions in the stories.
# The pos_tagging() function puts all the token tagged 'PUNCT' (punctuation) by spacy in the punctuations dict and this function goes through this list to record the different features.
# The pos_tagging() puts directly the token text in the dict so this function uses regex to recognize the type of each punctuation.
#
def calcul_ner(txt, nb_token):

    # txt.ents returns a list of all the named entities in the text.
    nb_entities = len(txt.ents)

    # Initialization if the entities dict needed to count the number of each entity type in the entities list.
    entities = {"PERSON":0,"NORP":0, "FAC":0, "ORG":0, "GPE":0, "LOC":0, "PRODUCT":0, "EVENT":0}

    # Result contains all the new features values and that's what is returned by the function.
    result = {}

    # Iteration through the list to recognize the type of each entity.
    for entity in txt.ents:
        label=entity.label_
        if label in entities.keys():
            entities[label]+=1

    # Each count of entity is divided by the number of tokens.
    result["ner_prop"] = nb_entities/nb_token
    result["person_prop"] = entities["PERSON"]/nb_token
    result["norp_prop"] = entities["NORP"]/nb_token
    result["fac_prop"] = entities["FAC"]/nb_token
    result["org_prop"] = entities["ORG"]/nb_token
    result["gpe_prop"] = entities["GPE"]/nb_token
    result["loc_prop"] = entities["LOC"]/nb_token
    result["product_prop"] = entities["PRODUCT"]/nb_token
    result["event_prop"] = entities["EVENT"]/nb_token

    return result


# This function calculates vocabulary diversity in the stories.
# While the pos_tagging() function goes through all the token, it counts the vocabulary diversity in every 100 words.
# This function calculates the mean of those vocabulary diversity to get the vocabulary diversity of the complete text
#
def calcul_sttr(voc_mean):

    sttr=0
    if voc_mean!=[]:
        sttr=sum(voc_mean)/len(voc_mean)

    return {"sttr":sttr}


###         pos_tagging funtcion            ###
# This function is the main one of this section and calls all the others above.
# It calculates the features which need of spacy by going through the tokens and counting each tag.
# Moreover it uses all the dictionaries to identifie the tokens.
#
def pos_tagging(txt): #calcule certaines features en utilisant le pos tagging : temps (cardinalité temps), pos, punct, negation(marche pas top)

    # Tokenize the text with spacy.
    txt = str(txt)
    with Timer("nlp"):
        txt = nlp(txt)

    #
    # Counters initialization.
    #
    # Counters for features using directly the spacy results.
    nb_word = 0
    nb_numbers = 0
    nb_pronp = 0
    nb_propernoun = 0

    # Counters for features calling the nlp dictionaries.
    nb_dictwords = 0
    language_level = {"level0":0, "level1":0, "level2":0, "autre":0}

    # Counters for features which need a futher treatment with another function (above).
    pos_counting = defaultdict(int)
    punctuations = defaultdict(int)
    verbs = []

    # Counters for the vocabulary diversity (sttr) feature (futher explanations in the documentation).
    voc_counter = 0   # Counts every 100 words range.
    voc_mean = []     # Records the vocabulary diversity for each 100 words range.
    voc = set()       # Records all the different word in a 100 words range.

    # Iteration through the tokens.
    # With spacy each token has several attributes:
    #               - token.lemma_ : lematized token
    #               - token.pos_ : token's pos name
    #               - token.text : token's text
    #               - token.tag_ : token's tag (contains futher information then just the pos name)
    #
    for token in txt:

        # Update the pos counters with the pos name of the actual token.
        pos_counting[token.pos_] += 1

        # Update the language level counters with the language level of the actual token.
        language_level = get_language_level(language_level, token.lemma_, token.text)


        if "PUNCT" not in token.pos_ and "SPACE" not in token.pos_:
            nb_word += 1

            if token.text.istitle():

                # If the word is capitalized and not in the dictionary then is porper noun.
                if token.lemma_.lower() not in DICTIONARY and token.text.lower() not in DICTIONARY or token.text in PROPER_NOUN_EXCEPTIONS:
                    nb_propernoun += 1

            # Update the counters for the voc diversity feature.
            if token.lemma_.lower() in DICTIONARY or token.text.lower() in DICTIONARY:
                voc_counter += 1
                voc.add(token.text)
                nb_dictwords += 1

        # If it reached the 100 words.
        # Update the voc_mean counter (different words divided by 100 for the passed 100 words range).
        # Clear the others counters.
        if voc_counter == 100:
            voc_mean.append((len(voc)/voc_counter))
            voc.clear()
            voc_counter = 0

        if "PUNCT" in token.pos_:
            punctuations[token.text] += 1

        elif "NUM" in token.pos_:
            nb_numbers += 1

        elif "VERB" in token.pos_ or "AUX" in token.pos_:
           verbs.append(token.tag_)

        elif "PRON" in token.pos_ and "PronType=Prs" in token.tag_:
            nb_pronp += 1

    # Other functions calling for thinner information
    punctuation_results = calcul_punct(punctuations, pos_counting["PUNCT"], len(txt))
    verbs_results = calcul_verb(verbs, pos_counting["VERB"] + pos_counting["AUX"])
    pos_results = calcul_pos(pos_counting,len(txt))
    ner_results = calcul_ner(txt, len(txt))
    sttr = calcul_sttr(voc_mean)

    # Result contains all the new features values and that's what is returned by the function.
    results = {}

    results.update(punctuation_results)
    results.update(verbs_results)
    results.update(pos_results)
    results.update(ner_results)
    results.update(sttr)

    results["nb_word"] = nb_word
    results["dictwords_prop"] = nb_dictwords/nb_word
    results["proper_noun_prop"] = nb_propernoun/nb_word
    results["pronp_prop"] = nb_pronp/len(txt)
    results["numbers_prop"] = nb_numbers/len(txt)
    results["level0_prop"] = language_level["level0"]/nb_word
    results["level1_prop"] = language_level["level1"]/nb_word
    results["level2_prop"] = language_level["level2"]/nb_word
    results["autre_prop"] = language_level["autre"]/nb_word

    return results



# --------------------------------------
# Functions for the CALCUL_ARI function
# --------------------------------------
#
# ARI is a readability metric which needs the number of sentences to be computed. However, spacy's sentence tokenizer is really slow. That's why this second function using NLTK is needed.
# This function returns results for the folowing features: ["nb_sent", "nb_char", "mean_cw", "mean_ws", "median_cw", "median_ws", "max_len_word", "shortwords_prop", "longwords_prop"]
#bias
# Moreover, it also computes the proportions of some letters in the stories. These proportions are biases: if the algorithm finds a result on these, then that would be a sign of a default in te computation.
# The function count_letters(letters, word) is used to compute them.
#

# This function calculates the biais.
# For that a letters dict is updated at each word to count the number "e", "l", "o", "a", "i" and "n".
#
def count_letters(letters, word):
    elaouin=["e","l","o","a","i","n"]

    for char in word:
        char=char.lower()

        if char in elaouin:
            letters[char]+=1

    return letters



###         calcul_ARI funtcion            ###
# This function is the main one of this section and calls all the others above.
# It calculates the features which need of spacy by going through the tokens and counting each tag.
# Moreover it uses all the dictionaries to identifie the tokens.
#
def calcul_ARI(txt):

    # To ensure tht the word tokenizer and the sentence tokenizer work correctly.
    txt=squeeze(txt)

    # Sentence tokenize the entire text.
    # Then word tokenize each sentence.
    # That way, the txt variable contains a list of sentences which are themselves a list of words.
    sentences=nltk.tokenize.sent_tokenize(txt, language="french")
    txt=[nltk.word_tokenize(sentence) for sentence in sentences]

    # Counter initialization
    ARI = 0.0
    nb_char = 0
    nb_word = 0
    nb_sentence = 0
    nb_shortwords = 0
    nb_longwords = 0
    nb_stopwords = 0
    letters = {"e":0, "l":0, "o":0, "a":0, "i":0, "n":0}


    # cw --> char per word
    # ws --> word per sentence
    # Those are for the calculation of mean_cw, median_cw, mean_ws and median_ws.
    nb_cw = []
    nb_ws = []

    # Iteration through the sentences.
    for sentence in txt:

        # The sentence is considered only if its lengh isn't absurd (if it has between 3 and 300 words)
        if len(sentence) > 3 and len(sentence) < 300:
            nb_sentence += 1

            # In each sentence iteration through the words
            for word in sentence:
                nb_ws.append(len(sentence))

                # The word is considered only if its lengh isn't absurd (if it has less ten 50 characters) and if it is made of characters
                if is_char(word) and len(word) < 50:
                    word = word.lower()
                    nb_word += 1
                    nb_char += len(word)
                    nb_cw.append(len(word))

                    if nb_char < 100:
                        letters = count_letters(letters, word)

                    if len(word) < 5:
                        nb_shortwords += 1

                    if len(word) > 5:
                        nb_longwords += 1

                    if word in STOPWORDS:
                        nb_stopwords += 1


    # Results initialization.
    max_len_word = 0
    shortwords_prop = 0
    longwords_prop = 0
    median_cw = 0
    median_ws = 0
    mean_cw = 0
    mean_ws = 0

    # Stories with less then 3 sentences are not considered because they're must be paywalled or not stylistically interesting.
    if nb_word>0 and nb_sentence>3:

        mean_cw=nb_char/nb_word
        mean_ws=nb_word/nb_sentence

        median_cw=median(nb_cw)
        median_ws=median(nb_ws)

        shortwords_prop=(nb_shortwords/nb_word)
        longwords_prop=(nb_longwords/nb_word)

        max_len_word=max(nb_cw)

        #### ARI formula ####
        ARI=4.71*(mean_cw)+0.5*(mean_ws)-21.43

        # If the ARI has an absurd result that means the text isn't correctly written
        if ARI<0 or 30<ARI:
            ARI=0

    # Result contains all the new features values and that's what is returned by the function.
    result={}

    result["ARI"] = ARI
    result["nb_sent"] = nb_sentence
    result["nb_char"] = nb_char
    result["mean_cw"] = mean_cw
    result["mean_ws"] = mean_ws
    result["median_cw"] = median_cw
    result["median_ws"] = median_ws
    result["max_len_word"] = max_len_word
    result["shortwords_prop"] = shortwords_prop
    result["longwords_prop"] = longwords_prop

    result.update({"a":letters["a"], "e":letters["e"], "l":letters["l"], "o":letters["o"], "i":letters["i"], "n":letters["n"]})

    return result


# --------------------------------------
# Functions CALCUL_FEATURES
# --------------------------------------
#
# This is the function of this script which gather all the computation functions above.
# It takes the path to the story as an argument and returns an array with all the features values.
#

def calcul_features(path):

    row=path[1]
    results={key:row[key] for key in row.keys()}


    # It has to use thise try beacause some stories weren't import correctly from the data base to the sample file, but their ID remained in the fil with all the ids.
    # This represent approximately 10% of the 100 000 stories initialy imported.
    try:
        with open (path[0],"r") as ft:
            txt=ft.read()

    except:
        print("opening failed")
        return False

    # Result contains all the new features values and that's what is returned by the function.
    results={}

    txt=clean_from_html(txt)

    # Calling others functions (seen above)
    results.update(pos_tagging(txt))
    results.update(calcul_ARI(txt))
    results.update(count_negation(txt,results["nb_word"], results["nb_sent"]))
    results.update(count_interpellation(txt, results["nb_word"], results["nb_sent"]))
    results.update(count_nous(txt, results["nb_word"], results["nb_sent"]))
    results.update(count_subjectivity(txt, results["nb_word"],  results["nb_sent"]))

    return results




# --------------------------------------
# Functions for the MULTIPROCESSING and WRITE the results into a new file
# --------------------------------------
#
# The multiprocessing is a way to optimize the script's execution time while using several processors at the same time, 4 in this case but can be more with a computer with better capacity.
# As source file it uses the sample_normalized_sorted.csv file and the results are written in the sample_with_features.csv file.
#

def generate_path(row):
    story_id = row["stories_id"]
    return "sample/" + story_id + ".txt"


def generator():
    fs = open("tables/sample_normalized_sorted.csv", "r")
    reader = csv.DictReader(fs)

    for row in reader:
        print(row["stories_id"])
        yield (generate_path(row), row)


# This is the main function of this script and the one to run to re-compute all the features values.
def add_info():

    with open("tables/sample_normalized_sorted.csv", "r") as fs:
        reader = csv.DictReader(fs)
        # Seting the writer fieldnames to the reader fieldnames plus the features computed in the script.
        fieldnames = reader.fieldnames + ["ARI", "nb_sent", "nb_word", "nb_char", "mean_cw", "mean_ws", "median_cw", "median_ws", "shortwords_prop" , "longwords_prop" ,"max_len_word", "dictwords_prop", "proper_noun_prop", "negation_prop1", "negation_prop2", "subjectivity_prop1", "subjectivity_prop2", "interpellation_prop1", "interpellation_prop2", "nous_prop1", "nous_prop2", "verb_prop", "past_verb_cardinality", "pres_verb_cardinality", "fut_verb_cardinality", "imp_verb_cardinality", "other_verb_cardinality","past_verb_prop", "pres_verb_prop", "fut_verb_prop","imp_verb_prop", "plur_verb_prop","sing_verb_prop","tenses_diversity", "conditional_prop","question_prop","exclamative_prop","quote_prop","bracket_prop","noun_prop","cconj_prop", "sconj_prop", "pronp_prop", "adj_prop","adv_prop", "a", "e", "i", "l", "n", "o", "sttr", "comma_prop", "numbers_prop", "level0_prop", "level1_prop", "level2_prop", "autre_prop", "ner_prop", "person_prop", "norp_prop", "fac_prop", "org_prop", "gpe_prop", "loc_prop", "product_prop", "event_prop" ]

    fd = open("tables/sample_with_features.csv", "w")
    writer = csv.DictWriter(fd, fieldnames = fieldnames)
    writer.writeheader()

    with Timer("multiprocessing"):
        with Pool(4) as pool:
            for features in pool.imap_unordered(calcul_features, generator()):
                if features != {}:
                    writer.writerow(features)

    fd.close()

    return 0


# --------------------------------------
# EXTRA FUNCTIONS to compute the script but on other testing stories.
# --------------------------------------
#
# The functions of this section are quite similar to the ones of the previous section.
# In fact they are doing the same thing execpt that the functions from this section computes the features for other stories, that we'll call "testing stories".
# Those stories will be used to check if the stylistic measurement algorithm is reliable, while running the algorithm on the values of the features of the testing stories and then see if the outputs are coherent.

# This function is really similar to the calcul_features() function except that it creates the path to the story itself.
# Moreover, those paths are different from the paths for the stories of the sample. Indeed, those testing stories are stored in the subfile testing_stories.
#
def calcul_features_id(story):

    with open ("testing_stories/sample/" + story,"r") as ft:
        txt = ft.read()

    results={}
    txt=clean_from_html(txt)
    results.update(pos_tagging(txt))
    results.update(calcul_ARI(txt))
    results.update(count_negation(txt,results["nb_word"], results["nb_sent"]))
    results.update(count_interpellation(txt, results["nb_word"], results["nb_sent"]))
    results.update(count_nous(txt, results["nb_word"], results["nb_sent"]))
    results.update(count_subjectivity(txt, results["nb_word"],  results["nb_sent"]))
    return results




# This function is really similar to the add_info() function except that it has an extra condition.
# This condition is to filter those testing stories. The sample stories are filtered with those same conditions after the features values calculation but in another sctipt.
#
def add_other_stories():
    fd = open("testing_stories/testing_stories_features.csv", "w")

    fieldnames = ["story" ,"ARI", "nb_sent", "nb_word", "nb_char", "mean_cw", "mean_ws", "median_cw", "median_ws", "shortwords_prop" , "longwords_prop" ,"max_len_word", "dictwords_prop", "proper_noun_prop", "negation_prop1", "negation_prop2", "subjectivity_prop1", "subjectivity_prop2", "interpellation_prop1", "interpellation_prop2", "nous_prop1", "nous_prop2", "verb_prop", "past_verb_cardinality", "pres_verb_cardinality", "fut_verb_cardinality", "imp_verb_cardinality", "other_verb_cardinality","past_verb_prop", "pres_verb_prop", "fut_verb_prop","imp_verb_prop", "plur_verb_prop","sing_verb_prop","tenses_diversity", "conditional_prop","question_prop","exclamative_prop","quote_prop","bracket_prop","noun_prop","cconj_prop", "sconj_prop", "pronp_prop", "adj_prop","adv_prop", "a", "e", "i", "l", "n", "o", "sttr", "comma_prop", "numbers_prop", "level0_prop", "level1_prop", "level2_prop", "autre_prop", "ner_prop", "person_prop", "norp_prop", "fac_prop", "org_prop", "gpe_prop", "loc_prop", "product_prop", "event_prop" ]
    writer = csv.DictWriter(fd, fieldnames = fieldnames)
    writer.writeheader()

    for story in os.listdir('./testing_stories/sample'):
        print(story)

        result = calcul_features_id(story)
        result["story"] = story[:-4]

        # A story is considered only of the ARI result isn't absurd (between 0 and 30), if the story has enought words ads sentences (more then 250 sentences and more then 3 sentences), but not too many words (less then 1500 words).
        if result["ARI"] <30 and 0<result["ARI"] and result["nb_word"] != 0 and result["nb_sent"] <= 3 and result["nb_word"]>250 and 1500>result["nb_word"]:
            writer.writerow(result)

    fd.close()
    return 0


add_info()
#add_other_stories()

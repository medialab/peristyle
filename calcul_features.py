import statistics
import csv
import json
import re
import nltk
import ural
import spacy
from nltk.tokenize import sent_tokenize
from ural import LRUTrie
from statistics import median
from collections import defaultdict
from timeit import default_timer as timer


HTML=re.compile(r'<[^>]*>')
VIDE=re.compile(r'[\s\n\t\r]+')
USELESS=re.compile(r'[\'’`\- ]+')


POINT=re.compile(r'[!?.]+')
PUNCT=re.compile(r'[!?,;:_()\[\]«»—"]|[.]+')
NOT_CHAR=re.compile(r'[.!?,;:\'\-\s\n\r_()\[\]«»’`/"0-9]+')
NEGATION=re.compile(r' ne | n[^A-z]| non ')
SUB=re.compile(r'')
QUOTE=re.compile(r'[\'"’`«»]')
BRACKET=re.compile(r'[(){}\[\]]')

PERSON=re.compile(r'Gender=[A-z]+\||Number=[A-z]+\||Person=*\|')

csv.field_size_limit(100000000)


class Timer(object):
    def __init__(self, name='Timer'):
        self.name = name

    def __enter__(self):
        self.start = timer()

    def __exit__(self, *args):
        self.end = timer()
        self.duration = self.end - self.start
        print('%s:' % self.name, self.duration)


def is_char(word):
    return not bool(NOT_CHAR.match(word))




def squeeze(txt): #pour être sur que le sent tokenizer de nltk marche bien
    txt=re.sub(r'[.]+', '.', txt)
    txt=re.sub(USELESS, ' ', txt)
    return txt

def clean(txt):
    txt=re.sub(HTML, ' ', txt)
    txt=re.sub(VIDE, ' ', txt)
    return txt



def generate_sources():

    f2=open('sources.csv', 'r')
    sources=csv.DictReader(f2)

    sources_list=[]

    for row in sources:
        source={'url': row['url'],
                'name':row['name'],
                'id':row['id'],
                'politics':row['politics'],
                'level0':row['level0_title'],
                'level1':row['level1_title'],
                'level2':row['level2_title'],
                'webentity':row['webentity']}
        sources_list.append(source)

    f2.close()

    return sources_list

def generate_stopwords():

    with open ('stopwords_français.txt', 'r') as f:
        stopwords=f.readlines()

    for i in range (0,len(stopwords)):
        stopwords[i]=stopwords[i].strip()

    return stopwords


def generate_dictionary():

    with open ('french.txt', 'r') as f:
        dictionary=f.readlines()

    for i in range (0,len(dictionary)):
        dictionary[i]=dictionary[i].strip()

    return dictionary


#def generate_linkingwords():



def calcul_verb(verbs, nb_verbs):
    result={}

    nb_past_verbs=0
    nb_fut_verbs=0
    nb_pres_verbs=0
    nb_imp_verbs=0
    nb_other_verbs=0

    tenses=defaultdict(set)
    persons=defaultdict(int)

    for verb in verbs:

        if 'Plur' in verb:
            persons['plur']+=1
        elif 'Sing' in verb:
            persons['sing']+=1

        tens=re.sub(PERSON, '', verb)
        if 'Pres' in tens:
            tenses['pres'].add(tens)
            nb_pres_verbs+=1
        elif 'Past' in tens:
            tenses['past'].add(tens)
            nb_past_verbs+=1
        elif 'Fut' in tens:
            tenses['fut'].add(tens)
            nb_fut_verbs+=1
        elif 'Imp' in tens:
            tenses['imp'].add(tens)
            nb_imp_verbs+=1
        else:
            tenses['others'].add(tens)
            nb_other_verbs+=1


    verbs_diversity=0
    for tens in tenses:
        verbs_diversity+=len(tens)


    result={}

    result['past_verb_cardinality']=(len(tenses['past'])/verbs_diversity)*100
    result['pres_verb_cardinality']=(len(tenses['pres'])/verbs_diversity)*100
    result['fut_verb_cardinality']=(len(tenses['fut'])/verbs_diversity)*100
    result['imp_verb_cardinality']=(len(tenses['imp'])/verbs_diversity)*100
    result['other_verb_cardinality']=(len(tenses['others'])/verbs_diversity)*100

    result['past_verb_prop']=(nb_past_verbs/nb_verbs)*100
    result['pres_verb_prop']=(nb_pres_verbs/nb_verbs)*100
    result['fut_verb_prop']=(nb_fut_verbs/nb_verbs)*100
    result['imp_verb_prop']=(nb_imp_verbs/nb_verbs)*100

    result['plur_verb_prop']=(persons['plur']/nb_verbs)*100
    result['sing_verb_prop']=(persons['sing']/nb_verbs)*100

    result['verbs_diversity']=(verbs_diversity/nb_verbs)*100

    return result

def calcul_punct(punctuations, nb_puncts):

    punctuation_diversity=len(punctuations)
    nb_sent=0
    nb_quote=0
    nb_braket=0

    result={}

    for punct in punctuations.keys():
        if POINT.match(punct):
            nb_sent+=1
        elif QUOTE.match(punct):#je compare ça à quoi?
            nb_quote+=1
        elif BRACKET.match(punct):
            nb_braket+=1


    result['question_prop']=(punctuations['?']/nb_sent)*100
    result['exclamative_prop']=(punctuations['!']/nb_sent)*100

    return result

def calcul_pos(pos_counting, nb_tokens):
    result={}

    result['noun_prop']=(pos_counting['NOUN']/nb_tokens)*100
    result['cconj_prop']=(pos_counting['CCONJ']/nb_tokens)*100
    result['adj_prop']=(pos_counting['ADJ']/nb_tokens)*100
    result['verb_prop']=((pos_counting['VERB']+pos_counting['AUX'])/nb_tokens)*100
    result['adv_prop']=(pos_counting['ADV']/nb_tokens)*100

    return result

#def calcul_ner(entities):



def pos_tagging(txt): #calcule certaines features en utilisant le pos tagging : temps (cardinalité temps), pos, punct, negation(marche pas top)

    with Timer('nlp'):
        nlp = spacy.load('fr_core_news_sm', disable=['textcat', 'parser'])
        txt=str(txt)
        txt = nlp(txt)

    pos_counting=defaultdict(int)
    negation=defaultdict(int)
    punctuations=defaultdict(int)
    verbs=[]
    entities=defaultdict(set)
    nb_word=0
    nb_char=0

    for token in txt:
        pos_counting[token.pos_]+=1

        if 'PUNCT' in token.pos_:
            punctuations[token.text]+=1
        elif 'VERB' in token.pos_ or 'AUX' in token.pos_:
           verbs.append(token.tag_)

    for ent in txt.ents:
        entities[ent.label_].add(ent.text)

    verbs_results=calcul_verb(verbs, pos_counting['VERB']+pos_counting['AUX'])
    punctuation_results=calcul_punct(punctuations, pos_counting['PUNCT'])
    pos_results=calcul_pos(pos_counting,len(txt))
    #ner_results=calcul_ner(entities)
    results={}

    results.update(verbs_results)
    results.update(punctuation_results)
    results.update(pos_results)
    #results.update(ner_results)
    return results


def count_negation(txt): #semble mieux marcher que le pos tagging
    negations=re.findall(NEGATION, txt)
    return {'nb_negation':len(negations)}

def tokenize(txt):

    txt=squeeze(txt)
    sentences=nltk.tokenize.sent_tokenize(txt, language='french')

    for i in range(0, len(sentences)):
        sentences[i]=nltk.word_tokenize(sentences[i])

    return(sentences)

def count_letters(nb_letters, word):

    for char in word:
        if is_char(char):
            nb_letters[char]+=1
    return nb_letters

def calcul_letters(letters, nb_char): #calcul la moyenne d'apparition d'une lettre dans le txt

    mean_occ_letter=0

    for nb_occ_letter in letters.values():
        mean_occ_letter+=nb_occ_letter

    mean_occ_letter=mean_occ_letter/31
    median_occ_letter=median(letters.values())



    return {
            'letters':letters,
            'mean_occ_letter':mean_occ_letter,
            'median_occ_letter':median_occ_letter
            }



def calcul_ARI(txt, stopwords, dictionary): #on pourrait faire tout dans l'un à condition d'abandonner la médiane du nb de mots par phrase

    txt=tokenize(txt)

    ARI=0.0
    nb_word=0
    nb_char=0
    nb_sentence=0
    TYPE=''
    nb_shortwords=0
    nb_stopwords=0
    letters=defaultdict(int)
    voc=defaultdict(int)
    nb_dictwords=0

    nb_cw=[] # cw => char per word
    nb_ws=[] # ws => word per sent

    for sentence in txt:

        if len(sentence)>3 and len(sentence)<300:
            nb_sentence+=1

            for word in sentence:

                if is_char(word):

                    if len(word)<300:
                        word=word.lower()
                        voc[word]+=1
                        letters=count_letters(letters, word)
                        nb_word+=1
                        nb_char+=len(word)
                        nb_cw.append(len(word))

                    if len(word)<5:
                        nb_shortwords+=1
                    if word in stopwords:
                        nb_stopwords+=1
                    if word in dictionary:
                        nb_dictwords+=1

            nb_ws.append(len(sentence))


    results_letters=calcul_letters(letters, nb_char)

    mean_cw=nb_char/nb_word
    mean_ws=nb_word/nb_sentence

    median_cw=median(nb_cw)
    median_ws=median(nb_ws)

    prop_shortword=(nb_shortwords/nb_word)*100
    prop_dictwords=(nb_dictwords/nb_word)*100

    if nb_sentence>3:
        ARI=4.71*(mean_cw)+0.5*(mean_ws)-21.43


    if 0<ARI<30:
        result={
            'ARI':ARI ,
            'nb_sent':nb_sentence,
            'nb_word':nb_word,
            'nb_char':nb_char,
            'mean_cw':mean_cw,
            'mean_ws':mean_ws,
            'median_cw':median_cw,
            'median_ws':median_ws,
            'nb_shortwords':nb_shortwords,
            'prop_shortwords':prop_shortword,
            'prop_dictwords':prop_dictwords,
            'voc cardinality':(len(voc)/nb_word)*100
            }
        result.update(results_letters)
        return result
    else:
        return False



def calcul_features(txt):
    results={}
    stopwords=generate_stopwords()
    dictionary=generate_dictionary()
    results.update(pos_tagging(txt))
    results.update(calcul_ARI(txt, stopwords, dictionary))
    results.update(count_negation(txt))
    return results


##### Fonction pour calculer les nouvelles features sur tous les textes et les enregistrées

def find_media_info(sources, media_id, info='level0'):

    for source in sources:
        if source['id']==media_id:
            return source

    return False

def produce_data():

    f_sample=open('sample_with_features.csv', 'r')
    samples=csv.DictReader(f_sample)

    sources=generate_sources()
    data={"values":[]}

    for row in samples:

        info=find_media_info(sources, row['media_id'])
        value={}

        if "" not in info:
            for key in row.keys():
                value[key]=row[key]
            for key in info.keys():
                value[key]=info[key]
            data['values'].append(value)

    f_sample.close()

    return data

def ajout_info():

    fs=open('sample_normalized_sorted.csv', 'r')
    reader=csv.DictReader(fs)
    reader.fieldnames+=['ARI', 'nb_sent', 'nb_word', 'nb_char', '']#ajouter les nouveaux features

    fd=open('sample_with_features.csv', 'w')
    writer=csv.DictWriter(fd, fieldnames=reader.fieldnames)
    writer.writeheader()

    i=0
    for row in reader:

        i+=1
        story_id=row['stories_id']
        txt_name='sample/'+story_id+'.txt'

        try:
            with open (txt_name,'r') as ft:
                txt=ft.readline()

        except:
            continue

        '''
        là il faut utiliser toutes les fonctions dans le bon ordre
        à la fois nltk et spacy pour ne pas utiliser spacy parser
        très long...
        '''

        for key in results.keys():
            row[key]=results_ARI[key]

        writer.writerow(row)
        print(story_id, i)

    fd.close()
    fs.close()

    return 0



##### ESSAIE SUR UN TEXT #####

with open ('sample/837192958.txt','r') as ft:
    txt=ft.readline()


txt=clean(txt)

#print(count_punctuation(txt))
#print(count_negation(txt))

with Timer('calcul_features'):
    features=calcul_features(txt)


for feature in features.keys():
    print(feature, features[feature])
    print('')

#print(calcul_ARI(txt))

print(txt)



import statistics
import numpy
import math
import json
import csv

from math import exp

from multiprocessing import Pool
from collections import defaultdict
from timeit import default_timer as timer

from statistics import median
from statistics import stdev
from statistics import mean


features=['ARI', 'nb_sent', 'nb_word', 'nb_char', 'mean_cw', 'mean_ws', 'median_cw', 'median_ws', 'shortwords_prop' , 'longwords_prop' ,'max_len_word', 'dictwords_prop', 'negation_prop1', 'negation_prop2', 'subjectivity_prop1', 'subjectivity_prop2', 'verb_prop', 'past_verb_cardinality', 'pres_verb_cardinality', 'fut_verb_cardinality', 'imp_verb_cardinality', 'other_verb_cardinality','past_verb_prop', 'pres_verb_prop', 'fut_verb_prop','imp_verb_prop', 'plur_verb_prop','sing_verb_prop','verbs_diversity', 'conditional_prop','question_prop','exclamative_prop','quote_prop','bracket_prop','noun_prop','cconj_prop', 'sconj_prop', 'pronp_prop', 'adj_prop','adv_prop', 'a', 'e', 'i', 'l', 'n', 'o', 'sttr', 'comma_prop', 'numbers_prop', "level0_prop", "level2_prop", "autre_prop" ]

media_infos=["name","id","politics", "edito", "specialization","digital_native", "level0", "level1", "level2", "level3", "level0_title", "level1_title", "level2_title", "level3_title"]

with open("sources.csv", "r") as f:
    sources=csv.DictReader(f)
    SOURCES=[{key:row[key] for key in media_infos} for row in sources]


def find_media_source(media_id):
    for source in SOURCES:
        if source["id"]==media_id:
            return source
    return False


fs=open("sample_filtered_with_features.csv")
sample=csv.DictReader(fs)

medias=defaultdict(lambda: defaultdict(list)) #media>feature>values list
count_stories=defaultdict(int)
count_stories_total=defaultdict(int)


for row in sample:
    if row["filter"]=="False":
        count_stories[row["media_id"]]+=1
        for feature in features:
            medias[row["media_id"]][feature].append(float(row[feature]))

print(medias)

fd=open("media_with_mean_features.csv", "w")
fieldnames=["nb_stories"]+media_infos+features
writer=csv.DictWriter(fd, fieldnames=fieldnames)
writer.writeheader()

for media_id in medias.keys():
    row=find_media_source(media_id)
    row["nb_stories"]=count_stories[media_id]
    for feature in features:
        row[feature]=mean(medias[media_id][feature])
    writer.writerow(row)
fd.close()


with open('media_with_mean_features.csv', 'r') as f_sample:
    sample=csv.DictReader(f_sample)
    values=[]
    for row in sample:
        value={key:row[key] for key in row.keys()}
        values.append(value)

with open('media_mean_features_data.json','w') as f:
    json.dump(values, f, indent=2, ensure_ascii=False)


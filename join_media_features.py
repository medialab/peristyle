import statistics
import numpy as np
import math
import json
import csv

from sklearn.preprocessing import scale

from collections import defaultdict
from timeit import default_timer as timer

from statistics import median, stdev, mean


FEATURES_NAMES=["ARI", "nb_sent", "nb_word", "nb_char", "mean_cw", "mean_ws", "shortwords_prop" , "longwords_prop" ,"max_len_word", "dictwords_prop", "proper_noun_prop", "negation_prop1", "negation_prop2", "subjectivity_prop1", "subjectivity_prop2","interpellation_prop1", "interpellation_prop2", "nous_prop1","nous_prop2", "verb_prop", "past_verb_cardinality", "pres_verb_cardinality", "fut_verb_cardinality", "imp_verb_cardinality", "other_verb_cardinality","past_verb_prop", "pres_verb_prop", "fut_verb_prop","imp_verb_prop", "plur_verb_prop","sing_verb_prop","verbs_diversity", "conditional_prop","question_prop","exclamative_prop","quote_prop","bracket_prop","noun_prop","cconj_prop", "sconj_prop", "pronp_prop", "adj_prop","adv_prop", "a", "e", "i", "l", "n", "o", "sttr", "comma_prop", "numbers_prop", "level0_prop", "level1_prop", "level2_prop", "autre_prop", "ner_prop", "person_prop", "norp_prop", "fac_prop", "org_prop", "gpe_prop", "loc_prop", "product_prop", "event_prop" ]
media_infos=["name","id","politics", "edito", "specialization","digital_native", "level0", "level1", "level2", "level3", "level0_title", "level1_title", "level2_title", "level3_title"]


with open("tables/sources.csv", "r") as f:
    sources=csv.DictReader(f)
    SOURCES=[{key:row[key] for key in media_infos} for row in sources]

def find_media_source(media_id):
    for source in SOURCES:
        if source["id"]==media_id:
            return source
    return False


f=open("tables/sample_filtered_with_features.csv", "r", encoding="latin1")
sample=csv.DictReader(f)
matrix_stories=[]

for row in sample:
    if row["filter"]=="False":
        sample=(row["stories_id"], row["media_id"], row["url"])
        for feature in FEATURES_NAMES:
            try:
                row[feature]=float(row[feature])
            except:
                row[feature]=0
            sample+=(row[feature],)
        if sample:
            matrix_stories.append(sample)
matrix_stories = np.array(matrix_stories)
f.close()


stories_id=matrix_stories[:,0]
medias_id=matrix_stories[:,1]
urls=matrix_stories[:,2]
stories_features=scale(matrix_stories[:,3:])


medias=defaultdict(lambda: defaultdict(list)) #media>feature>values list
count_stories = defaultdict(int)
count_stories_total = defaultdict(int)


stories=[]

for i in range(stories_features.shape[0]):
    story={"story_id":stories_id[i], "media_id":medias_id[i], "url":urls[i]}
    count_stories[medias_id[i]]+=1
    for j, feature in enumerate(FEATURES_NAMES):
        story[feature]=stories_features[i, j]
        medias[medias_id[i]][feature].append(story[feature])
    stories.append(story)


fd=open("tables/media_with_mean_features.csv", "w")
fieldnames=["nb_stories"]+media_infos+FEATURES_NAMES
writer=csv.DictWriter(fd, fieldnames=fieldnames)
writer.writeheader()

values=[]
for media_id in medias.keys():
    media=find_media_source(media_id)
    media["nb_stories"]=count_stories[media_id]
    for feature in FEATURES_NAMES:
        media[feature]=mean(medias[media_id][feature])
    values.append(media)
    writer.writerow(media)


with open("visualization/data/media_mean_features_data.json", "w") as f:
    json.dump(medias, f, indent=2, ensure_ascii=False)
fd.close()
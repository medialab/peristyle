import numpy as np
from sklearn.manifold import TSNE
from collections import defaultdict

import hdbscan
import json
import csv

FEATURES_NAMES = ["ARI", "nb_sent", "nb_word", "nb_char", "mean_cw", "mean_ws", "shortwords_prop" , "longwords_prop" , "dictwords_prop", "proper_noun_prop", "negation_prop1", "subjectivity_prop1", "verb_prop","past_verb_prop", "pres_verb_prop", "fut_verb_prop","imp_verb_prop", "plur_verb_prop","sing_verb_prop", "conditional_prop","question_prop","exclamative_prop","quote_prop","bracket_prop","noun_prop","cconj_prop", "sconj_prop", "pronp_prop", "adj_prop","adv_prop", "sttr", "comma_prop", "numbers_prop", "level0_prop", "level1_prop", "level2_prop", "autre_prop", "ner_prop", "person_prop", "norp_prop", "fac_prop", "org_prop", "gpe_prop", "loc_prop", "product_prop", "event_prop"]

with open("tables/sources.csv", "r") as f:
    reader = csv.DictReader(f)
    SOURCES = {row["id"]:row["name"] for row in reader}


f = open("tables/media_with_mean_features.csv", "r", encoding="latin1")
samples_media=csv.DictReader(f)

matrix_media=[]

for row in samples_media:
    sample=(row["id"],)
    for feature in FEATURES_NAMES:
        try:
            row[feature]=float(row[feature])
        except:
            row[feature]=0
        sample+=(row[feature],)
    if sample and sum!=0:
        matrix_media.append(sample)


matrix_media = np.array(matrix_media)
f.close()

medias_id=matrix_media[:,0]
features=matrix_media[:,1:]


n_components = 3
media_embedding = TSNE(n_components = n_components).fit_transform(features)

clusterer = hdbscan.HDBSCAN(min_cluster_size=5, gen_min_span_tree=True)
clusterer.fit(media_embedding)

media_values = np.concatenate((media_embedding,medias_id.T[:,None]), axis=1)
media_results = []
clustered_media = defaultdict(list)

for counter, value in enumerate(media_values):
    cluster = int(clusterer.labels_[counter])
    if n_components == 3:
        media = SOURCES[value[3]]
        result = {"x":value[0], "y":value[1], "z":value[2], "media":media, "color":cluster}

    else:
        media = SOURCES[value[2]]
        result = {"x":value[0], "y":value[1], "media":media, "color":cluster}

    clustered_media[cluster].append(media)
    media_results.append(result)

with open("visualization/data/reg_dim_media_tsne.json","w") as fd:
    json.dump(media_results, fd, indent=2, ensure_ascii=False)



print("n_components: ", n_components)
print("")
for cluster, media_list in clustered_media.items():
    print(cluster)
    print("contient ", len(media_list), " medias")
    print("soit ", len(media_list)/len(media_values))
    print(media_list)
    print("")


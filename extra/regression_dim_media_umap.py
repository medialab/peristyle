from collections import defaultdict
import numpy as np
import hdbscan
import umap
import json
import csv

FEATURES_NAMES = ["ARI", "nb_sent", "nb_word", "nb_char", "mean_cw", "mean_ws", "shortwords_prop" , "longwords_prop" , "dictwords_prop", "proper_noun_prop", "negation_prop1", "subjectivity_prop1", "verb_prop","past_verb_prop", "pres_verb_prop", "fut_verb_prop","imp_verb_prop", "plur_verb_prop","sing_verb_prop", "conditional_prop","question_prop","exclamative_prop","quote_prop","bracket_prop","noun_prop","cconj_prop", "sconj_prop", "pronp_prop", "adj_prop","adv_prop", "sttr", "comma_prop", "numbers_prop", "level0_prop", "level1_prop", "level2_prop", "autre_prop", "ner_prop", "person_prop", "norp_prop", "fac_prop", "org_prop", "gpe_prop", "loc_prop", "product_prop", "event_prop"]

with open("tables/sources.csv", "r") as f:
    reader = csv.DictReader(f)
    SOURCES = { row["id"]:row["name"] for row in reader}


nb_components = 3
reducer = umap.UMAP(n_components = nb_components)


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

medias_id = matrix_media[:,0]
features = matrix_media[:,1:]
media_embedding = reducer.fit_transform(features)

media_values = np.concatenate((media_embedding,medias_id.T[:,None]), axis=1)


clusterer = hdbscan.HDBSCAN(min_cluster_size=5, gen_min_span_tree=True)
clusterer.fit(media_embedding)

media_results = []
clustered_media = defaultdict(list)


if nb_components == 3:
    fd = open("tables/media_clustered_3D.csv", "w")
    fieldnames = ["media", "media_id", "cluster", "x", "y", "z"]
else:
    fd = open("tables/media_clustered_2D.csv", "w")
    fieldnames = ["media", "media_id", "cluster", "x", "y"]

writer = csv.DictWriter(fd, fieldnames = fieldnames)
writer.writeheader()


for counter, value in enumerate(media_values):
    cluster = str(clusterer.labels_[counter])
    media = SOURCES[value[nb_components]]

    if nb_components == 3:
        result = {"x":value[0], "y":value[1], "z":value[2], "media":media, "color": cluster}
        row = {"x":value[0], "y":value[1], "z":value[2], "media":media, "cluster": cluster, "media_id":value[3]}

    else:
        result = {"x":value[0], "y":value[1], "media":media, "color": cluster}
        row = {"x":value[0], "y":value[1], "media":media, "cluster": cluster, "media_id":value[3]}

    media_results.append(result)
    clustered_media[cluster].append(media)
    writer.writerow(row)

fd.close()

if nb_components == 3:
    with open("visualization/data/reg_dim_media_umap_3D.json","w") as fd:
        json.dump(media_results, fd, indent=2, ensure_ascii=False)

else:
    with open("visualization/data/reg_dim_media_umap_2D.json","w") as fd:
        json.dump(media_results, fd, indent=2, ensure_ascii=False)

print(nb_components)
print("")
for cluster, media_list in clustered_media.items():
    print("     ", cluster)
    print("contient ", len(media_list), " médias")
    print(len(media_list)/len(media_values))
    print(media_list)
    print("")


f=open("tables/sample_filtered_with_features.csv", "r", encoding="latin1")
sample_stories=csv.DictReader(f)
matrix_stories=[]

for row in sample_stories:
    sample=(row["media_id"], row["stories_id"])
    for feature in FEATURES_NAMES:
        try:
            row[feature] = float(row[feature])
        except:
            row[feature] = 0
        sample+=(row[feature],)
    matrix_stories.append(sample)

matrix_stories = np.array(matrix_stories)
f.close()

print(matrix_stories.shape)

medias_id = matrix_stories[:,0]
stories_id = matrix_stories[:,1]
features = matrix_stories[:, 2:]
stories_embedding = reducer.transform(features)

stories_values = np.concatenate((stories_embedding,medias_id.T[:,None]), axis=1)
stories_values = np.concatenate((stories_values,stories_id.T[:,None]), axis=1)

clusterer = hdbscan.HDBSCAN(min_cluster_size=5, gen_min_span_tree=True)
clusterer.fit(stories_embedding)


stories_results = []

for counter, value in enumerate(stories_values):
    cluster = str(clusterer.labels_[counter])
    media = SOURCES[value[nb_components]]

    if nb_components == 3:
        result = {"x":value[0], "y":value[1], "z":value[2], "media":media, "story":value[3], "color": cluster}
    else:
        result = {"x":value[0], "y":value[1], "media":media, "story":value[2], "color": cluster}

    stories_results.append(result)

if nb_components == 3:
    with open("visualization/data/reg_dim_stories_umap_3D.json","w") as fd:
        json.dump(stories_results, fd, indent=2, ensure_ascii=False)
else:
    with open("visualization/data/reg_dim_stories_umap_2D.json","w") as fd:
        json.dump(stories_results, fd, indent=2, ensure_ascii=False)

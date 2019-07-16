import numpy as np
import math
import json
import csv

from sklearn.preprocessing import scale

from collections import defaultdict
from timeit import default_timer as timer
from statistics import median, stdev, mean


# =============================================================================
# (3) Join MEDIA features
# =============================================================================
#
# This script is made to get features values for the media and it has to be run after the calcul_features and the fiter_sample scripts.
# The aim of this one is to deduce features values for the media based on the features values of its stories.
# Those media features values are calculated in two steps:
#               -1- All the stories values are scaled with the scale function of the sklearn python library;
#               -2- Then, the mean of the scaled values for each feature is calculated on all the stories from the same media.
# Those media values will be used to have a idea of the average position of all the stories of a media to help the interpretation.
#



# --------------------------------------
# SETTINGS
# --------------------------------------
FEATURES_NAMES = ["ARI", "nb_sent", "nb_word", "nb_char", "mean_cw", "mean_ws", "shortwords_prop" , "longwords_prop" ,"max_len_word", "dictwords_prop", "proper_noun_prop", "negation_prop1", "negation_prop2", "subjectivity_prop1", "subjectivity_prop2","interpellation_prop1", "interpellation_prop2", "nous_prop1","nous_prop2", "verb_prop", "past_verb_cardinality", "pres_verb_cardinality", "fut_verb_cardinality", "imp_verb_cardinality", "other_verb_cardinality","past_verb_prop", "pres_verb_prop", "fut_verb_prop","imp_verb_prop", "plur_verb_prop","sing_verb_prop","verbs_diversity", "conditional_prop","question_prop","exclamative_prop","quote_prop","bracket_prop","noun_prop","cconj_prop", "sconj_prop", "pronp_prop", "adj_prop","adv_prop", "a", "e", "i", "l", "n", "o", "sttr", "comma_prop", "numbers_prop", "level0_prop", "level1_prop", "level2_prop", "autre_prop", "ner_prop", "person_prop", "norp_prop", "fac_prop", "org_prop", "gpe_prop", "loc_prop", "product_prop", "event_prop" ]
media_info = ["id", "name", "site", "bloc", "level_1", "level_2", "final_categories", "nb_stories"]
# --------------------------------------

#####                   SOURCES GENERATION PART                    #####
#
# This part is made to get the information about a media from it id useful for the vizualisation.
# All the info are stored in a dictionary which accesible anywhere in the code, and the find_source function permits to find the wanted media in this dictionary.
#
def generate_sources():

    f2 = open("tables/sources_update.csv", "r")
    sources = csv.DictReader(f2)

    sources_list = []

    for row in sources:
        source = {"id": row["id"],
                "name":row["name"],
                "site":row["site"],
                "bloc":row["bloc"],
                "level_1":row["level 1"],
                "level_2":row["level 2"],
                "final_categories":row["final categories"]}
        sources_list.append(source)

    f2.close()

    return sources_list

# Global variable declaration
#
SOURCES = generate_sources()

def find_source(media_id):
    for source in SOURCES:
        if source["id"] == media_id:
            return source
    return False



#####                   SCALE THE FEATURES PART                    #####
#
# In this part the script iterates on the sample_filtered_with_features.csv file and stores all the values in a matrix which is scaled with the sklearn function afterward.
# Each array of the matrix corresponds to the features values for one story.
#

f = open("tables/sample_filtered_with_features.csv", "r", encoding = "latin1")
reader = csv.DictReader(f)
matrix_stories = []

for row in reader:

    # Are considered only the stories which haven't been filtered.
    if row["filter"] == "False":
        # The first three elements of the array are information needful to identify the story.
        story_array = (row["stories_id"], row["media_id"], row["url"])

        # Adding each feature value to the array, add 0 if it doesn't exist.
        for feature in FEATURES_NAMES:
            try:
                row[feature]=float(row[feature])
            except:
                row[feature]=0

            story_array += (row[feature],)

        matrix_stories.append(story_array)

# Convert the matrix to a numpy array to use the scale method.
matrix_stories = np.array(matrix_stories)
f.close()

# Storing all the stories information in variables. Those will be reas
stories_id = matrix_stories[:,0]
media_id = matrix_stories[:,1]
urls = matrix_stories[:,2]

# Scaling the values.
#
stories_features=scale(matrix_stories[:,3:])
#

#####                    RELINKING THE FEATURES WITH THE MEDIA INFO + COUNTING STORIES PART                    #####
#
# In this part, the script iterates on all the matrix to reassociate the stories values with the media info corresponding.
# Moreover it counts the number of stories for each media.

# This variable stores all the features values.
# The keys of the defaultdict are the media id's,
#            then the keys of the subdefaultdicts are the names of the features.
#                       Finally the subdefaultdicts contain a list of all the values of the feature.
#
media = defaultdict(lambda: defaultdict(list))

# This variable is here to count how many stories each media has.
count_stories = defaultdict(int)

# The iteration.
for i in range(stories_features.shape[0]):

    count_stories[media_id[i]] += 1

    for j, feature in enumerate(FEATURES_NAMES):
        value = stories_features[i, j]
        media[media_id[i]][feature].append(value)


#####                    WRITING + CALCULATING THE MEDIA VALUES PART                    #####
#
# In this part, it iterates on the medias variable to calculate the mean of each feature.
# After, those results are written in a new file called media_with_mean_features.csv but also in a json file for the visualization.
#

fd = open("tables/media_with_mean_features.csv", "w")
fieldnames = media_info + FEATURES_NAMES
writer = csv.DictWriter(fd, fieldnames = fieldnames)
writer.writeheader()
print(writer.fieldnames)
values = []
# For each media:
for media_id in media.keys():

    media_row = {}
    # Get the media information
    source = find_source(media_id)
    if source:
        media_row = source
        media_row["nb_stories"] = count_stories[media_id]

        # For each feature, caluclate it mean value.
        for feature in FEATURES_NAMES:
            media_row[feature] = mean(media[media_id][feature])

        values.append(media_row)
        writer.writerow(media_row)

fd.close()

with open("visualization/data/media_mean_features_data.json", "w") as f:
    json.dump(media, f, indent = 2, ensure_ascii = False)

import json
import re
from collections import defaultdict, OrderedDict
from operator import itemgetter
from csv import DictReader

from statistics import median, stdev, mean
from math import sqrt, pow, isclose
import numpy as np

from sklearn.decomposition import PCA, IncrementalPCA
from sklearn.preprocessing import scale






# =============================================================================
# Dimensions Regressions in the MEDIA space Script (4)
# =============================================================================
#
# This script runs the AI algorithm which is a linear dimensionality reduction using Singular Value Decomposition.
# It reduces the dimension of each story array to two or three dimensions to project the result to a lower dimensional space.
#
# Two types of data are used to create this space: first the media are projected with the values calculates with the join_media_features.py script, then the stories.
# But they aren't process in the same way except for the matrices creation step:
#           -1- create_matrices(): puts the data in matrices which will be used to train te algorithm.
#                                One matrix is for the stories and another one for the media.
#                                Those matrices have as many lines as there are stories or media, and each column represents a feature.
#                               ---> return: matrix_stories, matrix_media.
#
#           -2- pca_function(marix_media): creates the low dimension space from the media matrix and initialize the pca.
#                                It uses the fit transform function off sklearn to do that.
#                                Thus, for each media the function returns a two or three dimensions array that we can project in the space.
#                               ---> return: x_pca, pca.
#
#           -3- pca_transform_function(matrix_stories, pca): to project the stories in the space created with the media values, the stories values are also reduced to a two or three elements array.
#                                The function transform of sklearn permits to adapt this reduction to an existing space, thus the media and the stories are in the same space.
#                               ---> return: x_pca.
#
#           -4- produce_data_'media/stories': puts all the results in a json file for the visualization.



# --------------------------------------
# SETTINGS
# --------------------------------------
# This is the list of the features wanted to train the algorithm.
FEATURES_NAMES = ["ARI", "nb_sent", "nb_word", "nb_char", "mean_cw", "mean_ws", "shortwords_prop" , "longwords_prop" , "dictwords_prop", "proper_noun_prop", "negation_prop1", "subjectivity_prop1", "verb_prop","past_verb_prop", "pres_verb_prop", "fut_verb_prop","imp_verb_prop", "plur_verb_prop","sing_verb_prop", "conditional_prop","question_prop","exclamative_prop","quote_prop","bracket_prop","noun_prop","cconj_prop", "sconj_prop", "pronp_prop", "adj_prop","adv_prop", "sttr", "comma_prop", "numbers_prop", "level0_prop", "level1_prop", "level2_prop", "autre_prop", "ner_prop", "person_prop", "norp_prop", "fac_prop", "org_prop", "gpe_prop", "loc_prop", "product_prop", "event_prop", "interpellation_prop1", "nous_prop1"]

# This is the number of components wanted to do the PCA, it's the final number of dimensions.
n_components = 3
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
        source = {"id": int(row["id"]),
                "name":row["name"],
                "site":row["site"],
                "bloc":row["bloc"],
                "level_1":row["level 1"],
                "level_2":row["level 2"],
                "final_categories":row["final categories"]}
        sources_list.append(source)

    f2.close()

    return sources_list

SOURCES = generate_sources()

def find_source(media_id):
    for source in SOURCES:
        if int(source["id"]) == media_id:
            return source
    return False



#####                   CREATE MATRIX FUNCTION                    #####
#
# This function returns two numpy matrices needed to create the space, one with the media features values and the second with the stories features values.
# They are both made in the same way, except that the data aren't stored in the same file.
#
def create_matrices():

    # Creating the MEDIA MATRIX.
    # The data are in the media_with_mean_features.csv file
    f_media = open("tables/media_with_mean_features.csv", "r", encoding = "latin1")
    reader_media = csv.DictReader(f_media)
    matrix_media = []

    for row in reader_media:

        # The first element of the array is to recognize the media.
        media = (row["id"], )
        # All the features selected are stored in the array.
        for feature in FEATURES_NAMES:
            try:
                row[feature] = float(row[feature])
            except:
                row[feature] = 0
            media += (row[feature], )
        matrix_media.append(media)

    # Make a numpy matrix
    matrix_media = np.array(matrix_media)
    f_media.close()

    # Creating the STORIES MATRIX.
    # The data are in the sample_filtered_with_features.csv file
    f_stories = open("tables/sample_filtered_with_features.csv", "r", encoding = "latin1")
    reader_stories = csv.DictReader(f_stories)
    matrix_stories = []

    for row in reader_stories:

        # All the stories which weren't filtered are considered.
        if row["filter"] == "False":

            # The first elements of the array are to recognize the story.
            story = (row["stories_id"], row["media_id"], row["url"])

            # All the features selected are stored in the array.
            for feature in FEATURES_NAMES:
                try:
                    row[feature] = float(row[feature])
                except:
                    row[feature] = 0
                story += (row[feature],)

            matrix_stories.append(story)

    # Make a numpy matrix
    matrix_stories = np.array(matrix_stories)
    f_stories.close()

    return (matrix_media, matrix_stories)



#####                   PCA FUNCTION                    #####
#
# This function creates the low dimension space depending on the setting of n_components (two or three) and the media values.
# Otherwise it also gives information about the variables, including their orthogonal projections on the axis.
# It returns a matrix were each array represents a media position in a two or three dimensions space and the pca.
#
def pca_function(matrix):

    # The ids which aren't used in the PCA are stored in the media_id variable.
    # The features variable stores all the features values.
    media_id = matrix[:,0]
    features = matrix[:,1:]

    # -- PCA initialization + features fit transform -- #
    pca = PCA(n_components = n_components)
    x_pca = pca.fit_transform(features)
    # Relinking each array to it id.
    x_pca = np.concatenate((x_pca, media_id.T[:,None]), axis = 1)



    # -- From here, the rest of the function studies the different components and variables. -- #
    #
    # All those prints print information on each dimension.
    ordered_components = {}
    i = 0
    for component in pca.components_:
        component = {FEATURES_NAMES[i]:float(component[i]) for i in range(len(component))}

        print("")
        print("     component", i)
        print("mean ",mean(component.values()))
        print("median ",median(component.values()))
        print("stdev ",stdev(component.values()))
        print(type(component.values()))
        print("q1 ",np.percentile([value for value in component.values()],25))
        print("q2 ",np.percentile([value for value in component.values()],75))
        maximum = max(component.values())
        minimum = min(component.values())
        print("max ", [(key, component[key]) for key in component.keys() if component[key] == maximum])
        print("min ", [(key, component[key]) for key in component.keys() if component[key] == minimum])
        print("")
        ordered_component = OrderedDict(sorted(component.items(), key = itemgetter(1)))
        ordered_components[i] = ordered_component
        print("ORDERED :",ordered_component.items())
        print("")
        print("NOT ORDERED :",component.items())
        print("sum: ",sum(component.values()))
        print("")
        i += 1

    # Explained variance ratio
    print("explained_variance_ratio_: ")
    print(pca.explained_variance_ratio_)
    print("sum: ",sum(pca.explained_variance_ratio_))
    print("n_components: ")
    print(pca.n_components_)
    print("ICIIIIIIIIIII FDP", ordered_components)


    # -- Computation of the influence of each variable on every axis -- #
    # The if condition doesn't change a lot except considering the numlber of dimension wanted.
    # The variable ordered_components contains the projection of each variable on each dimension.
    # Those information are put and stored into the value variable.
    # The value variable is a defaultdict containing a subdefaultdict for each variable with its value on the components.
    #               variable (features) --> x: value, y:value (, z:value)

    values = defaultdict(lambda: defaultdict(float))
    print(ordered_components)
    component0 = ordered_components[0]
    component1 = ordered_components[1]

    if n_components == 3:
        component2 = ordered_components[2]

        for feature0, feature1, feature2 in zip(component0.keys(), component1.keys(), component2.keys()):
            values[feature0]["x"] = component0[feature0]
            values[feature1]["y"] = component1[feature1]
            values[feature2]["z"] = component2[feature2]

            # Data stores all the values for the visualization with VegaLite
            data = []
            for feature in values:
                value_zero = {"feature":feature,"name":"no", "x":0, "y":0, "z":0, "x_color":values[feature]["x"]*10  ,"y_color":values[feature]["y"]*10 ,"z_color":values[feature]["z"]*10, }
                value = {"feature":feature,"name":"yes", "x":(values[feature]["x"]*10), "y":values[feature]["y"]*10, "z":values[feature]["z"]*10, "x_color":values[feature]["x"]*10  ,"y_color":values[feature]["y"]*10 ,"z_color":values[feature]["z"]*10}
                data.append(value)
                data.append(value_zero)

        with open("visualization/data/vector_mean_data_3D.json","w") as fd:
            json.dump(data, fd, indent = 2, ensure_ascii = False)

    else:
        # Same than before.
        for feature0, feature1 in zip(component0.keys(), component1.keys()):
            values[feature0]["x"] = component0[feature0]
            values[feature1]["y"] = component1[feature1]
            data = []

            for feature in values:
                value_zero = {"feature":feature,"name":"no", "x":0, "y":0, "x_color":values[feature]["x"]*10  ,"y_color":values[feature]["y"]*10 }
                value = {"feature":feature,"name":"yes", "x":(values[feature]["x"]*10), "y":values[feature]["y"]*10, "x_color":values[feature]["x"]*10  ,"y_color":values[feature]["y"]*10}
                data.append(value)
                data.append(value_zero)

        with open("visualization/data/vector_mean_data_2D.json","w") as fd:
            json.dump(data, fd, indent = 2, ensure_ascii = False)

    return (x_pca,pca)



#####                   PCA TRANSFORM FUNCTION                    #####
#
# This function transform the matrix_stories function to put the stories array in the low dimension space of the pca with the media.
# For that the values are scaled then transform with the pca functions.
# It returns a matrix were each array represents a story position in the pca space.
#
def pca_transform_function(matrix_stories, pca):

    # Storing all the meta-information.
    stories_id = matrix_stories[:,0]
    media_id = matrix_stories[:,1]
    urls = matrix_stories[:,2]

    # Scale + transform the features values in the pca space.
    features = matrix_stories[:,3:]
    features = scale(features)
    x_pca = pca.transform(features)

    # Relinking with the meta-information.
    x_pca = np.concatenate((x_pca,stories_id.T[:,None]), axis = 1)
    x_pca = np.concatenate((x_pca,media_id.T[:,None]), axis = 1)
    x_pca = np.concatenate((x_pca,urls.T[:,None]), axis = 1)

    return x_pca



#####                   PRODUCE DATA FUNCTIONS                    #####
#
# This part contains two function really similar: produce_data_media(x_pca) and produce_data_stories(x_pca).
# They are used to put all the info into json files needed for the visualizations (with VagaLite and the visualization App).
# They take the matrices returned by the functions using setting the pca and the media and stories postions in that space and put all the values into files with the needed meta-information.
# To do that, those functions are iterating on those matrices.
#
def produce_data_media(x_pca):
    values = []

    # Writing media information for 3 components.
    if n_components == 3:
        for i in range(x_pca.shape[0]):
            value = {}
            media=find_source(x_pca[i,3])

            if media != False:
                value["name"] = media["name"]
                value["id"] = media["id"]
                value["x"] = float(x_pca[i, 0])
                value["y"] = float(x_pca[i, 1])
                value["z"] = float(x_pca[i,2])
                values.append(value)
            else:
                print(x_pca[i,3])

        with open("visualization/data/reg_dim_mean_features_media_data_3D.json","w") as fd:
            json.dump(values, fd, ensure_ascii = False)

    # Writing media information for 2 components
    else:
        for i in range(x_pca.shape[0]):
            value={}
            media=find_source(int(x_pca[i,2]))

            if media != False:
                value["name"] = media["name"]
                value["id"] = media["id"]
                value["x"] = float(x_pca[i, 0])
                value["y"] = float(x_pca[i, 1])
                values.append(value)

        with open("visualization/data/reg_dim_mean_features_media_data_2D.json","w") as fd:
            json.dump(values, fd, ensure_ascii = False)

    return values

def produce_data_stories(x_pca):

    values=[]

    # Writing stories information for 3 components.
    if n_components == 3:
        for i in range(x_pca.shape[0]):
            value = {"story_id":x_pca[i, 3], "url":x_pca[i, 5]}
            media = find_source(int(x_pca[i,4]))

            if media != False:
                value["media_id"] = media["id"]
                value["x"] = float(x_pca[i, 0])
                value["y"] = float(x_pca[i, 1])
                value["z"] = float(x_pca[i, 2])
                values.append(value)


        with open("visualization/data/reg_dim_mean_features_stories_transform_3D.json","w") as fd:
            json.dump(values, fd, ensure_ascii = False)

    # Writing stories information for 2 components.
    else:
        for i in range(x_pca.shape[0]):
            value = {"story_id":x_pca[i, 2], "url":x_pca[i, 4]}
            media = find_source(int(x_pca[i, 3]))

            if media != False:
                value["media_id"] = media["id"]
                value["x"] = float(x_pca[i, 0])
                value["y"] = float(x_pca[i, 1])
                values.append(value)

        with open("visualization/data/reg_dim_mean_features_stories_transform_2D.json","w") as fd:
            json.dump(values, fd, ensure_ascii = False)

    return values


matrix_media, matrix_stories = create_matrices()
x_pca, pca = pca_function(matrix_media)
produce_data_media(x_pca)

x_pca = pca_transform_function(matrix_stories, pca)
produce_data_stories(x_pca)

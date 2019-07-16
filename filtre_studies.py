import csv
import json
import numpy as np

from statistics import median, stdev, mean
from math import sqrt, pow, isclose, fabs
from collections import defaultdict, OrderedDict
from operator import itemgetter



# =============================================================================
# Results Studies Script (5)
# =============================================================================
#
# This script contains a lot of varied functions to run at the end of regression_dim_media.py.
# There are different type of function also, some of them are just to study quantitatively the results of the regression_dim_media.py script, some others are needed to create new visualizations and some others return some stories text to make a more qualitative study.
# Here is the list of those functions:
#
#       ==> For a quantitative study
#           -  calcul_filter(): prints information about how many stories have been filtered thanks to the filter_sample.py script.
#
#           -  calcul_filter_media(): prints information about how many media have been filtered thanks to the filter_sample.py script.
#
#           -  study_features(media_wanted_id): prints statistics about the values for every features of the media wanted.
#
#           -  study_new_features(features_list): prints statistics to see the distribution of the stories for given features.
#
#
#       ==> For a qualitative study
#           -  print_media(media_id_wanted): prints the text of 100 stories not filtered of the media wanted.
#
#           -  print_stories(stories): prints the texts and the features values of the stories in the list taken as an argument.
#
#           -  extract_articles(): extracts the 10 first articles the nearest of each barycenter and puts them into a csv file.
#
#           -  print_quarter(num_quarter, num_articles=100): prints the num_articles articles the nearest to the barycenter corresponding to the num_quarter.
#
#
#       ==> For a visualated study
#           -  barycenters_extraction(): calculates barycenters positions, the distribution of the stories in them and extracts the five stories texts the nearest of each barycenter.
#
#           -  extract_var_distances(): calculates the Eulidean distance between the variables.
#
#


# --------------------------------------
# SETTINGS
# --------------------------------------
INFOS = ["story_id", "url", "name", "webentity", "media_id", "quarter", "distance", "distance_type", "bloc", "level_1", "level_2", "final_categories"]
FEATURES_NAMES = ["ARI", "nb_sent", "nb_word", "nb_char", "mean_cw", "mean_ws", "shortwords_prop" , "longwords_prop" , "dictwords_prop", "proper_noun_prop", "negation_prop1", "subjectivity_prop1", "verb_prop","past_verb_prop", "pres_verb_prop", "fut_verb_prop","imp_verb_prop", "plur_verb_prop","sing_verb_prop", "conditional_prop","question_prop","exclamative_prop","quote_prop","bracket_prop","noun_prop","cconj_prop", "sconj_prop", "pronp_prop", "adj_prop","adv_prop", "sttr", "comma_prop", "numbers_prop", "level0_prop", "level1_prop", "level2_prop", "autre_prop", "ner_prop", "person_prop", "norp_prop", "fac_prop", "org_prop", "gpe_prop", "loc_prop", "product_prop", "event_prop", "interpellation_prop1", "nous_prop1"]
nb_dimension = 3
# --------------------------------------


# --------------------------------------
# USEFUL FUNCTIONS section
# --------------------------------------
#
### Sources generation
#
# This function generates a dictionary with all the information on the media to associate each story to the information of it corresponding media.
#
def generate_sources():
    f2 = open("tables/sources_update.csv", "r", encoding="latin1")
    reader = csv.DictReader(f2)

    sources_list = list()

    for row in reader:
        source={"id": row["id"],
                "name":row["name"],
                "webentities":row["site"],
                "bloc":row["bloc"],
                "level_1":row["level 1"],
                "level_2":row["level 2"],
                "final_categories":row["final categories"]
                }
        sources_list.append(source)

    f2.close()

    return sources_list

# Global variable declaration
SOURCES = generate_sources()

# Get the media information in the SOURCES dictionary thanks to the media id.
#
def find_media_source(media_id):
    for source in SOURCES:
        if source["id"] == media_id:
            return source
    return False

### Prints statistics of a dictionary with numerical values.
# List of values printed: [mean, median, max, min, q1, qu2]
#
def print_statistics(results):

    print("")
    print("mean: ", mean(results.values()))
    print("median: ", median(results.values()))
    print("max: ", max(results.values()))
    print(" -media", [key for key in results.keys() if results[key] == max(results.values())])
    print("min: ", min(results.values()))
    print(" -media", [key for key in results.keys() if results[key] == min(results.values())])
    values = [value for value in results.values()]
    print("q1 ", np.percentile(values, 10))
    print("q2 ", np.percentile(values, 75))
    print("")


    print("")
    print(type(results))
    print("")

    return 0



# --------------------------------------
# Functions for a QUANTITATIVE study section
# --------------------------------------
#
#
#
###   Calculates how many stories/media have been filtered by the filter_sample.py
# This function goes through the sample_filtered_with_features.csv and focus on the filter and reason cells to count the filtered stories.
# While the iteration the function counts how many stories are filtered in general and how many stories are filtered for each reason.
#
def calcul_filter():
    # File opening.
    f = open("tables/sample_filtered_with_features.csv", "r", encoding = "latin1")
    reader = csv.DictReader(f)

    # Counters initialization.
    nb_stories = 0
    nb_stories_filtered = 0
    reasons = defaultdict(int)

    # Iteration.
    for row in reader:
        nb_stories += 1

        # If it has been filtered,
        if row["filter"] == "True":

            # Update the counters.
            nb_stories_filtered += 1
            reasons[row["reason"]] += 1


    # Printing the results.
    filtered_stories_ratio = (nb_stories_filtered/nb_stories)
    print("nb stories: ", nb_stories)
    print("nb stories filtered: ", nb_stories_filtered)
    print("sf/s ratio: ", filtered_stories_ratio)
    print("")

    for reason, nb_stories in reasons.items():
        print(reason, nb_stories)

    f.close()

    return {"nb_stories":nb_stories, "nb_stories_filtered":nb_stories_filtered, "filtered_stories_ratio":filtered_stories_ratio}



# This function goes through the sample_filtered_with_features.csv and focus on the filter cell to account all the media in and out.
# Some media are half filtered because of their partial paywall, so the media in count plus the media out count isn't necessary equal to the total media count.
#
def calcul_filter_media():
    # File opening.
    f = open("tables/sample_filtered_with_features.csv", "r", encoding = "latin1")
    reader = csv.DictReader(f)

    # Counters initialization.
    media_total = set()
    media_in = set()
    media_out = set()

    # Iteration.
    for row in reader:
        media_total.add(row["media_id"])

        # If the story isn't filtered, then it media is stored in the media_in variable.
        if row["filter"] == "False":
            media_in.add(row["media_id"])

        # If the story is filtered, then it media is stored in the media_out variable.
        else:
            media_out.add(row["media_id"])

    # Printing results.
    print("")
    print("")

    print("   medias in    ")
    for media_id in media_in:

        # Get the corresponding media information to print the name of the media.
        media = find_media_source(media_id)
        if media:
            print(media["name"])

    print("")
    print("")

    print("   medias out   ")
    for media_id in media_total:
        if media_id not in media_in:

            # Get the corresponding media information to print the name of the media.
            media = find_media_source(media_id)
            if media:
                print(media["name"])

    print("")
    print("")

    print("media in total: ", len(media_total))
    print("media in: ", len(media_in))
    print("medias out: ", len(media_out))


### Features study for one particular media
#
# This function stores all the features values of the stories of the wanted media, then the print_statistics function is called to print statistics for each feature.
#
def study_features(media_wanted_id):
    # File opening.
    f = open("tables/sample_with_features.csv", "r")
    reader = csv.DictReader(f)

    # Counter initialization.
    # This one is a defaultdict where each feature has it own subdictionary with the stories ids and their value for the corresponding feature.
    features = defaultdict(dict)

    # Iteration.
    for row in reader:

        # If the story is valid (not filtered and from the media wanted):
        if row["filter"] == "False" and int(row["media_id"]) == media_wanted_id:

            # Update the counter.
            for feature in FEATURES_NAMES:
                features[feature][row["stories_id"]] = float(row[feature])

    # Printing the results with the print_statistics function for each feature.
    for feature in features.keys():
        print("     ", feature)
        print_statistics(features[feature])

    f.close()
    return 0


#
# This function takes a list of features names as argument and for each of them it returns its statistics on all the stories.
#
def study_new_features(features_list):
    # File opening.
    f = open("tables/sample_filtered_with_features.csv", "r", encoding = "latin1")
    reader = csv.DictReader(f)

    # Storing variable initialization.
    features_values = defaultdict(dict)

    # Iteration.
    for row in reader:

        # If the story is valid (not filtered).
        if row["filter"] == "False":

            # Update the storing variable.
            for feature in features_list:
                features_values[feature][row["stories_id"]] = float(row[feature])

    # Printing the results with the print_statistics function for each feature.
    for feature in features_values.keys():
        print(feature ,max(features_values[feature].items(), key = operator.itemgetter(1)))
        print_statistics(features_values[feature])

    f.close()
    return 0



# --------------------------------------
# Functions for a QUALITATIVE study section
# --------------------------------------
#
# This function prints in the shell a hundred stories text from one media wanted.
#
def print_media(media_id_wanted):
    # File opening.
    fs=open("tables/sample_filtered_with_features.csv", "r", encoding="latin1")
    reader=csv.DictReader(fs)

    # Counter initialization.
    i = 0

    #Iteration
    for row in reader:

        # If the story is valid (not filtered and from the right media).
        if row["filter"] == "False" and int(row["media_id"]) == media_id_wanted:

            # Update the counter.
            i+=1

            # Printing the text.
            with open("sample/"+row["stories_id"]+".txt", "r") as f:
                text=f.read()
            print(text)

        # If enough stories have been printed, break the loop.
        if i>100:
            break

    return 0


#
# This function prints in the shell some stories that you want to read.
# It requires the list of the stories id to read as an argument.
#
def print_stories(stories):
    # File opening.
    f = open("tables/sample_filtered_with_features.csv", "r", encoding="latin1")
    reader = csv.DictReader(f)
    sample = defaultdict(dict)

    # Iteration.
    for row in reader:

        # If the story is valid.
        if row["filter"]=="False":

            # Storing the stories features values.
            sample[row["stories_id"]] = {key:value for key, value in row.items() if key in FEATURES_NAMES}

    # Printing the results.
    for story in stories:
        with open("sample/"+str(story)+".txt", "r") as f:
            txt=f.read()
        print(story)
        print(sample[str(story)])
        print(txt)
        print("")
    return 0


#
# This funtion puts the 10 stories texts the nearest of each barycenter in a csv file.
#
def extract_articles():

    ## Creating a dictionary with all the features values of all the stories.
    # Opening the file.
    with open("tables/sample_filtered_with_features.csv", "r", encoding = "latin1") as f:
        reader = csv.DictReader(f)

        # Declaring the storing variable.
        # This variable will contain all the wanted stories information.
        sample = defaultdict(lambda: defaultdict())

        # Iteration.
        for row in reader:

            # If the story is valid (not filtered).
            if row["filter"] == "False":

                # Update the storing variable.
                sample[row["stories_id"]] = {key:value for key, value in row.items() if key in FEATURES_NAMES}

    # Opening the sources file with the distance to barycenters for each stories (works for 2 and 3 dimensions).
    if nb_dimension == 3:
        fs = open("tables/stories_with_distance_to_barycenters_3D.csv", "r")
    else:
        fs = open("tables/stories_with_distance_to_barycenters_2D.csv", "r")
    reader = csv.DictReader(fs)

    # Declaring the extracted texts storingg variable. The texts contents are stored depending on their position in the space (which quarter they are in).
    extraction = defaultdict(list)

    # Iteration through the source file.
    for row in reader:
        quarter = int(row["quarter"])

        # Update the storing variable. Put the stories in of their quarter's subdictionary.
        extraction[quarter].append({key:value for key, value in row.items()})

    fs.close()

    # Sort in a descending way the extraction variable by value.
    for quarter in range(1,9):
        extraction[quarter] = sorted(extraction[quarter], key = itemgetter("distance"))


    # Destination file opening depending on the number of dimensions working with.
    if nb_dimension == 3:
        fd = open("tables/text_near_barycenters_extraction_3D.csv", "w")
    else:
        fd = open("tables/text_near_barycenters_extraction_2D.csv", "w")

    fieldnames = ["story_id", "media_name", "quarter", "range", "distance", "url", "text"] + FEATURES_NAMES
    writer = csv.DictWriter(fd, fieldnames = fieldnames)
    writer.writeheader()

    # Writing the stories in the extraction variable in the destination file for each quarter.
    for values in extraction.values():

        for index, value in enumerate(values):

            # Opening the txt file.
            with open("sample/" + value["story_id"]+".txt", "r") as f:
                text = f.read()

            # Adding to the row to write the information about the text, it distance to the barycenter and it range.
            new_value = {"story_id":value["story_id"], "media_name":value["name"], "quarter":value["quarter"], "range":index, "distance":value["distance"], "url":value["url"], "text":text}

            # Adding to the row to write its features values.
            new_value.update(sample[value["story_id"]])

            # Write the row.
            writer.writerow(new_value)

            # Write only 10 texts.
            if index > 10:
                break

    fd.close()

    return 0


#
# This funtion prints in the shell the 'num_articles' first stories texts the nearest to the quarter wanted.
#
def print_quarter(num_quarter, num_articles = 100):

    # File opening.
    if nb_dimension == 3:
        fs = open("tables/stories_with_distance_to_barycenters_3D.csv", "r", encoding = "latin1")
    else:
        fs = open("tables/stories_with_distance_to_barycenters_2D.csv", "r", encoding = "latin1")
    reader = csv.DictReader(fs)

    # Declaring the storing variable.
    # This variable will contain all the wanted stories information.
    values = []

    # Iteration.
    for row in reader:

        # If the story is in the quarter wanted.
        if int(row["quarter"]) == num_quarter:

            # Update the storing variable with all the story information.
            values.append({key:value for key, value in row.items()})

    # Sorting the stories by their distance to the barycenter of their quarter.
    values = sorted(values, key = itemgetter("distance"))


    ## Printing results.
    # Counter initialization.
    i = 0

    # Iteration.
    for value in values:
        # Update counter.
        i += 1

        # Text file opening.
        with open("sample/" + value["story_id"] + ".txt", "r") as f:
            text = f.read()

        # Printing the results.
        print("")
        print(value["story_id"], value["name"])
        print(value["url"])
        print(text)

        # If 'num_articles' texts have been printed then break.
        if i > num_articles:
            break

    return 0






# --------------------------------------
# Functions for a VISUALATED study section
# --------------------------------------
#
#
#
# This function calculates the barycenter in each quarter, thus it permits to also calculate the distribution of the stories in the space.
# This aim is reached in four steps:
#               - determinating the quarter of each story;
#               - computing the barycenters positions;
#               - computing the distance of each story to the barycenter of it quarter;
#               - computing the distance of each media to the barycenter of it quarter.
#
def barycenters_extraction():

    # Loading the values (the position in the space of each story).
    if nb_dimension == 3:
        with open("visualization/data/reg_dim_mean_features_stories_transform_3D.json","r") as fs:
            values = json.load(fs)
    else:
        with open("visualization/data/reg_dim_mean_features_stories_transform_2D.json","r") as fs:
            values = json.load(fs)


    # -- STEP 1 -- Determinating the quarter of each story (working for 2 or 3 dimensions).

    # Storing variable declaration.
    # This value will store for each quarter the list of stories in this last.
    quarters = defaultdict(list)

    # Iteration.
    if nb_dimension == 3:

        for value in values:
            x , y, z = float(value["x"]), float(value["y"]), float(value["z"])

            if x > 0 and y > 0 and z > 0: # X, Y, Z POSITIVE -- NEGATIVE  => QUARTER 1
                quarters["1"].append(value)

            elif x > 0 and y > 0 and z < 0: # X, Y POSITIVE --  Z NEGATIVE  => QUARTER 2
                quarters["2"].append(value)

            elif x > 0 and y < 0 and z < 0: # X POSITIVE -- Y, Z NEGATIVE  => QUARTER 3
                quarters["3"].append(value)

            elif x < 0 and y < 0 and z < 0: # NO POSITIVE -- X, Y, Z NEGATIVE  => QUARTER 4
                quarters["4"].append(value)

            elif x < 0 and y > 0 and z > 0: # Y, Z POSITIVE -- X NEGATIVE  => QUARTER 5
                quarters["5"].append(value)

            elif x < 0 and y > 0 and z < 0: # Y POSITIVE -- X, Z NEGATIVE  => QUARTER 6
                quarters["6"].append(value)

            elif x > 0 and y < 0 and z > 0: # Z, X POSITIVE -- Y NEGATIVE  => QUARTER 7
                quarters["7"].append(value)

            elif x < 0 and y < 0 and z > 0: # Z POSITIVE -- X, Y NEGATIVE  => QUARTER 8
                quarters["8"].append(value)

    else:
        for value in values:
            x, y = float(value["x"]), float(value["y"])

            if x > 0 and y > 0: # X, Y POSITIVE => QUARTER 1
                quarters["1"].append(value)

            elif x > 0 and y < 0: # X POSITIVE -- Y NEGATIVE  => QUARTER 2
                quarters["2"].append(value)

            elif x < 0 and y < 0: # X, Y NEGATIVE => QUARTER 3
                quarters["3"].append(value)

            elif x < 0 and y > 0: # Y POSITIVE -- X NEGATIVE => QUARTER 4
                quarters["4"].append(value)



    # -- STEP 2 -- Computing the barycenters positions (working for 2 or 3 dimensions).

    # Storing variable declaration.
    # Both are to store the barycenters coordinates, but baryceter_coordinates stores them in a json compatible way for the visualization.
    barycenters = defaultdict(lambda: dict)
    barycenter_coordinates = []

    # Iteration over the quarters to calculate each quarter's barycenter.
    if nb_dimension == 3:
        for key, quarter in quarters.items():

            # Store in a values variable all the stories position of this quarter.
            values = defaultdict(list)

            for value in quarter:
                x , y, z = float(value["x"]), float(value["y"]), float(value["z"])
                values["x"].append(x)
                values["y"].append(y)
                values["z"].append(z)

            # Calculate the mean of all the stories positions in this quarter.
            barycenters[key] = {"x":mean(values["x"]), "y":mean(values["y"]), "z":mean(values["z"]), "nb_articles":len(quarter)}
            barycenter_coordinates.append({"quarter":key, "x":barycenters[key]["x"], "y": barycenters[key]["y"], "z":barycenters[key]["z"]})

        # Writing the results in the results in a json file for the visualization.
        with open("visualization/data/barycenter_coordinates_3D.json","w") as fd:
            json.dump(barycenter_coordinates, fd, ensure_ascii=False)
        print("")

    else:
        for key, quarter in quarters.items():

            # Store in a values variable all the stories position of this quarter.
            values=defaultdict(list)

            for value in quarter:
                x , y = float(value["x"]), float(value["y"])
                values["x"].append(x)
                values["y"].append(y)

            # Calculate the mean of all the stories positions in this quarter.
            barycenters[key] = {"x":mean(values["x"]), "y":mean(values["y"]), "nb_articles":len(quarter)}
            barycenter_coordinates.append({"quarter":key, "x":barycenters[key]["x"], "y":barycenters[key]["y"]})

        # Writing the results in a json file for the visualization.
        with open("visualization/data/barycenter_coordinates_2D.json","w") as fd:
            json.dump(barycenter_coordinates, fd, ensure_ascii = False)
        print("")



    # -- STEP 3 -- Computing for each story it distance to barycenter of it quarter (working for 2 or 3 dimensions).

    # Opening the destination file wtih the results.
    if nb_dimension == 3:
        fd = open("tables/stories_with_distance_to_barycenters_3D.csv", "w")
        fieldnames_dimensions = ["x", "y", "z"]
    else:
        fd = open("tables/stories_with_distance_to_barycenters_2D.csv", "w")
        fieldnames_dimensions = ["x", "y"]

    fieldnames = fieldnames_dimensions + INFOS
    writer = csv.DictWriter(fd, fieldnames = fieldnames)
    writer.writeheader()

    # This variable stores the results in a json compatible way for the visualization.
    values = []

    # Iteration through the quarters.
    for key, quarter in quarters.items():

        # For each value of the quarter:
        for value in quarter:

            # Calculate the euclidean distance
            if nb_dimension == 3:
                distance = sqrt(pow(float(barycenters[key]["x"]) - float(value["x"]), 2) + pow(float(barycenters[key]["y"]) - float(value["y"]), 2) + pow(float(barycenters[key]["z"]) - float(value["z"]), 2))
            else:
                distance = sqrt(pow(float(barycenters[key]["x"]) - float(value["x"]), 2) + pow(float(barycenters[key]["y"]) - float(value["y"]), 2))

            # Derterminate the type of te distance.
            if distance < 5e-1:
                distance_type = "really close (<5e-1)"
            elif distance < 1:
                distance_type = "close (5e-1< <1)"
            elif distance < 1.5:
                distance_type = "close enought (1< <1.5)"
            elif distance < 2.5:
                distance_type = "normal (1.5< <2.5)"
            else:
                distance_type = "far (2.5<)"

            # Set the new value information.
            value["quarter"] = key
            value["distance"] = distance
            value["distance_type"] = distance_type
            media_information = find_media_source(value["media_id"])
            value["level_1"] = media_information["level_1"]
            value["level_2"] = media_information["level_2"]
            value["bloc"] = media_information["bloc"]
            value["final_categories"] = media_information["final_categories"]

            # Write the value.
            writer.writerow(value)
            values.append(value)

        print("quarter ", key)
        print("")

    # Writing the results in a json file for the visualization.
    if nb_dimension == 3:
        with open("visualization/data/stories_barycenter_distribution_3D.json","w") as fd:
            json.dump(values, fd, indent = 2, ensure_ascii = False)
    else:
        with open("visualization/data/stories_barycenter_distribution_2D.json","w") as fd:
            json.dump(values, fd, indent = 2, ensure_ascii = False)

    fd.close()


    # -- STEP 4 -- Computing for each media it distance to barycenter of it quarter (working for 2 or 3 dimensions).
    # This step has several substeps:
    #               - Determinating in which quarter is each media;
    #               - Calculating the distance between the media and the corresponding quarter;
    #               - Determinating the distance type.
    #

    ## Determinating in which quarter is each media.

    # Opening the source and destination file.
    # The source file contains the position in the space of each media.
    if nb_dimension == 3:
        with open("visualization/data/reg_dim_mean_features_media_data_3D.json") as fs:
            medias = json.load(fs)

        fd = open("tables/medias_with_distance_to_barycenters_3D.csv", "w")
        fieldnames = [ "id", "name", "webentities", "bloc", "level_1", "level_2", "final_categories", "x", "y", "z", "quarter", "distance", "range", "distance_type"]

    else:
        with open("visualization/data/reg_dim_mean_features_media_data_2D.json") as fs:
            medias = json.load(fs)

        fd = open("tables/medias_with_distance_to_barycenters_2D.csv", "w")
        fieldnames = ["id", "name", "quarter", "distance",  "distance_type", "webentities", "bloc", "level_1", "level_2", "final_categories", "x", "y"]

    writer = csv.DictWriter(fd, fieldnames=fieldnames)
    writer.writeheader()

    # Storing variables initialization.
    quarters = defaultdict(list)
    values = []
    print("")

    # For each media:
    for media in medias:
        quarter = 0

        # Determinate the quarter corresponding.
        if nb_dimension == 3:
            x, y, z = float(media["x"]),  float(media["y"]),  float(media["z"])
            if x > 0 and y > 0 and z > 0: # X, Y, Z POSITIVE -- NEGATIVE  => QUARTER 1
                quarter = 1
            elif x > 0 and y > 0 and z < 0: # X, Y POSITIVE -- Z NEGATIVE => QUARTER 2
                quarter = 2
            elif x > 0 and y < 0 and z < 0: # X POSITIVE -- Y, Z NEGATIVE => QUARTER 3
                quarter = 3
            elif x < 0 and y < 0 and z < 0: # NO POSITIVE -- X, Y, Z NEGATIVE => QUARTER 4
                quarter = 4
            elif x < 0 and y > 0 and z > 0: # Y, Z POSITIVE -- X NEGATIVE => QUARTER 5
                quarter = 5
            elif x < 0 and y > 0 and z < 0: # Y POSITIVE -- X, Z NEGATIVE => QUARTER 6
                quarter = 6
            elif x > 0 and y < 0 and z > 0: # Z, X POSITIVE -- Y NEGATIVE => QUARTER 7
                quarter = 7
            elif x < 0 and y < 0 and z > 0: # Z POSITIVE -- X, Y NEGATIVE => QUARTER 8
                quarter = 8

            quarter = str(quarter)
            # Calculate the distance to it barycenter.
            distance = sqrt(pow(float(barycenters[quarter]["x"])-x, 2)+pow(float(barycenters[quarter]["y"])-y, 2)+pow(float(barycenters[quarter]["z"])-z, 2))

        else:
            x, y = float(media["x"]), float(media["y"])
            if x > 0 and y > 0: # X, Y POSITIVE => QUARTER 1
                quarter = 1
            elif x > 0 and y < 0: # X POSITIVE -- Y NEGATIVE  => QUARTER 2
                quarter = 2
            elif x < 0 and y < 0: # X, Y NEGATIVE => QUARTER 3
                quarter = 3
            elif x < 0 and y > 0: # Y POSITIVE -- X NEGATIVE => QUARTER 4
                quarter = 4

            quarter = str(quarter)
            distance = sqrt(pow(float(barycenters[quarter]["x"])-x, 2)+pow(float(barycenters[quarter]["y"])-y, 2))

        # Determinate distance type.
        if distance < 5e-1:
            distance_type = "really close (<5e-1)"
        elif distance < 1:
            distance_type = "close (5e-1< <1)"
        elif distance < 1.5:
            distance_type = "close enought (1< <1.5)"
        elif distance < 2.5:
            distance_type = "normal (1.5< <2.5)"
        else:
            distance_type = "far (2.5<)"

        media.update(find_media_source(media["id"]))
        media["quarter"] = quarter
        media["distance"] = distance
        media["distance_type"] = distance_type

        writer.writerow(media)
        quarters[quarter].append(media)

    # Writing the results for the visualization.
    if nb_dimension == 3:
        with open("visualization/data/medias_barycenter_distribution_3D.json","w") as fd:
            json.dump(values, fd, indent = 2, ensure_ascii = False)
    else:
        with open("visualization/data/medias_barycenter_distribution_2D.json","w") as fd:
            json.dump(values, fd, indent = 2, ensure_ascii = False)

    fd.close()
    return 0


#
# This functions calculates the Euclidean distances between the features vectors.
#
def extract_var_distances():

    # Opening the sources file.
    if nb_dimension == 3:
        with open("visualization/data/vector_mean_data_3D.json","r") as fs:
            data = json.load(fs)
    else:
        with open("visualization/data/vector_mean_data_2D.json","r") as fs:
            data = json.load(fs)

    data1 = {}
    # Storing all the vectors coordinates.
    # The state attribute will be used to ensure there isn't double associations.
    for vector in data:
        if vector["name"] == "yes":
            if nb_dimension == 3:
                data1[vector["feature"]] = {"x":vector["x"], "y":vector["y"], "z":vector["z"], "state":True}

            else:
                data1[vector["feature"]] = {"x":vector["x"], "y":vector["y"], "state":True}

    data1=OrderedDict(sorted(data1.items()))

    # Duplicating the data variable to do a double iteration.
    data2 = data1
    results = []

    # Double iteration.
    for value1 in data1:
        for value2 in data2:

            # If it's two different features and the second hasn't already been associates with all the other:
            if value1 != value2 and data2[value2]["state"] == True:

                # Then calculating the distance between them.
                if nb_dimension == 3:
                    distance = sqrt(pow(data1[value1]["x"] - data2[value2]["x"], 2) + pow(data1[value1]["y"] - data2[value2]["y"], 2) + pow(data1[value1]["z"] - data2[value2]["z"], 2))
                else:
                    distance = sqrt(pow(data1[value1]["x"] - data2[value2]["x"], 2) + pow(data1[value1]["y"] - data2[value2]["y"], 2))

                new = {"feature1":value1, "feature2":value2, "distance":distance}
                results.append(new)

        data2[value1]["state"] = False

    # Writing the results in a json file for the visualization.
    if nb_dimension == 3:
        with open("visualization/data/features_distances_3D.json","w") as fd:
            json.dump(results, fd, indent = 2, ensure_ascii = False)
    else:
        with open("visualization/data/features_distances_2D.json","w") as fd:
            json.dump(results, fd, indent = 2, ensure_ascii = False)








# --------------------------------------
# EXECUTE the functions section
# --------------------------------------
#
#
#
barycenters_extraction()
#extract_articles()
#extract_var_distances()

#features_to_study = ["interpellation_prop1", "nous_prop1"]
#study_new_features(features_to_study)

#print_stories([891278500])
#print_media(221)

#calcul_filter()
#calcul_filter_media()
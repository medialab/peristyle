import csv
import json

from collections import defaultdict
from timeit import default_timer as timer
from langdetect import detect



# =============================================================================
# Filter Stories Script (2)
# =============================================================================
#
# This script is the second one to run, from the outputs of the features values from the calcul_features.py script it filters the stories which will be used after to train the algorithm.
# This script goes through all the features values results in the sample_with_features.cs file, and from those values it filters some stories.
# This selection is based on several criteria and each one has a specific reason to be. Here are all those conditions and their justification:
#           - media paywalled : Some media has been tagged as "paywall" while we were having more and more information about the corpus.
#                      If a media is paywalled it doesn't let its articles in free access on the internet, so we couldn't get the text of the articles the stories of this kind of media.
#                      Therefor the stories from those media are filtered;
#
#           - partial paywall: Some paywalled media are tagged "partial paywalled". Those media let accesible a part of their articles long enought to do a stylistic analysis;
#
#           - language: This project is only about french stylistic, therefor if some stories gathered in french, those are filtered also.
#                      To do this the script uses the function dectect from the python library langdetect which returns the language of a text;
#
#           - ARI result: An ARI result should be between 0 and 20 according to the documentation on the it, stories outside the range are abnormally written, they aren't proper text (often only two words, or a text with a lot of URLs for instance).
#                      So to keep only coherently written texts, one of the filter conditions is based on the ARI result.
#                      But as the metric is in for English, to adapt it the range of tolerated results had been expanded;
#
#           - must have word: Seems obvious to do a stylistic analysis;
#
#           - must have at least 4 sentences: This condition is made to ensure that the work is made on proper press text and not on advertising for instance.
#                      Usually a press article has at least 4 sentences;
#
#           - story's lenght must be in the right range (between 250 and 1500 words): As the stories are really different, they can also have really different length.
#                      To make them comparable it has been chosen to select the stories between 250 and 1500 words. Have a look to the documentation for further justifications.
#
#           - number of stories per media: It has been decided to do not consider stories from a media not enought represented in the sample.
#                      Indeef, as this stylistic analysis on the articles is meant to be generalized to the media level, all the media must ne notably represented.
#                      To do this only stories from a media with more than 20 stories have been selected.
#
# To do this script goes through the file sample_with_features.csv two times. The first loop checks all the conditions on the features values and on the media's statu, if it's paywalled or not.
# This loop also records how many stories each media has. Then the condition on the number of stories per media is checked in the second loop with the information of the first loop.
#
# Moreover, this loop serves to write if the stories are filtered or not in the new file: sample_with_features_filtered.csv.
# Those information are also writen in a json file, called features_data.json, to help the visualizations.
#
#


#####                   SOURCES GENERATION PART                     #####

# This generates a dictionary with all the information on the media to associate each story to the information of the media corresponding.
#
with open("tables/sources_update.csv", "r") as fs:
    reader = csv.DictReader(fs)
    SOURCES = [{"media_id": row["id"],
            "media_name":row["name"],
            "webentity":row["site"],
            "bloc":row["bloc"],
            "level1":row["level 1"],
            "level2":row["level 2"],
            "final categories":row["final categories"]
            } for row in reader]

# This generates a dictionary with all the paywalled media ids.
#
with open ("tables/paywall.csv", "r") as fs:
    reader = csv.DictReader(fs)
    PAYWALLS = [{"media_id":row["media_id"],
                "partial_paywall":row["partial_paywall"]
                } for row in reader]


# These functions are made to get the information on the media for each story.
#
def is_paywall(media_id):
    for paywall in PAYWALLS:
        if paywall["media_id"] == media_id:
            return paywall
    else:
        return False

def find_media_info(media_id):
    for source in SOURCES:
        if source["media_id"] == media_id:
            return source
    return False



#####                   OPERATION PART                     #####


# This variable stores all the stories features values in the first loop and where the second loop will be done.
rows = []

# This counter count the number of stories per media.
stories_counter = defaultdict(int)


### First loop ###
fs = open("tables/sample_with_features.csv", "r")
reader = csv.DictReader(fs)

for row in reader:

    # Initialization of the filter information.
    # By default the story isn't filtered
    paywall = is_paywall(row["media_id"])
    row["filter"] = False
    row["paywall_media"] = False
    row["reason"] = "none"


    # There are 2 kinds of paywalled media:
    #                           - normal paywalls: all the stories are filtered;
    #                           - partial paywalls: those media let some articles accesible. Then the lenght of the stories has to be checked after.
    #
    if paywall:
        row["paywall_media"] = True
        if paywall["partial_paywall"] == "no":
            row["filter"] = True
            row["reason"] = "paywall"

    # Opening the txt file is needed to check the language of the story.
    try:
        with open ("sample/"+row["stories_id"]+".txt","r") as ft:
            txt = ft.read()
    except:
        continue

    row["language"] = detect(txt)

    ## Contidions checking

    # Language must be french.
    if row["language"] != "fr":
        row["filter"] = True
        row["reason"] = "not french"

    # ARI result must be coherent
    elif float(row["ARI"]) < 0 or 30 < float(row["ARI"]):
        row["filter"] = True
        row["reason"] = "ARI strange"

    # Must has words
    elif float(row["nb_word"]) == 0:
        row["filter"] = True
        row["reason"] = "nb_word==0"

    # Must has at least 4 sentences
    elif float(row["nb_sent"]) <= 3:
        row["filter"] = True
        row["reason"] = "nb_sentence<4"

    # If it's a paywalled media but the lenght of the story is long enought
    elif float(len(txt)) < 1000 and row["paywall_media"] == True:
        row["filter"] = True
        row["reason"] = "long paywall"

    # Must be in correct range words
    elif float(row["nb_word"]) < 250 or 1500 < float(row["nb_word"]):
        row["filter"] = True
        row["reason"] = "text out of range (-250 or +1500 words)"

    # Update the stories counter
    elif row["filter"] == False:
        print(row["media_id"])
        stories_counter[row["media_id"]] += 1

    rows.append(row)



### Second loop ###

# Opening the destination file
fd = open("tables/sample_filtered_with_features.csv", "w")
fieldnames = reader.fieldnames + ["filter", "paywall_media", "language", "reason"]
writer = csv.DictWriter(fd, fieldnames = fieldnames)
writer.writeheader()

i = 0
for row in rows:
    # Check if the media of the story has enought stories to be recognized
    if row["filter"] == False and stories_counter[row["media_id"]] < 20:
        i += 1
        row["filter"] = True
        row ["reason"] = "media with less then 20 stories"
    writer.writerow(row)

print(i)

fd.close()
fs.close()


### Adding those new information in a JSON file ###

values = []

with open("tables/sample_filtered_with_features.csv", "r") as f:
    sample = csv.DictReader(f)

    for row in sample:
        info = find_media_info(row["media_id"])
        value = {}
        if info and row["filter"] == "False":
            for key in row.keys():
                value[key] = row[key]
            for key in info.keys():
                value[key] = info[key]
            value["nb_stories"] = stories_counter[row["media_id"]]
            values.append(value)


with open("visualization/data/features_data.json","w") as f:
    json.dump(values, f, indent=2, ensure_ascii=False)
import csv
import json
import numpy as np
import operator

from collections import defaultdict

from statistics import median
from statistics import stdev
from statistics import mean

from math import sqrt, pow, isclose, fabs
from collections import defaultdict, OrderedDict
from operator import itemgetter



# =============================================================================
# EXTRACT ARTICLES SCRIPT (6)
# =============================================================================
#
# This script extracts text contents of stories from each quarter for given media.
#




# --------------------------------------
# SETTINGS
# --------------------------------------
wanted_ids = {175:"Le Figaro", 181:"Le Monde", 214:"Liberation"}
nb_articles = 2
# --------------------------------------


# Text contents storing variable declaration.
# This is a defaultdict of defaultdict, where each defaultdict corresponds to a media and subdefaultdict to a quarter which are storing the stories with their distance to the barycenter.
articles = defaultdict(lambda: defaultdict(dict))

# Source file opening.
fs = open("tables/stories_with_distance_to_barycenters_3D.csv", "r")
reader = csv.DictReader(fs)


# Iteration through all the stories.
for row in reader:
    print(type(row["media_id"]))
    media_id = int(row["media_id"])
    story_id = row["story_id"]
    distance = float(row["distance"])
    distance_type = row["distance_type"]
    quarter = int(row["quarter"])

    # If it's a story from a wanted media.
    if (media_id in wanted_ids.keys()):

        # Store the distance to the barycenter.
        articles[media_id][quarter][story_id] = distance

# For each wanted media:
for media_id, media_name in wanted_ids.items():
    print(media_name)

     # For each quarter:
    for quarter in articles[media_id].keys():

        # Store the subdefaultdict containing the stories ids and their distance to the barycenter.
        articles[media_id][quarter] = sorted(articles[media_id][quarter].items(), key = lambda dist:dist[1])

fs.close()

print(articles)

# Opening the CSV destination file.
fd = open("tables/extraction_articles_lemonde_figaro_liberation.csv", "w")
fieldnames = ["story_id", "media", "quarter", "range", "distance", "article"]
writer = csv.DictWriter(fd, fieldnames = fieldnames)
writer.writeheader()

# Iteration through the articles variable.
# For each wanted media:
for media_id, quarters in articles.items():
    print("                 ", media_id)
    print("")
    print("")

    # Settings to open the txt file.
    media = wanted_ids[media_id]
    file_name = "texts_to_read_" + media + ".txt"

    # Opening the txt destination file (one for each wanted media).
    with open('texts/' + file_name, "w") as text_file:

        # Write the name of the media.
        text_file.write("\n")
        text_file.write("######" + media.upper() + "######")
        text_file.write("\n")
        text_file.write("\n")

    # For each quarter:
    for quarter, stories in quarters.items():
        print(quarter)
        print("")
        i = 0

        # Opening the txt file again but in the append mode.
        with open("texts/" + file_name, "a") as text_file:

            # Write the corresponding quarter name.
            text_file.write("\n")
            text_file.write("\n")
            text_file.write("\n")
            text_file.write("      QUARTER NUMBER: "+str(quarter))
            text_file.write("\n")
            text_file.write("\n")

        # For each story:
        for story in stories:
            i +=1
            print(story)
            story_id = story[0]

            # Reading the txt story file.
            with open("sample/"+story_id+".txt", "r") as f:
                article = f.read()

            # Write the text content in the txt file.
            # As the dict has been stored by value in a descending way only the nearest stories to the barycenters are written in txt file.
            with open("texts/" + file_name, "a") as text_file:
                    text_file.write(story_id)
                    text_file.write("\n")
                    text_file.write(article)
                    text_file.write("\n")
                    text_file.write("\n")

            if i == nb_articles:
                break













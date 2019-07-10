import collections
import json
import csv
import re
from csv import DictReader, DictWriter
from collections import defaultdict



# =============================================================================
# Topic analysis (6)
# =============================================================================
# This script is made to calculate the distribution of the stories of a given topic in the stylistic space created by the PCA on the extracted features.
# The topic is setted from a list of specific words turned into a regular expression.
#               ---> calcul_topic_distribution(topic)
#
# Morever it has a function to calculate the distribution of the stories from the different media tag.
# The different levels of media tag to study are "level_1", "level_2", "bloc" and "final_categories".
#               ---> calcul_level_distribution(level_wanted)
#
# Finally, it can extract stories from a given topic to have an idea of the text of the story of a topic.
#               ---> get_5_stories_from_topic(topic)
#

# --------------------------------------
# SETTINGS
# --------------------------------------
# Set the list of words to create the topic
#custom_topic = ["films", "film", "scène", "scènes", "festivals", "festivals", "réalisé", "réalisés", "photo", "réalisateurs", "réalisateur", "réalisatrice", "réalisatrices", "musique", "musiques", "photo","photos", "artiste", "artistes"]
#custom_topic = ["France", "français", "macron", "président", "ministre", "ministres", "politique", "politiques", "gouvernement", "social", "national", "parties", "partie", "loi", "lois", "député", "députés"]
#custom_topic = ["police", "policier", "policière", "policiers", "policières", "victime", "victimes", "morts", "mortes", "morte", "mort", "jugé", "jugée", "jugés", "jugées", "comdamnation", "violence", "coup", "prison", "tribunal"]
#custom_topic = ["israël", "palestinien", "palestiniens", "arabie saoudite", "saoudien", "saoudiens", "juif", "juifs", "gaza", "israélien", "israélienne", "israéliens", "israéliennes"]
custom_topic = ["pays", "européennes", "européens", "migrants", "américain", "ministre", "président", "gouvernement", "accord", "allemagne", "chine"]

STORIES_DISTRIBUTION = {}
QUARTER_COUNTER = {"1":0, "2":0, "3":0, "4":0, "5":0, "6":0, "7":0, "8":0}

with open("tables/stories_with_distance_to_barycenters_3D.csv", "r") as f:
    reader = csv.DictReader(f)

    for row in reader:
        STORIES_DISTRIBUTION[row["story_id"]] = {
                                                "quarter" : row["quarter"],
                                                "distance" : row["distance"],
                                                "distance_type" : row["distance_type"]
                                                }
        QUARTER_COUNTER[row["quarter"]] += 1
# --------------------------------------



## calcul_level_distribution(level_wanted)
# This function calculates the distribution of the stories from the different media tag.
# The different levels of media tag to study are "level_1", "level_2", "bloc" and "final_categories".

def calcul_level_distribution(level_wanted):

    # Counters initialization.
    stories_counter = defaultdict(lambda: defaultdict(int))
    level_counter = defaultdict(int)

    # Source file opening.
    fs = open("tables/stories_with_distance_to_barycenters_3D.csv", "r")
    reader = csv.DictReader(fs)

    # Counting the distribution in the quarters for each type of the level studied.
    for row in reader:
        stories_counter[row[level_wanted]][row["quarter"]] += 1
        level_counter[row[level_wanted]] += 1

    print(level_counter)
    fs.close()

    # Destination file opening.
    fd = open("tables/" + level_wanted + "_stories_distribution.csv", "w")
    fieldnames = [level_wanted, "total_stories", "nb_quarter1", "pc_quarter1", "pc_level_quarter1", "nb_quarter2", "pc_quarter2", "pc_level_quarter2","nb_quarter3", "pc_quarter3", "pc_level_quarter3","nb_quarter4", "pc_quarter4", "pc_level_quarter4","nb_quarter5", "pc_quarter5", "pc_level_quarter5","nb_quarter6", "pc_quarter6", "pc_level_quarter6","nb_quarter7", "pc_quarter7", "pc_level_quarter7", "nb_quarter8", "pc_quarter8", "pc_level_quarter8"]
    writer = csv.DictWriter(fd, fieldnames = fieldnames)
    writer.writeheader()

    # Iteration.
    # For each type of the level studied:
    for level, distribution in stories_counter.items():
        new_row = {}
        new_row[level_wanted] = level

        # Initialization of the counter of the total numbre of stories of this level type.
        total_stories = 0

        # For each quarter:
        for quarter in ["1", "2", "3", "4", "5", "6", "7", "8"]:
                nb_stories =  stories_counter[level][quarter]

                total_stories += nb_stories
                new_row["nb_quarter_" + quarter] = nb_stories

                # Calculating the percentage of the number of stories of this level type in this quarter.
                if QUARTER_COUNTER[quarter] != 0:
                    new_row["pc_quarter" + quarter] = nb_stories/QUARTER_COUNTER[quarter]
                else:
                    new_row["pc_quarter" + quarter] = 0

                # Calculating the percentage of the number of stories of this level type in the total number of stories of this type of level.
                if level_counter[level] != 0:
                    new_row["pc_level_quarter" + quarter] = nb_stories/level_counter[level]
                else:
                    new_row["pc_level_quarter" + quarter] = 0

        new_row["total_stories"] = total_stories
        writer.writerow(new_row)
    fd.close()

# set_regex(keywords_list)
# This function set a regex from the list of the keywords of the topic.
#
def set_regex(keywords_list):
    regex = ""
    for keyword in keywords_list:
        regex += "\\b" + keyword + "\\b|"
    regex = regex[:-1]
    REGEX = re.compile(regex, re.I)
    return REGEX


# get_5_stories_from_topic(topic)
# This function extracts 5 stories from the given topic to have an idea of the text of the story of a topic.
# This function takes a list of words as an argument.
#
def get_5_stories_from_topic(topic):
    # Set the topic regex.
    TOPIC_REGEX = set_regex(topic)

    # Source file opening.
    f_sample = open("tables/sample_filtered_with_features.csv", "r")
    reader_sample = csv.DictReader(f_sample)

    # Counters initialization.
    topic_counter = 0
    stories_strenght = {}

    # Iteration.
    # For each story:
    for row in reader_sample:

        # If it isn't filtered:
        if row["filter"] == "False":
            file_name = "./sample/" + row["stories_id"] + ".txt"
            with open(file_name, "r") as f:
                text = f.read()

            # Search the keywords in the text.
            find = re.findall(TOPIC_REGEX, text)

            # If at least one of keywords is found in the text.
            if find:
                topic_counter += 1

                # The strenght is the number of keywords found.
                strenght = len(find)
                stories_strenght[row["stories_id"]] = strenght

    f_sample.close()

    # Sort stories strenghts.
    sorted_stories_strenght = collections.OrderedDict(sorted(stories_strenght.items(), key = lambda kv: kv[1], reverse = True))

    # Destination file opening.
    f_destination = open("tables/topic_stories_examples.csv", "w")
    fieldnames = ["stories_id", "topic", "keywords", "nb_topic_stories", "quarter", "distance", "distance_type", "text"]
    writer = csv.DictWriter(f_destination, fieldnames = fieldnames)
    writer.writeheader()

    # Writing iteration.
    for story_id, strenght in sorted_stories_strenght.items():

        # Textt file opening.
        with open("sample/" + story_id + ".txt", "r") as ft:
            text = ft.read()

        # The topic name is the first keyword of the list.
        topic_name = topic[0]
        keywords = topic

        try:
            # Get the story information
            story_place = STORIES_DISTRIBUTION[story_id]
            new_row = {"stories_id" : story_id, "topic" : topic_name, "keywords" : topic, "nb_topic_stories" : topic_counter, "quarter" : story_place["quarter"], "distance" : story_place["distance"], "distance_type" : story_place["distance_type"], "text" : text}

            # Write the information.
            writer.writerow(new_row)
        except:
            print(story_id)
            continue

    f_destination.close()
    return 0


# calcul_topic_distribution(topic)
# This function calculates the distribution in the quarters of the stories of a given topic.
# The topic is setted from a list of specific words turned into a regular expression.
#
def calcul_topic_distribution(topic):
    # Set the topic regex.
    TOPIC_REGEX = set_regex(topic)

    # Source file opening.
    f_sample = open("tables/sample_filtered_with_features.csv", "r")
    reader_sample = csv.DictReader(f_sample)

    # Counters initialization.
    topic_counter = 0
    topic_stories_distribution = {"1":0, "2":0, "3":0, "4":0, "5":0, "6":0, "7":0, "8":0}

    # Iteration.
    # For each story:
    for row in reader_sample:

        # If it isn't filtered:
        if row["filter"] == "False":

            # Text file opening.
            file_name = "./sample/" + row["stories_id"] + ".txt"
            with open(file_name, "r") as f:
                text = f.read()

            # If there is one of the keywords in the text:
            if TOPIC_REGEX.search(text):

                # Update the counter (number of stories of this topic).
                topic_counter += 1

                # Get the quarter of the story.
                try:
                    story_quarter = STORIES_DISTRIBUTION[row["stories_id"]]["quarter"]
                except:
                    continue

                # Update the counter (number of stories of this topic in each quarter).
                topic_stories_distribution[story_quarter] += 1

    # Destination file opening.
    f_destination = open("tables/topic_distribution.csv", "a", newline = "")
    fieldnames = ["topic", "keywords", "nb_stories" ,"nb_quarter1", "pc_topic_quarter1" ,"nb_quarter2", "pc_topic_quarter2", "nb_quarter3", "pc_topic_quarter3", "nb_quarter4", "pc_topic_quarter4", "nb_quarter5", "pc_topic_quarter5", "nb_quarter6", "pc_topic_quarter6", "nb_quarter7", "pc_topic_quarter7", "nb_quarter8", "pc_topic_quarter8"]
    writer = csv.DictWriter(f_destination, fieldnames = fieldnames)

    new_row = {
            "topic" : topic[0],
            "keywords" : topic,
            "nb_stories" : topic_counter,
    }

    for quarter, nb_stories in topic_stories_distribution.items():
        nb_quarter = "nb_quarter" + quarter
        pc_topic_quarter = "pc_topic_quarter" + quarter
        new_row[nb_quarter] = nb_stories
        new_row[pc_topic_quarter] = nb_stories/topic_counter


    writer.writerow(new_row)
    f_destination.close()

    # Create the json file for the visualization
    with open("visualization/data/topic_distribution.json", "r") as f:
        values = json.load(f)


    for quarter, nb_stories in topic_stories_distribution.items():
        new_value = {
            "topic" : topic[0],
            "quarter" : quarter,
            "nb_total_quarter_stories" : QUARTER_COUNTER[quarter],
            "nb_total_topic_stories" : topic_counter,
            "nb_topic_stories" : nb_stories
        }
        values.append(new_value)

    with open("visualization/data/topic_distribution.json", "w") as f:
        json.dump(values, f, indent=2, ensure_ascii=False)

    return 0



calcul_level_distribution("bloc")

print("start")
calcul_topic_distribution(custom_topic)
print("happy ending")

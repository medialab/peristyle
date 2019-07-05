import collections
import json
import csv
import re
from csv import DictReader, DictWriter
from collections import defaultdict


QUARTER_COUNTER = {"1":0, "2":0, "3":0, "4":0, "5":0, "6":0, "7":0, "8":0}
with open('tables/stories_with_distance_to_baricenters_3D.csv', 'r') as f:
    reader = csv.DictReader(f)
    STORIES_DISTRIBUTION = {}

    for row in reader:
        STORIES_DISTRIBUTION[row["story_id"]] = {"quarter" : row["quarter"], "distance" : row["distance"], "distance_type" : row["distance_type"]}
        QUARTER_COUNTER[row['quarter']] += 1



def calcul_level_distribution(level_wanted):
    stories_counter = defaultdict(lambda: defaultdict(int))
    level_counter = defaultdict(int)
    fs = open('tables/stories_with_distance_to_baricenters_3D.csv', 'r')
    reader = csv.DictReader(fs)


    for row in reader:
        stories_counter[row[level_wanted]][row["quarter"]] += 1
        level_counter[row[level_wanted]] += 1

    print(level_counter)
    fs.close()
    fd = open('tables/' + level_wanted + '_stories_distribution.csv', 'w')
    fieldnames = [level_wanted, 'total_stories', 'nb_quarter1', 'pc_quarter1', 'pc_level_quarter1', 'nb_quarter2', 'pc_quarter2', 'pc_level_quarter2','nb_quarter3', 'pc_quarter3', 'pc_level_quarter3','nb_quarter4', 'pc_quarter4', 'pc_level_quarter4','nb_quarter5', 'pc_quarter5', 'pc_level_quarter5','nb_quarter6', 'pc_quarter6', 'pc_level_quarter6','nb_quarter7', 'pc_quarter7', 'pc_level_quarter7', 'nb_quarter8', 'pc_quarter8', 'pc_level_quarter8']
    writer = csv.DictWriter(fd, fieldnames = fieldnames)
    writer.writeheader()

    for level, distribution in stories_counter.items():
        new_row = {}
        new_row[level_wanted] = level
        total_stories = 0
        for quarter in ["1", "2", "3", "4", "5", "6", "7", "8"]:
                nb_stories =  stories_counter[level][quarter]
                total_stories += nb_stories
                new_row['nb_quarter' + quarter] = nb_stories

                if QUARTER_COUNTER[quarter] != 0:
                    new_row['pc_quarter' + quarter] = nb_stories/QUARTER_COUNTER[quarter]
                else:
                    new_row['pc_quarter' + quarter] = 0

                if level_counter[level] != 0:
                    new_row['pc_level_quarter' + quarter] = nb_stories/level_counter[level]
                else:
                    new_row['pc_level_quarter' + quarter] = 0

        new_row["total_stories"] = total_stories
        writer.writerow(new_row)
    fd.close()

def set_regex(keywords_list):
    regex = ""
    for keyword in keywords_list:
        regex += "\\b" + keyword + "\\b|"
    regex = regex[:-1]
    REGEX = re.compile(regex, re.I)
    print(REGEX)
    print(regex)
    return REGEX


def get_5_stories_from_topic(topic):
    TOPIC_REGEX = set_regex(topic)

    f_sample = open('tables/sample_filtered_with_features.csv', 'r')
    reader_sample = csv.DictReader(f_sample)

    topic_counter = 0
    stories_strenght = {}

    for row in reader_sample:
        if row["filter"] == "False":
            file_name = './sample/' + row['stories_id'] + '.txt'
            with open(file_name, 'r') as f:
                text = f.read()
            find = re.findall(TOPIC_REGEX, text)
            if find:
                topic_counter += 1
                strenght = len(find)
                stories_strenght[row["stories_id"]] = strenght

    f_sample.close()

    sorted_stories_strenght = collections.OrderedDict(sorted(stories_strenght.items(), key = lambda kv: kv[1], reverse = True))


    f_destination = open('tables/topic_stories_examples.csv', 'w')
    fieldnames = ["stories_id", "topic", "keywords", "nb_topic_stories", "quarter", "distance", "distance_type", "text"]
    writer = csv.DictWriter(f_destination, fieldnames = fieldnames)
    writer.writeheader()

    for story_id, strenght in stories_strenght.items():

        with open('sample/' + story_id + ".txt", "r") as ft:
            text = ft.read()

        topic_name = topic[0]
        keywords = topic
        try:
            story_place = STORIES_DISTRIBUTION[story_id]
            new_row = {"stories_id" : story_id, "topic" : topic_name, "keywords" : topic, "nb_topic_stories" : topic_counter, "quarter" : story_place["quarter"], "distance" : story_place["distance"], "distance_type" : story_place["distance_type"], "text" : text}
            writer.writerow(new_row)
        except:
            print(story_id)
            continue

    f_destination.close()
    return 0



def calcul_topic_distribution(topic):
    TOPIC_REGEX = set_regex(topic)
    f_sample = open('tables/sample_filtered_with_features.csv', 'r')
    reader_sample = csv.DictReader(f_sample)


    topic_counter = 0
    topic_stories_distribution = {"1":0, "2":0, "3":0, "4":0, "5":0, "6":0, "7":0, "8":0}

    for row in reader_sample:
        if row["filter"] == "False":
            file_name = './sample/' + row['stories_id'] + '.txt'
            with open(file_name, 'r') as f:
                text = f.read()
            if TOPIC_REGEX.search(text):
                topic_counter += 1
                try:
                    story_quarter = STORIES_DISTRIBUTION[row["stories_id"]]["quarter"]
                except:
                    continue

                topic_stories_distribution[story_quarter] += 1

    f_destination = open('tables/topic_distribution.csv', 'a', newline = '')
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

    ### create the json file for the vizualisation

    with open('visualization/data/topic_distribution.json', 'r') as f:
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

    with open('visualization/data/topic_distribution.json', 'w') as f:
        json.dump(values, f, indent=2, ensure_ascii=False)

    return 0



#calcul_level_distribution("bloc")


get_5_stories_from_topic(["révolution", "révolutions", "guerre civile", "guerres civiles", "révolte","révoltes", "manifestation", "manifestations","grève", "grèves", "révoltant", "révoltants", "révoltante", "évoltantes", "rébellion", "rébellions","rebelles", "rebelle"])


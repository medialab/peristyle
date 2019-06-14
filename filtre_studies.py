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

def generate_sources():

    f2=open("tables/sources.csv", "r", encoding="latin1")
    sources=csv.DictReader(f2)

    sources_list=list()

    for row in sources:
        source={"url": row["url"],
                "name":row["name"],
                "id":row["id"],
                "politics":row["politics"],
                "level0":row["level0_title"],
                "level1":row["level1_title"],
                "level2":row["level2_title"],
                "webentity":row["webentity"]}
        sources_list.append(source)

    f2.close()

    return sources_list

SOURCES=generate_sources()
INFOS=["url","name","id","politics","level0","level1","level2","webentity"]
#FEATURES_NAMES=["ARI", "nb_sent", "nb_word", "nb_char", "mean_cw", "mean_ws", "median_cw", "median_ws", "shortwords_prop" , "longwords_prop" ,"max_len_word", "dictwords_prop", "proper_noun_prop", "negation_prop1", "subjectivity_prop1", "verb_prop","past_verb_prop", "pres_verb_prop", "fut_verb_prop","imp_verb_prop", "plur_verb_prop","sing_verb_prop", "conditional_prop","question_prop","exclamative_prop","quote_prop","bracket_prop","noun_prop","cconj_prop", "sconj_prop", "pronp_prop", "adj_prop","adv_prop", "sttr", "comma_prop", "numbers_prop", "level0_prop", "level1_prop", "level2_prop", "autre_prop", "ner_prop", "person_prop", "norp_prop", "fac_prop", "org_prop", "gpe_prop", "loc_prop", "product_prop", "event_prop", "e" , "a", "l", "o", "i", "n"]
FEATURES_NAMES=["ARI", "nb_sent", "nb_word", "nb_char", "mean_cw", "mean_ws", "shortwords_prop" , "longwords_prop" , "dictwords_prop", "proper_noun_prop", "negation_prop1", "subjectivity_prop1", "verb_prop","past_verb_prop", "pres_verb_prop", "fut_verb_prop","imp_verb_prop", "plur_verb_prop","sing_verb_prop", "conditional_prop","question_prop","exclamative_prop","quote_prop","bracket_prop","noun_prop","cconj_prop", "sconj_prop", "pronp_prop", "adj_prop","adv_prop", "sttr", "comma_prop", "numbers_prop", "level0_prop", "level1_prop", "level2_prop", "autre_prop", "ner_prop", "person_prop", "norp_prop", "fac_prop", "org_prop", "gpe_prop", "loc_prop", "product_prop", "event_prop", "interpellation_prop1", "nous_prop1"]


def find_media_source(media_id):
    for source in SOURCES:
        if source["id"]==media_id:
            return source
    return False


def print_statistics(results):


    print("")
    #print(results)
    print("mean: ",mean(results.values()))
    print("median: ",median(results.values()))
    print("max: ",max(results.values()))
    print(" -media", [key for key in results.keys() if results[key]==max(results.values())])
    print("min: ",min(results.values()))
    print(" -media", [key for key in results.keys() if results[key]==min(results.values())])
    values=[value for value in results.values()]
    print("q1 ",np.percentile(values,10))
    print("q2 ",np.percentile(values,75))
    print("")


    print("")
    print(type(results))
    print("")

    return 0

def calcul_filter():
    f=open("tables/sample_filtered_with_features.csv", "r", encoding="latin1")
    sample=csv.DictReader(f)

    nb_stories=0
    nb_stories_filtered=0
    list_stories_filtered=[]
    reasons=defaultdict(int)

    for row in sample:
        nb_stories+=1
        if row["filter"]=="True":
            nb_stories_filtered+=1
            reasons[row["reason"]]+=1
            list_stories_filtered.append(row["stories_id"])

    filtered_stories_ratio=(nb_stories_filtered/nb_stories)
    print("nb stories: ", nb_stories)
    print("nb stories filtered: ", nb_stories_filtered)
    print("sf/s ration: ", filtered_stories_ratio)
    print("")


    for reason in reasons.keys():
        print(reason, reasons[reason])

    f.close()

    return {"nb_stories":nb_stories, "nb_stories_filtered":nb_stories_filtered, "filtered_stories_ratio":filtered_stories_ratio}


def calcul_filter_media():
    medias_total=set()
    medias_in=set()
    f=open("tables/sample_filtered_with_features.csv", "r", encoding="latin1")
    sample=csv.DictReader(f)

    for row in sample:
        medias_total.add(row["media_id"])
        if row["filter"]=="False":
            medias_in.add(row["media_id"])
    print("")
    print("   medias in    ")
    for media_id in medias_in:
        media=find_media_source(media_id)
        print(media["name"])

    print("")
    print("")
    print("   medias out   ")
    for media_id in medias_total:
        if media_id not in medias_in:
            media=find_media_source(media_id)
            print(media["name"])

    print("")
    print("")
    print("media in total: ", len(medias_total))
    print("media in: ", len(medias_in))
    print("medias out: ", len(medias_total)-len(medias_in))



def study_features(media_wanted_id=0):
    with open("tables/sample_with_features.csv", "r") as f:
        samples=csv.DictReader(f)
        features=defaultdict(dict)
        for row in samples:
            if row["filter"]=="False" and int(row["nb_word"])>250:
                if media_wanted_id==0 or int(row["media_id"])==media_wanted_id:
                    for feature in FEATURES_NAMES:
                        features[feature][row["stories_id"]]=float(row[feature])
        for feature in features.keys():
            print("     ", feature)
            print_statistics(features[feature])
    return 0


def study_new_features(features_list):

    fs=open("tables/sample_filtered_with_features.csv", "r", encoding="latin1")
    reader=csv.DictReader(fs)

    features_values=defaultdict(dict)

    for row in reader:
        if row["filter"]=="False":
            for feature in features_list:
                features_values[feature][row["stories_id"]] = float(row[feature])

    for feature in features_values.keys():
        print(feature ,max(features_values[feature].items(), key=operator.itemgetter(1)))
        print_statistics(features_values[feature])

    return 0


def print_media(media_id_wanted):
    i=0
    fs=open("tables/sample_filtered_with_features.csv", "r", encoding="latin1")
    reader=csv.DictReader(fs)

    for row in reader:
        if row["filter"]=="False" and int(row["media_id"])==media_id_wanted:
            i+=1
            with open("sample/"+row["stories_id"]+".txt", "r") as f:
                text=f.read()
            print(text)
        if i>100:
            break
    return 0


def print_stories(stories):  ##Takes a list as argument
    with open("tables/sample_filtered_with_features.csv", "r", encoding="latin1") as fs:
        reader=csv.DictReader(fs)
        sample=defaultdict(dict)
        for row in reader:
            if row["filter"]=="False":
                sample[row["stories_id"]]={key:value for key, value in row.items() if key in FEATURES_NAMES}

    for story in stories:
        with open("sample/"+str(story)+".txt", "r") as f:
            txt=f.read()
        print(story)
        print(sample[str(story)])
        print(txt)
        print("")
    return 0



##Calcule les baricentres de chaques quartiers et la distribution des articles et des médias dans chaque baricentre
def baricenters_extraction():

    if nb_dimension == 3:
        with open("visualization/data/reg_dim_mean_features_stories_transform_3D.json","r") as fs:
            values=json.load(fs)
    else:
        with open("visualization/data/reg_dim_mean_features_stories_transform_2D.json","r") as fs:
            values=json.load(fs)
    print(len(values))
    quarters=defaultdict(list)


    #1/ distribue les artciles dans chaque quartier
    if nb_dimension == 3:
        for value in values:
            x , y, z = float(value["x"]), float(value["y"]), float(value["z"])

            if x>0 and y>0 and z>0: #POSITIF EN X, Y, Z -- PAS NEGATIF  => QUARTER 1
                quarters["1"].append(value)

            elif x>0 and y>0 and z<0: #POSITIF EN X, Y -- NEGATIF EN Z  => QUARTER 2
                quarters["2"].append(value)

            elif x>0 and y<0 and z<0: #POSITIF EN X -- NEGATIF EN Y, Z  => QUARTER 3
                quarters["3"].append(value)

            elif x<0 and y<0 and z<0: #PAS POSITIF -- NEGATIF EN X, Y, Z  => QUARTER 4
                quarters["4"].append(value)

            elif x<0 and y>0 and z>0: #POSITIF EN Y, Z -- NEGATIF EN X  => QUARTER 5
                quarters["5"].append(value)

            elif x<0 and y>0 and z<0: #POSITIF EN Y -- NEGATIF EN X, Z  => QUARTER 6
                quarters["6"].append(value)

            elif x>0 and y<0 and z>0: #POSITIF EN Z, X -- NEGATIF EN Y  => QUARTER 7
                quarters["7"].append(value)

            elif x<0 and y<0 and z>0: #POSITIF EN Z -- NEGATIF EN X, Y  => QUARTER 8
                quarters["8"].append(value)

    else:
        for value in values:
            x, y = float(value["x"]), float(value["y"])

            if x>0 and y>0: #POSITIF EN X, Y => QUARTER 1
                quarters["1"].append(value)

            elif x>0 and y<0: #POSITIF X -- NEGATIF en Y => QUARTER 2
                quarters["2"].append(value)

            elif x<0 and y<0: #NEGATIF X, Y => QUARTER 3
                quarters["3"].append(value)

            elif x<0 and y>0: #POSITIF Y -- NEGATIF X => QUARTER 4
                quarters["4"].append(value)

    baricenters=defaultdict(lambda: dict)
    baricenter_coordinates=[]


    #2/ Calcule les coordonnées des baricentres
    if nb_dimension == 3:
        for key, quarter in quarters.items():
            values=defaultdict(list)

            for value in quarter:
                x , y, z = float(value["x"]), float(value["y"]), float(value["z"])
                values["x"].append(x)
                values["y"].append(y)
                values["z"].append(z)

            baricenters[key]={"x": mean(values["x"]), "y": mean(values["y"]), "z": mean(values["z"]), "nb_articles": len(quarter)}
            baricenter_coordinates.append({"quarter":str(key), "x": str(baricenters[key]["x"]), "y": str(baricenters[key]["y"]), "z": str(baricenters[key]["z"])})

        with open("visualization/data/baricenter_coordinates_3D.json","w") as fd:
            json.dump(baricenter_coordinates, fd, indent=2, ensure_ascii=False)
        print("")

    else:
        for key, quarter in quarters.items():
            values=defaultdict(list)

            for value in quarter:
                x , y = float(value["x"]), float(value["y"])
                values["x"].append(x)
                values["y"].append(y)

            baricenters[key]={"x": mean(values["x"]), "y": mean(values["y"]), "nb_articles": len(quarter)}
            baricenter_coordinates.append({"quarter":str(key), "x": str(baricenters[key]["x"]), "y": str(baricenters[key]["y"])})

        with open("visualization/data/baricenter_coordinates_2D.json","w") as fd:
            json.dump(baricenter_coordinates, fd, indent=2, ensure_ascii=False)
        print("")


    #3/ Calcule la distance au baricentre de chaque article
    if nb_dimension == 3:
        fd=open("tables/stories_with_distance_to_baricenters_3D.csv", "w")
    else:
        fd=open("tables/stories_with_distance_to_baricenters_2D.csv", "w")

    fieldnames=[key for key in value.keys()]
    fieldnames+=["quarter", "distance", "distance_type"]
    writer=csv.DictWriter(fd, fieldnames=fieldnames)
    writer.writeheader()

    print("")
    values=[]
    counter=defaultdict(lambda: defaultdict(int))

    for key, quarter in quarters.items():
        for value in quarter:
            value["quarter"]=key
            if nb_dimension == 3:
                distance=sqrt(pow(float(baricenters[key]["x"])-float(value["x"]), 2)+pow(float(baricenters[key]["y"])-float(value["y"]), 2)+pow(float(baricenters[key]["z"])-float(value["z"]), 2))
            else:
                distance=sqrt(pow(float(baricenters[key]["x"])-float(value["x"]), 2)+pow(float(baricenters[key]["y"])-float(value["y"]), 2))

            value["distance"]=distance
            if distance<5e-1:
                distance_type="really close (<5e-1)"
            elif distance<1:
                distance_type="close (5e-1< <1)"
            elif distance<1.5:
                distance_type="close enought (1< <1.5)"
            elif distance<2.5:
                distance_type="normal (1.5< <2.5)"
            else:
                distance_type="far (2.5<)"

            counter[key][distance_type]+=1
            value["distance_type"]=distance_type
            values.append(value)
            writer.writerow(value)

        print("quarter ", key)
        print("")

    if nb_dimension == 3:
        with open("visualization/data/stories_baricenter_distribution_3D.json","w") as fd:
            json.dump(values, fd, indent=2, ensure_ascii=False)
    else:
        with open("visualization/data/stories_baricenter_distribution_2D.json","w") as fd:
            json.dump(values, fd, indent=2, ensure_ascii=False)

    fd.close()


    #4/ Calcule la distance au baricentre de chaque médias
    if nb_dimension == 3:
        with open("visualization/data/reg_dim_mean_features_media_data_3D.json") as fs:
            medias=json.load(fs)

        fd=open("tables/medias_with_distance_to_baricenters_3D.csv", "w")
        fieldnames=[ "url", "name", "id", "politics", "level0", "level1", "level2", "webentity", "x", "y", "z", "quarter", "distance", "range", "distance_type"]

    else:
        with open("visualization/data/reg_dim_mean_features_media_data_2D.json") as fs:
            medias=json.load(fs)

        fd=open("tables/medias_with_distance_to_baricenters_2D.csv", "w")
        fieldnames=[ "url", "name", "id", "politics", "level0", "level1", "level2", "webentity", "x", "y", "quarter", "distance", "range", "distance_type"]

    writer=csv.DictWriter(fd, fieldnames=fieldnames)
    writer.writeheader()

    quarters=defaultdict(list)
    values=[]
    print("")
    for media in medias:
        quarter=0
        if nb_dimension == 3:
            x, y, z=float(media["x"]),  float(media["y"]),  float(media["z"])
            if x>0 and y>0 and z>0: #POSITIF EN X, Y, Z -- PAS NEGATIF  => QUARTER 1
                quarter=1
            elif x>0 and y>0 and z<0: #POSITIF EN X, Y -- NEGATIF EN Z  => QUARTER 2
                quarter=2
            elif x>0 and y<0 and z<0: #POSITIF EN X -- NEGATIF EN Y, Z  => QUARTER 3
                quarter=3
            elif x<0 and y<0 and z<0: #PAS POSITIF -- NEGATIF EN X, Y, Z  => QUARTER 4
                quarter=4
            elif x<0 and y>0 and z>0: #POSITIF EN Y, Z -- NEGATIF EN X  => QUARTER 5
                quarter=5
            elif x<0 and y>0 and z<0: #POSITIF EN Y -- NEGATIF EN X, Z  => QUARTER 6
                quarter=6
            elif x>0 and y<0 and z>0: #POSITIF EN Z, X -- NEGATIF EN Y  => QUARTER 7
                quarter=7
            elif x<0 and y<0 and z>0: #POSITIF EN Z -- NEGATIF EN X, Y  => QUARTER 8
                quarter=8

            quarter=str(quarter)
            distance=sqrt(pow(float(baricenters[quarter]["x"])-x, 2)+pow(float(baricenters[quarter]["y"])-y, 2)+pow(float(baricenters[quarter]["z"])-z, 2))

        else:
            x, y = float(media["x"]), float(media["y"])
            if x>0 and y>0:
                quarter = 1
            elif x>0 and y<0:
                quarter = 2
            elif x<0 and y<0:
                quarter = 3
            elif x<0 and y>0:
                quarter = 4

            quarter=str(quarter)
            distance=sqrt(pow(float(baricenters[quarter]["x"])-x, 2)+pow(float(baricenters[quarter]["y"])-y, 2))


        if distance<5e-1:
            distance_type="really close (<5e-1)"
        elif distance<1:
            distance_type="close (5e-1< <1)"
        elif distance<1.5:
            distance_type="close enought (1< <1.5)"
        elif distance<2.5:
            distance_type="normal (1.5< <2.5)"
        else:
            distance_type="far (2.5<)"

        media["quarter"]=quarter
        media["distance"]=distance
        media["distance_type"]=distance_type

        quarters[quarter].append(media)


    for quarter in quarters.keys():
        quarters[quarter]=sorted(quarters[quarter], key=itemgetter("distance"))
        print([value["distance"] for value in quarters[quarter]])


    for quarter, medias  in quarters.items():
        for index, media in enumerate(medias):
            media["range"]=index
            values.append(media)
            writer.writerow(media)

    if nb_dimension == 3:
        with open("visualization/data/medias_baricenter_distribution_3D.json","w") as fd:
            json.dump(values, fd, indent=2, ensure_ascii=False)
    else:
        with open("visualization/data/medias_baricenter_distribution_2D.json","w") as fd:
            json.dump(values, fd, indent=2, ensure_ascii=False)

    fd.close()
    return 0


#Projection orthogonales des variables sur les 3 dimensions
def extract_var_distances():
    if nb_dimension == 3:
        with open("visualization/data/vector_mean_data_3D.json","r") as fs:
            data=json.load(fs)
    else:
        with open("visualization/data/vector_mean_data_2D.json","r") as fs:
            data=json.load(fs)

    data1={}

    for vector in data:
        if vector["name"]=="yes":
            if nb_dimension == 3:
                data1[vector["feature"]]={"x":vector["x"], "y":vector["y"], "z":vector["z"], "state": True}

            else:
                data1[vector["feature"]]={"x":vector["x"], "y":vector["y"], "state": True}

    data1=OrderedDict(sorted(data1.items()))
    data2=data1
    results=[]

    for value1 in data1:
        for value2 in data2:
            if value1!=value2 and data2[value2]["state"]==True:
                if nb_dimension == 3:
                    distance=sqrt(pow(data1[value1]["x"]-data2[value2]["x"], 2)+pow(data1[value1]["y"]-data2[value2]["y"], 2)+pow(data1[value1]["z"]-data2[value2]["z"], 2))
                else:
                    distance=sqrt(pow(data1[value1]["x"]-data2[value2]["x"], 2)+pow(data1[value1]["y"]-data2[value2]["y"], 2))

                new={"feature1":value1, "feature2":value2, "distance":distance}
                new1={"feature1":value2, "feature2":value1, "distance":distance}
                results.append(new)

        data2[value1]["state"]=False


    if nb_dimension ==  3:
        with open("visualization/data/features_distances_3D.json","w") as fd:
            json.dump(results, fd, indent=2, ensure_ascii=False)
    else:
        with open("visualization/data/features_distances_2D.json","w") as fd:
            json.dump(results, fd, indent=2, ensure_ascii=False)


#Extraction des 10 textes les plus proches de chaques baricentres
def extract_articles():
    with open("tables/sample_filtered_with_features.csv", "r", encoding="latin1") as fs:
        reader=csv.DictReader(fs)
        sample=defaultdict(lambda: defaultdict())
        for row in reader:
            if row["filter"]=="False":
                sample[row["stories_id"]]={key:value for key, value in row.items() if key in FEATURES_NAMES}
    if nb_dimension == 3:
        fs=open("tables/stories_with_distance_to_baricenters_3D.csv", "r")
    else:
        fs=open("tables/stories_with_distance_to_baricenters_2D.csv", "r")
    reader=csv.DictReader(fs)
    extraction=defaultdict(list)

    for row in reader:
        quarter=int(row["quarter"])
        extraction[quarter].append({key:value for key, value in row.items()})


    for quarter in range(1,9):
        extraction[quarter]=sorted(extraction[quarter], key=itemgetter("distance"))

    fs.close()
    if nb_dimension == 3:
        fd=open("tables/text_near_baricenters_extraction_3D.csv", "w")
    else:
        fd=open("tables/text_near_baricenters_extraction_2D.csv", "w")
    fieldnames=["story_id", "media_name", "quarter", "range", "distance", "url", "text"]+FEATURES_NAMES
    writer=csv.DictWriter(fd, fieldnames=fieldnames)
    writer.writeheader()

    for values in extraction.values():
        for index, value in enumerate(values):
            with open("sample/"+value["story_id"]+".txt", "r") as f:
                text=f.read()
            new_value={"story_id":value["story_id"], "media_name":value["name"], "quarter":value["quarter"], "range":index, "distance":value["distance"], "url":value["url"], "text":text}
            new_value.update(sample[value["story_id"]])
            writer.writerow(new_value)
            if index>10:
                break
    fd.close()

    return 0


#Affiche les num_articles premiers articles du quartier voulu dans la console
def print_quarter(num_quarter, num_articles=100):
    fs=open("tables/stories_with_distance_to_baricenters.csv", "r", encoding="latin1")
    reader=csv.DictReader(fs)

    values=[]
    for row in reader:
        if int(row["quarter"])==num_quarter:
            values.append({key:value for key, value in row.items()})

    values=sorted(values, key=itemgetter("distance"))
    i=0

    for value in values:
        i+=1
        with open("sample/"+value["story_id"]+".txt", "r") as f:
            text=f.read()
        print("")
        print(value["story_id"], value["name"])
        print(value["url"])
        print(text)
        if i>num_articles:
            break


nb_dimension = 3

#baricenters_extraction()
#extract_articles()
#extract_var_distances()

features_to_study = ["interpellation_prop1", "nous_prop1"]
study_new_features(features_to_study)

#print_stories([891278500])
#print_media(221)

#calcul_filter()
#calcul_filter_media()
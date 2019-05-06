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

    f2=open('sources.csv', 'r')
    sources=csv.DictReader(f2)

    sources_list=list()

    for row in sources:
        source={'url': row['url'],
                'name':row['name'],
                'id':row['id'],
                'politics':row['politics'],
                'level0':row['level0_title'],
                'level1':row['level1_title'],
                'level2':row['level2_title'],
                'webentity':row['webentity']}
        sources_list.append(source)

    f2.close()

    return sources_list

SOURCES=generate_sources()
INFOS=["url","name","id","politics","level0","level1","level2","webentity"]

def find_media_source(media_id):
    for source in SOURCES:
        if source["id"]==media_id:
            return source
    return False


def print_statistics(results):

    if type(results)==dict or type(results)==defaultdict:
        print("")
        #print(results)
        print("mean: ",mean(results.values()))
        print("median: ",median(results.values()))
        print("max: ",max(results.values()))
        print(" -media", [key for key in results.keys() if results[key]==max(results.values())])
        print("min: ",min(results.values()))
        print(" -media", [key for key in results.keys() if results[key]==min(results.values())])
        values=[value for value in results.values()]
        print('q1 ',np.percentile(values,10))
        print('q2 ',np.percentile(values,75))
        print("")

    else:
        print("")
        print(type(results))
        print("")

    return 0

def calcul_filter():
    f=open("sample_filtered_with_features.csv", "r")
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
    f=open("sample_filtered_with_features.csv", "r")
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


def study_new_features():
    fs=open("sample_filtered_with_features.csv", "r")
    reader=csv.DictReader(fs)


    level0={}
    level2={}
    autre={}
    negation={}
    subjectivity={}
    comma={}


    for row in reader:
        if row["filter"]=="False":
            level0[row["stories_id"]]=row["level0_prop"]
            level2[row["stories_id"]]=row["level2_prop"]
            autre[row["stories_id"]]=row["autre_prop"]
            negation[row["stories_id"]]=row["negation_prop1"]
            subjectivity[row["stories_id"]]=row["subjectivity_prop1"]
            comma[row["stories_id"]]=row["comma_prop"]

    print("level0 ",max(level0.items(), key=operator.itemgetter(1)))
    print("level2 ",max(level2.items(), key=operator.itemgetter(1)))
    print("autre ", max(autre.items(), key=operator.itemgetter(1)))
    print("negation ",max(negation.items(), key=operator.itemgetter(1)))
    print("subjectivity ",max(subjectivity.items(), key=operator.itemgetter(1)))
    print("comma ",max(comma.items(), key=operator.itemgetter(1)))

    return 0


def print_media(media_id_wanted):
    i=0
    fs=open("sample_filtered_with_features.csv", "r")
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
    for story in stories:
        print(story)
        with open("sample/"+str(story)+".txt", "r") as f:
            txt=f.read()
        print(story)
        print(txt)
        print("")
    return 0



##Calcule les baricentres de chaques quartiers et la distribution des articles et des médias dans chaque baricentre
def baricenters_extraction():

    with open("reg_dim_mean_features_stories_transform.json","r") as fs:
        values=json.load(fs)

    print(len(values))
    quarters=defaultdict(list)


    #1/ distribue les artciles dans chaque quartier
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

    baricenters=defaultdict(lambda: dict)
    baricenter_coordinates=[]


    #2/ Calcule les coordonnées des baricentres
    for key, quarter in quarters.items():
        values=defaultdict(list)
        print("")
        print("QUARTER NUMBER ", key)

        for value in quarter:
            x , y, z = float(value["x"]), float(value["y"]), float(value["z"])
            values["x"].append(x)
            values["y"].append(y)
            values["z"].append(z)

        baricenters[key]={"x": mean(values["x"]), "y": mean(values["y"]), "z": mean(values["z"]), "nb_articles": len(quarter)}
        baricenter_coordinates.append({"quarter":str(key), "x": str(baricenters[key]["x"]), "y": str(baricenters[key]["y"]), "z": str(baricenters[key]["z"])})

        print("mean x", baricenters[key]["x"])
        print("mean y", baricenters[key]["y"])
        print("mean z", baricenters[key]["z"])
        print("nb_articles", baricenters[key]["nb_articles"])

    with open("baricenter_coordinates.json","w") as fd:
        json.dump(baricenter_coordinates, fd, indent=2, ensure_ascii=False)
    print("")


    #3/ Calcule la distance au baricentre de chaque article
    fd=open("stories_with_distance_to_baricenters.csv", "w")
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
            distance=sqrt(pow(float(baricenters[key]["x"])-float(value["x"]), 2)+pow(float(baricenters[key]["y"])-float(value["y"]), 2)+pow(float(baricenters[key]["z"])-float(value["z"]), 2))
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

    with open("stories_baricenter_distribution.json","w") as fd:
        json.dump(values, fd, indent=2, ensure_ascii=False)

    fd.close()


    #4/ Calcule la distance au baricentre de chaque médias
    with open("reg_dim_mean_features_media_data.json") as fs:
        medias=json.load(fs)

    fd=open("medias_with_distance_to_baricenters.csv", "w")
    fieldnames=[ "url", "name", "id", "politics", "level0", "level1", "level2", "webentity", "x", "y", "z", "quarter", "distance", "distance_type"]
    writer=csv.DictWriter(fd, fieldnames=fieldnames)
    writer.writeheader()

    print("")

    for media in medias:
        quarter=0
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
        writer.writerow(media)

    with open("medias_baricenter_distribution.json","w") as fd:
        json.dump(values, fd, indent=2, ensure_ascii=False)

    fd.close()

    return 0


#Projection orthogonales des variables sur les 3 dimensions
def extract_var_distances():
    with open("vector_mean_data.json",'r') as fs:
        data=json.load(fs)
    data1={}

    for vector in data:
        if vector["name"]=="yes":
            if vector["z"]:
                data1[vector["feature"]]={"x":vector["x"], "y":vector["y"], "z":vector["z"], "state": True}

            else:
                data1[vector["feature"]]={"x":vector["x"], "y":vector["y"], "state": True}

    data1=OrderedDict(sorted(data1.items()))
    data2=data1
    results=[]

    for value1 in data1:
        for value2 in data2:
            if value1!=value2 and data2[value2]["state"]==True:
                if vector["z"]:
                    distance=sqrt(pow(data1[value1]["x"]-data2[value2]["x"], 2)+pow(data1[value1]["y"]-data2[value2]["y"], 2)+pow(data1[value1]["z"]-data2[value2]["z"], 2))
                else:
                    distance=sqrt(pow(data1[value1]["x"]-data2[value2]["x"], 2)+pow(data1[value1]["y"]-data2[value2]["y"], 2))

                new={"feature1":value1, "feature2":value2, "distance":distance}
                new1={"feature1":value2, "feature2":value1, "distance":distance}
                results.append(new)

        data2[value1]["state"]=False


    with open('features_distances.json','w') as fd:
        json.dump(results, fd, indent=2, ensure_ascii=False)


#Extraction des 10 textes les plus proches de chaques baricentres
def extract_articles():
    fs=open("baricenters_extraction.csv", "r")
    reader=csv.DictReader(fs)
    extraction=defaultdict(list)

    for row in reader:
        print(row)
        quarter=int(row["quarter"])
        extraction[quarter].append({key:value for key, value in row.items()})

    for quarter in range(1,9):
        extraction[quarter]=sorted(extraction[quarter], key=itemgetter("distance"))

    fs.close()
    fd=open("text_extraction.csv", "w")
    fieldnames=["story_id", "media_name", "quarter", "range", "distance", "url", "text"]
    writer=csv.DictWriter(fd, fieldnames=fieldnames)
    writer.writeheader()

    for values in extraction.values():
        for index, value in enumerate(values):
            with open("sample/"+value["story_id"]+".txt", "r") as f:
                text=f.read()
            new_value={"story_id":value["story_id"], "media_name":value["name"], "quarter":value["quarter"], "range":index, "distance":value["distance"], "url":value["url"], "text":text}
            writer.writerow(new_value)
            if index>10:
                break

    fd.close()

    return 0


#Affiche les num_articles premiers articles du quartier voulu dans la console
def print_quarter(num_quarter, num_articles=100):
    fs=open("baricenters_extraction.csv", "r")
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


baricenters_extraction()
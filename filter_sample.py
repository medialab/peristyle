import csv
import json

from collections import defaultdict
from timeit import default_timer as timer
from langdetect import detect


def generate_sources():

    f2=open("tables/sources.csv", "r")
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
                "webentity":row["webentity"]
                }
        sources_list.append(source)

    f2.close()

    return sources_list

def generate_paywalls():
    with open ("tables/paywall.csv", "r") as f:
        paywalls_file=csv.DictReader(f)
        paywalls=[{"media_id":int(row["media_id"]), "partial_paywall":row["partial_paywall"]} for row in paywalls_file]
    return paywalls


PAYWALLS=generate_paywalls()
SOURCES=generate_sources()


def is_paywall(media_id):
    return[paywall for paywall in PAYWALLS if paywall["media_id"]==media_id]

def find_media_info(media_id):
    for source in SOURCES:
        if source["id"]==media_id:
            return source
    return False



fs=open("tables/sample_with_features.csv", "r")
reader=csv.DictReader(fs)

fd=open("tables/sample_filtered_with_features.csv", "w")
fieldnames=reader.fieldnames+["filter", "paywall_media", "language", "reason"]

writer=csv.DictWriter(fd, fieldnames=fieldnames)
writer.writeheader()

stories_counter=defaultdict(int)
rows=[]

i=0

for row in reader:
    i+=1
    paywall=is_paywall(row["media_id"])
    row["filter"]=False
    row["paywall_media"]=False
    row["reason"]="none"

    if paywall:
        row["paywall_media"]=True
        if not paywall["partial_paywall"]:
            row["filter"]=True
            row["reason"]="paywall"

    try:
        with open ("sample/"+row["stories_id"]+".txt","r") as ft:
            txt=ft.read()
    except:
        continue

    row["language"]=detect(txt)

    if row["language"]!="fr":
        row["filter"]=True
        row["reason"]="not french"

    elif float(row["ARI"])<0 or 30<float(row["ARI"]):
        row["filter"]=True
        row["reason"]="ARI strange"

    elif float(row["nb_word"])==0:
        row["filter"]=True
        row["reason"]="nb_word==0"

    elif float(row["nb_sent"])<=3:
        row["filter"]=True
        row["reason"]="nb_sentence<4"

    elif float(len(txt))<1000 and row["paywall_media"]==True:
        row["filter"]=True
        row["reason"]="long paywall"

    elif float(row["nb_word"])<250 or 1500<float(row["nb_word"]):
        row["filter"]=True
        row["reason"]="text out of range (-250 or +1500 words)"

    elif row["filter"]==False:
        print(row["media_id"])
        stories_counter[row["media_id"]]+=1

    rows.append(row)
    print(i)



print(stories_counter)

fs.close()
i=0
for row in rows:
    if row["filter"]==False and stories_counter[row["media_id"]]<20:
        i+=1
        row["filter"]=True
        row ["reason"]="media with less then 20 stories"
    writer.writerow(row)

print(i)
fd.close()



values=[]
with open("tables/sample_filtered_with_features.csv", "r") as f:
    sample=csv.DictReader(f)

    for row in sample:

        info=find_media_info(row["media_id"])
        value={}

        if "" not in info and row["filter"]=="False":
            for key in row.keys():
                value[key]=row[key]
            for key in info.keys():
                value[key]=info[key]
            value["nb_stories"]=stories_counter[row["media_id"]]
            values.append(value)


with open("visualization/data/features_data.json","w") as f:
    json.dump(values, f, indent=2, ensure_ascii=False)
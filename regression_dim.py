import statistics
import matplotlib.pyplot as plt
import numpy as np
import csv
import random
import json
import re


from collections import OrderedDict
from operator import itemgetter

from langdetect import detect

from statistics import mean
from statistics import median
from statistics import stdev

from collections import defaultdict
from sklearn.decomposition import PCA, IncrementalPCA
from sklearn.preprocessing import scale
from matplotlib import colors as mcolors
from multiprocessing import Pool

HTML=re.compile(r'<[^>]*>')
VIDE=re.compile(r'[\s\n\t\r]+')
USELESS=re.compile(r'[\'’`\- ]+')

def print_statistics(results):

    if type(results)==dict or type(results)==defaultdict:

        #print(results)
        print("mean: ",mean(results.values()))
        print("median: ",median(results.values()))
        maximum=max(results.values())
        minimum=min(results.values())
        print("max: ", maximum)
        print(" -media", [key for key in results.keys() if results[key]==maximum])
        print("min: ",minimum)
        print(" -media", [key for key in results.keys() if results[key]==minimum])
        values=[value for value in results.values()]
        print('q1 ',np.percentile(values,10))
        print('q2 ',np.percentile(values,75))
        print("")
        print("")
    else:
        print("")
        print(type(results))
        print("")

    return 0


def squeeze(txt): #pour être sur que le sent tokenizer de nltk marche bien
    txt=re.sub(r'[.]+', '.', txt)
    txt=re.sub(USELESS, ' ', txt)
    return txt

def clean(txt):
    txt=re.sub(HTML, ' ', txt)
    txt=re.sub(VIDE, ' ', txt)
    return txt

def generate_sources():

    f2=open('sources.csv', 'r')
    sources=csv.DictReader(f2)

    sources_list=[]

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

def find_source(media_id):
    for source in SOURCES:
        if int(source['id'])==int(media_id):
            return source
    print(media_id, int(media_id))
    return False

def produce_url():
    url={}
    f_sample=open('sample_filtered_with_features.csv', 'r')
    samples=csv.DictReader(f_sample)
    for row in samples:
        url[int(row['stories_id'])]=row['url']
    f_sample.close()
    return url


URLS=produce_url()
SOURCES=generate_sources()

#FEATURES_NAMES=['ARI', 'shortwords_prop' , 'longwords_prop' , 'dictwords_prop', 'sttr', 'negation_prop1', 'subjectivity_prop1', 'verb_prop','noun_prop','cconj_prop','adj_prop','adv_prop', "sttr"]
#FEATURES_NAMES=['ARI', 'nb_sent', 'nb_word', 'nb_char', 'mean_cw', 'mean_ws', 'shortwords_prop' , 'longwords_prop' , 'dictwords_prop', 'sttr', 'negation_prop1', 'subjectivity_prop1', 'verb_prop', 'question_prop','exclamative_prop','quote_prop','bracket_prop','noun_prop','cconj_prop','adj_prop','adv_prop']
FEATURES_NAMES=['ARI', 'nb_sent', 'nb_word', 'nb_char', 'mean_cw', 'mean_ws', 'shortwords_prop' , 'longwords_prop' , 'dictwords_prop', 'negation_prop2', 'subjectivity_prop2', 'verb_prop', 'past_verb_prop', 'pres_verb_prop', 'fut_verb_prop', 'conditional_prop','question_prop','exclamative_prop','quote_prop','bracket_prop','noun_prop','cconj_prop', 'sconj_prop', 'pronp_prop', 'adj_prop','adv_prop', 'sttr', 'comma_prop', 'numbers_prop', 'level0_prop', 'level2_prop', 'autre_prop']

nb_component= 3


def create_matrix(media_wanted_id=0):
    f=open('sample_filtered_with_features.csv', 'r')
    samples=csv.DictReader(f)
    matrix=[]
    for row in samples:
        if row["filter"]=="False":
            if media_wanted_id!=0 and int(row["media_id"])==media_wanted_id:
                sample=(int(row["stories_id"]), int(row["media_id"]))
                for feature in FEATURES_NAMES:
                    sample+=(float(row[feature]),)
                matrix.append(sample)
            elif media_wanted_id==0:
                sample=(int(row["stories_id"]), int(row["media_id"]))
                for feature in FEATURES_NAMES:
                    sample+=(float(row[feature]),)
                matrix.append(sample)

    matrix = np.array(matrix)
    f.close()
    return matrix

def pca_function(matrix, media_wanted_id=0):

    stories_id=matrix[:,0]
    medias_id=matrix[:,1]
    features=matrix[:,2:]


    features=scale(features)
    pca = PCA(n_components=nb_component)
    x_pca=pca.fit_transform(features)
    ordered_components={}

    print(pca.components_)
    i=0
    for component in pca.components_:
        component=component.tolist()
        component1=[float(feature) for feature in component]
        component={FEATURES_NAMES[i]:float(component[i]) for i in range(len(component))}
        print("")
        print("     component", i)
        print("mean ",mean(component.values()))
        print("median ",median(component.values()))
        print("stdev ",stdev(component.values()))
        print('q1 ',np.percentile(component1,25))
        print('q2 ',np.percentile(component1,75))
        maximum=max(component.values())
        minimum=min(component.values())
        print("max ", [(key, component[key]) for key in component.keys() if component[key]==maximum])
        print("min ", [(key, component[key]) for key in component.keys() if component[key]==minimum])
        ordered_component=OrderedDict(sorted(component.items(), key=itemgetter(1)))
        ordered_components[i]=ordered_component

        i+=1
        print("")
        print("ORDERED COMPONENT ", ordered_component.items())
        print("")
        print("NOT ORDERED ", component.items())
        print("")



    if nb_component==3:
        values=defaultdict(lambda: defaultdict(int))
        component0=ordered_components[0]
        component1=ordered_components[1]
        component2=ordered_components[2]

        for feature0, feature1, feature2 in zip(component0.keys(), component1.keys(), component2.keys()):
            values[feature0]["x"]=component0[feature0]
            values[feature1]["y"]=component1[feature1]
            values[feature2]["z"]=component2[feature2]
        data=[]

        for feature in values:
            value_zero={"feature":feature, "middle":"no", "x":0, "y":0, "z":0,  "x_color":values[feature]["x"]*10  ,"y_color":values[feature]["y"]*10 ,"z_color":values[feature]["z"]*10}
            value={"feature":feature, "middle":"yes", "x":values[feature]["x"]*10, "y":values[feature]["y"]*10, "z":values[feature]["z"]*10,  "x_color":values[feature]["x"]*10  ,"y_color":values[feature]["y"]*10 ,"z_color":values[feature]["z"]*10}#####ICI POUR CHANGER LA TAILLE DES VECTEURS

            data.append(value)
            data.append(value_zero)

            with open('vector_data.json','w') as fd:
                json.dump(data, fd, indent=2, ensure_ascii=False)

    elif nb_component==2:
        values=defaultdict(lambda: defaultdict(int))
        component0=ordered_components[0]
        component1=ordered_components[1]

        for feature0, feature1 in zip(component0.keys(), component1.keys()):
            values[feature0]["x"]=component0[feature0]
            values[feature1]["y"]=component1[feature1]
        data=[]

        for feature in values:
            value_zero={"feature":feature, "middle":"no", "x":0, "y":0,  "x_color":values[feature]["x"]*10  ,"y_color":values[feature]["y"]*10}
            value={"feature":feature, "middle":"yes", "x":values[feature]["x"]*10, "y":values[feature]["y"]*10,  "x_color":values[feature]["x"]*10  ,"y_color":values[feature]["y"]*10 }#####ICI POUR CHANGER LA TAILLE DES VECTEURS

            data.append(value)
            data.append(value_zero)

            with open('vector_data.json','w') as fd:
                json.dump(data, fd, indent=2, ensure_ascii=False)


    print("explained_variance_ratio_: ", pca.explained_variance_ratio_)
    somme=0
    for value in pca.explained_variance_ratio_:
        somme+=value


    print("somme explained variance ratio: ", somme)

    print("n_components: ",pca.n_components_)



    x_pca=np.concatenate((x_pca,medias_id.T[:,None]), axis=1)
    x_pca=np.concatenate((x_pca,stories_id.T[:,None]), axis=1)

    return x_pca



def produce_data(x_pca, option="none"):
    values=[]

    if option=="none":
        n=10000
        index = np.random.choice(x_pca.shape[0], n, replace=False)

        for i in index:
            if nb_component==3:
                value={}
                media=find_source(x_pca[i,3])
                for key in media.keys():
                    value[key]=media[key]
                value['url']=URLS[int(x_pca[i,4])]
                value['story_id']=x_pca[i, 4]
                value['media_id']=x_pca[i, 3]
                value['x']=x_pca[i, 0]
                value['y']=x_pca[i, 1]
                value['z']=x_pca[i, 2]

                values.append(value)

            else:
                value={}
                media=find_source(x_pca[i,2])
                for key in media.keys():
                    value[key]=media[key]
                value['url']=URLS[int(x_pca[i,3])]
                value['story_id']=x_pca[i, 3]
                value['media_id']=x_pca[i, 2]
                value['x']=x_pca[i, 0]
                value['y']=x_pca[i, 1]


                values.append(value)


    elif option=="all":
        for i in range(x_pca.shape[0]):
            value={}
            media=find_source(x_pca[i,2])
            for key in media.keys():
                value[key]=media[key]
            value['url']=URLS[int(x_pca[i,3])]
            value['story_id']=x_pca[i, 3]
            value['media_id']=x_pca[i, 2]
            value['x']=x_pca[i, 0]
            value['y']=x_pca[i, 1]

            values.append(value)
    return values

def produce_mean_data(x_pca):


    mean_data=defaultdict(lambda: defaultdict(list))
    n=10000
    index = np.random.choice(x_pca.shape[0], n, replace=False)

    for i in index:
        media_id=x_pca[i, 3]
        mean_data[media_id]["x"].append(x_pca[i, 0])
        mean_data[media_id]["y"].append(x_pca[i, 1])
        mean_data[media_id]["z"].append(x_pca[i, 2])

    values=[]
    for media_id in mean_data.keys():
        value={}
        media=find_source(int(media_id))
        for key in media.keys():
            value[key]=media[key]
        value["x"]=mean(mean_data[media_id]["x"])
        value["y"]=mean(mean_data[media_id]["y"])
        value["z"]=mean(mean_data[media_id]["z"])
        values.append(value)


    return values


def study_features(media_wanted_id=0):
    with open('sample_with_features.csv', 'r') as f:
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


def print_media(media_wanted_id=0):
    f_sample=open('sample_filtered_with_features.csv', 'r')
    samples=csv.DictReader(f_sample)
    i=0
    strange=0
    features_values=defaultdict(list)

    for row in samples:
        if row["stories_id"] and row["filter"]=="False" and int(row["nb_word"])>250:
            if int(row['media_id'])==media_wanted_id or media_wanted_id==0:
                i+=1
                print("HElllo")
                try:
                    with open("sample/"+row['stories_id']+'.txt', 'r') as f:
                        text=f.readline()
                        #if len(text)>1000:
                        text=clean(text)
                        text=squeeze(text)
                        strange+=1
                        print('text ',text)
                        print('len ', len(text))
                        print('title ',row['title'])
                        print('url ', row['url'])
                        print('')
                        print('')
                except:
                    print('il y a eu une couille dans le potage')
                    print('')
                    print('')
                if i==100000:
                    break

    print('strange ',strange)
    print('total ',i)
    study_features(media_wanted_id)
    return 0

#print("171 LCP")
#print_media(171)

#print("327 La Voix du Nord")
#print_media(327)

#print("YOOOYOYOYO 2016")
#print_media(2016)

def pca_all_stories():
    matrix=create_matrix()
    print("matrix shape", matrix.shape)

    x_pca=pca_function(matrix)
    values=produce_data(x_pca)
    data={"values":values}
    with open('reg_dim_data.json','w') as fd:
        json.dump(data, fd, indent=2, ensure_ascii=False)


    """
    values=produce_mean_data(x_pca)
    data={"values":values}

    with open('reg_dim_mean_data.json','w') as fd:
        json.dump(data, fd, indent=2, ensure_ascii=False)
    """

    #print("    STUDY FEATURES")
    #study_features()
    return 0


def pca_media_stories(media_wanted_id=0):

    with open("media_with_mean_features.csv", "r") as f:
         sample=csv.DictReader(f)
         medias=[int(row["id"]) for row in sample]

    data={"values":[]}


    for media in medias:
        if media_wanted_id==0 or media==media_wanted_id:
            media_id=media
            source=find_source(media_id)
            print("")
            print("   ",source["name"].upper(), media_id)
            matrix=create_matrix(media_id)
            print(matrix)
            print("matrix shape", matrix.shape)
            if matrix.shape[0]>10:
                x_pca=pca_function(matrix, media)
                values=produce_data(x_pca, "all")
                data["values"]+=values

    with open('reg_dim_per_media_data.json','w') as fd:
        json.dump(data, fd, indent=2, ensure_ascii=False)

    x_mean=[]
    y_mean=[]
    z_mean=[]



    return 0

pca_all_stories()
#pca_media_stories()
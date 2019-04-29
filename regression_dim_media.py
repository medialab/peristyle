import statistics
import numpy as np
import json
import csv
import re

from collections import OrderedDict

from sklearn.decomposition import PCA, IncrementalPCA
from collections import defaultdict

from sklearn.preprocessing import scale

from statistics import median
from statistics import stdev
from statistics import mean
from operator import itemgetter



HTML=re.compile(r'<[^>]*>')
VIDE=re.compile(r'[\s\n\t\r]+')
USELESS=re.compile(r'[\'’`\- ]+')

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

SOURCES=generate_sources()

#FEATURES_NAMES=['ARI', 'shortwords_prop' , 'longwords_prop' , 'dictwords_prop', 'sttr', 'negation_prop1', 'subjectivity_prop1', 'verb_prop','noun_prop','cconj_prop','adj_prop','adv_prop', "sttr"]

#FEATURES_NAMES=['ARI', 'shortwords_prop' , 'longwords_prop' , 'dictwords_prop', 'sttr', 'negation_prop1', 'subjectivity_prop1', 'verb_prop','noun_prop','cconj_prop','adj_prop','adv_prop', "sttr"]
FEATURES_NAMES=['ARI', 'nb_sent', 'nb_word', 'nb_char', 'mean_cw', 'mean_ws', 'shortwords_prop' , 'longwords_prop' , 'dictwords_prop', 'sttr', 'negation_prop1', 'subjectivity_prop1', 'verb_prop', 'question_prop','exclamative_prop','quote_prop','bracket_prop','noun_prop','cconj_prop','adj_prop','adv_prop']
#FEATURES_NAMES=['ARI', 'nb_sent', 'nb_word', 'nb_char', 'mean_cw', 'mean_ws', 'shortwords_prop' , 'longwords_prop' , 'dictwords_prop', 'negation_prop2', 'subjectivity_prop2', 'verb_prop', 'past_verb_prop', 'pres_verb_prop', 'fut_verb_prop', 'conditional_prop','question_prop','exclamative_prop','quote_prop','bracket_prop','noun_prop','cconj_prop', 'sconj_prop', 'pronp_prop', 'adj_prop','adv_prop', 'sttr', 'comma_prop', 'numbers_prop', 'level0_prop', 'level2_prop', 'autre_prop']
n_components = 3


def find_source(media_id):
    for source in SOURCES:
        if int(source['id'])==media_id:
            return source
    return False

SOURCES=generate_sources()

def create_matrix():
    f=open('media_with_mean_features.csv', 'r')
    samples=csv.DictReader(f)
    matrix=[]
    for row in samples:
        if int(row["nb_stories"]) and int(row["id"])!=250 and int(row["id"])!=171:
            sample=(row["id"],)
            for feature in FEATURES_NAMES:
                try:
                    row[feature]=float(row[feature])
                except:
                    row[feature]=0
                sample+=(row[feature],)

            if sample and sum!=0:
                matrix.append(sample)

    matrix = np.array(matrix)
    f.close()
    return matrix

def pca_function(matrix):

    medias_id=matrix[:,0]
    features=matrix[:,1:]
    features=scale(features)
    maximums={}
    for i, feature in enumerate(FEATURES_NAMES):
        maximum=max(features[:,i])
        minimum=min(features[:,i])*(-1)
        if minimum>maximum:
            maximum=minimum
        maximums[feature]=maximum


    pca = PCA(n_components=n_components)
    x_pca=pca.fit_transform(features)


    i=0
    ordered_components={}

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
        print("")
        ordered_component=OrderedDict(sorted(component.items(), key=itemgetter(1)))
        ordered_components[i]=ordered_component
        print("ORDERED :",ordered_component.items())
        print("")
        print("NOT ORDERED :",component.items())
        somme=0
        for value in component.values():
            somme+=value
        print("sum: ",somme)
        print("")
        i+=1

    values=defaultdict(lambda: defaultdict(int))
    component0=ordered_components[0]
    component1=ordered_components[1]

    if n_components==3:
        component2=ordered_components[2]
        for feature0, feature1, feature2 in zip(component0.keys(), component1.keys(), component2.keys()):
            values[feature0]["x"]=component0[feature0]
            values[feature1]["y"]=component1[feature1]
            values[feature2]["z"]=component2[feature2]
            data=[]

            for feature in values:
                value_zero={"feature":feature,"name":"no", "x":0, "y":0, "z":0, "x_color":values[feature]["x"]*10  ,"y_color":values[feature]["y"]*10 ,"z_color":values[feature]["z"]*10, }
                value={"feature":feature,"name":"yes", "x":(values[feature]["x"]*10), "y":values[feature]["y"]*10, "z":values[feature]["z"]*10, "x_color":values[feature]["x"]*10  ,"y_color":values[feature]["y"]*10 ,"z_color":values[feature]["z"]*10}
                data.append(value)
                data.append(value_zero)
    else:
        for feature0, feature1 in zip(component0.keys(), component1.keys()):
            values[feature0]["x"]=component0[feature0]
            values[feature1]["y"]=component1[feature1]
            data=[]

            for feature in values:
                value_zero={"feature":feature,"name":"no", "x":0, "y":0, "x_color":values[feature]["x"]*10  ,"y_color":values[feature]["y"]*10 }
                value={"feature":feature,"name":"yes", "x":(values[feature]["x"]*10), "y":values[feature]["y"]*10, "x_color":values[feature]["x"]*10  ,"y_color":values[feature]["y"]*10}

                data.append(value)
                data.append(value_zero)



    with open('vector_mean_data.json','w') as fd:
        json.dump(data, fd, indent=2, ensure_ascii=False)



    print("explained_variance_ratio_: ")
    print(pca.explained_variance_ratio_)
    sum=0
    for item in pca.explained_variance_ratio_:
        sum+=float(item)
    print("sum: ",sum)

    print("n_components: ")
    print(pca.n_components_)
    x_pca=np.concatenate((x_pca,medias_id.T[:,None]), axis=1)

    return x_pca


def produce_data(x_pca):

    values=[]

    if n_components==3:
        for i in range(x_pca.shape[0]):
            value={}
            media=find_source(int(x_pca[i,3]))
            for key in media.keys():
                value[key]=media[key]
            value['x']=x_pca[i, 0]
            value['y']=x_pca[i, 1]
            value['z']=x_pca[i,2]
            values.append(value)
    else:
        for i in range(x_pca.shape[0]):
            value={}
            media=find_source(int(x_pca[i,2]))
            for key in media.keys():
                value[key]=media[key]
            value['x']=x_pca[i, 0]
            value['y']=x_pca[i, 1]
            values.append(value)

    with open('reg_dim_mean_features_media_data.json','w') as fd:
        json.dump(values, fd, indent=2, ensure_ascii=False)

    return values


matrix=create_matrix()
print(matrix.shape)
x_pca=pca_function(matrix)
produce_data(x_pca)


def study_features():
    with open('media_with_mean_features.csv', 'r') as f:
        samples=csv.DictReader(f)
        features=defaultdict(dict)

        for row in samples:
            for feature in FEATURES_NAMES:
                features[feature][row["id"]]=float(row[feature])

        for feature in features.keys():
            print(feature)
            print("mean", mean(features[feature].values()))
            print("median", median(features[feature].values()))
            print("max", max(features[feature].values()))
            print("stdev", stdev(features[feature].values()))
            print(" -media", [key for key in features[feature].keys() if features[feature][key]==max(features[feature].values())])
            print("min", min(features[feature].values()))
            print(" -media", [key for key in features[feature].keys() if features[feature][key]==min(features[feature].values())])
            values=list(features[feature].values())
            print('q1 ',np.percentile(values,25))
            print('q2 ',np.percentile(values,75))
            print("")

    return 0

#study_features()


def print_media(media_wanted_id):
    f_sample=open('sample_with_features.csv', 'r')
    samples=csv.DictReader(f_sample)
    i=0

    for row in samples:
        if int(row['media_id'])==media_wanted_id and row["filter"]=="False" and int(row["nb_word"])>250:
            i+=1

            with open("sample/"+row['stories_id']+'.txt', 'r') as f:
                text=f.readline()
                text=clean(text)
                text=squeeze(text)
                print('text ',text)
                print('len ', len(text))
                print('title ',row['title'])
                print('url ', row['url'])
                print('')
                print(row)
                print('')
                print('')

            #except:
            #    print('il y a eu une couille dans le potage')
            #    print('')
            #    print('')

    print('HEYOOOOO ',i)
    return 0
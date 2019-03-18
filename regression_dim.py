import matplotlib.pyplot as plt
import numpy as np
import csv
import random
import json
from statistics import mean
from statistics import median

from collections import defaultdict
from sklearn.decomposition import PCA, IncrementalPCA
from matplotlib import colors as mcolors
from multiprocessing import Pool



def generator_colors(color):
    new_color = color
    while new_color==color or new_color in colors:
        new_color = "#"+''.join([random.choice('0123456789ABCDEF') for j in range(6)])
    print(new_color)
    colors.append(new_color)
    return new_color


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

def generate_media_id():

    f2=open('sources.csv', 'r')
    sources=csv.DictReader(f2)

    media_id_list=[]

    for row in sources:
        media_id_list.append(row['id'])

    f2.close()

    return media_id_list

def find_source(sources, media_id):
    for source in sources:
        if int(source['id'])==media_id:
            return source
    return False



def produce_data():
    i=0

    f_sample=open('sample_with_features.csv', 'r')
    samples=csv.DictReader(f_sample)

    count_stories=defaultdict(int)

    for row in samples:
        if row['media_id']:
            count_stories[row['media_id']]+=1

    f_sample.close()


    f_sample=open('sample_with_features.csv', 'r')
    samples=csv.DictReader(f_sample)

    sources=generate_sources()
    data={"values":[]}

    for row in samples:
        print(row)
        if row['media_id']:
            print(row['media_id'])
            info=find_source(sources, float(row['media_id']))
            value={}
            if info:

                for key in row.keys():
                    value[key]=row[key]
                for key in info.keys():
                    value[key]=info[key]
                value['nb_stories']=count_stories[row['media_id']]
                data['values'].append(value)
    f_sample.close()

    with open('features_data.json','w') as fd:
        json.dump(data, fd, indent=2, ensure_ascii=False)


    return data





def pca_function():
    f=open('sample_with_features.csv', 'r')
    samples=csv.DictReader(f)
    features_name=['stories_id', 'media_id','ARI','mean_cw','mean_ws','median_cw','median_ws','prop_shortwords','prop_longwords','prop_dictwords','voc_cardinality','mean_occ_letter','median_occ_letter','prop_negation','subjectivity_prop','verb_prop','past_verb_cardinality','pres_verb_cardinality','fut_verb_cardinality','imp_verb_cardinality','other_verb_cardinality','past_verb_prop','pres_verb_prop','fut_verb_prop','imp_verb_prop','plur_verb_prop','sing_verb_prop','verbs_diversity','question_prop','exclamative_prop','quote_prop','bracket_prop','noun_prop','cconj_prop','adj_prop','adv_prop']
    features_names=['ARI','mean_cw','mean_ws','median_cw','median_ws','prop_shortwords','prop_longwords','prop_dictwords','voc_cardinality','mean_occ_letter','median_occ_letter','prop_negation','subjectivity_prop','verb_prop','past_verb_cardinality','pres_verb_cardinality','fut_verb_cardinality','imp_verb_cardinality','other_verb_cardinality','past_verb_prop','pres_verb_prop','fut_verb_prop','imp_verb_prop','plur_verb_prop','sing_verb_prop','verbs_diversity','question_prop','exclamative_prop','quote_prop','bracket_prop','noun_prop','cconj_prop','adj_prop','adv_prop']

    i=0
    j=0
    k=0
    state=False
    matrice=[]
    for row in samples:
        j+=1
        sample=()

        for feature in features_name:
            try:
                row[feature]=float(row[feature])
            except:
                row[feature]=0
            sample+=(row[feature],)
        sum=0
        for item in sample:
            sum+=item
        if sample and sum!=0:
            matrice.append(sample)

    matrice = np.array(matrice)
    f.close()


    stories_id=matrice[:,0]
    medias_id=matrice[:,1]
    features=matrice[:,2:]
    n_components = 2
    pca = PCA(n_components=n_components)
    x_pca=pca.fit_transform(features)
    print('x_pca component :', pca.components_)


    for item in pca.components_:
        index=np.where(item==max(item))
        print(type(index))
        print(max(item), index)
        print(mean(item))
        print(median(item))
        index=np.where(item==min(item))
        print(min(item), index)
        print('')

    print('28 ', features_names[28])
    print('25 ', features_names[25])
    print('15 ', features_names[15])


    print('x_pca explained_variance : ', pca.explained_variance_)
    print('x_pca explained variance ratio : ', pca.explained_variance_ratio_)
    print(pca.explained_variance_ratio_.shape)

    x_pca=np.concatenate((x_pca,medias_id.T[:,None]), axis=1)
    x_pca=np.concatenate((x_pca,stories_id.T[:,None]), axis=1)


    print(x_pca)
    '''
    for i in range(500):
        maximums=np.argmax(x_pca, axis=0)
        x_pca=np.delete(x_pca, maximums[0], 0)
        story_id=x_pca[maximums[0]][3]
        extra.append(story_id)
        maximums=np.argmax(x_pca, axis=0)
        x_pca=np.delete(x_pca, maximums[1], 0)
        story_id=x_pca[maximums[1]][3]
        extra.append(story_id)

    print(extra)
    '''

    sources=generate_sources()
    data={"values":[]}

    print(x_pca.shape[0])
    for i in range(x_pca.shape[0]):

        value={}
        media=find_source(sources, int(medias_id[i]))
        value['story_id']=x_pca[i, 3]
        value['media_id']=x_pca[i, 2]
        value['x']=x_pca[i, 0]
        value['y']=x_pca[i, 1]
        for key in media.keys():
            value[key]=media[key]
        data['values'].append(value)

    with open('reg_dim_data.json','w') as fd:
        json.dump(data, fd, indent=2, ensure_ascii=False)

    return 0
#[897616998.0, 884051898.0, 1094353453.0, 899430978.0, 980894987.0, 937875675.0] les bizzarres


def count_stories():
    f_sample =  open('sample_with_features.csv', 'r')
    samples=csv.DictReader(f_sample)
    count_stories=defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(int))))
    medias=generate_sources()

    i=0
    for row in samples:
        if row['media_id']:
            media=find_source(medias, int(row['media_id']))
            count_stories[media['level2']][media['level1']][media['level0']][media['name']]+=1

    for level2 in count_stories.keys():
        print(level2)
        for level1 in count_stories[level2].keys():
            print(' -',level1)
            for level0 in count_stories[level2][level1].keys():
                print('  -', level0, 'medias diff: ',len(count_stories[level2][level1][level0]))
                nb_stories=0
                for value in count_stories[level2][level1][level0].values():
                    nb_stories+=value
                print('   ', nb_stories, ' stories')

    with open('count_stories.json','w') as fd:
        json.dump(count_stories, fd, indent=2, ensure_ascii=False)
    f_sample.close()

    return 0



def pca_function2(media_id_wanted):
    f=open('sample_with_features.csv', 'r')
    samples=csv.DictReader(f)
    features_name=['stories_id' , 'ARI','mean_cw','mean_ws','median_cw','median_ws','prop_shortwords','prop_longwords','prop_dictwords','voc_cardinality','mean_occ_letter','median_occ_letter','prop_negation','subjectivity_prop','verb_prop','past_verb_cardinality','pres_verb_cardinality','fut_verb_cardinality','imp_verb_cardinality','other_verb_cardinality','past_verb_prop','pres_verb_prop','fut_verb_prop','imp_verb_prop','plur_verb_prop','sing_verb_prop','verbs_diversity','question_prop','exclamative_prop','quote_prop','bracket_prop','noun_prop','cconj_prop','adj_prop','adv_prop']

    i=0
    j=0
    k=0
    matrice=[]
    for row in samples:
        j+=1
        sample=()
        try:
            media_id=int(row['media_id'])
        except:
            continue
        if media_id==media_id_wanted:
            print(media_id)
            for feature in features_name:
                try:
                    row[feature]=float(row[feature])
                except:
                    row[feature]=0
                sample+=(row[feature],)
            sum=0
            for item in sample:
                sum+=item
            if sample and sum!=0:
                matrice.append(sample)
    f.close()
    matrice=np.array(matrice)
    print(matrice)
    stories_id=matrice[:,0]
    features=matrice[:,1:]
    n_components = 2
    pca = PCA(n_components=n_components)

    x_pca=pca.fit_transform(features)
    x_pca=np.concatenate((x_pca,stories_id.T[:,None]), axis=1)


    for i in range(50):
        maximums=np.argmax(x_pca, axis=0)
        x_pca=np.delete(x_pca, maximums[0], 0)
        story_id=x_pca[maximums[0]][2]
        maximums=np.argmax(x_pca, axis=0)
        x_pca=np.delete(x_pca, maximums[1], 0)
        story_id=x_pca[maximums[1]][2]

    sources=generate_sources()
    data={"values":[]}


    for i in range(x_pca.shape[0]):
        value={}
        media=find_source(sources, media_id_wanted)
        value['story_id']=x_pca[i, 2]
        value['x']=x_pca[i, 0]
        value['y']=x_pca[i, 1]
        for key in media.keys():
            value[key]=media[key]
        data['values'].append(value)

    with open('reg_dim_data_media.json','w') as fd:
        json.dump(data, fd, indent=2, ensure_ascii=False)
    return 0

pca_function()


def create_matrice():
    f=open('sample_with_features.csv', 'r')
    samples=csv.DictReader(f)
    features_name=['stories_id' , 'ARI','mean_cw','mean_ws','median_cw','median_ws','prop_shortwords','prop_longwords','prop_dictwords','voc_cardinality','mean_occ_letter','median_occ_letter','prop_negation','subjectivity_prop','verb_prop','past_verb_cardinality','pres_verb_cardinality','fut_verb_cardinality','imp_verb_cardinality','other_verb_cardinality','past_verb_prop','pres_verb_prop','fut_verb_prop','imp_verb_prop','plur_verb_prop','sing_verb_prop','verbs_diversity','question_prop','exclamative_prop','quote_prop','bracket_prop','noun_prop','cconj_prop','adj_prop','adv_prop']

    i=0
    j=0
    k=0
    matrice=[]
    for row in samples:
        j+=1
        sample=()
        try:
            media_id=int(row['media_id'])
        except:
            continue
        if media_id==media_id_wanted:
            print(media_id)
            for feature in features_name:
                try:
                    row[feature]=float(row[feature])
                except:
                    row[feature]=0
                sample+=(row[feature],)
            sum=0
            for item in sample:
                sum+=item
            if sample and sum!=0:
                matrice.append(sample)
    f.close()
    matrice=np.array(matrice)
    print(matrice)
    stories_id=matrice[:,0]
    features=matrice[:,1:]
    n_components = 2
    pca = PCA(n_components=n_components)

    x_pca=pca.fit_transform(features)
    x_pca=np.concatenate((x_pca,stories_id.T[:,None]), axis=1)

    return 0


pca_function()
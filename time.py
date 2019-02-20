import spacy
import csv
from timeit import default_timer as timer




class Timer(object):
    def __init__(self, name='Timer'):
        self.name = name

    def __enter__(self):
        self.start = timer()

    def __exit__(self, *args):
        self.end = timer()
        self.duration = self.end - self.start
        print('%s:' % self.name, self.duration)

with Timer('nlp(fr)'):
    nlp = spacy.load('fr')

with Timer('print'):
    print('caca')

with Timer('nlp_article'):
    txt=nlp("Le 10 novembre 1793, il y a eu activation de la déesse de la raison et de la liberté dans l'église Notre-Dame de Paris: https://www.patheos.com/blogs/monkeymind/2017/11/goddess-reason-enthroned.html Cette église était l'emplacement du temple d'Isis à l'époque romaine: Où les initiés dans la déesse se rencontrent encore aujourd'hui: Exactement 225 ans après l'activation de la déesse de la raison, certaines prêtresses de la déesse du mouvement de la résistance sont venues à la surface à Paris et ont procédé à une activation spéciale de la kundalini à l'échelle planétaire. L'activation a eu lieu du 8 au 11 novembre 2018 lors de la réunion des leaders mondiaux à Paris. Le deuxième sous-sol existe, même si la serveuse l'a nié. Cette activation a servi de déclencheur au réveil de la kundalini planétaire où les gens vont enfin se soulever contre l'oppression des forces des ténèbres. Un aspect de cette activation planétaire de la kundalini était que les femmes commencent à récupérer leur énergie sexuelle et à exprimer la beauté de leur corps. L'effet de l'activation a été immédiatement ressenti le 10 novembre au Louvre: Et le lendemain, le 11 novembre, à quelques mètres de Donald Trump: Depuis le 11 novembre 2018, le vortex de la déesse de Paris ne cesse de déclencher l'activation de la kundalini chez tous les êtres humains à la surface de la planète. C’est la raison occulte du succès du mouvement des Gilets jaunes, un mouvement populaire contre toute oppression. Le mouvement se répand rapidement dans le monde entier et devrait avoir un impact considérable sur la situation géopolitique mondiale: Vous devez comprendre que nous sommes maintenant très proches du minimum solaire et qu'au fur et à mesure que l'activité solaire augmentera au cours des mois et des années à venir, l'étincelle révolutionnaire de l'humanité ne fera que s'intensifier: Ils évoquaient l'archétype de Marianne, déesse de la raison et de la liberté, dont l'énergie avait été activée à Paris il y a 225 ans:")

with Timer('nlp_articles'):
    f = open('data.csv', newline='')
    articles = csv.DictReader(f)
    i=0
    tokens=[]
    for row in articles:
        i+=1
        tokens.append(nlp(row['extracted_content']))
        if i==100:
            break
    f.close()


nb_sentences=0
with Timer('count_sentences'):
    for sent in txt.sents:
        nb_sentences+=1

nb_words=0
nb_characters=0

with Timer('count_words'):
    for word in txt:
        if not word.is_punct and not word.like_num:
            nb_words+=1
            nb_characters+=len(word)


print('nb_sentences: ', nb_sentences)
print('nb_words: ', nb_words)
print('nb_characters: ', nb_characters)
print('pour 80000', 27 * 800)

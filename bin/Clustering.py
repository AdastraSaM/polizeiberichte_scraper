#from urllib.request import urlopen
import spacy
from spacy.cli import link
from spacy.util import get_package_path
from gensim.models import LsiModel

import operator
import numpy as np
import os.path
from gensim import corpora
from gensim.models import LsiModel
from gensim.models import CoherenceModel, LdaModel, LsiModel, HdpModel
from gensim.models.coherencemodel import CoherenceModel
import matplotlib.pyplot as plt
import pandas as pd
import gensim
from gensim import corpora, models
import glob

def getElement(Liste):
    return ' '.join(Liste)


def getMyTopic(row, Model):
    try:
        bow = vocab.doc2bow(row)
        Topic = max((Model[bow]), key= lambda x: x[1])
    except:
        return ""
    return Topic[0]

def getMyTopic1(row, Model):
    try:
        bow = vocab.doc2bow(row)
        Topic = max((Model[bow]), key= lambda x: x[1])
    except:
        return ""
    return Topic[1]


# Load Spacy
model_name = "de_core_news_sm"
package_path = get_package_path(model_name)
link(model_name, model_name, force=True, model_path=package_path)
nlp = spacy.load("de_core_news_sm")

# Load News
news = pd.concat([pd.read_csv(f,sep=";",header="infer", encoding ="UTF-8") for f in glob.glob(r"../out/Polizeiberichte_transformed*.csv")], sort = True)
news.drop_duplicates()
news = news.fillna("")

news["Comb_all"] = news["Hauptartikel_lem_clean_no_stop"]+" " + news["Ueberschrift_kombi"]

# Split words before further processing
news["Ueberschrift_kombi"] = news["Ueberschrift_kombi"].apply(lambda x: [item for item in x.split()])
news["Hauptartikel_lem_clean_no_stop"] = news["Hauptartikel_lem_clean_no_stop"].apply(lambda x: [item for item in x.split()])
news["Comb_all"] = news["Comb_all"].apply(lambda x: [item for item in x.split()])

# Clustering
# Split in headline, and main article

dataset = news["Hauptartikel_lem_clean_no_stop"]
dataset_head = news["Ueberschrift_kombi"]

vocab = gensim.corpora.Dictionary(dataset)
vocab_heads = gensim.corpora.Dictionary(dataset_head)

bow_corpus = [vocab.doc2bow(doc) for doc in dataset]
bow_corpus_heads = [vocab.doc2bow(doc) for doc in dataset_head]

tfidf = models.TfidfModel(bow_corpus)
tfidf_head = models.TfidfModel(bow_corpus_heads)

corpus_tfidf = tfidf[bow_corpus]
corpus_tfidf_head = tfidf[bow_corpus_heads]

# Train model and set number of clusters

lsimodelUpdate = models.LsiModel(corpus_tfidf, id2word=vocab, num_topics=10)
# Update/give weight to headline

lsimodelUpdate.add_documents(corpus_tfidf_head, decay=0.5)
lsitopics_update = [[word for word, prob in topic] for topicid, topic in lsimodelUpdate.show_topics(formatted=False)]

# Get classifications and save in new file

news["Topic_LSI_Update"] = news["Comb_all"].apply(getMyTopic, args=[lsimodelUpdate])
news["Prob_LSI_Update"] = news["Comb_all"].apply(getMyTopic1, args=[lsimodelUpdate])


news.to_excel(r"C:\Users\Thomas.Zoellinger\Downloads\MYDF2.xlsx")
# from urllib.request import urlopen
import spacy
from spacy.cli import link
from spacy.util import get_package_path
import pandas as pd
from modules import transformer_tools as tt
from textblob_de import TextBlobDE as TextBlob

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
        Topic = max((Model[bow]), key=lambda x: x[1])
    except:
        return ""
    return Topic[0]


def getMyTopic1(row, Model):
    try:
        bow = vocab.doc2bow(row)
        Topic = max((Model[bow]), key=lambda x: x[1])
    except:
        return ""
    return Topic[1]


def get_sentiment(text):
    """
    :param text: Input Text
    :return: Sentiment for Text
    """
    return TextBlob(text).sentiment[0]


# Load Spacy
model_name = "de_core_news_sm"
package_path = get_package_path(model_name)
link(model_name, model_name, force=True, model_path=package_path)
nlp = spacy.load("de_core_news_sm")

# Load News
news = pd.concat([pd.read_csv(f, sep=";", header="infer", encoding="UTF-8") for f in
                  glob.glob(r"../out/Polizeiberichte_transformed*.csv")], sort=True)
news.drop_duplicates()
news = news.fillna("")

news["Comb_all"] = news["Hauptartikel_lem_clean_no_stop"] + " " + news["Ueberschrift_kombi"]

# Split words before further processing
news["Ueberschrift_kombi"] = news["Ueberschrift_kombi"].apply(lambda x: [item for item in x.split()])
news["Hauptartikel_lem_clean_no_stop"] = news["Hauptartikel_lem_clean_no_stop"].apply(
    lambda x: [item for item in x.split()])
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

for i in range(10, 15):
    lsimodelUpdate = models.LsiModel(corpus_tfidf, id2word=vocab, num_topics=i)
    # Update/give weight to headline

    lsimodelUpdate.add_documents(corpus_tfidf_head, decay=0.5)
    lsitopics_update = [[word for word, prob in topic] for topicid, topic in
                        lsimodelUpdate.show_topics(formatted=False)]

    # Get classifications and save in new file

    news["Topic_LSI_Update " + str(i)] = news["Comb_all"].apply(getMyTopic, args=[lsimodelUpdate])
    news["Prob_LSI_Update " + str(i)] = news["Comb_all"].apply(getMyTopic1, args=[lsimodelUpdate])

# Get Sentiment for each news
news["Comb_all"] = news["Comb_all"].apply(' '.join)
news["Sentiment"] = news["Comb_all"].apply(get_sentiment)

# Save File
cols_to_keep = ['Author', 'Author2', "Hauptartikel", "Link", "Loc1", "Loc2", "Loc3", "Loc4", "Timestamp",
                "Ueberschrift", "Ueberschrift_lem_no_stop", "Topic_LSI_Update 10", "Prob_LSI_Update 10",
                "Topic_LSI_Update 12", "Prob_LSI_Update 12",
                "Topic_LSI_Update 11", "Prob_LSI_Update 11","Prob_LSI_Update 13","Topic_LSI_Update 13",
                "Topic_LSI_Update 14", "Prob_LSI_Update 14",
                "Sentiment"]
news[cols_to_keep].to_excel(r"../out/FinalDF.xlsx", index=False)


# Create File that shows most common words per topic

def get_top_words(column):
    return pd.Series(' '.join(column).lower().split()).value_counts()[:6].index.tolist()


news = news.fillna(value="")
topics = pd.DataFrame(news.groupby(['Topic_LSI_Update 12'])['Ueberschrift_lem_no_stop'].apply(get_top_words))
topics.to_csv(r"../out/Topics_Words_Mapping.csv",
              sep=";",
              encoding="UTF-16",
              header=True,
              quotechar='"',
              index=True)

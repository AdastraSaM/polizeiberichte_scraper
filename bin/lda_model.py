"""
Building an LDA model on the transformed data
"""

import spacy
from spacy.cli import link
from spacy.util import get_package_path

import pandas as pd
import gensim
from gensim import models

from modules import transformer_tools as tt

model_name = "de_core_news_sm"
package_path = get_package_path(model_name)
link(model_name, model_name, force=True, model_path=package_path)
nlp = spacy.load("de_core_news_sm")

if __name__ == "__main__":
    berichte = pd.read_csv("../out/Polizeiberichte_transformed.csv",
                           sep=";",
                           encoding="UTF-8")

    dataset = berichte["Hauptartikel_lemmatized_cleaned_no_stopwords"].apply(lambda x: x.split(" "))
    dataset_head = berichte["Ueberschrift_lemmatized_cleaned_no_stopwords"].apply(lambda x: x.split(" "))


    vocab = gensim.corpora.Dictionary(dataset)
    vocab_heads = gensim.corpora.Dictionary(dataset_head)

    bow_corpus = [vocab.doc2bow(doc) for doc in dataset]
    bow_corpus_heads = [vocab.doc2bow(doc) for doc in dataset_head]

    tfidf = models.TfidfModel(bow_corpus)
    tfidf_head = models.TfidfModel(bow_corpus_heads)

    corpus_tfidf = tfidf[bow_corpus]
    corpus_tfidf_head = tfidf[bow_corpus_heads]


    data = dataset.apply(tt.get_string_from_list)


    #Running LDA using TF-IDF
    lda_model_tfidf = gensim.models.LdaMulticore(corpus_tfidf, num_topics=7, id2word=vocab, passes=2, workers=4)
    for idx, topic in lda_model_tfidf.print_topics(7):
        print('Topic: {} Word: {}'.format(idx, topic))


        def getTopics(lda_model_tfidf, bow_corpus):
            TopicList = []
            for i in range(0, len(lda_model_tfidf.get_document_topics(bow_corpus))):
                TopicList.append(max(lda_model_tfidf.get_document_topics(bow_corpus[i]), key=lambda x: x[1]))
            return TopicList


        TopicList = getTopics(lda_model_tfidf, bow_corpus)



    TopicList = pd.DataFrame(TopicList)
    berichte["TopicNumber"]= TopicList.iloc[:, 0]
    berichte["TopicProb"]= TopicList.iloc[:, 1]
    berichte.head()

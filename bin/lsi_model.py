"""
Builds an LSI model on the transformed data

"""

import pandas as pd
import gensim
from gensim import models
from gensim.models import LsiModel
from gensim.models.coherencemodel import CoherenceModel

from modules import transformer_tools as tt


if __name__ == "__main__":
    berichte = pd.read_csv("../out/Polizeiberichte_transformed.csv",
                           sep=";",
                           encoding="UTF-8")

    dataset = berichte["Hauptartikel_lem_clean_no_stop"].apply(lambda x: str(x).split(" "))
    dataset_head = berichte["Ueberschrift_lem_clean_no_stop"].apply(lambda x: str(x).split(" "))

    vocab = gensim.corpora.Dictionary(dataset)
    vocab_heads = gensim.corpora.Dictionary(dataset_head)

    bow_corpus = [vocab.doc2bow(doc) for doc in dataset]
    bow_corpus_heads = [vocab.doc2bow(doc) for doc in dataset_head]

    tfidf = models.TfidfModel(bow_corpus)
    tfidf_head = models.TfidfModel(bow_corpus_heads)

    corpus_tfidf = tfidf[bow_corpus]
    corpus_tfidf_head = tfidf[bow_corpus_heads]

    dataset = dataset.apply(tt.get_string_from_list)

    lsimodel = LsiModel(corpus=corpus_tfidf, num_topics=7, id2word=vocab)
    lsimodelUpdate = models.LsiModel(corpus_tfidf, id2word=vocab, num_topics=7)
    lsimodelUpdate.add_documents(corpus_tfidf_head, decay=0.5)  # now LSI has been trained on tfidf_corpus + another_tfidf_corpus

    lsitopics = [[word for word, prob in topic] for topicid, topic in lsimodel.show_topics(formatted=False)]
    lsitopics_update = [[word for word, prob in topic] for topicid, topic in lsimodelUpdate.show_topics(formatted=False)]

    print(lsitopics)
    print(lsitopics_update)


    #lsi_coherence = CoherenceModel(topics=lsitopics[:10], texts = berichte["Hauptartikel_lemmatized_cleaned_no_stopwords"], dictionary=vocab, window_size=10).get_coherence()
    #lsi_coherence_Update = CoherenceModel(topics=lsitopics_update[:10], texts = berichte["Hauptartikel_lemmatized_cleaned_no_stopwords"], dictionary=vocab, window_size=10).get_coherence()


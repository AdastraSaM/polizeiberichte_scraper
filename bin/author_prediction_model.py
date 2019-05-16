"""
Prediction of the author from the article text
"""

import pickle
import seaborn as sns
import pandas as pd

import matplotlib.pyplot as plt

import sys

article_text = sys.argv[1]

model_pkl = open(r"..\resources\pickled\SVC_author_classifier.pkl", 'rb')
model = pickle.load(model_pkl)
model_pkl.close()

transformer_count_pkl = open(r"..\resources\pickled\count_transformer.pkl", "rb")
count_transformer = pickle.load(transformer_count_pkl)
transformer_count_pkl.close()

transformer_tfidf_pkl = open(r"..\resources\pickled\tfidf_transformer.pkl", "rb")
tfidf_transformer = pickle.load(transformer_tfidf_pkl)
transformer_tfidf_pkl.close()

article_text_transf = tfidf_transformer.transform(count_transformer.transform([article_text]))

probas = model.predict_proba(article_text_transf)[0]

plotdata = pd.DataFrame()
plotdata["class"] = model.classes_
plotdata["probas"] = probas

sns.barplot(x="class", y="probas", data=plotdata)
plt.show()


# Create File that shows most common words per topic
import glob
import pandas as pd

pd.set_option('max_colwidth', 60)
import folium
from folium.plugins import HeatMap
import numpy as np


def get_top_words(column):
    return pd.Series(' '.join(column).lower().split()).value_counts()[:6].index.tolist()


news = pd.read_excel(r"../out/FinalDF.xlsx")

news = news.fillna(value="")
topics = pd.DataFrame(news.groupby(['Topic_LSI_Update 12'])['Ueberschrift_lem_no_stop'].apply(get_top_words))
topics.to_csv(r"../out/Topics_Words_Mapping.csv",
              sep=";",
              encoding="UTF-16",
              header=True,
              quotechar='"',
              index=True)

streets_mapping = pd.read_csv(r"../out/streets_mapping_full.csv", sep=";", header="infer", encoding="UTF-8")

# news["Hauptartikel"] = news["Hauptartikel"].str.lower()

adress_list = list(streets_mapping["Address"])
counts = []
for adress in adress_list:
    counts.append(news["Hauptartikel"].str.count(adress).sum())
series_counts = pd.Series(counts)
streets_mapping["Counts"] = series_counts

brand_number = streets_mapping.loc[streets_mapping["Address"] == "Brand"].index[0]
streets_mapping = streets_mapping.drop(brand_number)
streets_mapping.sort_values(by="Counts", ascending=False)

print(streets_mapping["Long"].head())

streets_mapping.to_csv(r"../out/Street_Counts.csv",
                       sep=";",
                       header=True,
                       encoding="UTF-16",
                       quotechar='"',
                       index=True)

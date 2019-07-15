"""
Cleaning, transformation and feature engineering on the scraped data
"""

import pandas as pd
from modules import transformer_tools as tt
import glob

if __name__ == "__main__":
    # Read the scraped raw data from file
    berichte = pd.concat(
        [pd.read_csv(f, sep=";", header="infer", encoding="UTF-8") for f in glob.glob(r"../out/ffm_news*.csv")])

    # Drop rows where words are included in the filter/not wanted (remove news that are not crime related)
    Topiclist = tt.get_topicfilter_list()
    berichte = tt.FilterTopics(berichte, "Ueberschrift", Topiclist)

    # Drop rows where the main article consists of less than 250 characters
    berichte = berichte[berichte["Hauptartikel"].str.len() > 250]

    # Parse timestamp strings as datetime
    berichte["Timestamp"] = tt.parse_timestamp(berichte["Timestamp"])

    # Clean headlines
    berichte["Ueberschrift"] = tt.clean_headline(berichte["Ueberschrift"])

    # Drop rows with NANs
    berichte = berichte.dropna()
    # Rearrange index
    berichte.index = range(len(berichte))

    # Extract locations
    berichte["Ort"], berichte["Sekundaerer Ort"] = tt.extract_location_from_headline(berichte["Ueberschrift"])

    # Get locations only from news that are younger because they have a more reliable format
    Loc_Tuple = tt.get_tuple_of_locations(berichte["Ort"][berichte["Year"] > 2008])
    print(Loc_Tuple)

    berichte["Loc1"], berichte["Loc2"], berichte["Loc3"], berichte["Loc4"] = tt.get_locations_by_tuple(
        berichte["Ueberschrift"], Loc_Tuple)

    # Remove location from headline
    berichte["Ueberschrift"] = berichte["Ueberschrift"].str.replace(' |'.join(list(Loc_Tuple)), '')

    # Extract author from description
    berichte["Author"] = tt.extract_author(berichte["Hauptartikel"])

    # Extract author from the end of the article
    berichte.index = range(len(berichte))
    berichte["Author2"] = tt.extract_author_from_end(berichte["Hauptartikel"])

    # Extract the authors from the end in a new column to remove them from the main article
    authors = berichte['Hauptartikel'].str[-40:-1].str.extract(r"\((.*?)\)", expand=False)
    authors = authors.fillna("")
    berichte['Hauptartikel'] = tt.remove_word_from_other_column(berichte['Hauptartikel'], authors)

    # Remove all dates from headline
    berichte["Ueberschrift"] = berichte["Ueberschrift"].str.replace(r'\d+', '')

    # Clean headline
    berichte["Ueberschrift_clean"] = tt.clean_column(berichte["Ueberschrift"])

    # Lemmatize words in headline text
    berichte["Ueberschrift_lem"] = tt.lemmatize_document_list(berichte["Ueberschrift_clean"])
    # Remove stopwords from headline
    berichte["Ueberschrift_lem_no_stop"] = berichte["Ueberschrift_lem"].apply(tt.remove_stopwords)

    # Split compound words
    berichte["Ueberschrift_split"] = tt.split_compound_words(berichte["Ueberschrift_lem_no_stop"])
    # Clean headline
    berichte["Ueberschrift_clean2"] = tt.clean_column(berichte["Ueberschrift_split"])
    # Lemmatize words in headline text
    berichte["Ueberschrift_lem2"] = tt.lemmatize_document_list(berichte["Ueberschrift_clean2"])
    # Clean headline again after lemmatization
    berichte["Ueberschrift_lem_clean2"] = tt.clean_column(berichte["Ueberschrift_lem2"])
    # Remove stopwords from headline
    # berichte["Ueberschrift_lem_clean2"].fillna(value="", inplace=True)

    berichte["Ueberschrift_lem_clean_no_stop"] = berichte["Ueberschrift_lem_clean2"].apply(tt.remove_stopwords)
    # Combine with original Headline
    berichte["Ueberschrift_kombi"] = berichte["Ueberschrift_lem_clean_no_stop"] + " " + berichte[
        "Ueberschrift_lem_no_stop"]
    # Remove duplicates from Uberschirft_kombi
    berichte["Ueberschrift_kombi"] =berichte["Ueberschrift_kombi"].str.split(' ').apply(set).str.join(' ')

    # Clean main article
    berichte["Hauptartikel_clean"] = tt.clean_column(berichte["Hauptartikel"])
    # Lemmatize words in main article text
    berichte["Hauptartikel_lem"] = tt.lemmatize_document_list(berichte["Hauptartikel_clean"])
    # Clean main article again after lemmatization
    berichte["Hauptartikel_lemm_clean"] = tt.clean_column(berichte["Hauptartikel_lem"])
    # Remove stopwords from main article
    berichte["Hauptartikel_lem_clean_no_stop"] = berichte["Hauptartikel_lemm_clean"].apply(tt.remove_stopwords)
    # Remove author from main article
    berichte['Hauptartikel_lem_clean_no_stop'] = berichte['Hauptartikel_lem_clean_no_stop'].replace(
        to_replace=r'\b' + berichte['Author'] + r'\b', value='', regex=True)

    for i, (name, group) in enumerate(berichte.groupby('Year')):
        group.to_csv(r"../out/Polizeiberichte_transformed{}.csv".format(i),
                     sep=";",
                     encoding="UTF-8",
                     header=True,
                     quotechar='"',
                     index=False)

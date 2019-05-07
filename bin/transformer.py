"""
Cleaning, transformation and feature engineering on the scraped data
"""

import pandas as pd
from modules import transformer_tools as tt


if __name__ == "__main__":
    # Read the scraped raw data from file
    berichte = pd.read_csv(r"../out/Polizeiberichte_raw.csv",
                           sep=";",
                           encoding="UTF-8")


    # Parse timestamp strings as datetime
    berichte["Timestamp"] = tt.parse_timestamp(berichte["Timestamp"])

    # Extract and clean headlines
    berichte = tt.extract_date_from_column(berichte, "Ueberschrift")
    berichte["Ueberschrift"] = tt.clean_headline(berichte["Ueberschrift"])

    # Extract locations
    berichte["Ort"], berichte["Sekundaerer Ort"] = tt.extract_location_from_headline(berichte["Ueberschrift"])
    # Remove location from headline
    berichte["Ueberschrift"] = berichte["Ueberschrift"].apply(lambda x: x[x.find(":") + 2:])

    # Extract place and author from description
    berichte["Author"] = tt.extract_author(berichte["Hauptartikel"])

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
    berichte["Ueberschrift_lem_clean_no_stop"] = berichte["Ueberschrift_lem_clean2"].apply(tt.remove_stopwords)
    # Combine with original Headline
    berichte["Ueberschrift_kombi"] = berichte["Ueberschrift_lem_clean_no_stop"]+" " +berichte["Ueberschrift_lem_no_stop"]


    # Clean main article
    berichte["Hauptartikel_clean"] = tt.clean_column(berichte["Hauptartikel"])
    # Lemmatize words in main article text
    berichte["Hauptartikel_lem"] = tt.lemmatize_document_list(berichte["Hauptartikel_clean"])
    # Clean main article again after lemmatization
    berichte["Hauptartikel_lemm_clean"] = tt.clean_column(berichte["Hauptartikel_lem"])
    # Remove stopwords from main article
    berichte["Hauptartikel_lem_clean_no_stop"] = berichte["Hauptartikel_lemm_clean"].apply(tt.remove_stopwords)
    # Remove author from main article
    berichte['Hauptartikel_lem_clean_no_stop'] = berichte['Hauptartikel_lem_clean_no_stop'].replace(to_replace=r'\b' + berichte['Author'] + r'\b', value='', regex=True)


    # Export transformed data to file
    berichte.to_csv(r"../out/Polizeiberichte_transformed.csv",
                    sep=";",
                    encoding="UTF-8",
                    header=True,
                    quotechar='"',
                    index=False)
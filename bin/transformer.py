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

    # Extract description
    berichte["Beschreibung"] = tt.extract_description(berichte["Hauptartikel"])

    # Remove start from the main article
    berichte["Hauptartikel"] = tt.remove_start_from_main_article(berichte["Hauptartikel"])

    # Extract place and author from description
    berichte["Author"] = tt.extract_author(berichte["Beschreibung"])

    # Remove author, which is the name of the author in brackets. This is the last word in the string
    berichte["Beschreibung"] = berichte["Beschreibung"].apply(lambda x: "".join(x.split(" ")[:-1]))

    # Remove all dates from headline
    berichte["Ueberschrift"] = berichte["Ueberschrift"].str.replace(r'\d+', '')
    # Clean headline
    berichte["Ueberschrift_cleaned"] = tt.clean_column(berichte["Ueberschrift"])
    # Lemmatize words in headline text
    berichte["Ueberschrift_lemmatized"] = tt.lemmatize_document_list(berichte["Ueberschrift_cleaned"])
    # Clean headline again after lemmatization
    berichte["Ueberschrift_lemmatized_cleaned"] = tt.clean_column(berichte["Ueberschrift_lemmatized"])
    # Remove stopwords from headline
    berichte["Ueberschrift_lemmatized_cleaned_no_stopwords"] = berichte["Ueberschrift_lemmatized_cleaned"].apply(tt.remove_stopwords)


    # Clean main article
    berichte["Hauptartikel_cleaned"] = tt.clean_column(berichte["Hauptartikel"])
    # Lemmatize words in main article text
    berichte["Hauptartikel_lemmatized"] = tt.lemmatize_document_list(berichte["Hauptartikel_cleaned"])
    # Clean main article again after lemmatization
    berichte["Hauptartikel_lemmatized_cleaned"] = tt.clean_column(berichte["Hauptartikel_lemmatized"])
    # Remove stopwords from main article
    berichte["Hauptartikel_lemmatized_cleaned_no_stopwords"] = berichte["Hauptartikel_lemmatized_cleaned"].apply(tt.remove_stopwords)


    # Export transformed data to file
    berichte.to_csv(r"../out/Polizeiberichte_transformed.csv",
                    sep=";",
                    encoding="UTF-8",
                    header=True,
                    quotechar='"',
                    index=False)
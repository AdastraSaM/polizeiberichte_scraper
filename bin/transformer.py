"""
Cleaning, transformation and feature engineering on the scraped data
"""

import pandas as pd
from modules import transformer_tools as st


if __name__ == "__main__":
    # Read the scraped raw data from file
    berichte = pd.read_csv(r"../out/Polizeiberichte_raw.csv",
                           sep=";",
                           encoding="UTF-8")


    # Parse timestamp strings as datetime
    berichte["Timestamp"] = st.parse_timestamp(berichte["Timestamp"])

    # Extract and clean headlines
    berichte = st.extract_date_from_column(berichte, "Ueberschrift")
    berichte["Ueberschrift"] = st.clean_headline(berichte["Ueberschrift"])

    # Extract locations
    berichte["Ort"], berichte["Sekundaerer Ort"] = st.extract_location_from_headline(berichte["Ueberschrift"])
    # Remove location from headline
    berichte["Ueberschrift"] = berichte["Ueberschrift"].apply(lambda x: x[x.find(":") + 2:])

    # Extract description
    berichte["Beschreibung"] = st.extract_description(berichte["Hauptartikel"])

    # Remove start from the main article
    berichte["Hauptartikel"] = st.remove_start_from_main_article(berichte["Hauptartikel"])

    # Extract place and author from description
    berichte["Author"] = st.extract_author(berichte["Beschreibung"])

    # Remove author, which is the name of the author in brackets. This is the last word in the string
    berichte["Beschreibung"] = berichte["Beschreibung"].apply(lambda x: "".join(x.split(" ")[:-1]))

    # Export transformed data to file
    berichte.to_csv(r"../out/Polizeiberichte_transformed.csv",
                    sep=";",
                    encoding="UTF-8",
                    header=True,
                    quotechar='"',
                    index=False)
"""
Scraping of the raw data from the websites
"""

import pandas as pd
from modules import scraping_tools as st

HOSTNAME = "https://www.presseportal.de"
START_PAGE = HOSTNAME + "/blaulicht/nr/4970"
COUNT_OF_SUBSEQUENT_SITES = 1

if __name__ == "__main__":
    # Extract data from the web pages
    all_sites = st.get_all_sites(START_PAGE, COUNT_OF_SUBSEQUENT_SITES)
    corpus = st.get_corpus_from_link(all_sites)
    link_for_all_news = st.get_links_from_corpus(corpus)
    all_headlines, all_main_articles, all_websites, all_timestamps = st.get_news_from_links(link_for_all_news)

    # Save data in dataframe
    berichte_raw = pd.DataFrame({"Timestamp": all_timestamps,
                       "Ueberschrift": all_headlines,
                       "Hauptartikel": all_main_articles,
                       "Link": all_websites})

    # Remove control characters
    st.remove_control_characters(berichte_raw, "Ueberschrift")
    st.remove_control_characters(berichte_raw, "Hauptartikel")

    berichte_raw.drop_duplicates(inplace=True)

    # Export data
    berichte_raw.to_csv(r"../out/Polizeiberichte_raw.csv",
                        sep=";",
                        encoding="UTF-8",
                        header=True,
                        quotechar='"',
                        index=False)
"""
Scraping of the raw data from the websites
"""

import pandas as pd
from modules import scraping_tools as st

HOSTNAME = "https://www.presseportal.de"
START_PAGE = HOSTNAME + "/blaulicht/nr/4970"
COUNT_OF_SUBSEQUENT_SITES = 220


def scrape_from_web():
    """
    Reads the raw article data from the websites and returns them in a dataframe.
    :return: A dataframe containing the timestamps, headlines, articles and link.
    """
    all_sites = st.get_all_sites(START_PAGE, COUNT_OF_SUBSEQUENT_SITES)
    corpus = st.get_corpus_from_link(all_sites)
    link_for_all_news = st.get_links_from_corpus(corpus)
    all_headlines, all_main_articles, all_websites, all_timestamps = st.get_news_from_links(link_for_all_news)
    # Save data in dataframe
    scraped_berichte = pd.DataFrame({"Timestamp": all_timestamps,
                                 "Ueberschrift": all_headlines,
                                 "Hauptartikel": all_main_articles,
                                 "Link": all_websites})
    return scraped_berichte


if __name__ == "__main__":
    # Extract data from the web pages
    berichte_raw = scrape_from_web()

    # Remove control characters
    st.remove_control_characters(berichte_raw, "Ueberschrift")
    st.remove_control_characters(berichte_raw, "Hauptartikel")

    berichte_raw.drop_duplicates(inplace=True)

    # Export data to file
    berichte_raw.to_csv(r"../out/Polizeiberichte_raw.csv",
                        sep=";",
                        encoding="UTF-8",
                        header=True,
                        quotechar='"',
                        index=False)
import pandas as pd
from modules import scraping_tools as st

HOSTNAME = "https://www.presseportal.de"
START_PAGE = HOSTNAME + "/blaulicht/nr/4970"
COUNT_OF_SUBSEQUENT_SITES = 1

if __name__ == "__main__":
    # Extract data from the web pages
    all_sites, sites_not_found = st.get_all_sites(START_PAGE, COUNT_OF_SUBSEQUENT_SITES)
    corpus, other = st.get_corpus_from_link(all_sites)
    link_for_all_news = st.get_links_from_corpus(corpus)
    all_headlines, all_main_articles, all_websites, links_not_found = st.get_news_from_links(link_for_all_news)

    # Save data in dataframe
    df = pd.DataFrame({"Headline": all_headlines, "Hauptartikel": all_main_articles, "Link": all_websites})

    # Clean and transform data
    st.remove_control_characters(df, "Headline")
    st.remove_control_characters(df, "Hauptartikel")

    df = st.extract_date_from_column(df, "Headline")
    df = st.clean_headline(df)
    df = st.extract_location_from_headline(df)
    df.drop_duplicates(inplace=True)

    # Export data
    df.to_csv(r"out\Test.csv", sep=";", encoding="UTF-8", header=True, quotechar='"')
import pandas as pd
from modules import scraping_tools as st

HOSTNAME = "https://www.presseportal.de"
START_PAGE = HOSTNAME + "/blaulicht/nr/4970"
COUNT_OF_SUBSEQUENT_SITES = 20

if __name__ == "__main__":
    # Extract data from the web pages
    all_sites = st.get_all_sites(START_PAGE, COUNT_OF_SUBSEQUENT_SITES)
    corpus = st.get_corpus_from_link(all_sites)
    link_for_all_news = st.get_links_from_corpus(corpus)
    all_headlines, all_main_articles, all_websites, all_timestamps = st.get_news_from_links(link_for_all_news)

    # Save data in dataframe
    df = pd.DataFrame({"Timestamp": all_timestamps,
                       "Ueberschrift": all_headlines,
                       "Hauptartikel": all_main_articles,
                       "Link": all_websites})

    # Remove control characters
    st.remove_control_characters(df, "Ueberschrift")
    st.remove_control_characters(df, "Hauptartikel")

    # Parse timestamp strings as datetime
    df["Timestamp"] = st.parse_timestamp(df["Timestamp"])

    # Extract and clean headlines
    df = st.extract_date_from_column(df, "Ueberschrift")
    df["Ueberschrift"] = st.clean_headline(df["Ueberschrift"])

    # Extract locations
    df["Ort"], df["Sekundaerer Ort"] = st.extract_location_from_headline(df["Ueberschrift"])
    # Remove location from headline
    df["Ueberschrift"] = df["Ueberschrift"].apply(lambda x: x[x.find(":")+2:])

    # Extract description
    df["Beschreibung"] = st.extract_description(df["Hauptartikel"])

    # Remove start from the main article
    df["Hauptartikel"] = st.remove_start_from_main_article(df["Hauptartikel"])

    # Extract place and author from description
    df["Author"] = st.extract_author(df["Beschreibung"])

    # Remove author, which is the name of the author in brackets
    df["Beschreibung"] = df["Beschreibung"].apply(lambda x: "".join(x.split(" ")[:-1]))

    df.drop_duplicates(inplace=True)

    # Export data
    df.to_csv(r"../out/Polizeiberichte.csv",
              sep=";",
              encoding="UTF-8",
              header=True,
              quotechar='"',
              index=False)
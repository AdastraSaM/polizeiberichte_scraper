from modules import scraping_tools as st
import pandas as pd
from modules import scraping_tools as st

if __name__ == "__main__":
    Links = open(r"../resources/ffm_links_00_19.csv", "r")
    all_headlines, all_main_articles, all_websites, all_timestamps = st.get_news_from_links(Links)
    scraped_berichte = pd.DataFrame({"Timestamp": all_timestamps,
                                     "Ueberschrift": all_headlines,
                                     "Hauptartikel": all_main_articles,
                                     "Link": all_websites})

    st.remove_control_characters(scraped_berichte, "Ueberschrift")
    st.remove_control_characters(scraped_berichte, "Hauptartikel")

    scraped_berichte.drop_duplicates(inplace=True)

    scraped_berichte.to_csv(r"../out/Polizeiberichte_raw_full_02_19.csv",
                            sep=";",
                            encoding="UTF-8",
                            header=True,
                            quotechar='"',
                            index=False)

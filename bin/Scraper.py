from urllib.request import urlopen
from bs4 import BeautifulSoup
import pandas as pd
import time


HOSTNAME = "https://www.presseportal.de"
START_PAGE = HOSTNAME + "/blaulicht/nr/4970"
SLEEP_SECS = 1
COUNT_OF_SUBSEQUENT_SITES = 20


def get_pages_not_found(all_pages_not_found):
    """
    Find links for all given pages. Pages that throw an error are returned as a separate list.

    :param all_pages_not_found: A list of pages for which links are to be found.
    :return: A list of links and a list of pages for which links could not be found
    """
    
    links = []
    links_not_found = []
    for page in all_pages_not_found:
        print(page)
        try:
            bs = BeautifulSoup(page, "html.parser")
            tag = bs.find(class_="pagination-next")
            links.append(HOSTNAME + tag.attrs["data-url"][1:])
            time.sleep(SLEEP_SECS)
        except:
            time.sleep(SLEEP_SECS)
            links_not_found.append("HOSTNAME" + tag.attrs["data-url"][1:])
    return links, links_not_found


def get_all_sites(start, count_of_subsequent_sites):
    """
    Get the links of a given number of subsequent sites from a given start page.

    :param start: The page from which to begin.
    :param count_of_subsequent_sites: The number of subsequent sites to be explored.
    :return: a list of links to pages and a list of pages for which no link could be found
    """

    print("Getting sites...")
    pages = []
    pages_not_found = []
    html = urlopen(start)
    successes = 0
    no_successes = 0
    for i in range(1, count_of_subsequent_sites + 1):
        try:
            bs = BeautifulSoup(html, "html.parser")
            tag = bs.find(class_="pagination-next")
            pages.append(HOSTNAME + tag.attrs["data-url"][1:])
            html = urlopen(HOSTNAME + tag.attrs["data-url"][1:])
            time.sleep(SLEEP_SECS)
            successes += 1
        except:
            time.sleep(SLEEP_SECS)
            no_successes += 1
            pages_not_found.append(HOSTNAME + tag.attrs["data-url"][1:])
        time.sleep(SLEEP_SECS)
        print("get_all_sites progress " + str(round(((i / count_of_subsequent_sites) * 100), 2)) + "%" + " successes: " + str(
            successes) + " no_successes: " + str(no_successes))
    links, links_still_not_found = get_pages_not_found(pages_not_found)

    for link in links:
        pages.append(link)

    print("Getting sites complete.")
    return pages, links_still_not_found


def get_corpus_from_link(links):
    """
    Get the corpus for each given link. Links for which no corpus could be found are stored in a separate list.

    links -- a list of links
    """
    print("Getting corpuses...")
    main_site_corpuses = []
    remaining_sites = []
    for link in links:
        try:
            html = urlopen(link)
            bs = BeautifulSoup(html, "html.parser")
            links = bs.find_all("h3", class_="news-headline-clamp")
            main_site_corpuses.append(links)
        except:
            remaining_sites.append(link)

    print("Getting corpuses complete.")
    return main_site_corpuses, remaining_sites


def get_links_from_corpus(corpus):
    """
    Extract the link to each article for a given corpus.

    :param corpus: the corpus for which the article link is to be extracted.
    :return: a list of links
    """
    print("Getting links from corpus...")
    links = []
    for site in corpus:
        for headline in site:
            article = (headline.findChild("")["href"])
            links.append(article)
    print("Got links.")
    return links


def find_main_article_for_given_text(corpus):
    """
    Find the main article for a given news-corpus.

    :param corpus: The corpus for which to determine the main article
    :return: A main article
    """
    print("Finding main article for corpus...")
    main_article = ""
    for element in corpus:
        main_article += "\n" + "".join(element.findAll(text=True))
        main_article
    opening_phrase = "Polizeipräsidium Frankfurt am Main"
    closing_phrase = "Rückfragen bitte an:"
    main_article = (
        main_article[main_article.find(opening_phrase) + len(opening_phrase):main_article.rfind(closing_phrase)])
    print("Main article found.")
    return main_article


def remove_control_characters(df, column):
    """
    Replaces all control characters in a given dataframe column by a space.

    :param df: A dataframe containing control characters
    :param column: A column of the dataframe
    :return: The dataframe with all control characters replaced by spaces.
    """
    print("Removing control characters...")
    df[column].replace({r"\t": " ", r"\n": " ", r"\n": " "}, regex=True, inplace=True)
    print("Control characters removed.")
    return df


def get_news_from_links(links):
    """
    Extracts the headline and main article text from each given link. Links that could not be found are placed in a
    separate list.

    :param links: A list of links to articles
    :return: The headline string, the main article text, a list for which no headline and article text could be found
    """
    print("Getting news text from links...")
    counter = 0
    counter2 = 0
    news = []
    headlines = []
    main_article_text = []
    links_not_found = []
    for link in links:
        print("Finding main article for link {}".format(link))
        html = urlopen(HOSTNAME + link)
        bs = BeautifulSoup(html, "html.parser")
        whole_text = bs.find_all("p")
        main_article_text += [find_main_article_for_given_text(whole_text)]
        headlines += [bs.find("h1").get_text()]
        counter += 1
        news.append(HOSTNAME + link)
        time.sleep(SLEEP_SECS)
        print("found-> " + str(counter) + "/" + str(counter2) + " of " + str(len(links)))
    print("Got news text.")
    return headlines, main_article_text, news, links_not_found


def extract_date_from_column(df, column):
    """
    Extracts the date from a given column. If a row does not contain a date, the date of the previous row is used.

    :param df: A dataframe with dates
    :param column: A column that contains the dates
    :return:
    """
    print("Extracting date from column {}".format(column))
    df["Date"] = df.Headline.str.extract('(\d+)')
    print("Date extracted")
    df["Date"] = df["Date"].apply(lambda x: "{}{}".format("20", x))
    df["Date"].fillna(method="ffill", inplace=True)
    # If first value was missing, propagate first known value backwards
    df["Date"].fillna(method="bfill", inplace=True)


    # Convert dates to datetime
    df["Date"] = df["Date"].apply(lambda x: pd.to_datetime(str(x), format="%Y%m%d") if len(x)==8 else "")

    # Remove extracted date from the original column
    df[column] = df[column].str.replace("\d+", "")
    print("Extraction complete.")
    return df


def clean_headline(df):
    """
    Removes leading and trailing whitespaces from the Headline column and removes unnecessary parts.

    :param df: The dataframe to be cleaned
    :return: Dataframe with cleaned headline column
    """
    print("Cleaning headlines...")
    df["Headline"] = df["Headline"].apply(lambda st: st.lstrip())
    # Remove beginning from Headline (remove 4digit Number)
    df["Headline"] = df["Headline"].str.replace("\d{4}", "", regex=True)
    df["Headline"] = df["Headline"].str.replace("\d{3}", "", regex=True)
    df["Headline"] = df["Headline"].str.replace("POL-F:", "")

    df["Headline"] = df["Headline"].apply(lambda st: st.lstrip())
    print("Headlines cleaned.")
    return df


def find_nth_occurrence(string, substring, n):
    """
    Finds the n-th occurence of a given substring in a given string.

    :param string: The string that contains occurences of the substring
    :param substring: The substring to search for
    :param n: The desired count of the occurence
    :return: The index of the n-th occurence of the substring in the string
    """
    i = 0
    while n >= 0:
        n -= 1
        i = string.find(substring, i + 1)
    return i


def extract_location_from_headline(df):
    """
    Extracts the location from the headline. The location begins after the first occurence of a ":".

    If there are multiple locations, these are separated by a space, "/" or "-", then all secondary locations (those
    after the first separator) will be stored in a new column Location2.
    :param df: The dataframe containing the Headline column.
    :return: The original dataframe with the location information for each row in new columns called Location and
    Location2.
    """
    print("Extracting location from headlines...")
    df["Location"] = df["Headline"].apply(lambda st: st[0:st.find(":")])
    df["Location"] = df["Location"].str.replace("/", " ")
    df["Location"] = df["Location"].str.replace("-", " ")
    df["Location"] = df["Location"].str.replace("Frankfurt", "")
    df["Location"] = df["Location"].apply(lambda x: x.lstrip())

    # Remove headline
    df["Headline"] = df["Headline"].apply(lambda st: st[st.find(":") + 1:])
    df["Headline"] = df["Headline"].apply(lambda st: st.lstrip())

    # Extract second location
    df["Location2"] = df["Location"].str.split(" ").str[1]

    # Clean location
    df["Location"] = df["Location"].str.split(" ").str[0]

    # Remove start of Hauptartikel e.g. Frankfurt (ots) - (ka)
    df["Headline"].apply(lambda st: st[st.find(" - ") + 2:find_nth_occurrence(st, " ", 3)])

    # Extract start of Hauptartikel
    df["Beschreibung"] = df["Hauptartikel"].apply(lambda st: st[0:find_nth_occurrence(st, ")", 1) + 1])

    # Remove start from Hauptartikel
    df["Hauptartikel"] = df["Hauptartikel"].apply(lambda st: st[find_nth_occurrence(st, ")", 1) + 1:])
    print("Extraction complete.")
    return df


if __name__ == "__main__":
    # Extract data from the web pages
    all_sites, sites_not_found = get_all_sites(START_PAGE, COUNT_OF_SUBSEQUENT_SITES)
    corpus, other = get_corpus_from_link(all_sites)
    link_for_all_news = get_links_from_corpus(corpus)
    all_headlines, all_main_articles, all_websites, links_not_found = get_news_from_links(link_for_all_news)

    # Save data in dataframe
    df = pd.DataFrame({"Headline": all_headlines, "Hauptartikel": all_main_articles, "Link": all_websites})

    # Clean and transform data
    remove_control_characters(df, "Headline")
    remove_control_characters(df, "Hauptartikel")

    df = extract_date_from_column(df, "Headline")
    df = clean_headline(df)
    df = extract_location_from_headline(df)
    df.drop_duplicates(inplace=True)

    # Export data
    df.to_csv("Test.csv", sep="@", encoding="UTF-8", header=True, quotechar='"')
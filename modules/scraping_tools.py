from urllib.request import urlopen
from bs4 import BeautifulSoup
import time
import pandas as pd
from dateutil.parser import parse

SLEEP_SECS = 1
HOSTNAME = "https://www.presseportal.de"
START_PAGE = HOSTNAME + "/blaulicht/nr/4970"
COUNT_OF_SUBSEQUENT_SITES = 1


def get_pages_not_found(all_pages_not_found):
    """
    Find links for all given pages.

    :param all_pages_not_found: A list of pages for which links are to be found.
    :return: A list of links
    """

    links = []
    links_not_found = []
    for page in all_pages_not_found:
        print(page)
        bs = BeautifulSoup(page, "html.parser")
        tag = bs.find(class_="pagination-next")
        links += [HOSTNAME + tag.attrs["data-url"][1:]]
        time.sleep(SLEEP_SECS)
    return links


def get_all_sites(start, count_of_subsequent_sites):
    """
    Get the links of a given number of subsequent sites from a given start page.

    :param start: The page from which to begin.
    :param count_of_subsequent_sites: The number of subsequent sites to be explored.
    :return: a list of links to pages
    """

    print("Getting sites...")
    pages = []
    pages_not_found = []
    html = urlopen(start)
    successes = 0
    no_successes = 0
    for i in range(1, count_of_subsequent_sites + 1):
        bs = BeautifulSoup(html, "html.parser")
        tag = bs.find(class_="pagination-next")
        pages += [HOSTNAME + tag.attrs["data-url"][1:]]
        html = urlopen(HOSTNAME + tag.attrs["data-url"][1:])
        time.sleep(SLEEP_SECS)
        successes += 1

        print("get_all_sites progress " + str(
            round(((i / count_of_subsequent_sites) * 100), 2)) + "%" + " successful: " + str(
            successes) + " unsuccessful: " + str(no_successes))
    links = get_pages_not_found(pages_not_found)

    for link in links:
        pages.append(link)
    print("Getting sites complete.")
    return pages


def get_corpus_from_link(links):
    """
    Get the corpus for each given link.

    links -- a list of links
    """
    print("Getting corpuses...")
    main_site_corpuses = []
    for link in links:
        html = urlopen(link)
        bs = BeautifulSoup(html, "html.parser")
        links = bs.find_all("h3", class_="news-headline-clamp")
        main_site_corpuses.append(links)

    print("Getting corpuses complete.")
    return main_site_corpuses


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
    :return: The headline string, the main article text, and timestamp of the article
    """
    print("Getting data from links...")
    counter = 0
    news = []
    headlines = []
    main_article_text = []
    timestamp = []
    for link in links:
        print("Finding main article for link {}".format(link))
        html = urlopen(HOSTNAME + link)
        bs = BeautifulSoup(html, "html.parser")
        whole_text = bs.find_all("p")
        main_article_text += [find_main_article_for_given_text(whole_text)]
        headlines += [bs.find("h1").get_text()]
        timestamp += [bs.find("p", class_="date").text]
        counter += 1
        news.append(HOSTNAME + link)
        time.sleep(SLEEP_SECS)
        print("found-> " + str(counter) + " of " + str(len(links)))
    print("Got data.")
    return headlines, main_article_text, news, timestamp


def parse_timestamp(timestamps):
    """
    Parses a pandas series of timestamps in the format dd.mm.YYYY - hh:MM into datetime

    :param timestamps: A pandas series of timestamps to be parsed
    :return: The transformed series as a list
    """
    # Remove dash and parse as datetime
    timestamps_parsed = [parse(x.replace("– ", "")) for x in timestamps]
    return timestamps_parsed


def extract_date_from_column(df, column):
    """
    Extracts the date from a given column. If a row does not contain a date, the date of the previous row is used.

    :param df: A dataframe with dates
    :param column: A column that contains the dates
    :return:
    """
    print("Extracting date from column {}".format(column))
    df["Date"] = df["Ueberschrift"].str.extract(r'(\d+)')
    print("Date extracted")
    df["Date"] = df["Date"].apply(lambda x: "{}{}".format("20", x))
    df["Date"].fillna(method="ffill", inplace=True)
    # If first value was missing, propagate first known value backwards
    df["Date"].fillna(method="bfill", inplace=True)

    # Convert dates to datetime
    df["Date"] = df["Date"].apply(lambda x: pd.to_datetime(str(x), format="%Y%m%d") if len(x) == 8 else "")

    # Remove extracted date from the original column
    df[column] = df[column].str.replace(r"\d+", "")
    print("Extraction complete.")
    return df


def clean_headline(headlines):
    """
    Removes leading and trailing whitespaces from the Headline column and removes unnecessary parts.

    :param headlines: A list of headlines
    :return: A list of cleaned headlines
    """
    print("Cleaning headlines...")
    headlines = headlines.apply(lambda x: x.lstrip())
    # Remove beginning from Headline (remove 4digit Number)
    headlines = headlines.str.replace(r"\d{4}", "", regex=True)
    headlines = headlines.str.replace(r"\d{3}", "", regex=True)
    headlines = headlines.str.replace("POL-F:", "")

    headlines = headlines.apply(lambda x: x.lstrip(" -"))
    print("Headlines cleaned.")
    return headlines


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


def extract_location_from_headline(headlines):
    """
    Extracts the location from the headlines. The location begins after the first occurence of a ":".

    If there are multiple locations, these are separated by a space, "/" or "-", then all secondary locations (those
    after the first separator) will be stored in a new column Location2.
    :param headlines: A list of headlines.
    :return: A list of Locations and a second list of secondary locations
    """
    print("Extracting location from headlines...")
    locations = headlines.apply(lambda st: st[0:st.find(":")])
    locations = locations.str.replace("/", " ")
    locations = locations.str.replace("-", " ")
    locations = locations.str.replace("Frankfurt", "")
    locations = locations.apply(lambda x: x.lstrip())

    # Extract second location
    secondary_locations = locations.str.split(" ").str[1]

    # Clean location
    locations = locations.str.split(" ").str[0]

    print("Extraction complete.")
    return locations, secondary_locations


def extract_description(main_article):
    """
    Extracts the descriptions from the main article text.

    :param main_article: A list of article texts
    :return: A list of descriptions
    """
    descriptions = main_article.apply(lambda x: x[0 : find_nth_occurrence(x, ")", 1) + 1])

    # Strip leading and trailing spaces from descriptions
    descriptions = descriptions.apply(lambda x: x.strip())


    return descriptions


def remove_start_from_main_article(main_articles):
    """
    Removes the beginning of the main articles which is not needed.
    :param main_articles: A list of main article texts
    :return: The given list but with the unnecessary beginning cleaned from the texts
    """
    return main_articles.apply(lambda x: x[find_nth_occurrence(x, ")", 1) + 1:])


def extract_place(descriptions):
    """
    Extracts the places from the descriptions
    :param descriptions: A list of descriptions
    :return: The list of places
    """
    places = pd.Series([t.split(" ")[0] for t in descriptions])
    return places


def extract_author(descriptions):
    """
    Extracts the authors from the given list of descriptions
    :param descriptions: A list of descriptions
    :return: The list of authors
    """
    authors = pd.Series([t.split(" ")[len(t.split(" ")) - 1] for t in descriptions])
    # Replace all authors with incorrect format (hinting to a mistake in the description structure) by a dummy value
    authors.replace(r'\(*+\)', '(Unknown)', inplace=True)
    # Remove the brackets from the author token
    authors = authors.map(lambda x: x.lstrip(r'(').rstrip(r')'))
    return authors

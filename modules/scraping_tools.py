from urllib.request import urlopen
from bs4 import BeautifulSoup
import time
import re
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait

SLEEP_SECS = 0.3
HOSTNAME = "https://www.presseportal.de"
START_PAGE = HOSTNAME + "/blaulicht/nr/4970"


def get_all_sites(start, count_of_subsequent_sites):
    """
    Get the links of a given number of subsequent sites from a given start page.

    :param start: The page from which to begin.
    :param count_of_subsequent_sites: The number of subsequent sites to be explored.
    :return: a list of links to pages
    """

    print("Getting sites...")
    pages = []
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


def get_news_from_links(links, use_host=False,timeout=10):
    """
    Extracts the headline and main article text from each given link. Links that could not be found are placed in a
    separate list.

    :param links: A list of links to articles
    :return: The headline string, the main article text, and timestamp of the article
    """
    print("Getting data from links...")
    # Set Hostname to an empty string by default
    if use_host ==False:
        HOSTNAME = ""
    links = list(links)
    lenght = len(links)
    counter = 0
    news = []
    headlines = []
    main_article_texts = []
    timestamp = []
    word_list = ["Rückfragen bitte an", 'Rufbereitschaft hat', "Original-Content von", "Bereitschaftsdienst",
                "ots-Originaltext"]

    for link in links:
        print("Parsing article from link {}".format(link))
        try:
            html = urlopen(HOSTNAME + link, timeout=timeout)
            bs = BeautifulSoup(html, "html.parser")
        except:
            try:
                html = urlopen(HOSTNAME + link, timeout=timeout)
                bs = BeautifulSoup(html, "html.parser")
            except:
                try:
                    browser = webdriver.Chrome(executable_path=r'C:\Users\webdrivers\chromedriver.exe')
                    browser.get(link)
                    source = browser.page_source
                    bs = BeautifulSoup(source, 'html')
                except:
                    pass

        article = bs.find("article")
        timestamp += [article.find("p", class_="date").text]
        headlines += [article.find("h1").get_text()]

        # Get text for the current article and add it to the list of texts
        main_article_text = ""
        # The first two <p> tags are timestamp and headline
        for tag in article.find_all("p")[3:]:
            # If the end is not reached, add text
            main_article_text += tag.text
            # Stop adding data when the end of the article text is reached
            if (findFirstOccurence(wordList=word_list, bigString=tag.text)) != (-1):
                break
        # Cut the end from the news if a word from the word_list is found
        num_last_word = findFirstOccurence(word_list, bigString=main_article_text)
        main_article_text = main_article_text[0:num_last_word]
        main_article_texts += [main_article_text]

        counter += 1
        news.append(HOSTNAME + link)
        time.sleep(SLEEP_SECS)
        print("found-> " + str(counter) + " of " + str(lenght))
    print("Got data.")
    return headlines, main_article_texts, news, timestamp

def findFirstOccurence(wordList, bigString, startIndex=0):
    """

    :param wordList: List of Words that are to be found
    :param bigString: String where the words shall be found
    :param startIndex: default is 0
    :return: Position of the string that got found, return "-1" if nothing found
    """
    try:
        num = (re.search('|'.join(wordList), bigString[startIndex:]).start())
    except:
        num = -1
    return num

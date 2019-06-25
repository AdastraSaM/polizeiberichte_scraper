"""
Utility functions for the cleaning of the scraped data, and transformation, extraction for feature engineering
"""

import pandas as pd
import re
from dateutil.parser import parse

from modules.ext import char_split

import spacy
from spacy.cli import link
from spacy.util import get_package_path

model_name = "de_core_news_sm"
package_path = get_package_path(model_name)
link(model_name, model_name, force=True, model_path=package_path)
nlp = spacy.load("de_core_news_sm")

# File of Stopwords to be excluded
STOPWORDS_FILE = "Stopwords1.txt"
# File of Topics to be excluded
TopicFilter = "Themenfilter.txt"


def parse_timestamp(timestamps):
    """
    Parses a pandas series of timestamps in the format dd.mm.YYYY - hh:MM into datetime

    :param timestamps: A pandas series of timestamps to be parsed
    :return: The transformed series as a list
    """
    # Remove dash and parse as datetime
    timestamps_parsed = [parse(x.replace("– ", "")) for x in timestamps]
    return timestamps_parsed


def clean_headline(headlines):
    """
    Removes leading and trailing whitespaces from the headline column and removes unnecessary parts.

    :param headlines: A list of headlines
    :return: A list of cleaned headlines
    """
    print("Cleaning headlines...")
    headlines = headlines.apply(lambda x: x.lstrip())
    # Remove beginning from Headline (remove 4digit Number)
    headlines = headlines.str.replace(r"\d{4}", "", regex=True)
    headlines = headlines.str.replace(r"\d{3}", "", regex=True)
    headlines = headlines.str.replace(r"\d+", "")
    headlines = headlines.str.replace("POL-F:", "")
    headlines = headlines.str.replace("Frankfurt-", "")

    headlines = headlines.str.replace("/", " ")
    headlines = headlines.str.replace("-", " ")
    headlines = headlines.str.replace(":", " : ")

    headlines = headlines.str.replace("Frankfurter Berg", "Frankfurter-Berg", n=1)
    headlines = headlines.str.replace("Frankfurter Weihnachtsmarkt", "Frankfurter-Weihnachtsmarkt", n=1)
    headlines = headlines.str.replace("Frankfurter Bahnhofsviertel", "Bahnhofsviertel", n=1)
    headlines = headlines.str.replace("Nieder Erlenbach", "Nieder-Erlenbach", n=1)
    headlines = headlines.str.replace("Nieder Eschbach", "Nieder-Eschbach", n=1)
    headlines = headlines.str.replace("BAB", "Bundesautobahn", n=1)
    headlines = headlines.str.replace("Bad Homburg", "Bad-Homburg", n=1)
    headlines = headlines.str.lower()

    headlines = headlines.apply(lambda x: x.lstrip(" -"))
    print("Headlines cleaned.")
    return headlines


def find_nth_occurrence(string, substring, n):
    """
    Finds the index of the n-th occurence of a given substring in a given string. Counting starts at 0, i.e. the n=0
    gives the index of the first occurrence.
    If the substring is not contained in the string, the result is -1.
    The empty string is part of every string, so if the substring is the empty string, the result will always be n+1.

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


def get_tuple_of_locations(Col):
    """
    Gets a lowercase tuple of the words that appear at least 10 times in the column and are longer than 2 characters.
    In this context used to extract locations
    :param Col: Column with the locations
    :return:
    """
    Col = Col.str.lower()
    Locations = Col.value_counts() > 10
    Locations = list(pd.DataFrame(Col.value_counts()[Locations]).index.values)
    Locations = ' '.join(Locations).split()
    Locations = [item for item in Locations if len(item) > 2]
    Locations = tuple(Locations)
    return Locations


def extract_location_from_headline(headlines):
    """
    Extracts the location from the headlines. The location begins after the first occurence of a ":".

    If there are multiple locations, these are separated by a space, "/" or "-", then all secondary locations (those
    after the first separator) will be stored in a new column Location2.
    :param headlines: A list of headlines.
    :return: A list of Locations and a second list of secondary locations
    """
    print("Extracting location from headlines...")
    locations = headlines.apply(lambda x: x[0:x.find(":")])
    locations = locations.str.replace("/", " ")
    locations = locations.str.replace("-", " ")
    locations = locations.str.replace("frankfurt ", "", n=1)
    locations = locations.str.replace("frankfurter berg", "frankfurter-berg", n=1)
    locations = locations.str.replace("frankfurter weihnachtsmarkt", "frankfurter-weihnachtsmarkt", n=1)
    locations = locations.str.replace("frankfurter bahnhofsviertel", "bahnhofsviertel", n=1)
    locations = locations.str.replace("nieder erlenbach", "nieder-erlenbach", n=1)
    locations = locations.str.replace("nieder eschbach", "nieder-eschbach", n=1)
    locations = locations.str.replace("bab", "bundesautobahn", n=1)
    locations = locations.str.replace("bad homburg", "bad-homburg", n=1)
    locations = locations.str.replace("alt sachsenhausen", "alt-sachsenhausen", n=1)
    locations = locations.apply(lambda x: x.lstrip())

    # Extract second location
    secondary_locations = locations.str.split(" ").str[1]

    # Clean location
    locations = locations.str.split(" ").str[0]

    print("Extraction complete.")
    return locations, secondary_locations


def get_locations_by_tuple(col, tuple):
    """
    Extracts locations from a given column for a given list
    :param col: Column containing the locations
    :param tuple: Tuple with the locations to be extracted
    :return: 3 columns of locations
    """
    col = col.apply(lambda x: [j for j in x.split() if j.lower() in tuple])
    col1 = col.str[0]
    col2 = col.str[1]
    col3 = col.str[2]
    col4 = col.str[3]
    return col1, col2, col3,col4


def remove_word_from_other_column(main_col, words_col1):
    """
    Removes word from a given column provided by a second column
    :param main_col: Column where the words should be removed from
    :param words_col1: Column containing the words that should be removed
    :return: Original column without the words that should be removed
    """

    return [e.replace(k, '') for e, k in zip(main_col.astype('str'), words_col1.astype('str'))]


def extract_description(main_articles):
    """
    Extracts the descriptions from the main article text.

    :param main_articles: A list of article texts
    :return: A list of descriptions
    """
    descriptions = main_articles.apply(lambda x: x[0: find_nth_occurrence(x, ")", 1) + 1])

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
    :param descriptions: A pandas column
    :return: The list of authors
    """
    # Get the 10 first characters
    authors = descriptions.str[:10]
    # Find ")" and get the text before
    authors = authors.apply(lambda x: x[:find_nth_occurrence(x, ")", 0) + 1])
    # Removing everything non-alphanumeric
    authors = [re.sub("[^a-zA-Z äöüÄÖÜß]+", "", x) for x in authors]
    # Convert to Pandas Series again
    authors = pd.Series(authors)
    # Strip white spaces or return empty string and convert to lower
    authors = authors.apply(lambda x: x.lstrip() if pd.notnull(x) else "").str.lower()
    return authors


def lemmatize_as_string(document):
    """
    Creates a string of all lemmatized words in the given document, the separator is space.
    :param document: A document to be lemmatized.
    :return: A string of lemmatized words, separated by spaces
    """
    try:
        doc = nlp(text=document)
        lemmatized_words = []
        for token in doc:
            lemmatized_words.append(token.lemma_)
        lemmatized_document = " ".join(lemmatized_words)
        return lemmatized_document
    except:
        return ""


def get_stopword_list():
    """
    Gets the stopwords from the file.
    :return: List of stopwords
    """
    stopwords = open(r"../resources/%s" % STOPWORDS_FILE, "r")
    stopwords = list(stopwords)
    stopwords = list(map(lambda s: s.strip(), stopwords))
    return stopwords


def get_topicfilter_list():
    """
    Gets the words that should not be included in topics from the file.
    :return: List of words/topics
    """
    Themenfilter = open(r"../resources/%s" % TopicFilter, "r")
    Themenfilter = list(Themenfilter)
    Themenfilter = list(map(lambda s: s.strip(), Themenfilter))
    return Themenfilter


def FilterTopics(DF, Column_Name, Filterwords_List):
    """
    Keeps only the rows of a Dataframe where the filter words are not present in the specified column
    :param DF: DataFrame which should be filtered
    :param Column_Name: Name of the Column of the Dataframe which should be filtered. Must be given as a string
    :param Filterwords_List: List of topics/words that should be filtered
    :return:
    """
    return DF[~DF[Column_Name].str.lower().str.contains('|'.join(Filterwords_List), na=False)]


def get_string_from_list(liste):
    """
    Turns the given list into a string, with the list elements separated by spaces.
    :param liste: A list of elements that can be turned into strings
    :return: A string of the list elements separated by spaces
    """
    return ' '.join([str(x) for x in liste])


def remove_stopwords(document):
    """
    Removes all stopwords from document.
    :param document: A document containing words.
    :return: The document without the stopwords
    """
    stopwords = get_stopword_list()
    words = document.split(" ")
    words_without_stopwords = [x for x in words if x not in stopwords]
    document_no_stopwords = get_string_from_list(words_without_stopwords)
    return document_no_stopwords


def clean_column(documents):
    """
    Clean the whole column: remove white spaces, digits and transform to lowercase.
    :param documents: A list of documents to clean
    :return: A list of cleaned documents
    """
    # Removing everything non-alphanumeric
    # documents.fillna(value="", inplace=True)
    documents = [re.sub("[^a-zA-Z äöüÄÖÜß]+", " ", x) for x in documents]
    # Converting to lowercase
    documents = [x.lower() for x in documents]
    documents = pd.Series(documents)
    # Remove digits
    documents = documents.str.replace(r'\d+', '')
    return documents


def split_compound_words(documents):
    """
    Split German compound words in all documents into their parts
    :param documents: A list of documents
    :return: A list of strings, where each string consists of the words from the input with compound words split.
    Word separator in the strings is a space.
    """
    # Create a matrix of the words from the documents. The n-th col contains the n-th word in the document.
    words = documents.str.split(' ', expand=True)
    words = words.rename(columns=lambda x: "string_{}".format(x + 1))

    for word_position in words.columns:
        documents = words[word_position]
        documents.fillna(value="", inplace=True)

        # Splitting
        compound_words_split = documents.apply(char_split.split_compound)
        compound_words_split = [item[0] for item in compound_words_split]
        compound_words_split = pd.DataFrame(compound_words_split)
        compound_words_split.columns = ["confidence", "first_word", "second_word"]

        # For non-compound words first_word and second_word are equal. To evade doubling these words, remove second word
        compound_words_split.loc[
            compound_words_split["first_word"] == compound_words_split["second_word"], "second_word"] = ""

        # Only keep words that received positive confidence from the splitter
        words_to_drop = compound_words_split["confidence"] < 0
        compound_words_split[words_to_drop] = " "
        compound_words_split["combined"] = compound_words_split["first_word"] + " " + compound_words_split[
            "second_word"]
        words[word_position] = compound_words_split["combined"]
        words.fillna(value="", inplace=True)
    # Connect the words for each document into a long, space-separated string
    words["all_combined"] = words.apply(' '.join, axis=1)
    return words["all_combined"]


def lemmatize_document_list(documents):
    """
    Lemmatizes the words in all given documents.
    :param documents: A list of documents made up of words to be lemmatized.
    :return: A list where each item is a string of the lemmatized words for each document, separated by spaces.
    """
    # Lemmatize
    lemmatized_berichte = [lemmatize_as_string(x) for x in documents]
    # Make everything lowercase
    lemmatized_berichte = [x.lower() for x in lemmatized_berichte]
    # Concatenate as a long string
    lemmatized_berichte = [' '.join(x.split(" ")) for x in lemmatized_berichte]
    return lemmatized_berichte
"""
Utility functions for the cleaning of the scraped data, and transformation, extraction for feature engineering
"""

import pandas as pd
import re
from dateutil.parser import parse

from modules.ext import char_split

import spacy
from spacy.cli import link
from spacy.util import get_package_path

model_name = "de_core_news_sm"
package_path = get_package_path(model_name)
link(model_name, model_name, force=True, model_path=package_path)
nlp = spacy.load("de_core_news_sm")

# File of Stopwords to be excluded
STOPWORDS_FILE = "Stopwords1.txt"
# File of Topics to be excluded
TopicFilter = "Themenfilter.txt"


def parse_timestamp(timestamps):
    """
    Parses a pandas series of timestamps in the format dd.mm.YYYY - hh:MM into datetime

    :param timestamps: A pandas series of timestamps to be parsed
    :return: The transformed series as a list
    """
    # Remove dash and parse as datetime
    timestamps_parsed = [parse(x.replace("– ", "")) for x in timestamps]
    return timestamps_parsed


def clean_headline(headlines):
    """
    Removes leading and trailing whitespaces from the headline column and removes unnecessary parts.

    :param headlines: A list of headlines
    :return: A list of cleaned headlines
    """
    print("Cleaning headlines...")

    headlines = headlines.str.lstrip()
    # Remove beginning from Headline (remove 4digit Number)
    headlines = headlines.str.replace(r"\d{4}", "", regex=True)
    headlines = headlines.str.replace(r"\d{3}", "", regex=True)
    headlines = headlines.str.replace(r"\d+", "")
    headlines = headlines.str.replace("POL-F:", "")
    headlines = headlines.str.replace("Frankfurt-", "")

    headlines = headlines.str.replace("/", " ")
    headlines = headlines.str.replace("-", " ")
    headlines = headlines.str.replace(":", " : ")

    headlines = headlines.str.replace("Frankfurter Berg", "Frankfurter-Berg", n=1)
    headlines = headlines.str.replace("Frankfurter Weihnachtsmarkt", "Frankfurter-Weihnachtsmarkt", n=1)
    headlines = headlines.str.replace("Frankfurter Bahnhofsviertel", "Bahnhofsviertel", n=1)
    headlines = headlines.str.replace("Nieder Erlenbach", "Nieder-Erlenbach", n=1)
    headlines = headlines.str.replace("Nieder Eschbach", "Nieder-Eschbach", n=1)
    headlines = headlines.str.replace("BAB", "Bundesautobahn", n=1)
    headlines = headlines.str.replace("Bad Homburg", "Bad-Homburg", n=1)
    headlines = headlines.str.replace("Bergen Enkheim", "Bergen-Enkheim", n=1)


    headlines = headlines.str.lower()

    headlines = headlines.str.strip(" -")
    print("Headlines cleaned.")
    return headlines


def find_nth_occurrence(string, substring, n):
    """
    Finds the index of the n-th occurence of a given substring in a given string. Counting starts at 0, i.e. the n=0
    gives the index of the first occurrence.
    If the substring is not contained in the string, the result is -1.
    The empty string is part of every string, so if the substring is the empty string, the result will always be n+1.

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


def get_tuple_of_locations(Col):
    """
    Gets a lowercase tuple of the words that appear at least 10 times in the column.
    In this context used to extract locations
    :param Col: Column with the locations
    :return:
    """
    Col = Col.str.lower()
    Locations = Col.value_counts() > 10
    Locations = list(pd.DataFrame(Col.value_counts()[Locations]).index.values)
    Locations = ' '.join(Locations).split()
    Locations = [item for item in Locations if len(item) > 2]
    Locations = tuple(Locations)
    return Locations


def extract_location_from_headline(headlines):
    """
    Extracts the location from the headlines. The location begins after the first occurence of a ":".

    If there are multiple locations, these are separated by a space, "/" or "-", then all secondary locations (those
    after the first separator) will be stored in a new column Location2.
    :param headlines: A list of headlines.
    :return: A list of Locations and a second list of secondary locations
    """
    print("Extracting location from headlines...")
    locations = headlines.apply(lambda x: x[0:x.find(":")])
    locations = locations.str.replace("/", " ")
    locations = locations.str.replace("-", " ")
    locations = locations.str.replace("frankfurt ", "", n=1)
    locations = locations.str.replace("frankfurter berg", "frankfurter-berg", n=1)
    locations = locations.str.replace("frankfurter weihnachtsmarkt", "frankfurter-weihnachtsmarkt", n=1)
    locations = locations.str.replace("frankfurter bahnhofsviertel", "bahnhofsviertel", n=1)
    locations = locations.str.replace("nieder erlenbach", "nieder-erlenbach", n=1)
    locations = locations.str.replace("nieder eschbach", "nieder-eschbach", n=1)
    locations = locations.str.replace("bab", "bundesautobahn", n=1)
    locations = locations.str.replace("bad homburg", "bad-homburg", n=1)
    locations = locations.str.replace("alt sachsenhausen", "alt-sachsenhausen", n=1)
    locations = locations.str.replace("bad Homburg", "bad-homburg", n=1)
    locations = locations.str.replace("bergen enkheim", "bergen-enkheim", n=1)
    locations = locations.str.replace("westend nord", "westend-nord", n=1)

    locations = locations.apply(lambda x: x.lstrip())

    # Extract second location
    secondary_locations = locations.str.split(" ").str[1]

    # Clean location
    locations = locations.str.split(" ").str[0]

    print("Extraction complete.")
    return locations, secondary_locations


def get_locations_by_tuple(col, tuple):
    """
    Extracts locations from a given column for a given list
    :param col: Column containing the locations
    :param tuple: Tuple with the locations to be extracted
    :return: 3 columns of locations
    """
    col = col.apply(lambda x: [j for j in x.split() if j.lower() in tuple])
    col1 = col.str[0]
    col2 = col.str[1]
    col3 = col.str[2]
    col4 = col.str[3]
    return col1, col2, col3,col4


def remove_word_from_other_column(main_col, words_col1):
    """
    Removes word from a given column provided by a second column
    :param main_col: Column where the words should be removed from
    :param words_col1: Column containing the words that should be removed
    :return: Original column without the words that should be removed
    """

    return [e.replace(k, '') for e, k in zip(main_col.astype('str'), words_col1.astype('str'))]


def extract_description(main_articles):
    """
    Extracts the descriptions from the main article text.

    :param main_articles: A list of article texts
    :return: A list of descriptions
    """
    descriptions = main_articles.apply(lambda x: x[0: find_nth_occurrence(x, ")", 1) + 1])

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
    :param descriptions: A pandas column
    :return: The list of authors
    """
    # Get the 10 first characters
    authors = descriptions.str[:10]
    # Find ")" and get the text before
    authors = authors.apply(lambda x: x[:find_nth_occurrence(x, ")", 0) + 1])
    # Removing everything non-alphanumeric
    authors = [re.sub("[^a-zA-Z äöüÄÖÜß]+", "", x) for x in authors]
    # Convert to Pandas Series again
    authors = pd.Series(authors)
    # Strip white spaces or return empty string and convert to lower
    authors = authors.apply(lambda x: x.lstrip() if pd.notnull(x) else "").str.lower()
    return authors

def extract_author_from_end(hauptartikel):
    """
    Extracts the authors from the end of the article
    :param hauptartikel: the column of the main news article
    :return: column with the extracted authors
    """
    authors = hauptartikel.str[-60:-1].str.extract(r"\((.*?)\)", expand=False)
    authors = authors.fillna("")
    authors = [re.sub("[^a-zA-Z äöüÄÖÜß]+", "", x) for x in authors]
    authors = [re.sub("Telefon", "", x) for x in authors]
    authors = [re.sub("Tel.", "", x) for x in authors]
    authors = pd.Series(authors)
    authors = authors.apply(lambda x: x.strip() if pd.notnull(x) else "").str.lower()
    authors = pd.Series(authors)
    return authors

def lemmatize_as_string(document):
    """
    Creates a string of all lemmatized words in the given document, the separator is space.
    :param document: A document to be lemmatized.
    :return: A string of lemmatized words, separated by spaces
    """
    try:
        doc = nlp(text=document)
        lemmatized_words = []
        for token in doc:
            lemmatized_words.append(token.lemma_)
        lemmatized_document = " ".join(lemmatized_words)
        return lemmatized_document
    except:
        return ""


def get_stopword_list():
    """
    Gets the stopwords from the file.
    :return: List of stopwords
    """
    stopwords = open(r"../resources/%s" % STOPWORDS_FILE, "r")
    stopwords = list(stopwords)
    stopwords = list(map(lambda s: s.strip(), stopwords))
    return stopwords


def get_topicfilter_list():
    """
    Gets the words that should not be included in topics from the file.
    :return: List of words/topics
    """
    Themenfilter = open(r"../resources/%s" % TopicFilter, "r")
    Themenfilter = list(Themenfilter)
    Themenfilter = list(map(lambda s: s.strip(), Themenfilter))
    return Themenfilter


def FilterTopics(DF, Column_Name, Filterwords_List):
    """
    Keeps only the rows of a Dataframe where the filter words are not present in the specified column
    :param DF: DataFrame which should be filtered
    :param Column_Name: Name of the Column of the Dataframe which should be filtered. Must be given as a string
    :param Filterwords_List: List of topics/words that should be filtered
    :return:
    """
    return DF[~DF[Column_Name].str.lower().str.contains('|'.join(Filterwords_List), na=False)]


def get_string_from_list(liste):
    """
    Turns the given list into a string, with the list elements separated by spaces.
    :param liste: A list of elements that can be turned into strings
    :return: A string of the list elements separated by spaces
    """
    return ' '.join([str(x) for x in liste])


def remove_stopwords(document):
    """
    Removes all stopwords from document.
    :param document: A document containing words.
    :return: The document without the stopwords
    """
    stopwords = get_stopword_list()
    words = document.split(" ")
    words_without_stopwords = [x for x in words if x not in stopwords]
    document_no_stopwords = get_string_from_list(words_without_stopwords)
    return document_no_stopwords


def clean_column(documents):
    """
    Clean the whole column: remove white spaces, digits and transform to lowercase.
    :param documents: A list of documents to clean
    :return: A list of cleaned documents
    """
    # Removing everything non-alphanumeric
    # documents.fillna(value="", inplace=True)
    documents = [re.sub("[^a-zA-Z äöüÄÖÜß]+", " ", x) for x in documents]
    # Converting to lowercase
    documents = [x.lower() for x in documents]
    documents = pd.Series(documents)
    # Remove digits
    documents = documents.str.replace(r'\d+', '')
    return documents


def split_compound_words(documents):
    """
    Split German compound words in all documents into their parts
    :param documents: A list of documents
    :return: A list of strings, where each string consists of the words from the input with compound words split.
    Word separator in the strings is a space.
    """
    # Create a matrix of the words from the documents. The n-th col contains the n-th word in the document.
    words = documents.str.split(' ', expand=True)
    words = words.rename(columns=lambda x: "string_{}".format(x + 1))

    for word_position in words.columns:
        documents = words[word_position]
        documents.fillna(value="", inplace=True)

        # Splitting
        compound_words_split = documents.apply(char_split.split_compound)
        compound_words_split = [item[0] for item in compound_words_split]
        compound_words_split = pd.DataFrame(compound_words_split)
        compound_words_split.columns = ["confidence", "first_word", "second_word"]

        # For non-compound words first_word and second_word are equal. To evade doubling these words, remove second word
        compound_words_split.loc[
            compound_words_split["first_word"] == compound_words_split["second_word"], "second_word"] = ""

        # Only keep words that received positive confidence from the splitter
        words_to_drop = compound_words_split["confidence"] < 0
        compound_words_split[words_to_drop] = " "
        compound_words_split["combined"] = compound_words_split["first_word"] + " " + compound_words_split[
            "second_word"]
        words[word_position] = compound_words_split["combined"]
        words.fillna(value="", inplace=True)
    # Connect the words for each document into a long, space-separated string
    words["all_combined"] = words.apply(' '.join, axis=1)
    return words["all_combined"]


def lemmatize_document_list(documents):
    """
    Lemmatizes the words in all given documents.
    :param documents: A list of documents made up of words to be lemmatized.
    :return: A list where each item is a string of the lemmatized words for each document, separated by spaces.
    """
    # Lemmatize
    lemmatized_berichte = [lemmatize_as_string(x) for x in documents]
    # Make everything lowercase
    lemmatized_berichte = [x.lower() for x in lemmatized_berichte]
    # Concatenate as a long string
    lemmatized_berichte = [' '.join(x.split(" ")) for x in lemmatized_berichte]
    return lemmatized_berichte

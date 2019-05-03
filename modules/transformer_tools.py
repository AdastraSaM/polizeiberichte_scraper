"""
Utility functions for the cleaning of the scraped data, and transformation, extraction for feature engineering
"""


import pandas as pd
from dateutil.parser import parse


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
    df["Datum"] = df["Ueberschrift"].str.extract(r'(\d+)')
    print("Date extracted")
    df["Datum"] = df["Datum"].apply(lambda x: "{}{}".format("20", x))
    df["Datum"].fillna(method="ffill", inplace=True)
    # If first value was missing, propagate first known value backwards
    df["Datum"].fillna(method="bfill", inplace=True)

    # Convert dates to datetime
    df["Datum"] = df["Datum"].apply(lambda x: pd.to_datetime(str(x), format="%Y%m%d") if len(x) == 8 else "")

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
    locations = locations.str.replace("Frankfurt", "")
    locations = locations.apply(lambda x: x.lstrip())

    # Extract second location
    secondary_locations = locations.str.split(" ").str[1]

    # Clean location
    locations = locations.str.split(" ").str[0]

    print("Extraction complete.")
    return locations, secondary_locations


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
    :param descriptions: A list of descriptions
    :return: The list of authors
    """
    authors = pd.Series([t.split(" ")[len(t.split(" ")) - 1] for t in descriptions])
    # Replace all authors with incorrect format (hinting to a mistake in the description structure) by a dummy value
    authors.replace(r'\(*+\)', '(Unknown)', inplace=True)
    # Remove the brackets from the author token
    authors = authors.map(lambda x: x.lstrip(r'(').rstrip(r')'))
    return authors

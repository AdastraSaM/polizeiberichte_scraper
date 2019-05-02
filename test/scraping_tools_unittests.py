import unittest
import pandas as pd
from modules import scraping_tools as st


class ScrapingToolsTest(unittest.TestCase):

    def setUp(self):
        self.test_berichte = pd.read_csv(r"testdata/Polizeiberichte_testdata.csv",
                                         sep=";",
                                         encoding="UTF-8")
        print("Testdata loaded.")

    def test_parse_timestamp(self):
        pass

    def test_extract_date_from_column(self):
        pass

    def test_clean_headline(self):
        pass

    def test_find_nth_occurence(self):
        pass

    def test_extract_location_from_headline(self):
        pass

    def test_extract_description(self):
        pass

    def test_extract_place(self):
        self.assertEqual(list(st.extract_place(self.test_berichte["Beschreibung"])),
                         ["Frankfurt", "Frankfurt"])

    def test_extract_author(self):
        self.assertEqual(list(st.extract_author(self.test_berichte["Beschreibung"])),
                          ["fue", "ka"])


if __name__ == "__main__":
    unittest.main()

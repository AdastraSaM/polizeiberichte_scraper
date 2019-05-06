import unittest

class TransformerToolsTest():

    def test_parse_timestamp(self):
        self.fail()

    def test_extract_date_from_column(self):
        self.fail()

    def test_clean_headline(self):
        self.fail()

    def test_find_nth_occurrence(self):
        self.assertEqual(st.find_nth_occurrence("aaaaa", "a", 0), 1)
        self.assertEqual(st.find_nth_occurrence("aaaaa", "a", 1), 2)
        self.assertEqual(st.find_nth_occurrence("bbbbb", "a", 1), -1)
        self.assertEqual(st.find_nth_occurrence("abc abc abc", "abc", 0), 0)
        self.assertEqual(st.find_nth_occurrence("abc:-abc:abc ", ":", 0), 3)


        self.assertNotEqual(st.find_nth_occurrence("bbbbb", "a", 1), 2)

    def test_extract_location_from_headline(self):
        self.fail()

    def test_extract_description(self):
        self.fail()

    def test_remove_start_from_article(self):
        self.fail()

    def test_extract_place(self):
        self.assertEqual(list(st.extract_place(self.test_berichte["Beschreibung"])),
                         ["Frankfurt", "Frankfurt"])

    def test_extract_author(self):
        self.assertEqual(list(st.extract_author(self.test_berichte["Beschreibung"])),
                          ["fue", "ka"])

    def test_lemmatize_as_string(self):
        self.fail()

    def test_get_stopword_list(self):
        self.fail()

    def test_get_string_from_list(self):
        self.fail()

    def test_remove_stopwords(self):
        self.fail()

    def test_clean_column(self):
        self.fail()

    def test_split_compound_words(self):
        self.fail()

    def test_lemmatize_document_list(self):
        self.fail()


if __name__ == "__main__":
    unittest.main()

import unittest
import pandas as pd
from modules import transformer_tools as tt

from dateutil.parser import parse


class TransformerToolsTest(unittest.TestCase):
    def test_parse_timestamp(self):
        self.assertEqual(tt.parse_timestamp(["05.05.2019 – 10:47",
                                             "06.10.2018 – 1:47",
                                             "04.05.2016 - 00:00"]),
                         [parse("05.05.2019 10:47"),
                          parse("06.10.2018 1:47"),
                          parse("04.05.2016 00:00")]
                         )

    def test_extract_date_from_column(self):
        df_with_dates = pd.DataFrame(columns=["datecol", "othercol"])
        df_with_dates["datecol"] = ["There is some date (06.05.2019) in this string", "There is no date here"]
        df_with_dates["othercol"] = ["This is some other data", 12345]

        df_expected = pd.DataFrame(df_with_dates)
        df_expected["Datum"] = ["20190506", ""]

        df_extracted = tt.extract_date_from_column(df_with_dates, "datecol")

        result = df_extracted.equals(df_expected)

        self.assertEqual(result, True)

    def test_clean_headline(self):
        headline = pd.Series(["POL-F: 190512 - 522 Frankfurt-Sachsenhausen: Fußgängerin angefahren",
                             "POL-F: 190512 - 521 Frankfurt-Bahnhofsviertel: 27-Jährige flüchtet nach Auffahrunfall"])
        cleaned_headlines = tt.clean_headline(headline)

        expected = ["12 -  Frankfurt-Sachsenhausen: Fußgängerin angefahren",
                    "12 -  Frankfurt-Bahnhofsviertel: 27-Jährige flüchtet nach Auffahrunfall"]

        result = (cleaned_headlines == expected).all()

        self.assertTrue(result)

    def test_find_nth_occurrence(self):
        self.assertEqual(tt.find_nth_occurrence("aaaaa", "a", 0), 1)
        self.assertEqual(tt.find_nth_occurrence("aaaaa", "a", 1), 2)
        self.assertEqual(tt.find_nth_occurrence("bbbbb", "a", 1), -1)
        self.assertEqual(tt.find_nth_occurrence("abc abc abc", "abc", 0), 0)
        self.assertEqual(tt.find_nth_occurrence("abc:-abc:abc ", ":", 0), 3)

        self.assertNotEqual(tt.find_nth_occurrence("bbbbb", "a", 1), 2)

    def test_extract_location_from_headline(self):
        test_headlines = pd.Series(["Frankfurt-Heddernheim: Polizei sucht Zeugen!",
                                    "Frankfurt-Bornheim: Hund entlaufen",
                                    "Bahnhofsviertel: Kein Frankfurt vor dem Ort"])
        found_primary, found_secondary = tt.extract_location_from_headline(test_headlines)
        expected_primary = pd.Series(["Heddernheim", "Bornheim", "Bahnhofsviertel"])

        result = (found_primary == expected_primary).all()
        self.assertTrue(result)

    def test_extract_author(self):
        found_authors = tt.extract_author(pd.Series([" (ka) In der Nacht von Montag auf Dienstag brannten zwei Autos in der Ilbenstädter Straße, Ecke Nußbaumstraße (Frankfurt).",
                                          " (fue) Am Dienstag, den [abc] 23. April 2019, etwa (...) gegen 17.00 Uhr"]))
        expected_authors = ["ka", "fue"]

        result = (found_authors == expected_authors).all()
        self.assertTrue(result)

    def test_lemmatize_as_string(self):
        test_text = "Wie bereits bekannt, wurde bei einem Übungstauchen der Frankfurter  Feuerwehr," \
                    " im Bereich der Alten Brücke," \
                    " im Main eine 250 kg  Fliegerbombe aus dem 2. Weltkrieg entdeckt."
        lemmatized_test_text = tt.lemmatize_as_string(test_text)
        expected_lemmatized_text = "wie bereits bekennen ," \
                                   " werden bei einer Übungstauchen der Frankfurter   Feuerwehr ," \
                                   " im Bereich der Alte Brücke ," \
                                   " im Main einen 250 kg   Fliegerbombe aus der 2 . Weltkrieg entdecken ."
        self.assertEqual(lemmatized_test_text, expected_lemmatized_text)

    def test_get_string_from_list(self):
        test_list = ["eins", "zwei", "()", "123", "~"]
        string_from_list = tt.get_string_from_list(test_list)
        expected_string = "eins zwei () 123 ~"
        self.assertEqual(string_from_list, expected_string)

    def test_clean_column(self):
        test_documents = pd.Series([" (em) In der Nacht von Sonntag (21.04.2019) auf Montag (22.04.2019)"
                                    " verirrte sich ein 26-jähriger mutmaßlicher Fahrraddieb in den Innenhof"
                                    " des 8. Polizeireviers. Seine Fahrt war damit beendet."
                                    " Gegen 02.15 Uhr nachts fiel den Polizeibeamten ein Fahrradfahrer"
                                    " im Innenhof des Polizeireviers auf. Ein unbekannter Mann drehte dort auf einem"
                                    " Damenrad eine Runde. Als er schließlich den Hof mit dem Zweirad verlassen wollte,"
                                    " kontrollierten die Beamten den jungen Mann. Sie fanden circa 0,52 Gramm Marihuana"
                                    " sowie einen Bolzenschneider bei ihm auf und stellten beides sicher.",
                                    "(ka) In der Nacht von Freitag auf Samstag trug ein 34-Jähriger nach einer"
                                    " körperlichen Auseinandersetzung in der Hanauer Landstraße schwere"
                                    " Schnittverletzungen davon. Die Kriminalpolizei sucht nach Zeugen des Vorfalls."
                                    " Gegen 01.45 Uhr gerieten vier Männer im Bereich des Union-Geländes aus bislang"
                                    " unbekannten Gründen aneinander. Die Streitigkeiten entwickelten sich zu einer"
                                    " Schlägerei, wobei ein 34-Jähriger von zwei der Männer mit einem scharfen"
                                    " Gegenstand verletzt wurde."])
        cleaned_test_documents = tt.clean_column(test_documents)
        expected_result = ["  em  in der nacht von sonntag   auf montag   verirrte sich ein  jähriger mutmaßlicher" \
                          " fahrraddieb in den innenhof des   polizeireviers  seine fahrt war damit beendet  gegen " \
                          "  uhr nachts fiel den polizeibeamten ein fahrradfahrer im innenhof des polizeireviers auf" \
                          "  ein unbekannter mann drehte dort auf einem damenrad eine runde  als er schließlich den hof" \
                          " mit dem zweirad verlassen wollte  kontrollierten die beamten den jungen mann  sie fanden" \
                          " circa   gramm marihuana sowie einen bolzenschneider bei ihm auf und stellten beides sicher ",
                           " ka  in der nacht von freitag auf samstag trug ein  jähriger nach einer körperlichen"
                           " auseinandersetzung in der hanauer landstraße schwere schnittverletzungen davon  die"
                           " kriminalpolizei sucht nach zeugen des vorfalls  gegen   uhr gerieten vier männer im bereich"
                           " des union geländes aus bislang unbekannten gründen aneinander  die streitigkeiten"
                           " entwickelten sich zu einer schlägerei  wobei ein  jähriger von zwei der männer mit einem"
                           " scharfen gegenstand verletzt wurde "]
        result = (cleaned_test_documents == expected_result).all()

        self.assertTrue(result)

    def test_split_compound_words(self):
        self.fail()

    def test_lemmatize_document_list(self):
        self.fail()


if __name__ == "__main__":
    unittest.main()

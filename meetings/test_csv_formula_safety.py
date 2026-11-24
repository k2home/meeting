from django.test import SimpleTestCase

from .topic_csv import _csv_value as topic_csv_value
from .user_csv import _csv_value as user_csv_value


class CsvFormulaSafetyTests(SimpleTestCase):
    def test_user_and_topic_exports_escape_formulas_after_leading_whitespace(self):
        dangerous_values = (
            "=1+1",
            " =1+1",
            "\t=1+1",
            "\r\n=1+1",
            "  @SUM(A1:A2)",
            "\n-1+2",
        )
        for sanitizer in (user_csv_value, topic_csv_value):
            for value in dangerous_values:
                with self.subTest(sanitizer=sanitizer.__module__, value=repr(value)):
                    self.assertEqual(sanitizer(value), "'" + value)

    def test_user_and_topic_exports_leave_ordinary_text_unchanged(self):
        ordinary_values = ("Besprechungsreihe", "Ada Lovelace", "  normaler Text", "")
        for sanitizer in (user_csv_value, topic_csv_value):
            for value in ordinary_values:
                with self.subTest(sanitizer=sanitizer.__module__, value=repr(value)):
                    self.assertEqual(sanitizer(value), value)

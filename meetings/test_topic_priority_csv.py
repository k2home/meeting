from django.test import TestCase

from .models import MeetingSeries, Topic
from .topic_csv import parse_topic_agenda_csv


class TopicPriorityCsvTests(TestCase):
    def setUp(self):
        self.series = MeetingSeries.objects.create(name="Prioritäts-CSV")

    def test_csv_import_parser_accepts_and_preserves_priority(self):
        content = (
            "record_type;series;topic_series;meeting_date;meeting_title;topic_title;"
            "topic_status;topic_priority;archive_previous_status;agenda_status\n"
            f"topic;;{self.series.name};;;;open;urgent;;\n"
        )

        rows, errors = parse_topic_agenda_csv(content)

        self.assertEqual(errors, [])
        self.assertEqual(rows[0]["topic"]["priority"], "urgent")

    def test_csv_import_parser_rejects_unknown_priority(self):
        content = (
            "record_type;series;topic_series;meeting_date;meeting_title;topic_title;"
            "topic_status;topic_priority;archive_previous_status;agenda_status\n"
            f"topic;;{self.series.name};;;;open;critical;;\n"
        )

        rows, errors = parse_topic_agenda_csv(content)

        self.assertEqual(rows, [])
        self.assertTrue(any("topic_priority" in error for error in errors))

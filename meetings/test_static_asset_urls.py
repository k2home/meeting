from django.conf import settings
from django.templatetags.static import static
from django.test import SimpleTestCase


class StaticAssetUrlTests(SimpleTestCase):
    def test_static_url_is_root_relative(self):
        self.assertEqual(settings.STATIC_URL, "/static/")

    def test_static_assets_resolve_from_nested_pages(self):
        self.assertEqual(
            static("meetings/favicon.svg"),
            "/static/meetings/favicon.svg",
        )

from pathlib import Path

from django.test import SimpleTestCase

from .brand_colors import MINIMUM_CONTRAST, accessible_button_colors, contrast_ratio


class DynamicBrandTextContrastTests(SimpleTestCase):
    def test_button_text_meets_wcag_aa_for_light_and_dark_brand_colors(self):
        for background in ("#00549F", "#8FC5FF", "#FFCC00", "#FFFFFF", "#111111", "#777777"):
            with self.subTest(background=background):
                result = accessible_button_colors(background)
                self.assertGreaterEqual(
                    contrast_ratio(result["text"], result["background"]),
                    MINIMUM_CONTRAST,
                )

    def test_base_template_recalculates_only_branded_action_text(self):
        template = (
            Path(__file__).resolve().parent.parent
            / "templates/meetings/base.html"
        ).read_text(encoding="utf-8")

        self.assertIn('const selectors = [', template)
        self.assertIn('record.attributeName === "data-theme"', template)
        self.assertIn("if (refreshAll) refresh(document);", template)
        self.assertIn('".sidebar .nav-links a"', template)
        self.assertNotIn("apply(document.body)", template)
        self.assertNotIn('querySelectorAll("*")', template)

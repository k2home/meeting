from django.test import SimpleTestCase

from .brand_colors import accessible_button_colors, contrast_ratio


class AccessibleBrandButtonColorTests(SimpleTestCase):
    def test_keeps_original_color_when_white_text_meets_wcag_aa(self):
        result = accessible_button_colors("#00549F")
        self.assertEqual(result["background"], "#00549F")
        self.assertEqual(result["text"], "#FFFFFF")
        self.assertGreaterEqual(result["contrast"], 4.5)

    def test_uses_dark_text_for_light_custom_color(self):
        result = accessible_button_colors("#FFCC00")
        self.assertEqual(result["background"], "#FFCC00")
        self.assertEqual(result["text"], "#243247")
        self.assertGreaterEqual(result["contrast"], 4.5)

    def test_adjusts_custom_color_when_neither_text_color_is_sufficient(self):
        result = accessible_button_colors("#777777")
        self.assertNotEqual(result["background"], "#777777")
        self.assertGreaterEqual(contrast_ratio(result["text"], result["background"]), 4.5)

from django.test import SimpleTestCase

from .brand_colors import accessible_button_colors, contrast_ratio


class AccessibleBrandButtonColorTests(SimpleTestCase):
    def test_preserves_dark_brand_color_and_uses_white_text(self):
        result = accessible_button_colors("#00549F")
        self.assertEqual(result["background"], "#00549F")
        self.assertEqual(result["text"], "#FFFFFF")
        self.assertGreaterEqual(result["contrast"], 4.5)

    def test_preserves_light_custom_color_and_uses_dark_text(self):
        result = accessible_button_colors("#FFCC00")
        self.assertEqual(result["background"], "#FFCC00")
        self.assertEqual(result["text"], "#243247")
        self.assertGreaterEqual(result["contrast"], 4.5)

    def test_preserves_mid_gray_and_uses_black_text_for_wcag_aa(self):
        result = accessible_button_colors("#777777")
        self.assertEqual(result["background"], "#777777")
        self.assertEqual(result["text"], "#000000")
        self.assertGreaterEqual(contrast_ratio(result["text"], result["background"]), 4.5)

    def test_never_changes_any_valid_custom_background(self):
        for color in ("#000000", "#FFFFFF", "#777777", "#FF00AA", "#00FFFF"):
            with self.subTest(color=color):
                self.assertEqual(accessible_button_colors(color)["background"], color.upper())

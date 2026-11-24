from pathlib import Path
from django.test import SimpleTestCase


class UpdateBranchConfirmationTests(SimpleTestCase):
    def test_feature_is_present_in_template(self):
        template = Path(__file__).resolve().parent.parent / "templates/meetings/deployment_updates.html"
        source = template.read_text(encoding="utf-8")
        self.assertIn("update-branch-confirmation", source)
        self.assertIn('button[name="action"][value="disable-testing"]', source)
        self.assertIn('form.dataset.confirmApproved = "true"', source)

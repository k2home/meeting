from io import BytesIO
from zipfile import ZipFile

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from .forms import AttachmentForm


def office_document_bytes(part):
    buffer = BytesIO()
    with ZipFile(buffer, "w") as archive:
        archive.writestr("[Content_Types].xml", "<Types/>")
        archive.writestr(part, "<document/>")
    return buffer.getvalue()


class AttachmentContentValidationTests(TestCase):
    def make_form(self, filename, content):
        uploaded = SimpleUploadedFile(filename, content)
        return AttachmentForm(
            data={"label": "Anlage", "network_path": ""},
            files={"uploaded_file": uploaded},
        )

    def test_rejects_mismatched_pdf_extension(self):
        form = self.make_form("not-a-pdf.pdf", b"<html>not a PDF</html>")
        self.assertFalse(form.is_valid())
        self.assertIn("uploaded_file", form.errors)

    def test_rejects_fake_office_document(self):
        form = self.make_form("fake.docx", b"PK this is not a ZIP archive")
        self.assertFalse(form.is_valid())
        self.assertIn("uploaded_file", form.errors)

    def test_accepts_pdf_with_pdf_signature(self):
        form = self.make_form("protocol.pdf", b"%PDF-1.7\nminimal test")
        self.assertTrue(form.is_valid(), form.errors)

    def test_accepts_docx_with_required_package_parts(self):
        form = self.make_form(
            "document.docx",
            office_document_bytes("word/document.xml"),
        )
        self.assertTrue(form.is_valid(), form.errors)

    def test_rejects_binary_text_file(self):
        form = self.make_form("binary.txt", b"plain text\x00executable")
        self.assertFalse(form.is_valid())
        self.assertIn("uploaded_file", form.errors)

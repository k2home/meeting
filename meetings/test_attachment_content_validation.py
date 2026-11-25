from io import BytesIO
from pathlib import Path
import tempfile
from zipfile import ZipFile
from unittest.mock import patch

from django.core.exceptions import ValidationError
from django.test import override_settings

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from .antivirus import scan_uploaded_file
from .forms import AttachmentForm
from .models import OrganizationSettings


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

    def test_accepts_png_with_png_signature(self):
        form = self.make_form("image.png", b"\x89PNG\r\n\x1a\nminimal")
        self.assertTrue(form.is_valid(), form.errors)

    def test_accepts_jpeg_with_jpeg_signature(self):
        form = self.make_form("image.jpg", b"\xff\xd8\xffminimal")
        self.assertTrue(form.is_valid(), form.errors)

    @override_settings(CLAMD_ENABLED=True, CLAMD_HOST="127.0.0.1", CLAMD_PORT=3310)
    def test_clamav_clean_response_allows_upload(self):
        class FakeClamdSocket:
            def __init__(self):
                self.sent = []
            def __enter__(self):
                return self
            def __exit__(self, *args):
                return False
            def settimeout(self, value):
                self.timeout = value
            def sendall(self, value):
                self.sent.append(value)
            def recv(self, size):
                return b"stream: OK\0"

        uploaded = SimpleUploadedFile("clean.txt", b"hello")
        fake = FakeClamdSocket()
        with patch("meetings.antivirus.socket.create_connection", return_value=fake):
            scan_uploaded_file(uploaded)

        self.assertEqual(fake.sent[0], b"zINSTREAM\0")
        self.assertEqual(fake.sent[1], (5).to_bytes(4, "big"))
        self.assertEqual(fake.sent[2], b"hello")
        self.assertEqual(fake.sent[3], b"\0\0\0\0")

    @override_settings(CLAMD_ENABLED=True, CLAMD_HOST="127.0.0.1", CLAMD_PORT=3310)
    def test_clamav_detected_malware_rejects_upload(self):
        class FakeClamdSocket:
            def __enter__(self):
                return self
            def __exit__(self, *args):
                return False
            def settimeout(self, value):
                pass
            def sendall(self, value):
                pass
            def recv(self, size):
                return b"stream: Eicar-Test-Signature FOUND\0"

        uploaded = SimpleUploadedFile("infected.txt", b"test")
        with patch("meetings.antivirus.socket.create_connection", return_value=FakeClamdSocket()):
            with self.assertRaisesMessage(ValidationError, "Schadsoftware"):
                scan_uploaded_file(uploaded)

    @override_settings(CLAMD_ENABLED=True, CLAMD_HOST="127.0.0.1", CLAMD_PORT=3310)
    def test_clamav_unavailable_fails_closed(self):
        uploaded = SimpleUploadedFile("unscanned.txt", b"test")
        with patch("meetings.antivirus.socket.create_connection", side_effect=OSError("offline")):
            with self.assertRaisesMessage(ValidationError, "Scanner"):
                scan_uploaded_file(uploaded)

    @override_settings(CLAMD_ENABLED=False)
    def test_clamav_disabled_skips_connection(self):
        uploaded = SimpleUploadedFile("dev.txt", b"test")
        with patch("meetings.antivirus.socket.create_connection") as connect:
            scan_uploaded_file(uploaded)
        connect.assert_not_called()

    def test_production_installers_enable_private_clamav_scanning(self):
        root = Path(__file__).resolve().parent.parent
        compose = (root / "docker" / "compose.yaml").read_text(encoding="utf-8")
        installer = (root / "deploy" / "install-debian.sh").read_text(encoding="utf-8")

        self.assertIn("image: clamav/clamav:stable", compose)
        self.assertIn('CLAMD_ENABLED: "1"', compose)
        self.assertIn("CLAMD_HOST: clamav", compose)
        self.assertIn("clamav-daemon clamav-freshclam", installer)
        self.assertIn('set_env_value "CLAMD_ENABLED" "1"', installer)
        self.assertIn("TCPAddr 127.0.0.1", installer)

    def test_organization_logo_upload_is_scanned(self):
        logo = SimpleUploadedFile("logo.svg", b"<svg xmlns='http://www.w3.org/2000/svg'/>")
        with tempfile.TemporaryDirectory() as media_dir, override_settings(MEDIA_ROOT=media_dir):
            with patch("meetings.antivirus.scan_uploaded_file") as scan:
                OrganizationSettings(logo=logo).save()
            scan.assert_called_once()

    def test_organization_logo_size_is_limited_before_scanning(self):
        logo = SimpleUploadedFile("logo.svg", b"x" * (2 * 1024 * 1024 + 1))
        with patch("meetings.antivirus.scan_uploaded_file") as scan:
            with self.assertRaisesMessage(ValidationError, "2 MB"):
                OrganizationSettings(logo=logo).save()
        scan.assert_not_called()

    def test_organization_logo_rejects_active_svg_content(self):
        logo = SimpleUploadedFile(
            "logo.svg",
            b"<svg xmlns='http://www.w3.org/2000/svg'><script>alert(1)</script></svg>",
        )
        with tempfile.TemporaryDirectory() as media_dir, override_settings(MEDIA_ROOT=media_dir):
            with self.assertRaisesMessage(ValidationError, "aktive Inhalte"):
                OrganizationSettings(logo=logo).save()

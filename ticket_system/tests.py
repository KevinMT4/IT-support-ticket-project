from django.test import TestCase
import io
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient

User = get_user_model()


class PDFGenerationTests(TestCase):
    def setUp(self):
        # create a superuser to access the report endpoint
        self.superuser = User.objects.create_user(
            username="admin",
            password="password123",
            rol="superuser",
            is_staff=True,
            is_superuser=True,
        )
        # use DRF client so token auth works
        self.client = APIClient()
        self.client.force_authenticate(user=self.superuser)

    def test_pdf_stats_spanish_default(self):
        """When requesting statistics pdf with lang=es we expect Spanish title."""
        url = reverse('pdf_estadisticas') + '?lang=es'
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp['Content-Type'], 'application/pdf')
        # parse PDF and look for Spanish title
        from PyPDF2 import PdfReader
        reader = PdfReader(io.BytesIO(resp.content))
        text = "".join(page.extract_text() or "" for page in reader.pages)
        self.assertIn('Reporte Semanal de Tickets', text)

    def test_pdf_stats_english(self):
        """Requesting with lang=en should embed English headings."""
        url = reverse('pdf_estadisticas') + '?lang=en'
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp['Content-Type'], 'application/pdf')
        from PyPDF2 import PdfReader
        reader = PdfReader(io.BytesIO(resp.content))
        text = "".join(page.extract_text() or "" for page in reader.pages)
        self.assertIn('Weekly Ticket Report', text)

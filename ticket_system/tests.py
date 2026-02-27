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

    def test_motivo_translation_via_api_header(self):
        """When requesting motivos with Accept-Language en the name should be English."""
        # create a couple of motivos including one with an english name
        dept = self.superuser.departamento or None
        if not dept:
            from ticket_system.models import Departamento
            dept = Departamento.objects.create(nombre='Test Dept', gerente='', email='')
        from ticket_system.models import Motivo
        m1 = Motivo.objects.create(nombre='Prueba', nombre_en='Test', departamento=dept)
        url = reverse('motivo-list')
        resp = self.client.get(url, HTTP_ACCEPT_LANGUAGE='en')
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        # find our motivo in response
        found = next((m for m in data if m['id'] == m1.id), None)
        self.assertIsNotNone(found)
        self.assertEqual(found['nombre'], 'Test')

    def test_ticket_pdf_includes_translated_reason(self):
        """Ticket detail PDF should show motive in chosen language."""
        from ticket_system.models import Motivo, Departamento, Ticket, Usuario
        dept = Departamento.objects.create(nombre='Dept2', gerente='', email='')
        motivo = Motivo.objects.create(nombre='Contraseñas', nombre_en='Passwords', departamento=dept)
        user = Usuario.objects.create_user(
            username='user1', password='pass', rol='user', email='u@x.com'
        )
        ticket = Ticket.objects.create(
            usuario=user,
            departamento=dept,
            motivo=motivo,
            asunto='Hi',
            contenido='Hello',
        )
        url = reverse('pdf_ticket', args=[ticket.id]) + '?lang=en'
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        from PyPDF2 import PdfReader
        reader = PdfReader(io.BytesIO(resp.content))
        text = "".join(page.extract_text() or "" for page in reader.pages)
        self.assertIn('Passwords', text)

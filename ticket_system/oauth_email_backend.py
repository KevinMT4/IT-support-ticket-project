import os
import base64
import pickle
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from django.core.mail.backends.base import BaseEmailBackend
from django.conf import settings
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


SCOPES = ['https://www.googleapis.com/auth/gmail.send']


class OAuth2EmailBackend(BaseEmailBackend):
    """
    Backend de email que usa OAuth2 para autenticarse con Gmail.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.creds = None
        self.service = None

    def _get_credentials(self):
        """Obtiene las credenciales OAuth2 desde el archivo token.pickle o genera nuevas."""
        token_path = os.path.join(settings.BASE_DIR, 'token.pickle')
        credentials_path = os.path.join(settings.BASE_DIR, 'credentials.json')

        if os.path.exists(token_path):
            with open(token_path, 'rb') as token:
                self.creds = pickle.load(token)

        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                try:
                    self.creds.refresh(Request())
                except Exception as e:
                    print(f"Error refrescando token: {e}")
                    self.creds = None

            if not self.creds:
                if not os.path.exists(credentials_path):
                    raise FileNotFoundError(
                        f"No se encontró el archivo credentials.json en {credentials_path}. "
                        "Por favor, descarga las credenciales desde Google Cloud Console."
                    )

                flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
                self.creds = flow.run_local_server(port=0)

            with open(token_path, 'wb') as token:
                pickle.dump(self.creds, token)

        return self.creds

    def _get_service(self):
        """Obtiene el servicio de Gmail API."""
        if not self.service:
            creds = self._get_credentials()
            self.service = build('gmail', 'v1', credentials=creds)
        return self.service

    def send_messages(self, email_messages):
        """Envía una lista de mensajes de email."""
        if not email_messages:
            return 0

        try:
            service = self._get_service()
            num_sent = 0

            for message in email_messages:
                try:
                    mime_message = self._create_mime_message(message)
                    raw_message = base64.urlsafe_b64encode(mime_message.as_bytes()).decode('utf-8')
                    send_message = {'raw': raw_message}

                    service.users().messages().send(userId='me', body=send_message).execute()
                    num_sent += 1
                except HttpError as error:
                    if not self.fail_silently:
                        raise
                    print(f"Error enviando email: {error}")

            return num_sent
        except Exception as e:
            if not self.fail_silently:
                raise
            print(f"Error en OAuth2EmailBackend: {e}")
            return 0

    def _create_mime_message(self, email_message):
        """Crea un mensaje MIME desde un EmailMessage de Django."""
        if email_message.alternatives:
            message = MIMEMultipart('alternative')
        else:
            message = MIMEMultipart()

        message['To'] = ', '.join(email_message.to)
        message['From'] = email_message.from_email or settings.DEFAULT_FROM_EMAIL
        message['Subject'] = email_message.subject

        if email_message.cc:
            message['Cc'] = ', '.join(email_message.cc)
        if email_message.bcc:
            message['Bcc'] = ', '.join(email_message.bcc)

        if email_message.reply_to:
            message['Reply-To'] = ', '.join(email_message.reply_to)

        text_part = MIMEText(email_message.body, 'plain')
        message.attach(text_part)

        if hasattr(email_message, 'alternatives') and email_message.alternatives:
            for content, mimetype in email_message.alternatives:
                if mimetype == 'text/html':
                    html_part = MIMEText(content, 'html')
                    message.attach(html_part)

        if hasattr(email_message, 'attachments') and email_message.attachments:
            for attachment in email_message.attachments:
                if isinstance(attachment, MIMEImage):
                    message.attach(attachment)
                else:
                    from email.mime.base import MIMEBase
                    from email import encoders

                    filename, content, mimetype = attachment
                    maintype, subtype = mimetype.split('/', 1)

                    if maintype == 'text':
                        part = MIMEText(content, _subtype=subtype)
                    elif maintype == 'image':
                        part = MIMEImage(content, _subtype=subtype)
                    else:
                        part = MIMEBase(maintype, subtype)
                        part.set_payload(content)
                        encoders.encode_base64(part)

                    part.add_header('Content-Disposition', f'attachment; filename="{filename}"')
                    message.attach(part)

        return message

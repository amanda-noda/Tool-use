"""Ferramenta de e-mail (Gmail)."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
import config


class EmailTool:
    def __init__(self):
        self.service = None
        self._init_service()

    def _init_service(self):
        if not config.GOOGLE_EMAIL_ENABLED or not config.GOOGLE_CREDENTIALS_PATH.exists():
            return
        try:
            from google.oauth2.credentials import Credentials
            from google_auth_oauthlib.flow import InstalledAppFlow
            from google.auth.transport.requests import Request
            from googleapiclient.discovery import build

            SCOPES = ["https://www.googleapis.com/auth/gmail.send"]
            creds = None
            if config.GOOGLE_EMAIL_TOKEN_PATH.exists():
                creds = Credentials.from_authorized_user_file(str(config.GOOGLE_EMAIL_TOKEN_PATH), SCOPES)
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file(str(config.GOOGLE_CREDENTIALS_PATH), SCOPES)
                    creds = flow.run_local_server(port=0)
                with open(config.GOOGLE_EMAIL_TOKEN_PATH, "w") as token:
                    token.write(creds.to_json())
            self.service = build("gmail", "v1", credentials=creds)
        except Exception as e:
            print(f"[E-mail] Erro: {e}")

    def is_available(self):
        return self.service is not None

    def send_email(self, to, subject, body):
        if not self.is_available():
            return "E-mail nao configurado."
        import base64
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart
        from googleapiclient.errors import HttpError
        try:
            message = MIMEMultipart()
            message["to"] = to
            message["subject"] = subject
            message.attach(MIMEText(body, "plain", "utf-8"))
            raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
            self.service.users().messages().send(userId="me", body={"raw": raw}).execute()
            return f"E-mail enviado para {to}"
        except HttpError as e:
            return f"Erro: {e}"

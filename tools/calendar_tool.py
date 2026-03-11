"""Ferramenta de calendario (Google Calendar)."""
import sys
from pathlib import Path
from datetime import datetime, timedelta

sys.path.insert(0, str(Path(__file__).parent.parent))
import config


def _format_event(date_str: str, title: str) -> str:
    """Formata um evento para exibicao."""
    return f"- {date_str} — {title}"


def _get_demo_events(days_ahead: int) -> str:
    """Retorna eventos de demonstracao quando o Google Calendar nao esta configurado."""
    now = datetime.now()
    demo = [
        (now + timedelta(hours=2), "Reuniao com equipe"),
        (now + timedelta(days=1, hours=10), "Consulta medica"),
        (now + timedelta(days=2, hours=14), "Apresentacao do projeto"),
        (now + timedelta(days=3, hours=9), "Cafe com cliente"),
        (now + timedelta(days=5, hours=16), "Treino na academia"),
    ]
    lines = [_format_event(e[0].strftime("%d/%m %H:%M"), e[1]) for e in demo]
    header = f"Eventos dos proximos {days_ahead} dias (modo demonstracao):\n\n"
    return header + "\n".join(lines)


class CalendarTool:
    def __init__(self):
        self.service = None
        self._init_service()

    def _init_service(self):
        if not config.GOOGLE_CALENDAR_ENABLED or not config.GOOGLE_CREDENTIALS_PATH.exists():
            return
        try:
            from google.oauth2.credentials import Credentials
            from google_auth_oauthlib.flow import InstalledAppFlow
            from google.auth.transport.requests import Request
            from googleapiclient.discovery import build

            SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]
            creds = None
            if config.GOOGLE_CALENDAR_TOKEN_PATH.exists():
                creds = Credentials.from_authorized_user_file(str(config.GOOGLE_CALENDAR_TOKEN_PATH), SCOPES)
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file(str(config.GOOGLE_CREDENTIALS_PATH), SCOPES)
                    creds = flow.run_local_server(port=0)
                with open(config.GOOGLE_CALENDAR_TOKEN_PATH, "w") as token:
                    token.write(creds.to_json())
            self.service = build("calendar", "v3", credentials=creds)
        except Exception as e:
            print(f"[Calendario] Erro: {e}")

    def is_available(self):
        return self.service is not None

    def get_events(self, days_ahead=7, max_results=10):
        if not self.is_available():
            return _get_demo_events(days_ahead)
        from googleapiclient.errors import HttpError
        try:
            now = datetime.utcnow()
            time_min = now.isoformat() + "Z"
            time_max = (now + timedelta(days=days_ahead)).isoformat() + "Z"
            events_result = self.service.events().list(
                calendarId="primary",
                timeMin=time_min,
                timeMax=time_max,
                maxResults=max_results,
                singleEvents=True,
                orderBy="startTime",
            ).execute()
            events = events_result.get("items", [])
            if not events:
                return f"Nenhum evento nos proximos {days_ahead} dias."
            return "\n".join(f"- {e['start'].get('dateTime', e['start'].get('date', '?'))[:16]} - {e.get('summary', 'Sem titulo')}" for e in events)
        except HttpError as e:
            return f"Erro: {e}"

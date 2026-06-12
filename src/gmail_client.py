"""Gmail API client for sending and reading review emails."""

from __future__ import annotations

import base64
import os
from email.mime.text import MIMEText

from dotenv import load_dotenv
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

load_dotenv()

SCOPES = [
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.readonly",
]


def get_gmail_service():
    creds_path = os.environ["GMAIL_CREDENTIALS_PATH"]
    token_path = os.environ["GMAIL_TOKEN_PATH"]

    creds = None
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(creds_path, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(token_path, "w") as f:
            f.write(creds.to_json())

    return build("gmail", "v1", credentials=creds)


def send_message(to: str, subject: str, body_plain: str) -> dict:
    """Send a plain-text email. Returns Gmail API message resource (id, threadId)."""
    service = get_gmail_service()

    message = MIMEText(body_plain, "plain", "utf-8")
    message["to"] = to
    message["subject"] = subject

    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
    return (
        service.users()
        .messages()
        .send(userId="me", body={"raw": raw})
        .execute()
    )

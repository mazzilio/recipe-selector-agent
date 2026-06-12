import os
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

service = build("gmail", "v1", credentials=creds)
profile = service.users().getProfile(userId="me").execute()
print("Success! Logged in as:", profile["emailAddress"])
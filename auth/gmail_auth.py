"""Gmail OAuth2 authentication and service construction."""
import os

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Scopes required by the agent:
#   - gmail.modify : list, read, label/archive, trash, mark-as-read
#   - gmail.compose: create draft replies
SCOPES = [
    "https://www.googleapis.com/auth/gmail.modify",
    "https://www.googleapis.com/auth/gmail.compose",
]


def get_gmail_service(
    credentials_file: str = "credentials.json",
    token_file: str = "token.json",
):
    """Return an authenticated Gmail API service resource.

    On the first run this opens a browser window for OAuth2 consent and
    saves the resulting token to *token_file*.  Subsequent runs load and
    refresh the token automatically.

    Args:
        credentials_file: Path to the OAuth2 client-secrets JSON downloaded
            from Google Cloud Console.
        token_file: Path where the user token is persisted between runs.

    Returns:
        A ``googleapiclient`` Resource object for the Gmail v1 API.
    """
    creds: Credentials | None = None

    if os.path.exists(token_file):
        creds = Credentials.from_authorized_user_file(token_file, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(credentials_file):
                raise FileNotFoundError(
                    f"credentials.json not found at '{credentials_file}'. "
                    "Download it from Google Cloud Console → APIs & Services → "
                    "Credentials → your OAuth2 client."
                )
            flow = InstalledAppFlow.from_client_secrets_file(
                credentials_file, SCOPES
            )
            creds = flow.run_local_server(port=0)

        with open(token_file, "w", encoding="utf-8") as fh:
            fh.write(creds.to_json())

    return build("gmail", "v1", credentials=creds)
